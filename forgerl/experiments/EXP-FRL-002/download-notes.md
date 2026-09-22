# Checkpoint acquisition attempt

The pinned free MLX checkpoint metadata and tokenizer assets were retrieved. Xet transport stalled with a zero-byte model partial. Standard HTTP transferred about 40 MB before its peer closed the connection; a resume outside the sandbox was also slow. These attempts are infrastructure observations, not model failures.

The task-owned downloader was stopped after MLX successfully loaded the existing local Ollama GGUF and the adapter pilot completed. Small tokenizer/config files and the partial weight transfer remain in ignored `models/` for possible resumption; no model file was deleted. No complete alternate checkpoint was downloaded. No paid endpoint or token was used.

Preferred current path: existing GGUF plus the retrieved tokenizer/config assets, subject to inference-parity qualification. The new public checkpoint is an optional fallback, not a prerequisite for further local testing.
