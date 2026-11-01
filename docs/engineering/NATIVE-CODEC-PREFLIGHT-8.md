# Metadata preflight native check

Separate scratch chain: a964174 metadata preflight after77a799d canonical expansion-budget fix, with d1f963a redundant-parse fix cleanly cherry-picked. Combined local commit ae654b0550e0eba9a353105adc3ab6b14e27891f, source/build/embedded SHA25647c2659adccbfbd32c857d1911f0d7cfcaa7f436c4fdcce2a0425a7844b92e02. Existing private signer and API30/WebView83 emulator; production flag remains disabled.

Recreated owner3001-household/3001-firm fixture and prior8387584-byte near-budget wire. The same malformed firms.total++ case was rejected, with strict complete canonical model, RNG and save epoch unchanged. Direct hydrate rejection time10493.3ms; time including independent full-state comparison37585.9ms.

Correction to interpretation of the earlier38330.2ms number: it included canonical model serialization/comparison after rejection. It was not pure rejection latency. Therefore10493.3ms must not be presented as an isolated38→10second preflight speedup. Comparable inclusive observations are38.33 versus37.59seconds, single software-emulator samples. The new preflight case remains slow enough to keep the candidate disabled pending acceptance and broader native review. This is one attack, not the owner's18-case full native matrix. No budget or comparison was relaxed, and no unchanged process-death case was rerun.
