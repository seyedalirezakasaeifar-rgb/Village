"""Real duplicate-preserving JSON fixtures exercise the production field guard on JVM."""
from pathlib import Path
import json,subprocess,tempfile,hashlib,os
ROOT=Path(__file__).resolve().parents[1]
class Pairs(list):pass
prefix='"id":1,"epoch":0,"ok":true,"admitted":true,"committed":true'
cases=[('valid','{'+prefix+',"result":{"persisted":true}}',True),('restore','{'+prefix+',"result":{"restored":true}}',True),('nullResult','{'+prefix+',"result":null}',True),('archiveText','{'+prefix+',"result":{"archive":"{\\"x\\":1,\\"x\\":2}"}}',True),('duplicateResult','{'+prefix+',"result":{"persisted":false},"result":{"persisted":true}}',False),('nullThenResult','{'+prefix+',"result":null,"result":{"restored":true}}',False),('persistedFalseTrue','{'+prefix+',"result":{"persisted":false,"persisted":true}}',False),('restoredTrueFalse','{'+prefix+',"result":{"restored":true,"restored":false}}',False),('duplicateArchive','{'+prefix+',"result":{"archive":"a","archive":"b"}}',False),('escapedAlias','{'+prefix+',"result":{"persisted":false,"persist\\u0065d":true}}',False),('duplicateError','{'+prefix+',"error":"a","error":"b"}',False),('duplicateOutcome','{'+prefix+',"outcome":"a","outcome":"b"}',False),('duplicateIdentity','{'+prefix+',"id":2}',False),('scopeIsolation','{'+prefix+',"extra":1,"result":{"extra":2}}',True)]
cases += [('failureStatus','{'+prefix.replace('true','false')+',"error":"rejected","result":{"restored":false,"persisted":false}}',True),('duplicateUnknownTop','{'+prefix+',"extra":1,"extra":2}',False),('duplicateUnknownResult','{'+prefix+',"result":{"extra":1,"extra":2}}',False),('escapedResultAlias','{'+prefix+',"result":null,"\\u0072esult":{"persisted":true}}',False)]
methods=[]
for name,raw,accepted in cases:
 parsed=json.loads(raw,object_pairs_hook=Pairs);calls=[]
 for key,value in parsed:
  calls.append('g.envelope('+json.dumps(key)+');')
  if key=='result'and isinstance(value,Pairs):
   calls.extend('g.result('+json.dumps(k)+');'for k,_ in value)
 methods.append('{boolean accepted=true;try{WorkerArchiveReplyFields g=new WorkerArchiveReplyFields();'+''.join(calls)+'}catch(IllegalArgumentException e){accepted=false;}if(accepted!='+str(accepted).lower()+')throw new AssertionError('+json.dumps(name)+');}')
source='package org.townledger.vale;public final class CompletionFieldsTest{public static void main(String[]a){'+''.join(methods)+'''WorkerArchiveReplyFields g=new WorkerArchiveReplyFields();for(int i=0;i<128;i++)g.envelope("k"+i);try{g.envelope("overflow");throw new AssertionError();}catch(IllegalArgumentException expected){}try{new WorkerArchiveReplyFields().result(new String(new char[257]));throw new AssertionError();}catch(IllegalArgumentException expected){}System.out.println("PASS duplicate-preserving completion JSON fixtures and field budgets");}}'''
with tempfile.TemporaryDirectory()as tmp:
 guard=ROOT/'android/app/src/main/java/org/townledger/vale/WorkerArchiveReplyFields.java'
 reference=os.environ.get('COMPLETION_FIELDS_REFERENCE')
 if reference:
  old=subprocess.check_output(['git','show',reference+':android/app/src/main/java/org/townledger/vale/WorkerArchiveReply.java'],cwd=ROOT,text=True);a=old.index('            if(("id"');policy=old[a:old.index('\n',a)].strip();guard=Path(tmp)/'WorkerArchiveReplyFields.java';guard.write_text('package org.townledger.vale;import java.util.*;final class WorkerArchiveReplyFields{Set<String> seen=new HashSet<String>();void envelope(String name){'+policy+'}void result(String name){}}');print('REFERENCE POLICY '+reference,flush=True)
 test=Path(tmp)/'CompletionFieldsTest.java';test.write_text(source);subprocess.run(['java','com.sun.tools.javac.Main','-d',tmp,str(guard),str(test)],check=True);subprocess.run(['java','-cp',tmp,'org.townledger.vale.CompletionFieldsTest'],check=True)
# Compile the real parser against declaration-only shapes of the documented
# Android API. These stubs deliberately have no executable parser behavior.
with tempfile.TemporaryDirectory()as tmp:
 api=Path(tmp)/'android/util';api.mkdir(parents=True)
 (api/'JsonToken.java').write_text('package android.util;public enum JsonToken{NULL,END_DOCUMENT}')
 methods={'beginObject':'void','endObject':'void','hasNext':'boolean','nextName':'String','nextLong':'long','nextBoolean':'boolean','nextString':'String','peek':'JsonToken','nextNull':'void','skipValue':'void'}
 (api/'JsonReader.java').write_text('package android.util;import java.io.Reader;public class JsonReader{public JsonReader(Reader r){}'+''.join('public '+kind+' '+name+'(){throw new UnsupportedOperationException("compile-only API declaration");}'for name,kind in methods.items())+'}')
 subprocess.run(['java','com.sun.tools.javac.Main','-d',tmp,str(api/'JsonToken.java'),str(api/'JsonReader.java'),*[str(ROOT/'android/app/src/main/java/org/townledger/vale'/name)for name in ['ArchiveIO.java','WorkerArchiveReply.java','WorkerArchiveReplyFields.java']]],check=True)
print('PASS actual parser/guard compilation against declaration-only Android API shapes; no Android parser execution claimed')
parser=(ROOT/'android/app/src/main/java/org/townledger/vale/WorkerArchiveReply.java').read_text();assert 'fields.envelope(name);'in parser and 'fields.result(field);'in parser
print(json.dumps({'cases':[{'name':n,'accepted':a}for n,_,a in cases],'fieldBudgetCases':2,'productionGuardSha256':hashlib.sha256((ROOT/'android/app/src/main/java/org/townledger/vale/WorkerArchiveReplyFields.java').read_bytes()).hexdigest(),'scope':'Production pure-Java uniqueness guard driven by decoded ordered JSON member events; Android JsonReader execution and APK integration require native-owner rerun.'},indent=2))
