# Tool Launchers

This repo includes two thin launchers so a fresh clone has a predictable entry point.

## Wine

Run the picker:

```sh
./launchpad wine
```

Run a specific crackme:

```sh
./launchpad wine crackmes/crackme_4_psyr3n/PIDXploit.exe
```

The launcher uses a repo-local Wine prefix at `.wine-prefix/`, which is ignored by git.

## Ghidra

Run:

```sh
./launchpad ghidra
```

Open one executable with the low-friction path:

```sh
./launchpad ghidra crackmes/crackme_1_TLOD/EasyCrackMe.exe
```

This imports the file into a per-binary local project under
`~/ghidra-projects/quick/`, runs analysis, then opens that `.gpr` in the Ghidra
GUI. Re-running the same command opens the existing project. Use `--reimport`
to refresh it from the executable.

If you have the repo wrapper on your shell `PATH`, this also works from
anywhere:

```sh
ghidra /path/to/some.exe
```

Install that wrapper with:

```sh
./launchpad install-ghidra
```

Useful variants:

```sh
./launchpad ghidra --import-only some.exe
./launchpad ghidra --no-analysis some.exe
./launchpad ghidra --project-dir /tmp/ghidra-projects some.exe
```

The launcher finds Ghidra in this order:

1. `$GHIDRA_HOME/ghidraRun`
2. `ghidraRun` on `PATH`
3. common locations under `/opt`, `/usr/local`, `$HOME`, and `$HOME/tools`

If Ghidra is installed somewhere else:

```sh
export GHIDRA_HOME=/path/to/ghidra
./launchpad ghidra
```

Ghidra project databases are intentionally ignored. Create/import projects
locally from the binaries in `crackmes/` and `practice/`.

The local import walkthrough is `docs/ghidra-import/README.md`.

## Repo Viewer

Run:

```sh
./launchpad view
```

Or choose a port:

```sh
./launchpad view 8787
```

Run without opening a browser automatically:

```sh
./launchpad view 8787 --no-browser
```

The viewer is a local Python server for browsing the repo. It indexes Markdown,
HTML, source files, PDFs, images, archives, and binaries; renders Markdown and
source files; previews HTML/PDF/image files; and shows basic metadata for
binaries. It runs through `uv`, and the script metadata asks `uv` to install
Pygments for source highlighting.

## Inventory

Write or refresh the tracked-file checksum manifest:

```sh
./launchpad inventory write
```

Verify the current checkout against the manifest:

```sh
./launchpad inventory verify
```

The manifest records SHA-256 hashes for tracked and unignored files, excluding
the manifest itself. It is useful after folder moves or after redownloading
practice bundles.
