from pathlib import Path
import struct,hashlib,zlib,zipfile
p=Path(__file__).resolve().parents[1]/'TownLedger-The-Living-Borough-5.6.apk'
def u16(d,o):return struct.unpack_from('<H',d,o)[0]
def u32(d,o):return struct.unpack_from('<I',d,o)[0]
def u64(d,o):return struct.unpack_from('<Q',d,o)[0]
def lp(d,o):n=u32(d,o);return (d[o+4:o+4+n],o+4+n)
def str8(data,off):
  def length(off):
    b=data[off];return ((b&127)*256+data[off+1],off+2) if b&128 else (b,off+1)
  n,off=length(off);b,off=length(off);return data[off:off+b].decode('utf8')
with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  d=z.read('classes.dex')
  assert d[:8]==b'dex\n035\x00'
  assert zlib.adler32(d[12:])&0xffffffff==u32(d,8)
  assert hashlib.sha1(d[32:]).digest()==d[12:32]
  assert u32(d,0x20)==len(d),len(d)
  print('DEX size',len(d),'header size',u32(d,0x24),'class defs',u32(d,0x60),'map_off',u32(d,0x34))
  # DEX table indices may not be > words, check class/super.
  si,so=u32(d,0x38),u32(d,0x3c)
  strings=[]
  for i in range(si):
    off=u32(d,so+i*4);n=d[off];k=off+1
    while d[k-1]&128:k+=1
    end=d.index(0,k);strings.append(d[k:end].decode())
  print('Strings',strings[:15]);assert 'Lorg/townledger/android/MainActivity;' in strings
  ti,to=u32(d,0x40),u32(d,0x44)
  typeids=[strings[u32(d,to+i*4)] for i in range(ti)];print('Types',typeids)
  assert 'Landroid/webkit/WebView;' in typeids
  mi,mo=u32(d,0x58),u32(d,0x5c)
  print('Methods',[(typeids[u16(d,mo+i*8)],strings[u32(d,mo+i*8+4)]) for i in range(mi)])
  # Check class_data and code headers
  co=u32(d,0x64);class_data_off=u32(d,co+24)
  assert class_data_off<len(d)
  print('class_data_off',class_data_off)
  ax=z.read('AndroidManifest.xml')
  assert u16(ax,0)==0x0003 and u32(ax,4)==len(ax)
  o=8;strings=[];nodes=[]
  while o<len(ax):
    tag=u16(ax,o);head=u16(ax,o+2);length=u32(ax,o+4)
    assert length>=head and length>0,(o,tag,length)
    if tag==1:
      count=u32(ax,o+8);start=u32(ax,o+20)
      print('pool',o,start,count);strings=[str8(ax,o+start+u32(ax,o+28+i*4)) for i in range(count)]
    elif tag==0x0102:
      n=strings[u32(ax,o+20)]; ac=u16(ax,o+28); attrs=[]
      for i in range(ac):
        off=o+16+u16(ax,o+24)+i*20
        nameidx=u32(ax,off+4);dataType=ax[off+15];value=u32(ax,off+16)
        attrs.append((strings[nameidx],strings[value] if dataType==3 else value))
      nodes.append((n,attrs))
    elif tag==0x0103:
      nodes.append(('/'+strings[u32(ax,o+20)],[]))
    o+=length
  print('Manifest',nodes)
  assert nodes[0][0]=='manifest'
  assert any(x[0]=='activity' and ('name','org.townledger.android.MainActivity') in x[1] for x in nodes)
  assert any(x[0]=='uses-sdk' and ('targetSdkVersion',28) in x[1] for x in nodes)
  assert 'assets/index.html' in z.namelist() and 'assets/game.js' in z.namelist()
  print('APK entries',z.namelist())
# Verify signature block and v2 signedData with independently parsed structure.
a=p.read_bytes();e=a.rfind(b'PK\x05\x06');cd=u32(a,e+16)
assert a[cd-16:cd]==b'APK Sig Block 42'
size=u64(a,cd-24);start=cd-size-8
assert start>=0 and u64(a,start)==size and a[start+8:start+16]!=b'\0'*8
print('Signing block offset',start,'size',size)
pair_len=u64(a,start+8);key=u32(a,start+16)
assert key==0x7109871a
v=a[start+20:start+16+pair_len];signerList,_=lp(v,0);signer,_=lp(signerList,0)
signed,pos=lp(signer,0);signatures,pos=lp(signer,pos);public,pos=lp(signer,pos)
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes,serialization
records,offset=lp(signed,0);record,_=lp(records,0)
alg=u32(record,0);digest,_=lp(record,4)
certs,off=lp(signed,offset);cert,_=lp(certs,0);certificate=x509.load_der_x509_certificate(cert)
sigr,_=lp(signatures,0);algorithm=u32(sigr,0);signature,_=lp(sigr,4)
assert alg==algorithm==0x0103
assert public==certificate.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
certificate.public_key().verify(signature,signed,padding.PKCS1v15(),hashes.SHA256())
# APK content digest: 1MB chunks of original content / central dir / corrected EOCD
ends=bytearray(a[e:]);struct.pack_into('<I',ends,16,start)
chunks=[]
for sect in [a[:start],a[cd:e],ends]:
  for i in range(0,len(sect),1048576):
    bit=sect[i:i+1048576];chunks.append(hashlib.sha256(b'\xa5'+struct.pack('<I',len(bit))+bit).digest())
actual=hashlib.sha256(b'\x5a'+struct.pack('<I',len(chunks))+b''.join(chunks)).digest()
assert actual==digest
print('APK v2 signature: GOOD; protected content digest: GOOD; SHA256',hashlib.sha256(a).hexdigest())
