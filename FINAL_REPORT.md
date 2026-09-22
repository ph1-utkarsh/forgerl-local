# ForgeRL bounded local report

ForgeRL provides bounded JSON tools, isolated Docker execution, host-held semantic graders, output/time/resource limits, replay, immutable traces, corrected GGUF-to-MLX loading, SFT/DPO/GRPO-surrogate LoRA training, and a three-repository BugsInPy pilot split with pinned commits, tests, licenses, and images.

Strict-schema local Qwen solved 3/18 authored qualification episodes. On the first real repository task it solved 0/3. A failure-derived 20-step SFT LoRA reduced sequence loss from 1.529 to 0.125 with unchanged base tensors and exact reload, but strict exact-repair evaluation was **base 0/3 and SFT 0/3** across train/development/test blocks.

Two additional real local updates close the preference/RL mechanics gap. Ten-step DPO increased the observed chosen-versus-rejected average-token log-probability margin from 0.382 to 4.684; a two-candidate clipped GRPO surrogate using verifier rewards increased it to 1.220. Both changed only 40,960 LoRA parameters and reproduced their margins after reload. Neither generalized: exact repair was **base 0/3, DPO 0/3, and GRPO 0/3**. DPO also produced a malformed long response on its training-domain task. These are deliberately preserved negative results: optimizing one preference pair is not a repair capability result.

The original five-point, three-seed curriculum hypothesis is not statistically tested by one task per split. The defensible result is a negative feasibility pilot, not evidence that failure-driven post-training works or cannot work at adequate scale. Preference collection, process supervision, and multi-turn recovery remain untested at research scale.
