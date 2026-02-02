# Import Configuration from G Drive

## Goal Description
Import configuration directories (`.gemini` and `.antigravity`) from the user's local G: drive (`G:\その他のパソコン\Forge`) into the current workspace (`C:\Users\user\.gemini\Forge`). This will synchronize the agent's memory and settings.

## User Review Required
> [!IMPORTANT]
> This operation will Overwrite existing files in `.gemini` and `.antigravity` folders if they exist.
> Based on initial inspection, these folders may not exist in the destination yet, but if they do, their contents will be merged/replaced.

## Proposed Changes

### Configuration Import
Use `robocopy` to mirror the directories. This ensures all subdirectories and files are copied correctly.

#### [NEW/MODIFY] .gemini Directory
- Source: `G:\その他のパソコン\Forge\.gemini`
- Destination: `C:\Users\user\.gemini\Forge\.gemini`

#### [NEW/MODIFY] .antigravity Directory
- Source: `G:\その他のパソコン\Forge\.antigravity`
- Destination: `C:\Users\user\.gemini\Forge\.antigravity`

## Verification Plan

### Automated Verification
After copy, run `list_dir` on destination to confirm files are present.
- `list_dir C:\Users\user\.gemini\Forge\.gemini`
- `list_dir C:\Users\user\.gemini\Forge\.antigravity`
