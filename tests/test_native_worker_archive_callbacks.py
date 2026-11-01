from pathlib import Path
import subprocess,tempfile

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(['java','com.sun.tools.javac.Main','-d',tmp,
        str(ROOT/'android/app/src/main/java/org/townledger/vale/WorkerArchiveRequests.java'),
        str(ROOT/'tests/java/WorkerArchiveRequestsTest.java')],check=True)
    subprocess.run(['java','-cp',tmp,'org.townledger.vale.WorkerArchiveRequestsTest'],check=True)
source=(ROOT/'src/92-government.js').read_text()
assert "window.__workerArchiveAsync&&typeof AndroidArchive.requestWorkerExport==='function'" in source
assert "window.__workerArchiveAsync&&typeof AndroidArchive.requestWorkerImport==='function'" in source
assert 'window.AndroidArchive.writeBackup(archivePayload())' in source
assert 'window.AndroidArchive.openBackup()' in source
java=(ROOT/'android/app/src/main/java/org/townledger/vale/MainActivity.java').read_text()
for method in ('workerArchiveStarted','workerArchiveRejected','workerArchiveResult','requestWorkerExport','requestWorkerImport'):
    assert method in java
print('PASS opt-in native worker archive callbacks preserve synchronous export/import fallback')
