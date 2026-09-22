# Infrastructure failure

The probe stopped before container execution because the host is Python 3.9 and does not support `tarfile.extractall(filter="data")`. The incomplete config is retained. No buggy/fixed outcome was measured. The compatibility fix is exercised only under a new run ID.
