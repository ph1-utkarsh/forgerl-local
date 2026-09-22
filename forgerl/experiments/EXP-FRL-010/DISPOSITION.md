# Dependency-image failure

Both revisions failed collection because the first dependency image omitted the repository's runtime requirements (`future`, `six`, and `decorator`) and used the wrong minimum `python_toolbox` version. This is an infrastructure failure, not bug discrimination. The corrected image pins the exact minimum versions declared by the buggy commit; rerun under a new experiment ID.
