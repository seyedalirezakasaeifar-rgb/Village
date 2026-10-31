# Fresh provision defaults

Based on integrated f26bbe0. Actual native report 5498445 identifies absent initial
serviceProvision/privateServiceProvision versus null after hydration. Fresh towns
now declare both null in the initial state, matching their actual unpurchased
first-day status and the existing hydration contract. No fiscal transfer or RNG
change is introduced. Frozen 662ec6f hour is untouched.

The regression now checks the UNION of top-level before/after keys, not only keys
present before export. That earlier test limitation missed newly added defaults;
it is corrected, not treated as an exact pass. Explicit-null assertions and twelve
four-scenario/three-seed strict first-save round trips pass. Generated bundle is
excluded; integration must reassemble and native owner should rerun process death.
Source-bound host result is in docs/evidence/fresh-provision8/result.json.
