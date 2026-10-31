#!/usr/bin/env python3
"""Run the existing independent compositor oracle at Android QA's viewport.

Run from a checkout of cc863115; requires existing Chromium/Playwright deps.
The unchanged strict oracle is expected to fail until the graphics issue is fixed.
"""
from pathlib import Path
import hashlib,sys
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'tests'))
print('game_sha256='+hashlib.sha256((root/'assets/game.js').read_bytes()).hexdigest(),flush=True)
source=(root/'tests/test_actor_compositor.py').read_text()
source=source.replace("{'width':1280,'height':720}","{'width':640,'height':360}")
exec(compile(source,str(root/'tests/test_actor_compositor.py'),'exec'))
