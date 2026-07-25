# orchestrator.stats package
#
# MERGE-TIME NOTE: B's branch (feat/agent1-auditor) may contain its own
# stats/ module with duplicate implementations of compute_dir() and
# Fisher/BH correction. Whoever merges second MUST:
#   1. Delete the duplicate stats/ copy
#   2. Re-point all imports to the single source of truth
#   3. Run smoke_test.py to confirm nothing broke
# Do NOT silently let two versions of this math coexist in main.
