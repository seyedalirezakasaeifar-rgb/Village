# Private service economy and integration API

## Ownership and funding

`src/16-private-services.js` owns private school and brigade economics. They are ordinary firms with `privateService: 'school' | 'fire'`, `kind` matching the building, private titles, private owners, qualified workers, payroll, taxes, fees, loan/default and liquidation behavior. Public school/fire buildings remain municipal. `isPublicFacility(building)` is the authoritative ownership discriminator; a closed private building does not turn into a free public facility.

Entrepreneurs evaluate unmet fee-paying demand, actual catchment, qualified labor, allowed fee and a financing return hurdle. Monthly `privateServiceInvestmentDay()` seeks one viable project. `seekPrivateServiceInvestment(kind)` runs the same assessment on an explicit invitation and returns a human-readable result; invitation is not a subsidy or a guaranteed building. Public development pause suppresses autonomous entry, while an explicit invitation can commission an independently financed proposal. Licensing stops new entry without confiscating existing enterprises.

Construction uses an existing 45-workday firm project with `privateService`, `serviceFee` and `serviceEscrow`. Construction is bought from real investors/contractors; working capital is reserved from regional cash in escrow at authorization. `totalMoney()` includes this escrow. Completion transfers it to the firm once. No municipal capital grant is implied. Closed institutions can be recapitalized after 120 days only if demand and finance justify a new operator.

## Operating API for UI and graphics workers

- `G.firms`: private providers use `privateService`, `serviceFee`, `clientsToday`, `clientsYesterday`, `serviceCapacity`, `privateReceipts`, `privateVouchers`, `closed`, `workers`, `jobs`, `cash`, `operating` and `netProfit`.
- `clientsToday` records actual paid service equivalents. It is not an unqualified count of students physically present. `serviceCapacity` is usable qualified staffing capacity for that day, reset for closed operators.
- School activity is valid when not closed and `clientsToday > 0`. Brigade response additionally requires positive capacity and actual road reach. Do not draw teaching at a private school merely because the town has a public education budget.
- `G.privateServiceProvision` is a derived daily report: household `school` and `fire` coverage maps, `pupils`, `fireMembers`, `tuition`, `memberships`, `vouchers`, and `day`. It is cleared on restore; it is not an authoritative bank account.
- `privateProviderPanel()` returns provider/finance UI; `renderCommunityFull` and `renderInspectFull` are wrapped by `src/98-private-service-ui.js`. UI owners may rearrange this panel for readability while preserving accounting labels and entry results.
- `isPublicFacility(b)`, `privateServiceDistance(f,h)`, `publicCivicCoverage(kind, householdId)`, `localCivicCoverage(kind, householdId)`, `privateFireResponse(building)` and `publicFireResponse(building)` expose actual ownership/access/response. Local school coverage combines public and purchased private contributions, capped at one.
- `seekPrivateServiceInvestment('school' | 'fire')` evaluates an invitation; no guaranteed success. Save/re-render after showing its result.
- Staged policy keys in `defs/defaults`: `privateServices` (0/1 entry licensing), `privateTuitionCap`, `privateFireFeeCap`, `serviceVoucherBudget`. Use the existing draft/enact/discard flow, not direct slider side effects.

## Service and affordability rules

Teachers require skill 0.55, firefighters 0.4, adult working age and adequate health; recruitment uses real commuting access. Qualified workers can switch from private employers for a sufficient wage premium, with a cooldown. A worker cannot fill both private and public capacity.

Private schools use remaining public-service gaps, finite learner places and household cash/income reserves. Low-wealth families may use actual targeted voucher purchases. There is no forced household borrowing. Fees pay providers; providers pay wages and operating costs. Learning takes 120 equivalent paid teaching days before a formal skill increment. Civic programme metrics recognize private learning and completed training alongside public provision.

Brigade membership funds prevention and priority readiness. A household declines a membership that offers no useful improvement over its public response. Fire response is geographically bounded. Nearby nonmembers receive a real spillover response from an operating brigade; rescue is not withheld for a doorstep payment. Closed or unstaffed private stations cannot create public capacity or spawn response vehicles.

## Current evidence and limits

Controlled matched public/none/private/voucher tests verify staffing, affordable paid capacity, targeted access, exact-once purchases, conservation, 190-day learning, closure, viable recapitalization and eventual exit under a zero-fee ceiling. Actual-control invitations for both school and brigade pass reserved-capital save/restore, construction, qualified staffing, fee-paying clients, staged voucher enactment, licensing and conservation checks through day 111. The controlled fixtures are clearly labeled; they are not proof that every town attracts a viable private institution.

The original public school-coverage index is resident-based, while private provision measures paid learner equivalents. Private provision is therefore complementary, not a promise that a private-only town can satisfy every public programme target. Absolute prices and behavioral coefficients are game rules, not calibrated real-world forecasts. Final playthroughs, interface hierarchy, dense-city performance and full immutable release acceptance remain pending.

Existing module hooks changed in this phase include school/fire facility filters, staffing, firm construction completion, treasury/escrow accounting, incidents/dispatch and civic programme observations. Graphics should retain the private-school activity guard in `97-workday-scenes.js` when integrating visual changes. Generated `assets/game.js` must always be reassembled after cherry-picks.
