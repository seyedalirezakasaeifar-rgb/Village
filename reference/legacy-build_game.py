from pathlib import Path
p=Path(__file__).parent/'assets'
s=(p/'game.js').read_text()
feature=(p/'features.js').read_text()
assert s.rstrip().endswith('})();')
s=s.rstrip()[:-5]+feature+'\n})();\n'
(p/'game.js').write_text(s)
print(len(s))
