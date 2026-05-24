# Curation Notes

The repository intentionally keeps a lot of material. The quality bar is in the
navigation: every major bundle is labeled by usefulness, spoiler risk, and
distance from classic crackmes.

## Quality Tiers

### Tier 1: Crackme Core

Best match for the repo:

- `../crackmes/`
- `../solutions/`
- `crackmes-one/`
- `crackmes-one-ctf-2026/wallpaper/`
- `crackmes-one-ctf-2026/FLRSCRNSVR/`
- `crackmes-one-ctf-2026/Fatmike/`
- `crackmes-one-ctf-2026/Fatmike_02/`

These are closest to the Ghidra/Wine crackme workflow.

### Tier 2: Guided Reverse Engineering

Good next steps once the basics feel easy:

- `pwncollege-program-security-dojo/reverse-engineering/`
- `nightmare/modules/00-intro/`
- `nightmare/modules/01-intro_assembly/`
- `nightmare/modules/02-intro_tooling/`
- `nightmare/modules/03-beginner_re/`
- `nightmare/modules/12-z3/`
- `nightmare/modules/13-angr/`
- `nightmare/modules/20-patching_and_jumping/`
- `nightmare/modules/21-dot_net/`

These are still RE-first, with varying levels of automation or patching.

### Tier 3: Weird RE

Useful for breadth and fun:

- `crackmes-one-ctf-2026/FlipVM/`
- `crackmes-one-ctf-2026/connected/`
- `crackmes-one-ctf-2026/httpd/`
- `nightmare/modules/22-movfuscation/`
- `nightmare/modules/23-custom_architecture/`
- `nightmare/modules/34-emulated_targets/`
- `nightmare/modules/36-obfuscated_reversing/`

These are less like normal key checks, but they build useful instincts around
VMs, emulation, obfuscation, network-shaped logic, and unusual formats.

### Tier 4: Exploitation-Adjacent

Keep these because they are useful security practice, but treat them as a
different lane from crackmes:

- `pwncollege-program-security-dojo/program-security/`
- `pwncollege-program-security-dojo/program-exploitation/`
- `pwncollege-program-security-dojo/return-oriented-programming/`
- `pwncollege-program-security-dojo/dynamic-allocator-misuse/`
- Nightmare modules from `04-bof_variable` onward when the topic is stack,
  heap, shellcoding, ROP, format strings, or allocator internals.

These are not bad material; they just should not be mistaken for beginner
Ghidra crackmes.

### Tier 5: Spoiler-Heavy Or Large CTF Material

Useful to archive, but read carefully:

- `crackmes-one-ctf-2026/A_MatterOfTime/`
- `crackmes-one-ctf-2026/Matryoshka v2/`
- `crackmes-one-ctf-2026/What did you type/`
- `crackmes-one-ctf-2026/cryptpad/`
- `crackmes-one-ctf-2026/moment/`

Some upstream READMEs contain flags or intended solutions. Prefer `Handout/`
first when present.

## Spoiler Policy

Many mirrored CTF folders include flags, source code, or official solutions.
That is useful for guided practice, but not for first attempts. A good habit:

1. Open the handout binary or handout README.
2. Make a first pass in Ghidra, x64dbg, Wine, gdb, or strings.
3. Use the top-level README/solution files only after getting stuck.

## CS.RIN.RU

CS.RIN.RU is not mirrored. The forum is account-gated and mixed-purpose. Use it
manually only for legal learning discussions, tooling notes, and public
references; avoid game files, cracks, DRM bypasses, or redistribution threads.
