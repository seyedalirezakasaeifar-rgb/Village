# Disabled worker model proof

Base ca0c6d07. Run from repository root:

```
npm ci --prefix experimental/worker --cache /tmp/worker-npm-cache
node experimental/worker/build.cjs
python experimental/worker/prove.py
```

No production entrypoint imports this experiment. Acorn extracts declarations and function assignments from the actual model sources; excluded initialization statements are recorded in excluded.json for audit. This is a prototype bootstrap, not a release bundle pipeline. No fake document/canvas is installed. Browser Blob Worker runs the authoritative model. UI is used only to generate the starting archive and synchronous oracle.

61 complete days, two monthly boundaries, actual minimum-wage policy change with journal/recompute, completed snapshot/export and stale council ID rejection pass exact model/RNG comparison. Only trafficState/visualState are excluded as the separately owned presentation envelope. Notifications, ambience refresh, panel/header invalidation and save requests go to a structured outbox. Save requests are intents delivered after commit, not storage writes. Mid-day version on an effect denotes the preceding committed version; snapshot version identifies the delivery boundary. Policy snapshot version currently counts days only, so a separate command revision is required before UI adoption.

proof.json records one bounded 60-day timing sample after equality gates: sync 414.9ms versus worker409.7ms, main timer maximum gap499.8ms versus10.5ms. This measures event-loop availability, not trusted physical input latency. It is a small generated town, not the late-town performance acceptance fixture; no general speed gain is claimed.

Remaining gates: valid council choice settlement extraction (currently explicitly rejects rather than discards it); UI readonly snapshot adoption and command routing; save-owner visual-envelope/archive validation contract; failures and cancellation; dense-town matched repetitions and trusted input; API30/WebView83 native Blob support. No security settings changed. Production remains synchronous.
