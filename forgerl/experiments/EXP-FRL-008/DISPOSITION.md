# Protocol failure

All three seeds attempted an invented `def _bool_filter(...)` replacement before reading the repository. The exact substring did not exist, so the host rejected every action; none finished and the source remained buggy. This is valid protocol-failure evidence but not evidence that Qwen could not reason about the observed implementation.

The next cohort requires `read` on step zero through the response schema, while leaving subsequent action and compute bounds unchanged.
