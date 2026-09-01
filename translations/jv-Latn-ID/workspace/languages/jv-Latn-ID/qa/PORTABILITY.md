# Cross-PC input replay limitation and metadata repair

2026-08-31. The committed readers embed their assets and have no network/CDN
dependency. Rebuilding requires the ignored pinned input repositories/archives
at repo-relative paths. A clean-clone rebuild on another PC has not been tested.
Do not infer portability approval from deterministic checks on this worktree.

The current sources.lock.json truthfully retains the original acquisition's
shared archive path on this PC. Builders consume only the repo-relative archive;
the recorded donor path is historical provenance, not an input dependency.
No source lock, donor archive, hard link or source evidence was rewritten here.

The acquisition script previously emitted that same hard-link/donor claim even
after downloading a new archive on another PC. Its metadata helper now separates
a new canonical-URL download from reuse of an existing verified local archive.
For reuse, matching previous shared-origin evidence is retained under an explicit
historical field, without claiming that the present file is a hard link or that
the old donor is reachable. Ambiguous prior evidence is rejected. Four pure
tests cover fresh acquisition, reuse, idempotent historical retention, absent or
different-byte evidence and ambiguity. They do not download or read the archive.

Acquisition's generated-file writes also use the existing atomic writer. The
large acquisition procedure was not executed for this repair; no repeated
archive CRC/module sweep, supply/license audit, substantial download, extraction,
source replacement or deletion occurred. These tests do not certify the full
fresh-acquisition workflow or storage topology on another PC.
