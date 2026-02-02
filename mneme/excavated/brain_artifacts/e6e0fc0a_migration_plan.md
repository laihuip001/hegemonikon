# Migration Plan: OS Reinitialization

## Goal
Securely backup the Antigravity environment (`.gemini` folder, workspaces) and provide a clear restoration guide after Windows is reset.

## ⚠️ Critical Warning
**OS reinitialization will wipe `C:\Users\raikh`.**
You MUST copy the folders listed below to an **External Drive (USB/HDD)** or **Cloud Storage (Google Drive/Dropbox)** before resetting Windows.

## 1. Backup Phase (Before Reset)

### A. Git Repositories
Ensure all changes are committed and pushed to remote repositories (GitHub/GitLab).
- [ ] Check `antigravity` repository status (Automated by Agent)
- [ ] Push all local branches

### B. Manual Copy List
Copy these folders to your external location:
1.  **Antigravity Brain & Core**
    *   Source: `C:\Users\raikh\.gemini`
    *   *Includes: `Forge` (Knowledge Base), `antigravity` (Workspaces), Agent Memory, Artifacts.*
2.  **SSH Keys & Configs (If applicable)**
    *   Source: `C:\Users\raikh\.ssh`
    *   Source: `C:\Users\raikh\.gitconfig`
3.  **Other Project Folders**
    *   Check `C:\Users\raikh\Projects` or similar if exists.

### C. VS Code / Antigravity Extensions
- Capture list of extensions (Agent will attempt to list these).

## 2. Restoration Phase (After Reset)

1.  **Install Prerequisites**
    *   Git, Python, VS Code (or Antigravity IDE).
    *   Docker (if used).
2.  **Restore Data**
    *   Copy `.gemini` folder back to `C:\Users\raikh\.gemini`.
    *   Restore `.ssh` keys.
3.  **Environment Setup**
    *   Re-login to Antigravity/Gemini.
    *   Check `git config --global user.name` and `email`.

## Agent Action Items
- [ ] Commit all changes in current workspace.
- [ ] Generate a list of critical paths to verify.
