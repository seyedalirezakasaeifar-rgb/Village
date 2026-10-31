#!/usr/bin/env python3
"""Compatibility entrypoint for the SDK-based Java Android build."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parent/'tools/build_android.py'),run_name='__main__')
