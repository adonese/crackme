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

The launcher finds Ghidra in this order:

1. `$GHIDRA_HOME/ghidraRun`
2. `ghidraRun` on `PATH`
3. common locations under `/opt`, `/usr/local`, `$HOME`, and `$HOME/tools`

If Ghidra is installed somewhere else:

```sh
export GHIDRA_HOME=/path/to/ghidra
./launchpad ghidra
```

Ghidra project databases are intentionally ignored. Create/import projects locally from
the binaries in `crackmes/` and `practice/`.

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
binaries. It has no required third-party Python dependencies.
