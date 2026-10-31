# Brownfield renewal: ordinary-player acceptance

Apply this follow-up after `125f9b0e6ddedda7fd22ceffa2a4eb1ecdf5ff38`. It fixes the first slice's discovery gap: a healthy city with no closed industrial premises previously had no mayor-controlled route to renewal. No new chemical model, free profits, resources or automatic closures are introduced.

## Changes and shared hooks

A mayor may now assess either working or closed factories, quarries and sawmills. The office shows current employees, a compensated-assembly estimate, worker severance, and any actual cargo/contract/property restriction before charging for assessment. Working businesses retain their staff, stocks, title and operations during assessment. Acquisition remains a separate explicit decision through existing `urbanClearanceQuote` / `urbanClearance`, paying all current compensation and twelve days of severance, settling lawful liquidation, and preserving the existing transit/cargo/claim guards. Assessment is not permission to confiscate an enterprise.

An active-site assessment records `wasClosed:false`, `formerWorkers`, and the current compensation/severance estimate. These optional fields remain compatible with old closed-site records. The recorded industrial-age proxy is age at assessment for a working firm, and the existing age-less-time-since-closure proxy for a closed firm. Ground preparation pricing and the absence of arbitrary contamination/health bonuses are unchanged.

Closed-site surveys cannot be used to acquire a firm after it reopens. Both UI and backend guard this case; the mayor can withdraw the old survey and obtain a new working-site proposal. `brownfieldWithdraw(id)` removes only an unacquired assessment. Its paid $300 is not refunded, and no firm/property/worker state changes. Acquired land and paid ground-work contracts remain committed. Industrial sites use the property guard so ordinary clearance cannot bypass the renewal assessment or accidentally discard an acquired site history. The survey and acquisition paths temporarily authorize only the specific reviewed site while preserving all other property guards. Acquisition still revalidates the reviewed price and actual funds.

The office shows reasons for blocked proposals and provides inspection links. With no industrial premises it explains the absence and links ordinary compensated land assembly. Candidate previews collapse once a project exists so paid work is not buried under other proposals. Industrial property inspectors expose their own current renewal quote, including sites beyond the office preview. Existing data-action attributes remain unchanged; `withdraw` is added to `data-brownfield-action`. `brownfieldReopened(site)` supplies the pure UI state check. `brownfieldDescriptor()` retains its existing graphics shape and states; renderer/migration files are untouched.

## Ordinary funded replay

`test_brownfield_player_path.py` starts regional seed 42 and runs **180 ordinary days** before any renewal intervention. It never invokes the closure helper and adds no cash, people, goods or customers. The treasury has $481,890.55 before the compensated acquisition. The actual office/inspector controls allow the mayor to assess a working quarry, cancel a review, withdraw a paid survey, obtain a fresh survey, acquire it, fund ground works and select each reuse alternative from the same ready-state replay.

The quarry has four real workers. Acquisition is $46,498.85: $42,900 property compensation, $1,850 clearance and $1,748.85 worker severance. Existing liquidation can make other legitimate transfers; the observed regional net is therefore labelled as including liquidation rather than misreported as pure compensation. Tests verify worker identities remain, nobody retains a job in the retired firm, severance reaches worker households, and total cash is conserved. The road tiles, complete passenger-transit state, regional shipments and local freight remain identical across assembly.

At this ordinary checkpoint **seven other industrial proposals are blocked by actual paid cargo or active contracts**. These are retained negative findings, and the UI explains why the mayor must settle those commitments rather than silently removing them.

The surveyed enterprise age is 180 days. Ground works cost $3,690 and require 26 connected/open-trade workdays. Two closed-trade days make no progress, so the site becomes ready on day 209. Each replacement is separately funded through the normal construction path:

| Alternative | Actual consequence |
| --- | --- |
| Municipal home | One real dwelling in the housing register, municipal title, and one tenant household after 30 ordinary days. |
| Grocer | Real enterprise and capital, one worker/job after 30 days, zero daily sales and approximately **-$41.19 daily operating profit** at the sample. This is a viable control path, not a promise of commercial success. |
| Park | Existing local amenity value rises from about 1.142857 to 2.142857. No direct cash or health bonus is granted. |

The intervening normal simulation conserves total cash within $0.00001. Archive round-trips, malformed-cost rejection, insufficient-funds rejection, explicit proposal cancellation and paid survey withdrawal pass. The comparison arms rewind only to the actual funded ready-state archive; they do not manufacture favorable starting resources.

## Restart and legacy limits

`test_brownfield_reopening.py` uses a separate explicitly controlled closure to examine old survey compatibility. An archive without the new optional survey fields loads. Ordinary simulation over the next 240 days **does not naturally reopen that quarry**. This absence is retained; no natural restart success is claimed.

A clearly marked cloned-state edge probe changes only the clone's closed flag to exercise the reopened-firm guard and UI warning. It confirms the stale proposal cannot transfer money or acquire the working property; the live town is restored unchanged. This is a conditional guard test, not a natural economic outcome. Actual withdrawal controls then remove the stale assessment without refunds or changes to enterprise/property rights. A separate pure empty-office render fixture verifies the explanation and existing lawful-assembly link without removing live buildings.

## Deliverables and checks

Source-bound outputs, screenshot and logs are under `docs/previews/brownfield-player-path/`. Tests:

- `test_brownfield_player_path.py`: ordinary mayor path, inspector discovery, blocked claims, workers/severance, transport preservation, real three-way capacity consequences and negative retail outcome.
- `test_brownfield_reopening.py`: legacy optional fields, bounded natural-restart negative outcome, isolated stale-reopening guard, empty-office guidance and actual withdrawal.
- Original `test_brownfield_renewal.py`, plus archive schema and review workflow regressions.

No main branch merge, deployment or new renderer assets are included. Graphics can continue using the existing descriptor; long-term retail viability and industrial replacement investment remain ordinary economic risks rather than success conditions patched into this slice.
