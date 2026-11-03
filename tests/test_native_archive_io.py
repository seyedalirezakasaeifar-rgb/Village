"""Run the dependency-free archive transport checks on the host JVM."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='townledger-archive-') as tmp:
 subprocess.run(['java','com.sun.tools.javac.Main','-d',tmp,str(ROOT/'android/app/src/main/java/org/townledger/vale/ArchiveIO.java'),str(ROOT/'tests/java/ArchiveIOTest.java')],check=True)
 subprocess.run(['java','-cp',tmp,'org.townledger.vale.ArchiveIOTest'],check=True)
print('Host-JVM transport tests; Android Activity/provider/lifecycle behavior requires device or emulator tests')
