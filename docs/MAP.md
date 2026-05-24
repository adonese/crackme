# Repo Map

This repo is intentionally broad, but it should not feel like a dump. Use this
file as the front door.

## Top Level

| Path | Purpose |
| --- | --- |
| `crackmes/` | Original four tutorial binaries. Start here if you want classic Ghidra/Wine crackmes. |
| `solutions/` | Spoiler walkthroughs for the original four. Open only after trying the matching binary. |
| `practice/crackmes/` | Extra standalone crackmes, currently selected crackmes.one downloads. |
| `practice/ctf/` | CTF challenge packs. Expect handouts, source, writeups, and spoiler files. |
| `practice/courses/` | Larger mirrored courses such as pwn.college and Nightmare. |
| `docs/` | Setup notes, this map, the Ghidra import tutorial, and the hash manifest. |
| `tools/` | Local Python helpers. They run through `uv`. |
| `launchpad` | Main entry point for Wine, Ghidra, viewer, maps, and inventory checks. |

## First Route

1. `crackmes/README.md`
2. `crackmes/crackme_1_TLOD/EasyCrackMe.exe`
3. `crackmes/crackme_2_RedXen/C File CrackMe.exe`
4. `crackmes/crackme_4_psyr3n/PIDXploit.exe`
5. `crackmes/crackme_3_Danofred/keygenMe - 01.exe`
6. `practice/ROUTES.md`

## Practice Lanes

| Lane | Good entry point | What to expect |
| --- | --- | --- |
| Extra crackmes | `practice/crackmes/crackmes-one/README.md` | Small standalone binaries and their downloaded source pages. |
| CTF RE | `practice/ctf/README.md` | Handouts first, then solutions/source only when stuck. |
| pwn.college | `practice/courses/pwncollege-program-security-dojo/README.md` | Many generated variants per level. Prefer the RE module first. |
| Nightmare | `practice/courses/nightmare/LOCAL_GUIDE.md` | Writeup-heavy modules from tooling through exploitation. |

## Commands

```sh
./launchpad map
./launchpad view
./launchpad list
./launchpad inventory verify
```

## Hash Checks

`docs/MATERIALS.sha256` records hashes for tracked and unignored files. Use it
after a folder move, clone, or redownload:

```sh
./launchpad inventory verify
```

Refresh it after intentionally changing files:

```sh
./launchpad inventory write
```
