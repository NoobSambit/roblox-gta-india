# Repository workflow

Remote: https://github.com/NoobSambit/roblox-gta-india

The first 15 commits import the existing project in logical batches. They are
an initial snapshot history, not a reconstruction of original development dates.

- Track original source code, editable Blender assets, assembled exports,
  manifests, documentation and original review images.
- Keep downloaded reference photographs, local recovery sessions, installed agent
  packages, credentials, caches and automatic backups out of Git. Reference URLs
  remain tracked. Ignoring files does not remove local copies.
- Use short task branches for new work and descriptive, coherent commits.
  Inspect `git status` and staged changes before committing. Never commit secrets.
- Preserve source/export correspondence when changing models. Commit the source,
  refreshed export and relevant manifest together. Preserve user edits.
- Use normal Git for current assets, all well below GitHub's file-size ceiling.
  Adopt Git LFS before adding substantially larger or frequently revised binaries.
- Do not force-push shared history. Push completed commits to the remote.

**Studio remains the source of truth for the authored world.** This repository
does not automatically sync or publish the place. Keep deliberate local place or
model snapshots when changing Studio content; the existing `.rbxm` milestone
files are recovery snapshots, not a complete current place backup.

Reference-photo files are intentionally absent in a fresh clone. Consult the
asset manifests and retrieval scripts before reference-dependent rebuilds.
