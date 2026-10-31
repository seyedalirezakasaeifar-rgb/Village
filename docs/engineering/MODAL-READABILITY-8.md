# Modal and inspector readability

On a 568×320 landscape phone, the existing council decision sheet placed its only Cancel/Defer action below the visible viewport. Enlarged text also left decision and help dialogs at their smaller default sizes. Very long account labels and amounts were not guaranteed to fit inside narrow ledger rows.

The decision sheet now separates its description and alternatives into independently scrollable areas. The alternatives retain at least 112 CSS pixels, and Cancel/Defer stays fixed at the bottom of the sheet. A long title or description can scroll within its own area without hiding a choice. The existing Larger text preference now enlarges modal prose and controls, with wrapping for long names and figures. Inspector ledger rows and headline values can wrap inside their available width.

The new test opens a real council petition and the real household inspector. It applies deliberately long translation-like labels and a large currency value to visible DOM text only; the saved town, petition choice, balances and policies remain real and untouched. It exercises the layout at 568×320 landscape and 390×844 portrait, checks the first and last choices, the always-visible cancel action, horizontal overflow, enlarged type, inspection and Back/Escape no-enactment behavior. It also checks the manual and backup sheets under enlarged text. Screenshots and measured results are in [`reports/modal-readability8`](../../reports/modal-readability8/).

Verification passed:

- `python tests/test_modal_readability.py`
- `python tests/test_review_workflows.py`
- `python tests/test_mobile_rendering.py` across seven phone/tablet layouts

The existing `tests/test_controls.py` uses a `file://` page, which this managed Chromium blocks with `ERR_BLOCKED_BY_ADMINISTRATOR`. Its relevant Escape, modal, account and no-enactment paths are covered by the new local inline-page test and the passing review-workflow test.

The button and paper text colors already exceed WCAG AA contrast for normal text in the tested theme: sampled solid pairs `#20372b` on `#e1e4c6` measure 9.81:1 and `#2f472f` on `#ece2c4` measure 7.87:1. This change leaves those colors intact.
