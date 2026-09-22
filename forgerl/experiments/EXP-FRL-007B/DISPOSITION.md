# Failed discrimination

Both source revisions passed because each revision was initially evaluated with its own test file. The buggy commit predates the regression assertions added by the fix, so its historical test cannot expose the defect. This is a benchmark-construction failure, not a valid negative model result.

The next immutable run freezes `test/test_utils.py` from the fixed commit and applies that exact test file to both source revisions.
