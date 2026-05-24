# Practice Index

This is the high-level route through the library.

## Start Here

1. Original guided set:
   - `../crackmes/crackme_1_TLOD/EasyCrackMe.exe`
   - `../crackmes/crackme_2_RedXen/C File CrackMe.exe`
   - `../crackmes/crackme_4_psyr3n/PIDXploit.exe`
   - `../crackmes/crackme_3_Danofred/keygenMe - 01.exe`
2. Newer crackmes.one beginner target:
   - `crackmes-one/extracted/iseey0u-crackme1-2026-05-10/crackmes.exe`
3. Short CTF-style RE:
   - `crackmes-one-ctf-2026/wallpaper/`
   - `crackmes-one-ctf-2026/FLRSCRNSVR/`
4. Guided classroom-style RE:
   - `pwncollege-program-security-dojo/reverse-engineering/`
5. Guided writeup-heavy RE:
   - `nightmare/modules/02-intro_tooling/ghidra/`
   - `nightmare/modules/03-beginner_re/`

## Topic Map

| Topic | Local paths |
| --- | --- |
| Beginner crackmes | `../crackmes/`, `crackmes-one/` |
| Windows crackmes | `../crackmes/`, `crackmes-one-ctf-2026/Fatmike*`, `nightmare/modules/21-dot_net/` |
| Ghidra/tooling | `../docs/TOOLS.md`, `nightmare/modules/02-intro_tooling/` |
| Keygen/math constraints | `../solutions/crackme_3/`, `nightmare/modules/12-z3/`, `nightmare/modules/13-angr/` |
| Patching | `nightmare/modules/20-patching_and_jumping/`, `crackmes-one-ctf-2026/Fatmike_02/` |
| VM/custom arch | `crackmes-one-ctf-2026/FlipVM/`, `nightmare/modules/23-custom_architecture/` |
| Emulation targets | `nightmare/modules/34-emulated_targets/` |
| Obfuscation | `nightmare/modules/22-movfuscation/`, `nightmare/modules/36-obfuscated_reversing/` |
| Network-shaped logic | `crackmes-one-ctf-2026/connected/`, `crackmes-one-ctf-2026/httpd/` |
| Exploitation-adjacent | `pwncollege-program-security-dojo/program-*`, `nightmare/modules/04-*` and later exploit modules |

## Commands

List likely binaries:

```sh
../launchpad list
```

Run a Windows binary with Wine:

```sh
../launchpad wine ../crackmes/crackme_4_psyr3n/PIDXploit.exe
```

Start Ghidra:

```sh
../launchpad ghidra
```

## Notes

- crackmes.one zip password: `crackmes.one`
- Some CTF folders include spoiler READMEs or official solutions.
- The pwn.college mirror is useful as source material, but the hosted dojo is
  still the best way to run those challenges as intended.
