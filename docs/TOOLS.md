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
