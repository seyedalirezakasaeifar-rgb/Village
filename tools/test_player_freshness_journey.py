"""Pinned actual-player journey, strict freshness and complete cold archive oracle."""
from pathlib import Path
import argparse,contextlib,io,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--source-file');ap.add_argument('--expect-stale',action='store_true');args=ap.parse_args()
ref='856f944b551296ebe3c61c862439a946c803dc21';baseline='01eeda3d2ff09822b9422721f75e97fabbc9958a'
script=subprocess.check_output(['git','show',ref+':tools/baseline_realtime_player_journey.py'],cwd=ROOT,text=True)
script=script.replace("probe=(ROOT/'tools/fixtures/realtime-player-journey-probe.js').read_text()", "probe=subprocess.check_output(['git','show','"+ref+":tools/fixtures/realtime-player-journey-probe.js'],cwd=ROOT,text=True)")
if args.source_file:script=script.replace("source=read('assets/game.js').decode()",'source=Path('+repr(str(Path(args.source_file).resolve()))+').read_text()')
(ROOT/'reports/current-paid-worker-audit').mkdir(exist_ok=True,parents=True);sys.argv=['baseline_realtime_player_journey.py','--commit',baseline]
namespace={'__file__':str(ROOT/'tools/baseline_realtime_player_journey.py'),'__name__':'__main__'}
with contextlib.redirect_stdout(io.StringIO()):exec(compile(script,'pinned-actual-player-journey','exec'),namespace)
out=namespace['out'];summary={k:out.get(k) for k in ['sourceSha256','completed','finalDay','daysElapsed','cashDrift','errors','strictFreshViewAccepted','stalePanelState','staleCargoPreview','rawArchiveRoundtripEqual','rawArchiveRoundtripDifferences','fullColdUiOracleEqual']};summary.update({'actualUiOnly':True,'fixtureRef':baseline,'pinnedJourneyRef':ref,'expectStale':args.expect_stale,'checkpoints':len(out['actions'])})
dest=ROOT/'reports'/('player-freshness-negative.json' if args.expect_stale else 'player-freshness-fixed.json');dest.write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
assert out['completed'] and out['fullColdUiOracleEqual']
if args.expect_stale:assert not out['strictFreshViewAccepted'],'Negative no longer reproduces; inspect exact source'
else:assert out['strictFreshViewAccepted'],'Player freshness/canonical roundtrip defect remains'
