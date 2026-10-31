import base64,json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
js=root/'assets'/'game.js';text=js.read_text();parts=text.splitlines(keepends=True)
assets=root/'assets'/'art'
art={f.stem:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode('ascii') for f in sorted(assets.glob('*.png'))}
parts[3]='const ART_DATA='+json.dumps(art,separators=(',',':'))+';\n'
text=''.join(parts)
text=text.replace("`tree-${season}-${item.id%4}`:","`tree-${season}-${item.id%8}`:")
text=text.replace("`${item.b.kind}-${item.b.kind==='home'?item.b.id%5:0}`", "`${item.b.kind}-${item.b.kind==='home'?item.b.id%16:['grocer','bakery','tavern','office','factory','warehouse','apartment'].includes(item.b.kind)?item.b.id%3:0}`")
js.write_text(text)
print('Embedded sprites',len(art),'JS bytes',js.stat().st_size)
