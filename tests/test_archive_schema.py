"""Reject unsupported save schemas while retaining schema-less legacy archives."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'assets/index.html').read_text()
HTML = HTML.replace(
    '<link rel="stylesheet" href="style.css">',
    '<style>' + (ROOT / 'assets/style.css').read_text() + '</style>',
).replace('<script src="game.js"></script>', '')


def test_archive_schema_bounds():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path='/usr/bin/chromium', args=['--no-sandbox']
        )
        page = browser.new_page(viewport={'width': 844, 'height': 390})
        page.set_content(HTML)
        page.add_script_tag(content=(ROOT / 'assets/game.js').read_text())
        result = page.evaluate('''()=>{
          __townTest.reset('settlement',42);
          const original=JSON.parse(__townTest.save()),before=__townTest.get();
          const negative=JSON.parse(JSON.stringify(original));negative.schema=-1;
          if(__townTest.load(negative))throw Error('Negative schema accepted');
          if(__townTest.get().day!==before.day||__townTest.get().population!==before.population)
            throw Error('Rejected archive changed the running town');
          const legacy=JSON.parse(JSON.stringify(original));delete legacy.schema;
          if(!__townTest.load(legacy))throw Error('Schema-less legacy archive rejected');
          const future=JSON.parse(JSON.stringify(original));future.schema=original.schema+1;
          if(__townTest.load(future))throw Error('Future schema accepted');
          return {negativeRejected:true,legacyAccepted:true,futureRejected:true};
        }''')
        assert result == {
            'negativeRejected': True,
            'legacyAccepted': True,
            'futureRejected': True,
        }
        browser.close()


if __name__ == '__main__':
    test_archive_schema_bounds()
    print('PASS negative and future schemas rejected; schema-less legacy save accepted')
