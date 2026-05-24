# Wine Audit

Generated with `tools/wine_audit.py` using `WINEPREFIX=/home/adonese/.cache/crackme-wine-audit`.
Per-file timeout: `8s`.

A timeout is not automatically a failure. Many crackmes open a GUI dialog
or wait for input, so the important failure signal is an immediate Wine
loader error, display error, missing runtime, or unhandled page fault.
The audit includes `.exe` files and renamed Windows executables such as
`*.exe.bin`, but it does not execute DLLs.

Summary: `crash`: 1, `launched-gui-timeout`: 5, `launched-timeout`: 5, `needs-input`: 1, `needs-interaction`: 1, `ok-exited`: 10

| Status | File | Type | Exit | Notes |
| --- | --- | --- | --- | --- |
| `ok-exited` | `crackmes/crackme_1_TLOD/EasyCrackMe-patched.exe` | PE32 executable (console) Intel 80386, for MS Windows, 5 sections | `0` | Process exited cleanly. |
| `ok-exited` | `crackmes/crackme_1_TLOD/EasyCrackMe.exe` | PE32 executable (console) Intel 80386, for MS Windows, 5 sections | `0` | Process exited cleanly. |
| `launched-timeout` | `crackmes/crackme_2_RedXen/C File CrackMe.exe` | PE32 executable (console) Intel 80386, for MS Windows, 13 sections | `timeout` | Process stayed alive; likely waiting for UI/input. |
| `launched-timeout` | `crackmes/crackme_2_RedXen/file.exe` | PE32 executable (console) Intel 80386, for MS Windows, 13 sections | `timeout` | Process stayed alive; likely waiting for UI/input. |
| `ok-exited` | `crackmes/crackme_3_Danofred/keygenMe - 01.exe` | PE32+ executable (console) x86-64, for MS Windows, 15 sections | `0` | Process exited cleanly. |
| `ok-exited` | `crackmes/crackme_4_psyr3n/PIDXploit.exe` | PE32 executable (console) Intel 80386, for MS Windows, 13 sections | `0` | Process exited cleanly. |
| `launched-timeout` | `practice/courses/nightmare/modules/20-patching_and_jumping/csawquals16_gametime/edit.exe` | PE32 executable (console) Intel 80386, for MS Windows, 6 sections | `timeout` | Process stayed alive; likely waiting for UI/input. |
| `launched-timeout` | `practice/courses/nightmare/modules/20-patching_and_jumping/csawquals16_gametime/gametime.exe` | PE32 executable (console) Intel 80386, for MS Windows, 6 sections | `timeout` | Process stayed alive; likely waiting for UI/input. |
| `launched-gui-timeout` | `practice/courses/nightmare/modules/21-dot_net/bikinibonanza/bikinibonanza.exe` | PE32 executable (GUI) Intel 80386 Mono/.Net assembly, for MS Windows, 5 sections | `timeout` | GUI process stayed open until timeout. |
| `ok-exited` | `practice/courses/nightmare/modules/21-dot_net/dot_net/DotNetReversing.exe` | PE32 executable (console) Intel 80386 Mono/.Net assembly, for MS Windows, 3 sections | `0` | Process exited cleanly. |
| `launched-gui-timeout` | `practice/courses/nightmare/modules/21-dot_net/whitehat18_re06/reverse.exe` | PE32 executable (GUI) Intel 80386 Mono/.Net assembly, for MS Windows, 3 sections | `timeout` | GUI process stayed open until timeout. |
| `ok-exited` | `practice/crackmes/crackmes-one/extracted/danofred-keygenme-2022-02-22/keygenMe - 01.exe` | PE32+ executable (console) x86-64, for MS Windows, 15 sections | `0` | Process exited cleanly. |
| `ok-exited` | `practice/crackmes/crackmes-one/extracted/iseey0u-crackme1-2026-05-10/crackmes.exe` | PE32+ executable (console) x86-64, for MS Windows, 7 sections | `0` | Process exited cleanly. |
| `ok-exited` | `practice/crackmes/crackmes-one/extracted/psyr3n-pidxploit-2024-10-04/PIDXploit.exe` | PE32 executable (console) Intel 80386, for MS Windows, 13 sections | `0` | Process exited cleanly. |
| `launched-timeout` | `practice/crackmes/crackmes-one/extracted/redxen-c-file-2022-07-25/C File CrackMe/C File CrackMe.exe` | PE32 executable (console) Intel 80386, for MS Windows, 13 sections | `timeout` | Process stayed alive; likely waiting for UI/input. |
| `ok-exited` | `practice/crackmes/crackmes-one/extracted/tlodeasy-2021-05-02/EasyCrackMe.exe` | PE32 executable (console) Intel 80386, for MS Windows, 5 sections | `0` | Process exited cleanly. |
| `needs-interaction` | `practice/ctf/crackmes-one-ctf-2026/A_MatterOfTime/Handout/a_matter_of_time.exe` | PE32+ executable (console) x86-64, for MS Windows, 7 sections | `3` | Console program reached an input prompt; audit stdin is disabled. |
| `launched-gui-timeout` | `practice/ctf/crackmes-one-ctf-2026/cryptpad/handout/cryptpad.exe` | PE32 executable (GUI) Intel 80386, for MS Windows, 4 sections | `timeout` | GUI process stayed open until timeout. |
| `launched-gui-timeout` | `practice/ctf/crackmes-one-ctf-2026/Fatmike/Handout/Crackme.exe` | PE32 executable (GUI) Intel 80386, for MS Windows, 5 sections | `timeout` | GUI process stayed open until timeout. |
| `launched-gui-timeout` | `practice/ctf/crackmes-one-ctf-2026/Fatmike_02/Handout/RecordPlayer.exe` | PE32+ executable (GUI) x86-64, for MS Windows, 6 sections | `timeout` | GUI process stayed open until timeout. |
| `ok-exited` | `practice/ctf/crackmes-one-ctf-2026/FLRSCRNSVR/handout/FLRSCRNSVR.SCR` | PE32+ executable (GUI) x86-64, for MS Windows, 6 sections | `0` | Process exited cleanly. |
| `needs-input` | `practice/ctf/crackmes-one-ctf-2026/Matryoshka v2/Handout/LicenseChecker.exe` | PE32+ executable (console) x86-64, for MS Windows, 6 sections | `1` | Challenge expects a candidate license.bin in the executable directory. |
| `crash` | `practice/ctf/crackmes-one-ctf-2026/moment/handout/moment.exe.bin` | PE32+ executable (console) x86-64, for MS Windows, 9 sections | `timeout` | Wine reported an unhandled page fault. |

## Known Findings

### RedXen C File CrackMe

The RedXen executable copies in this repo hash to `a6cdc45041d4af08571553c881fbb55a7f217d27c2a01310298f55b65034db98`. The bundled `password.bin` is present with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
This crackme is cwd-sensitive: launching it as `wine path/to/C File CrackMe.exe`
from the repo root can crash because the program opens `password.bin` relative to
the current directory and does not handle a missing file cleanly. The `wine-audit`
script and `./launchpad wine ...` both launch from the executable directory, which
keeps the sidecar file visible.

### A Matter Of Time

`a_matter_of_time.exe` is extracted from the passworded handout zip. The
program reaches its intro text and `Press ENTER` prompt under Wine. The
audit intentionally disables stdin, so a nonzero exit at that prompt is
classified as `needs-interaction`, not as a broken executable.

Upstream handout: https://github.com/crackmesone/ctf-2026-challenges-public/tree/main/A_MatterOfTime/Handout

### FLRSCRNSVR.SCR

`FLRSCRNSVR.SCR` is extracted from the passworded handout zip and launches
as a GUI screensaver binary under Wine. The upstream README records SHA-256
`65e0485c9780a856d0542aa88d921e253123b7326d064ff3cae6827509cf537f`,
which matches the extracted file.

Upstream challenge: https://github.com/crackmesone/ctf-2026-challenges-public/tree/main/FLRSCRNSVR

### Matryoshka v2 LicenseChecker

`LicenseChecker.exe` exits with `Failed to read license.bin` until you provide a
candidate `license.bin` in the same handout directory. The upstream public handout
contains only `Doll.dll` and `LicenseChecker.exe`, so this is not a local extraction
or re-zip problem.

Upstream handout: https://github.com/crackmesone/ctf-2026-challenges-public/tree/main/Matryoshka%20v2/Handout
Spoiler-sensitive writeup confirming the first-run behavior: https://blog.cloudlabs.ufscar.br/sec/matryoshka-v2/

### moment.exe.bin

`moment.exe.bin` is a Windows PE executable with a protective `.bin` suffix.
The handout README says the program can be run by removing `.bin`, and also
describes it as an anti-tamper challenge. The Wine audit still records an
unhandled page fault, and a temporary local rename to `moment.exe` produced
the same Wine crash. Treat this as a Wine/anti-tamper compatibility issue,
not as a missing file or bad archive.

Upstream handout: https://github.com/crackmesone/ctf-2026-challenges-public/tree/main/moment/handout

## Attention Logs

### practice/ctf/crackmes-one-ctf-2026/Matryoshka v2/Handout/LicenseChecker.exe

- Status: `needs-input`
- Type: PE32+ executable (console) x86-64, for MS Windows, 6 sections
- Exit: `1`

```text
Failed to read license.bin
```

### practice/ctf/crackmes-one-ctf-2026/moment/handout/moment.exe.bin

- Status: `crash`
- Type: PE32+ executable (console) x86-64, for MS Windows, 9 sections
- Exit: `timeout`

```text
0120:err:sync:RtlLeaveCriticalSection section 00006FFFFAA08FC0 "dlls/msvcp90/misc.c: _Lockit critical section" is not acquired
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x0000001
...
wine: Unhandled page fault on read access to 00006FFFFFFF003E at address 00000001400EE167 (thread 013c), starting debugger...
WineDbg attached to pid 011c
...
ormation (0x000000a3,(nil),0x00000000,0x7fffffc1fe4c) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0164:fixme:ntdll:NtQuerySystemInformation (0x000000a3,(nil),0x00000000,0x7fffffc1fe4c) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0164:fixme:ntdll:NtQuerySystemInformation (0x000000a3,(nil),0x00000000,0x7fffffc1fe4c) stub
0134:fixme:ntdll:NtQuerySystemInformation (0x00000016,(nil),0x00000000,0x7fffff40fe30) stub
0164:fixme:ntdll:NtQuerySystemInformation (0x000000a3,(nil),0x00000000,0x7fffffc1fe4c) stub
0164:fixme:ntdll:NtQuerySystemInformation (0x000000a3,(nil),0x00000000,0x7fffffc1fe4c) stub
WineDbg attached to pid 011c
```
