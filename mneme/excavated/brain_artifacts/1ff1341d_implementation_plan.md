# OMEGA Module Recovery Plan

## Goal Description
Recover the "OMEGA" configuration modules (M0, M1, M6, M7, M9, etc.) found in the backup location `G:\その他のパソコン\Forge\.gemini\prompts\modules` and integrate them into the current workspace to resume the refinement work.

## User Review Required
> [!IMPORTANT]
> The recovered files have timestamps from TODAY. Please confirm if these are the correct "midway" files.

## Proposed Changes

### Configuration Modules
Import the following modules to `C:\Users\raikh\.gemini\Forge\prompts\modules` (or appropriate path based on current structure):

#### [NEW] [M0_MISSION_COMMAND.xml](file:///G:/その他のパソコン/Forge/.gemini/prompts/modules/M0_MISSION_COMMAND.xml)
#### [NEW] [M1_INPUT_GATE.xml](file:///G:/その他のパソコン/Forge/.gemini/prompts/modules/M1_INPUT_GATE.xml)
#### [NEW] [M6_CONTEXT_NEXUS.xml](file:///G:/その他のパソコン/Forge/.gemini/prompts/modules/M6_CONTEXT_NEXUS.xml)
#### [NEW] [M7_ADVERSARIAL_COUNCIL.xml](file:///G:/その他のパソコン/Forge/.gemini/prompts/modules/M7_ADVERSARIAL_COUNCIL.xml)
#### [NEW] [M9_PROTOCOL_LOADER.xml](file:///G:/その他のパソコン/Forge/.gemini/prompts/modules/M9_PROTOCOL_LOADER.xml)

### Kernel Integration
#### [MODIFY] [GEMINI.md](file:///C:/Users/raikh/.gemini/GEMINI.md)
- Update code to load these external modules instead of inline definitions if that was the intent.
- Or simply place them for reference.

## Verification Plan

### Manual Verification
1.  User review of imported files.
2.  Check if `GEMINI.md` references them correctly (if applicable).
