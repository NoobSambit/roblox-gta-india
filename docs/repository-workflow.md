# Repository workflow

Remote: https://github.com/NoobSambit/roblox-gta-india

The first 15 commits import the existing project in logical batches. They are
an initial snapshot history, not a reconstruction of original development dates.

- Track original source code, editable Blender assets, assembled exports,
  manifests, documentation and original review images.
- Keep final original asset PNGs beside their assets and track them in Git;
  downloaded photographic references stay separate and untracked.
- Keep downloaded reference photographs, local recovery sessions, installed agent
  packages, credentials, caches and automatic backups out of Git. Reference URLs
  remain tracked. Ignoring files does not remove local copies.
- Work only on `main`, as directed by the user. Do not create task branches or
  worktrees. Use descriptive, coherent commits; inspect `git status` and staged
  changes before committing. Never commit secrets.
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

Task 005's 26-asset Howrah/riverfront delivery is approximately 22 MB, with its
largest file about 1.4 MiB. It uses normal Git, includes final original PNGs and
excludes the local `references/photos/` downloads. Recheck actual file sizes
before adding larger binaries; GitHub warns above 50 MiB and blocks files above
100 MiB. [Official guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
