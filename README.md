# Crackme Practice Lab

Local reverse engineering practice repo for Ghidra, Wine, and beginner-friendly
crackme ladders.

## Quick Start

```sh
git clone https://github.com/adonese/crackme.git
cd crackme
./launchpad list
./launchpad view
./launchpad wine
./launchpad ghidra
```

Use a VM, container, or isolated Wine prefix for unknown binaries.

## Layout

- `crackmes/` - the original four tutorial crackmes.
- `solutions/` - Ghidra-oriented walkthroughs for the original four crackmes.
- `practice/` - broad local mirrors and indexes for crackmes.one, pwn.college,
  Nightmare, and hosted-platform references.
- `launchpad` and `launchpads/` - Wine and Ghidra launch helpers.
- `tools/repo_viewer.py` - local browser for Markdown, HTML, PDFs, images,
  source files, and binary metadata. Python tooling runs through `uv`.
- `docs/TOOLS.md` - launcher and tool setup notes.

## Original Guided Set

Suggested order:

1. `crackmes/crackme_1_TLOD/EasyCrackMe.exe`
2. `crackmes/crackme_2_RedXen/C File CrackMe.exe`
3. `crackmes/crackme_4_psyr3n/PIDXploit.exe`
4. `crackmes/crackme_3_Danofred/keygenMe - 01.exe`

Read the matching files under `solutions/` after attempting each binary.

## Extra Practice

See `practice/README.md`.

The most useful local additions are:

- `practice/crackmes-one/extracted/iseey0u-crackme1-2026-05-10/`
- `practice/crackmes-one-ctf-2026/wallpaper/`
- `practice/pwncollege-program-security-dojo/reverse-engineering/`
- `practice/nightmare/modules/03-beginner_re/`

For a broader map, read `practice/INDEX.md` and `practice/CURATION.md`.

## Notes

- Ghidra project databases, lock files, and Wine prefixes are ignored so clones
  stay portable.
- Python tooling uses `uv`; run `./launchpad view` to let `uv` resolve the
  viewer script dependencies.
- Binary artifacts are marked as binary in `.gitattributes` to avoid noisy diffs.
- crackmes.one archives use the password `crackmes.one`.
