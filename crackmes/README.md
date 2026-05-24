# Original Crackmes

These are the four original tutorial binaries. They are the cleanest starting
point because the matching spoiler walkthroughs live in `../solutions/`.

Suggested order:

1. `crackme_1_TLOD/EasyCrackMe.exe`
2. `crackme_2_RedXen/C File CrackMe.exe`
3. `crackme_4_psyr3n/PIDXploit.exe`
4. `crackme_3_Danofred/keygenMe - 01.exe`

Run one with Wine:

```sh
./launchpad wine crackmes/crackme_1_TLOD/EasyCrackMe.exe
```

Open Ghidra:

```sh
./launchpad ghidra
```

Local Ghidra project files are ignored. Import binaries into your own local
project instead of committing `.gpr` or `.rep` directories.
