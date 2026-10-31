#!/usr/bin/env python3
"""Freeze assembly, run candidate gates sequentially, build and bind evidence hashes."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
subprocess.run([sys.executable,'tools/assemble.py'],cwd=ROOT,check=True)
asset_hashes={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'assets').rglob('*') if p.is_file()}
source=digest(ROOT/'assets/game.js');meta=json.loads((ROOT/'release.json').read_text());out=ROOT/'reports'/meta['version'];out.mkdir(parents=True,exist_ok=True)
env=os.environ.copy();env['TOWNLEDGER_CORE_ONLY']='1'
gates=['test_live_status.py','test_toast_layout.py','test_atlas_invalidation.py','test_native_back_recovery.py','test_foundation_land_titles.py','test_save_queue.py','test_save_chronology.py','test_save_storage.py','test_older_webview_layout.py','test_audio_lifecycle.py','test_goods_precision.py','test_region_survey.py','test_water_motion.py','test_waterfront_player_journey.py','test_sprite_envelopes.py','test_annexation.py','test_annexation_networks.py','test_waterfront.py','test_waterfront_mobile.py','test_seed_sort_stability.py','test_map_hierarchy.py','test_host_lifecycle.py','test_native_archive_io.py','test_council_programme.py','test_credit_crisis.py','test_council_accounting.py','test_workday_scenes.py','test_credit_cashflow.py','test_household_markets.py','test_local_civic_services.py','test_transport_visual_states.py','test_service_provision.py','test_older_webview_api.py','test_archive_schema.py','test_review_workflows.py','test_mobile_rendering.py','test_controls.py','test_v7_contrast.py','test_release.py','test_v7_model.py','test_v7_default_starts.py','test_v7_scenarios.py','test_v7_liquidity.py','test_v7_policy_experiments.py','test_regional_tradeoffs.py','test_v7_live_large_town.py']
manifest={'version':meta['version'],'source_sha256':source,'assets':asset_hashes,'gates':[]}
for name in gates:
 assert digest(ROOT/'assets/game.js')==source,'Source changed before '+name
 script_hash=digest(ROOT/'tests'/name)
 log=out/(name+'.log')
 with log.open('w') as stream:
  result=subprocess.run([sys.executable,'tests/'+name],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
 assert all(digest(ROOT/path)==sha for path,sha in asset_hashes.items()),'Assets changed during '+name
 assert digest(ROOT/'tests'/name)==script_hash,'Test changed during '+name
 manifest['gates'].append({'script':name,'script_sha256':script_hash,'exit_code':result.returncode,'source_sha256':source,'log_sha256':digest(log)})
 (out/'candidate-gates.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(name,result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
subprocess.run([sys.executable,'tools/build_android.py'],cwd=ROOT,env=env,check=True)
assert all(digest(ROOT/path)==sha for path,sha in asset_hashes.items()),'Build changed verified assets'
subprocess.run([sys.executable,'tests/verify_package.py'],cwd=ROOT,env=env,check=True)
manifest['android']=json.loads((ROOT/'reports/android-build.json').read_text())
manifest['package_assets_verified']=True
(out/'candidate-gates.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PASS all candidate evidence bound to source',source)
