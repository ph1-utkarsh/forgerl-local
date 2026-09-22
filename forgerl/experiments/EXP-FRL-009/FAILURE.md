# Archive safety failure

The first Tornado probe stopped before tests because the upstream archive includes a symlink and the extractor rejected all links. No buggy/fixed result was measured. The next run omits links after validating every member path; the targeted unit test does not require them.
