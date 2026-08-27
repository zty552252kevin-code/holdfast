# Quarantined: first-generation 8B DPO eval previews (D-025)

All three en-dpo-8B-4k seeds' first checkpoints were saved through
train_dpo.py's unguarded legacy FSDP gather and hit the D-016 stale-shard
race (layer 35 corrupt; s17 forensic: 5 tensors at max-abs-diff 2.6-17.6 vs
the SFT init while the other 394 sit at ~3e-5). These previews measure
corrupted checkpoints — degenerate signature: hold .33-.52, H5 acc .37-.39,
other_frac .49-.61 (healthy SFT-8B-4k: .78 / .64 / .21). Excluded from all
analysis; kept for provenance only. Replacement cells: chain9 under the
hardened save path (DCP + verify + drift gate). See DECISIONS.md D-025.
