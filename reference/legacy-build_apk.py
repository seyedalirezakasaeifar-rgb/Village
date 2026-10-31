#!/usr/bin/env python3
"""Standalone Android WebView APK assembler. Uses no Android SDK; emits dex035, AXML and v2 signing."""
import os, struct, hashlib, zlib, zipfile, io, datetime
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID
from cryptography import x509
P=Path(__file__).resolve().parent
u16=lambda v:struct.pack('<H',v)
u32=lambda v:struct.pack('<I',v)
u64=lambda v:struct.pack('<Q',v)
NONE=0xffffffff

def leb(n):
    out=bytearray()
    while True:
        b=n&127;n>>=7
        if n:b|=128
        out.append(b)
        if not n:return bytes(out)

def align(buf,a=4):buf.extend(b'\0'*(-len(buf)%a))

# Minimal Dalvik class - hand emitted; bytecode calls platform WebView APIs.
def build_dex():
    activity='Lorg/townledger/android/MainActivity;'
    A='Landroid/app/Activity;';B='Landroid/os/Bundle;';C='Landroid/content/Context;'
    W='Landroid/webkit/WebView;';S='Landroid/webkit/WebSettings;';
    V='Landroid/view/View;';J='Ljava/lang/String;'; VOID='V';Z='Z'
    protos=[(VOID,()),(VOID,(B,)),(VOID,(C,)),(S,()),(VOID,(Z,)),(VOID,(J,)),(VOID,(V,))]
    methods=[(A,'<init>',(VOID,())),(A,'onCreate',(VOID,(B,))),(A,'setContentView',(VOID,(V,))),
       (W,'<init>',(VOID,(C,))),(W,'getSettings',(S,())),
       (S,'setJavaScriptEnabled',(VOID,(Z,))),(S,'setDomStorageEnabled',(VOID,(Z,))),
       (W,'loadUrl',(VOID,(J,))), (activity,'<init>',(VOID,())),(activity,'onCreate',(VOID,(B,)))]
    all_types=sorted({activity,A,B,C,W,S,V,J,VOID,Z})
    short=lambda x:'L' if x[0]=='L' else x
    urls=['file:///android_asset/index.html']
    strs=sorted(set(all_types+[m[1] for m in methods]+[''.join([short(p[0])]+[short(t) for t in p[1]]) for p in protos]+urls))
    si={v:i for i,v in enumerate(strs)}
    types=sorted(all_types,key=lambda s:si[s]);ti={v:i for i,v in enumerate(types)}
    protos=sorted(protos,key=lambda p:(ti[p[0]],tuple(ti[t] for t in p[1])));pi={v:i for i,v in enumerate(protos)}
    methods=sorted(methods,key=lambda m:(ti[m[0]],si[m[1]],pi[m[2]]));mi={v:i for i,v in enumerate(methods)}
    buf=bytearray(b'\0'*0x70)
    def reserve(n):
        align(buf);o=len(buf);buf.extend(b'\0'*n);return o
    sids=reserve(len(strs)*4);tids=reserve(len(types)*4);pids=reserve(len(protos)*12);mids=reserve(len(methods)*8);cdefs=reserve(32)
    data_off=len(buf)
    string_data_off={}
    for s in strs:
        off=len(buf);string_data_off[s]=off;v=s.encode('utf8');buf.extend(leb(len(s))+v+b'\0')
    type_list_off={}
    for proto in protos:
        if not proto[1]:continue
        align(buf);o=len(buf);type_list_off[proto]=o
        buf.extend(u32(len(proto[1]))+b''.join(u16(ti[t]) for t in proto[1]));align(buf)
    align(buf)
    code_start=len(buf)
    def invoke(op, method, regs):
        i=mi[method];assert max(regs,default=0)<16 and len(regs)<=5
        rr=regs+[0]*(5-len(regs));return [op | (len(regs)<<12) | (rr[4]<<8),i,rr[0]|(rr[1]<<4)|(rr[2]<<8)|(rr[3]<<12)]
    def ins(op,a=0):return op|(a<<8)
    ctor=invoke(0x70,(A,'<init>',(VOID,())),[0])+[0x000e]
    main=[]
    main+=invoke(0x6f,(A,'onCreate',(VOID,(B,))),[3,4]) # invoke-super
    main += [ins(0x22,0),ti[W]] # new-instance v0
    main += invoke(0x70,(W,'<init>',(VOID,(C,))),[0,3])
    main += invoke(0x6e,(W,'getSettings',(S,())),[0])
    main += [ins(0x0c,1)] # move-result-object v1
    main += [0x1212] # const/4 v2, 1
    main += invoke(0x6e,(S,'setJavaScriptEnabled',(VOID,(Z,))),[1,2])
    main += invoke(0x6e,(S,'setDomStorageEnabled',(VOID,(Z,))),[1,2])
    main += [ins(0x1a,2),si[urls[0]]] # const-string v2
    main += invoke(0x6e,(W,'loadUrl',(VOID,(J,))),[0,2])
    main += invoke(0x6e,(A,'setContentView',(VOID,(V,))),[3,0])
    main += [0x000e]
    code_offsets={}
    for name,registers,ins_size,words in [('constructor',1,1,ctor),('onCreate',5,2,main)]:
        align(buf);code_offsets[name]=len(buf)
        buf.extend(struct.pack('<HHHHII',registers,ins_size,2,0,0,len(words)))
        buf.extend(b''.join(u16(w) for w in words))
    class_data_off=len(buf)
    ctr_id=mi[(activity,'<init>',(VOID,()))]
    on_id=mi[(activity,'onCreate',(VOID,(B,)))]
    buf.extend(leb(0)+leb(0)+leb(1)+leb(1)+leb(ctr_id)+leb(1|0x10000)+leb(code_offsets['constructor'])+leb(on_id)+leb(1)+leb(code_offsets['onCreate']))
    align(buf)
    map_off=len(buf)
    maps=[(0x0000,1,0),(0x0001,len(strs),sids),(0x0002,len(types),tids),(0x0003,len(protos),pids),
          (0x0005,len(methods),mids),(0x0006,1,cdefs),(0x2002,len(strs),min(string_data_off.values())),
          (0x1001,len(type_list_off),min(type_list_off.values()) if type_list_off else 0),
          (0x2001,2,code_start),(0x2000,1,class_data_off),(0x1000,1,map_off)]
    maps=[x for x in maps if x[1]]
    maps=sorted(maps,key=lambda x:x[2]);buf.extend(u32(len(maps)))
    for typ,num,off in maps:buf.extend(struct.pack('<HHII',typ,0,num,off))
    for idx,s in enumerate(strs):struct.pack_into('<I',buf,sids+idx*4,string_data_off[s])
    for idx,t in enumerate(types):struct.pack_into('<I',buf,tids+idx*4,si[t])
    for idx,p in enumerate(protos):
        shorty=''.join([short(p[0])]+[short(t) for t in p[1]])
        struct.pack_into('<III',buf,pids+idx*12,si[shorty],ti[p[0]],type_list_off.get(p,0))
    for idx,m in enumerate(methods):struct.pack_into('<HHI',buf,mids+idx*8,ti[m[0]],pi[m[2]],si[m[1]])
    struct.pack_into('<IIIIIIII',buf,cdefs,ti[activity],1,ti[A],0,NONE,0,class_data_off,0)
    # header
    buf[0:8]=b'dex\n035\0'
    struct.pack_into('<IIIIIIIIIIIIIIIIIIII',buf,0x20,len(buf),0x70,0x12345678,0,0,map_off,len(strs),sids,len(types),tids,len(protos),pids,0,0,len(methods),mids,1,cdefs,len(buf)-data_off,data_off)
    buf[12:32]=hashlib.sha1(buf[32:]).digest();struct.pack_into('<I',buf,8,zlib.adler32(buf[12:])&0xffffffff)
    return bytes(buf)

# Compile a resource-free Android binary manifest (AXML).
def build_manifest():
    android='http://schemas.android.com/apk/res/android';pkg='org.townledger.android'
    res={'name':0x01010003,'label':0x01010001,'versionCode':0x0101021b,'versionName':0x0101021c,
         'minSdkVersion':0x0101020c,'targetSdkVersion':0x01010270,'exported':0x01010010,
         'screenOrientation':0x0101001e,'hardwareAccelerated':0x010102d3,'theme':0x01010000}
    S=['android',android,'manifest','uses-sdk','application','activity','intent-filter','action','category',
       'package',pkg,'TownLedger: The Living Borough','android.intent.action.MAIN','android.intent.category.LAUNCHER',
       'versionCode','versionName','minSdkVersion','targetSdkVersion','name','label','exported','screenOrientation','hardwareAccelerated','theme','1','24','28','0','true',
       '5.6.0','org.townledger.android.MainActivity']
    # Theme reference is not necessary: use system default instead.
    S=list(dict.fromkeys(S));idx={s:i for i,s in enumerate(S)}
    def chunk(t,head,payload):return struct.pack('<HHI',t,head,8+len(payload))+payload
    def str_len(n):return bytes([n]) if n<=127 else bytes([(n>>8)|0x80,n&255])
    offsets=[];string_data=bytearray()
    for s in S:
        offsets.append(len(string_data));e=s.encode('utf-8');string_data.extend(str_len(len(s))+str_len(len(e))+e+b'\0')
    pool_data=b''.join(u32(x) for x in offsets)+string_data
    pool=struct.pack('<HHI',1,28,28+len(pool_data))+struct.pack('<IIIII',len(S),0,0x100,28+len(S)*4,0)+pool_data
    pool+=b'\0'*(-len(pool)%4);pool=pool[:4]+u32(len(pool))+pool[8:]
    # resource map maps string index -> resource name ID
    resources=[res.get(s,0) for s in S];resource_map=chunk(0x0180,8,b''.join(u32(x) for x in resources))
    def node(t,content):return chunk(t,16,u32(1)+u32(NONE)+content)
    def startns():return node(0x0100,u32(idx['android'])+u32(idx[android]))
    def endns():return node(0x0101,u32(idx['android'])+u32(idx[android]))
    def attr(k,value,typ,raw=None):
        raw_idx=idx[raw] if raw is not None else (idx[value] if isinstance(value,str) else NONE)
        data=idx[value] if typ==0x03 else value
        return (res[k],u32(idx[android])+u32(idx[k])+u32(raw_idx)+struct.pack('<HBBI',8,0,typ,data))
    def start(name,attrs=[]):
        attrs=sorted(attrs,key=lambda a:a[0]); body=u32(NONE)+u32(idx[name])+struct.pack('<HHHHHH',20,20,len(attrs),0,0,0)+b''.join(a[1] for a in attrs)
        return node(0x0102,body)
    def end(name):return node(0x0103,u32(NONE)+u32(idx[name]))
    def textattr(k,v):return attr(k,v,0x03)
    def boolattr(k,v):return attr(k,0xffffffff if v else 0,0x12)
    def intattr(k,v):return attr(k,v,0x10)
    m=bytearray(startns())
    m+=start('manifest',[(0,u32(NONE)+u32(idx['package'])+u32(idx[pkg])+struct.pack('<HBBI',8,0,0x03,idx[pkg])),
                         intattr('versionCode',11),textattr('versionName','5.6.0')])
    m+=start('uses-sdk',[intattr('minSdkVersion',24),intattr('targetSdkVersion',28)]);m+=end('uses-sdk')
    m+=start('application',[textattr('label','TownLedger: The Living Borough'),boolattr('hardwareAccelerated',True)])
    m+=start('activity',[textattr('name','org.townledger.android.MainActivity'),boolattr('exported',True),intattr('screenOrientation',0)])
    m+=start('intent-filter');m+=start('action',[textattr('name','android.intent.action.MAIN')]);m+=end('action')
    m+=start('category',[textattr('name','android.intent.category.LAUNCHER')]);m+=end('category')
    m+=end('intent-filter');m+=end('activity');m+=end('application');m+=end('manifest');m+=endns()
    data=pool+resource_map+m
    return struct.pack('<HHI',3,8,8+len(data))+data

def lp(d):return u32(len(d))+d

def apk_digest(sections):
    chunks=[]
    for sect in sections:
        for i in range(0,len(sect),1048576):
            c=sect[i:i+1048576];chunks.append(hashlib.sha256(b'\xa5'+u32(len(c))+c).digest())
    return hashlib.sha256(b'\x5a'+u32(len(chunks))+b''.join(chunks)).digest()

def sign_v2(unsigned,dest):
    from cryptography.hazmat.primitives.asymmetric import padding
    data=Path(unsigned).read_bytes()
    eocd=data.rfind(b'PK\x05\x06');assert eocd>=0
    cd_off=struct.unpack_from('<I',data,eocd+16)[0]
    assert cd_off<eocd and data[cd_off:cd_off+4]==b'PK\x01\x02'
    content_digest=apk_digest((data[:cd_off],data[cd_off:eocd],data[eocd:]))
    kp=P/'debug-signing-key.pem'; cp=P/'debug-signing-certificate.pem'
    if kp.exists():
        key=serialization.load_pem_private_key(kp.read_bytes(),password=None)
        cert=x509.load_pem_x509_certificate(cp.read_bytes())
    else:
        key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'TownLedger local build')])
        cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=1))
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=3650))
            .sign(key, hashes.SHA256()))
        kp.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
        cp.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    der=cert.public_bytes(serialization.Encoding.DER)
    signed_data=lp(lp(u32(0x0103)+lp(content_digest)))+lp(lp(der))+lp(b'')
    signature=key.sign(signed_data,padding.PKCS1v15(),hashes.SHA256())
    signer=lp(signed_data)+lp(lp(u32(0x0103)+lp(signature)))+lp(key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo))
    block_content=lp(lp(signer))
    pair=u64(len(block_content)+4)+u32(0x7109871a)+block_content
    size=len(pair)+24
    block=u64(size)+pair+u64(size)+b'APK Sig Block 42'
    e=bytearray(data[eocd:]);struct.pack_into('<I',e,16,cd_off+len(block))
    Path(dest).write_bytes(data[:cd_off]+block+data[cd_off:eocd]+e)
    # Independent v2 verification from actual output.
    verify=Path(dest).read_bytes();end=verify.rfind(b'PK\x05\x06');new_cd=struct.unpack_from('<I',verify,end+16)[0]
    assert verify[new_cd-16:new_cd]==b'APK Sig Block 42'
    assert verify[cd_off:cd_off+8]==u64(size)
    e2=bytearray(verify[end:]);struct.pack_into('<I',e2,16,cd_off)
    got=apk_digest((verify[:cd_off],verify[new_cd:end],e2))
    assert got==content_digest
    key.public_key().verify(signature,signed_data,padding.PKCS1v15(),hashes.SHA256())
    return hashlib.sha256(verify).hexdigest()

def main():
    assets=P/'assets';out=P/'TownLedger-The-Living-Borough-5.6.apk';tmp=P/'unsigned.apk'
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('AndroidManifest.xml',build_manifest(),compress_type=zipfile.ZIP_STORED)
        z.writestr('classes.dex',build_dex(),compress_type=zipfile.ZIP_STORED)
        for f in assets.rglob('*'):
            if f.is_file():z.write(f,arcname='assets/'+f.relative_to(assets).as_posix())
    digest=sign_v2(tmp,out)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert z.read('classes.dex')[:8]==b'dex\n035\0'
        assert b'TownLedger' in z.read('assets/index.html')
    print('Built:',out, 'size:',out.stat().st_size,'sha256:',digest)
if __name__=='__main__':main()
