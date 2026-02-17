# RDP Connectivity & Recovery Guide

> **Target**: Debian 13 Host accessed from Windows/macOS/Linux
> **Last Updated**: 2026-02-06

This guide provides comprehensive instructions for connecting to the Hegemonikón Debian host and recovering from common RDP-related failures.

---

## 📡 Connection Information

| Item | Value |
| :--- | :--- |
| **Tailscale IP** | `100.80.253.2` |
| **Local IP (LAN)** | `192.168.1.111` |
| **RDP Port** | `3389` |
| **Protocol** | RDP (Standard) |
| **Session** | Xfce4 (Recommended) |

---

## 🚀 Pre-Connection Checklist

To prevent the "Black Screen" issue (concurrent session conflict), **log out of the physical local session** before connecting via RDP.

### Remote Logout via SSH

```bash
# Windows (PowerShell) or macOS/Linux Terminal
ssh makaron8426@100.80.253.2 "gnome-session-quit --logout --no-prompt"

# Alternative: Force terminate session
ssh -tt makaron8426@100.80.253.2 "sid=\$(loginctl list-sessions --no-legend | awk '\$3==\"makaron8426\"{print \$1; exit}'); [ -n \"\$sid\" ] && sudo loginctl terminate-session \$sid"
```

---

## 🖥️ Client Setup

### 1. Windows (Native)

1. Open `mstsc` (Remote Desktop Connection).
2. Computer: `100.80.253.2`.
3. **Local Resources Tab**: Ensure **Clipboard** is checked.
4. Connect and enter credentials.

### 2. macOS / Mobile

Use **Microsoft Remote Desktop** app. Add PC with the Tailscale IP.

### 3. Linux (Remmina / xfreerdp)

```bash
# xfreerdp example
xfreerdp /v:100.80.253.2 /u:makaron8426 /size:1920x1080 /dynamic-resolution +clipboard
```

---

## 🚨 Immediate Recovery Procedures

### Pattern A: Connection Refused (Port 3389)

**Cause**: `gnome-remote-desktop` is blocking the port.
**Fix**:

```bash
ssh makaron8426@100.80.253.2 "sudo systemctl stop gnome-remote-desktop; sudo systemctl restart xrdp"
```

### Pattern B: Black Screen after Login

**Cause**: Session manager crash or idle lock.
**Fix**:

1. Check if another session is active: `loginctl list-sessions`.
2. Restart Xfce components: `killall xfdesktop; xfdesktop &`.

### Pattern C: Clipboard Sync Fails (One-way)

**Fix**:

1. **Restart chansrv**: `killall xrdp-chansrv` (It auto-restarts).
2. **CopyQ Test**: `copyq disable` (Check if CopyQ is intercepting and failing).
3. **Verify mstsc settings**: Ensure "Clipboard" is checked in Local Resources.
4. **Windows History Limitation**: Copies from RDP (Debian -> Windows) **do not** automatically appear in Windows `Win+V` history. They can be pasted directly, but to see them in `Win+V`, you must paste and re-copy them locally on Windows.

### Pattern D: Image Sharing Failure

**Cause**: xrdp natively only supports text-based clipboard.
**Workaround (Visual Bridge)**:

1. Windows: Install **ShareX**.
2. ShareX Settings: Set "Custom screenshots folder" to a **Syncthing** synced folder (e.g., `C:\Users\makar\Hegemonikon\screenshots`).
3. Screenshots will appear instantly in Debian at `~/Sync/screenshots/`.

---

## 🛠️ Windows Client Specific Fixes

### Disable UDP (Fixes Error 0x904 / 0x7)

Run in Admin PowerShell:

```powershell
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services\Client" /v fClientDisableUDP /t REG_DWORD /d 1 /f
```

---

## 📋 Core Lessons

1. **Mask > Disable**: Always `mask` conflicting services (like `gnome-remote-desktop`) to prevent them from "resurrecting".
2. **Session Identification**:
   - **Xfce**: Minimal panel at top/bottom.
   - **GNOME**: "Activities" in top-left, no taskbar.
   - **KDE**: Windows-like taskbar.
3. **Xsession Control**: Use `~/.xsession` containing `startxfce4` to force RDP into a lightweight environment.
