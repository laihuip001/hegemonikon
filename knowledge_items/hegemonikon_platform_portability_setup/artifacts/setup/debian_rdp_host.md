# Debian RDP Host Setup Guide

This guide details how to transform a Debian system into a Remote Desktop Protocol (RDP) host, allowing connections from Windows, Linux, or macOS clients.

## 1. Prerequisites

- Sudo access.
- Local IP address (check with `ip -br a`).
- Firewall (UFW) installed.

## 2. Desktop Environment Installation

XRDP requires a graphical environment. Lightweight environments are recommended for stability.

### Xfce4 (Recommended)

```bash
sudo apt update
sudo apt install -y xfce4 xfce4-goodies
sudo systemctl set-default graphical.target
```

### MATE (Alternative)

```bash
sudo apt install -y mate-desktop-environment
```

## 3. XRDP & VNC Server Installation

Install XRDP and TigerVNC for optimal performance on Debian 11+.

```bash
sudo apt install -y xrdp tigervnc-standalone-server
```

### 3.1. Interactive Configuration

During installation, you may be prompted to select a **Default Display Manager**.

- **Recommendation**: Select **`lightdm`**.
- **Reason**: `gdm3` (GNOME) triggers `gnome-remote-desktop`, which attempts to bind to port 3389, leading to the `g_tcp_bind` error and `xrdp` startup failure. **LightDM** is lightweight, Xfce-native, and does not compete for the RDP port.
- **Interaction**: Use `Tab` to navigate and `Enter` to confirm.

### 3.2. Switching to LightDM (Existing Installations)

If you already have `gdm3` installed and are experiencing port conflicts:

```bash
# Install LightDM
sudo apt install -y lightdm lightdm-gtk-greeter

# Set as default
sudo dpkg-reconfigure lightdm

# Disable GDM
sudo systemctl disable gdm
```

### 3.3. SDDM (Advanced/Customizable)

SDDM (Simple Desktop Display Manager) is the default for KDE but works excellently for Xfce + RDP environments. It supports high-quality themes (e.g., Sugar Candy, Aerial) and does not trigger GNOME-specific port conflicts.

```bash
# Install SDDM
sudo apt install -y sddm

# Set as default
sudo dpkg-reconfigure sddm

# Enable and start
sudo systemctl enable --now sddm
```

---

## 4. Desktop Sessions

Linux allows multiple desktop environments to be installed simultaneously. The **Session** determines which environment is loaded after login.

### 4.1. Common Sessions

| Session | Environment | Characteristics |
| :--- | :--- | :--- |
| **Xfce Session** | Xfce | Lightweight, Nemo integration, preferred for RDP. |
| **GNOME** | GNOME Shell | Modern, high resource usage, potential RDP port conflicts. |
| **GNOME Classic** | GNOME 2-style | Traditional layout using GNOME 3 backend. |

### 4.2. Switching Sessions (The "Confusion Fix")

If a login manager (like LightDM, SDDM, or GDM) is used, look for a "Session" or "Desktop" icon/dropdown (often in the bottom-left or top-right, sometimes only visible after selecting the username) to select the desired environment before entering your password.

**💡 Identification Trace:**

- **"It looks like before (Xfce)"**: You logged into the **Xfce Session**.
- **"It looks like Windows"**: You logged into the **Plasma (X11)** session.
- **"It looks like macOS (no taskbar, Activities top-left)"**: You logged into the **GNOME** session.

If the desktop environment "hasn't changed" after installation, you likely skipped this step and logged into the default (previous) session.

---

## 5. Service Configuration

Enable and start the XRDP service.

```bash
sudo systemctl enable xrdp
sudo systemctl start xrdp
```

### SSL Certificate Permissions

Add the `xrdp` user to the `ssl-cert` group to allow access to the snakeoil keys.

```bash
sudo usermod -a -G ssl-cert xrdp
```

## 5. Black Screen Prevention (DBUS)

To prevent the common "black screen" issue, modify the XRDP startup script.

Edit `/etc/xrdp/startwm.sh` and add these lines before `test -x /etc/xrdp/Xsession`:

```bash
unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR
```

## 6. User Session Configuration

Specify the session manager in the user's home directory.

**For Xfce4:**

```bash
echo "xfce4-session" > ~/.xsession
```

Restart the service:

```bash
sudo systemctl restart xrdp
```

## 7. Input and IDE Configuration (Optional)

### Japanese Input (Recommended: Fcitx5)

IBus can have pre-edit delay issues over RDP. **Fcitx5** is more stable.

```bash
# Install Fcitx5 + Mozc
sudo apt install -y fcitx5 fcitx5-mozc

# Add to ~/.xsession (before xfce4-session)
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
fcitx5 -d &
```

#### Fixing Input Delay (Batching/Contamination)

Characters appearing only after Enter or appearing as "garbled batch input" is due to pre-edit display issues over RDP.

#### Solution: Disable Pre-edit (Inline Input)

- **GUI (Recommended)**: Run `fcitx5-configtool` -> **Mozc** -> **Configure** -> Toggle **PreeditMode** to **Off**.
- **Framework Level (More robust)**:

  ```bash
  mkdir -p ~/.config/fcitx5/conf
  cat > ~/.config/fcitx5/conf/fcitx.conf << 'EOF'
  [Behavior]
  # Disable inline pre-edit (show in separate window instead)
  ShareInputState=No
  PreeditEnabledByDefault=False
  ShowInputMethodInformation=True
  EOF
  ```

- **Mozc Specific**:

  ```bash
  echo "PreeditMode=Off" > ~/.config/fcitx5/conf/mozc.conf
  fcitx5 -r
  ```

- **Deep Mozc Configuration**:
  If the input behavior still feels "batched" or latency is high, use the Mozc setup tool to adjust suggestion/input settings:

  ```bash
  /usr/lib/mozc/mozc_tool --mode=config_dialog
  ```

#### Troubleshooting Network Latency

If input is still delayed after disabling pre-edit, the issue may be network-level:

- **Tailscale Connection**: Ensure you have a "direct" connection.

  ```bash
  tailscale ping <HOST_IP>
  # Look for "via <direct-ip>" instead of "via DERP"
  ```

- **RDP Experience Settings**: In `mstsc` (Windows), set the performance level to "Low-speed broadband" to reduce visual features and improve input responsiveness.

  ```bash
  /usr/lib/mozc/mozc_tool --mode=config_dialog
  ```

#### Troubleshooting: Mozc stops producing Japanese

If Fcitx5 is running and Mozc is selected but the input remains in English (Alpha mode), there is likely a mismatch between the running process and the environment variables.

**Symptoms:**

- `fcitx5` process is running.
- Mozc is selected in the tray.
- Typing still produces English characters even after toggling.

**Cause:**
Environment variables (`GTK_IM_MODULE`, `QT_IM_MODULE`, `XMODIFIERS`) are still pointing to `ibus` (default on many Debian distros) while `fcitx5` is running.

**Immediate Fix:**
Unify the environment and restart the daemon.

```bash
# Check current variables
echo $GTK_IM_MODULE  # If it says 'ibus', this is the problem

# Correct and restart
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
fcitx5 -r -d
```

*To make this permanent, ensure these exports are in your `~/.xsession`. Avoid setting contradicting IM variables in `~/.bashrc`, or unify them to `fcitx` to prevent local shell sessions from breaking the IME state.*

#### Environment Variable Unification (Local vs. RDP)

If you use the machine both locally and via RDP, contradictory settings in `~/.bashrc` and `~/.xsession` will cause Mozc to stop responding.

**Fix**: Ensure `~/.bashrc` also points to `fcitx` or does not define these variables.

```bash
# In ~/.bashrc
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
fcitx5 -d &
```

#### ⚠️ Recovery: Complete Reset

If Mozc stops working or configuration gets cluttered:

```bash
# 1. Clear config and kill daemon
rm -rf ~/.config/fcitx5/
pkill fcitx5

# 2. Force default profile with Mozc
mkdir -p ~/.config/fcitx5/profile
cat > ~/.config/fcitx5/profile/default << 'EOF'
[Groups/0]
Name=Default
Default Layout=us
DefaultIM=mozc

[Groups/0/Items/0]
Name=keyboard-us

[Groups/0/Items/1]
Name=mozc

[GroupOrder]
0=Default
EOF

# 3. Restart daemon
fcitx5 -d
```

#### Alternative: IBus (if pre-edit delay is acceptable)

```bash
sudo apt install -y ibus ibus-mozc
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus
ibus-daemon -drx &
```

*Note: For Electron apps, reaching the correct GTK IM module often requires forcing the Ozone platform and specifying the GTK version.*

#### Convenience Wrapper Script (`antigravity-fcitx.sh`)

To simplify launching the IDE with these flags, use a wrapper script:

```bash
#!/bin/bash
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx

# Start fcitx5 if not running
pgrep -x fcitx5 > /dev/null || fcitx5 -d

# Launch with Wayland/X11 IME support flags
exec /usr/share/antigravity/antigravity \
    --enable-wayland-ime \
    --enable-features=UseOzonePlatform,WaylandWindowDecorations \
    --ozone-platform-hint=auto \
    --gtk-version=4 \
    "$@"
```

### Advanced Clipboard Management (CopyQ)

CopyQ is recommended for RDP users who need multi-item history and advanced filtering, outperforming the default `xfce4-clipman`.

```bash
# Install CopyQ
sudo apt install -y copyq

# Configure Autostart
cat > ~/.config/autostart/copyq.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=CopyQ
GenericName=Clipboard Manager
Comment=Advanced clipboard manager
Icon=copyq
Exec=copyq
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
EOF
```

### Launching the Environment

## 8. Firewall and NAT Traversal (Tailscale)

While port 3389 can be allowed on the local firewall, using **Tailscale** is the recommended method for secure, zero-config access from external networks.

### Installing Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

### Retrieving the Tailscale IP

```bash
tailscale ip -4
```

*Use this IP (usually 100.x.y.z) for all remote connections.*

## 9. Firewall Rules (Local Network Only)

If NOT using Tailscale, allow traffic on port 3389.

## 10. Troubleshooting: Black Screen

For a comprehensive guide on diagnosing and preventing RDP failures (including black screens and port conflicts), refer to the [RDP Connection Failure Prevention Guide](./rdp_failure_prevention.md).

### Common Causes

| Pattern | Cause | Solution |
| :--- | :--- | :--- |
| **After 10min idle** | Xfce power manager | Disable DPMS |
| **On reconnection** | Leftover sessions | sesman.ini cleanup |
| **Tab/Window switch** | Xfce Compositor | Disable Compositing |
| **Desktop icons vanish** | xfdesktop crash | Restart xfdesktop |
| **On startup** | Port binding conflict | Mask gnome-remote-desktop |
| **On startup** | Display server timeout | Check ~/.xorgxrdp.*.log |

### 10.1 The RDP Diagnostic Ritual (Layered Approach)

When RDP fails, follow these steps in order to identify where the "chain" is broken.

1. **Tailnet Connectivity**: Can you reach the machine?
    - `tailscale ping <IP>`
2. **Port Reachability**: Is the port open?
    - `tnc <IP> -p 3389` (PowerShell) or `nc -zv <IP> 3389` (Linux)
3. **Port Ownership**: Who is listening on 3389?
    - `sudo ss -ltnp | grep ':3389'`
    - Expected: `xrdp`. Fatal Conflict: `gnome-remote-desktop`.
4. **Service Logs**: Why did it fail?
    - `sudo journalctl -u xrdp`
    - Check for `[ERROR] g_tcp_bind(..., 3389) failed bind IPv6 (errno=98)`.

### 10.2 Disable Xfce Power Management (Idle Fix)

```bash
# Disable display blanking and DPMS
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-ac -s 0
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-enabled -s false
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-on-ac-off -s 0
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-on-ac-sleep -s 0

# Disable screensaver and locking
xfconf-query -c xfce4-screensaver -p /saver/enabled -s false
xfconf-query -c xfce4-screensaver -p /lock/enabled -s false

# Remove conflicting packages
sudo apt remove -y xscreensaver light-locker
```

### 10.2 Disable Compositing (Tab-switch Black Screen)

If the screen turns black unexpectedly when switching tabs or windows:

```bash
xfconf-query -c xfwm4 -p /general/use_compositing -s false
```

### 10.3 Auto-cleanup Disconnected Sessions (Reconnection Fix)

Edit `/etc/xrdp/sesman.ini`:

```ini
[Sessions]
KillDisconnected=true
DisconnectedTimeLimit=300
IdleTimeLimit=0
```

Then restart: `sudo systemctl restart xrdp xrdp-sesman`

### 10.4 Immediate Recovery

```bash
# List sessions
ssh user@host "loginctl list-sessions"
# Kill stale session
ssh -tt user@host "sudo loginctl terminate-session <ID>"
```

### 10.5 Port Binding Conflict (g_tcp_bind failed)

If `systemctl status xrdp` shows `[ERROR] g_tcp_bind(13, 3389) failed`, it means another service (like GNOME's built-in remote desktop) is already using port 3389.

**Diagnosis**:

```bash
sudo ss -ltnp | grep ':3389'
# Look for 'gnome-remote-desktop' or similar
```

**Fix**: Disable and **mask** GNOME Remote Desktop. Masking is essential because GNOME services can be re-enabled by updates or dependencies.

```bash
# System-wide service
sudo systemctl stop gnome-remote-desktop
sudo systemctl disable gnome-remote-desktop
sudo systemctl mask gnome-remote-desktop

# User-level service (the primary culprit in recent Debian/GNOME versions)
systemctl --user stop gnome-remote-desktop.service
systemctl --user disable gnome-remote-desktop.service
systemctl --user mask gnome-remote-desktop.service
```

*Note: After masking, verify that 3389 is held by `xrdp` using `sudo ss -ltnp | grep :3389`.*

### 10.6 Diagnostic Logs

```bash
sudo tail -n 100 /var/log/xrdp-sesman.log
sudo tail -n 100 /var/log/xrdp.log
ls -lt ~/.xorgxrdp.*.log | head
```

### 10.7 xfdesktop Crash Recovery

If the desktop background or icons disappear, or the screen turns black but the panel/terminal still work, `xfdesktop` may have crashed upon power management resume.

**Immediate Fix:**

```bash
killall xfdesktop; xfdesktop &
```

**Permanent Autostart Fix:**
Create an autostart entry to monitor and restart `xfdesktop` automatically.

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/xfdesktop-restart.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=xfdesktop restart
Exec=sh -c 'while true; do xfdesktop || sleep 5; done'
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

### 10.8 Xfce RDP Optimization Ritual

If using Xfce for RDP (even if GNOME/KDE is used locally), use this ritual to optimize for latency, aesthetics, and usability:

```bash
# 1. Aesthetics: Install Modern Themes
sudo apt install -y arc-theme papirus-icon-theme

# 2. Performance: Disable Compositing (Prevents black-screen on tab-switch)
xfconf-query -c xfwm4 -p /general/use_compositing -s false

# 3. Stability: Disable DPMS/ScreenSaver (Prevents black-screen on idle)
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-enabled -s false
xfconf-query -c xfce4-screensaver -p /saver/enabled -s false 2>/dev/null || true

# 4. Usability: Fix Taskbar (Window Buttons)
# (Desktop UI) Right-click Panel -> Panel -> Add New Items -> "Window Buttons"
# This restores the "taskbar" feel for switching between open windows.
```

*Note: Theme application (Arc-Dark, Papirus-Dark) should be done via Settings -> Appearance.*

## 11. Remote Connecting

- **Windows**: Use `mstsc`.
- **Linux**: Use `Remmina`.
- **SSH Tunneling (Secure alternative)**:

  ```bash
  ssh -L 3389:localhost:3389 user@remote-host
  ```

  Then connect to `localhost:3389` on your local machine.

## 12. Performance Optimization

### 12.1. Browser (Firefox) Lag

RDP often struggles with browser rendering/scrolling.

- **Disable Hardware Acceleration**: In `about:config`, set `gfx.webrender.all` to `false` and `layers.acceleration.disabled` to `true`.
- **Disable Smooth Scrolling**: Under Settings -> General -> Browsing, uncheck "Use smooth scrolling".

### 12.2. Xfce UI Responsiveness

- **Transparency**: Avoid transparent panels or windows.
- **Window Snapping**: Can be laggy over high-latency connections.

### 12.3. RDP Error 0x904 / 0x7 (UDP Issues)

If the connection fails with code `0x904` or `0x7` despite port 3389 being open, it is often due to RDP UDP negotiation failing.

**Fix (Client-side - Windows)**:
Run the following in an Administrator PowerShell to disable UDP for RDP:

```powershell
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services\Client" /v fClientDisableUDP /t REG_DWORD /d 1 /f
```

### 12.4. HiDPI / Scaling (Small Text Fix)

On high-density displays (e.g., 15.6" Full HD), text may appear too small over RDP. Instead of lowering resolution (which causes blurriness), increase the DPI scaling.

```bash
# Set DPI to 120 (approx 125% scaling)
xfconf-query -c xsettings -p /Xft/DPI -s 120

# Fine-tune if 120 is slightly too big (optimal for 15.6" 1080p is ~123% / DPI 118)
xfconf-query -c xsettings -p /Xft/DPI -s 118
```

*Note: You may need to restart applications (like Firefox or Antigravity) for the changes to take full effect.*

## 13. Real-world Verification (2026-02-04)

This procedure was verified on a local machine with the following specifications:

- **Host Hardware**: Debian 13 (Trixie) / Kernel 6.12
- **Client Hardware**: iiyama STYLE-15FH112-N-UCFXB (15.6" Full HD / Intel N100)
- **Pre-existing Desktop**: GNOME (gnome-session)
- **Status**: GNOME and XRDP concurrent sessions for the same user are incompatible. Installing **Xfce4** as a secondary desktop for RDP connections is the confirmed stable solution.

### Verification Checklist

1. [x] Xfce4 installation does not interfere with the local GNOME session.
2. [x] tigerVNC is required for optimal keyboard mapping on Debian 13.
3. [x] `unset DBUS_SESSION_BUS_ADDRESS` is mandatory to avoid "Connection Logged In" cycles.
4. [x] Disabling compositing prevents sudden black screens on tab switching.
5. [x] `KillDisconnected=true` prevents reconnection stale-session locks.
6. [x] Pre-edit mode disabled (Fcitx5) resolves RDP input latency (Behavior/PreeditEnabledByDefault=False).
7. [x] Electron-specific flags (`--enable-wayland-ime`) resolve IDE-specific batch input issues.
8. [x] xfdesktop autostart loop prevents permanent black-screen failures after power save.
9. [x] Disabling Firefox hardware acceleration improves browser responsiveness.
10. [x] Adjusting Xfce DPI (118-120) solves readability issues on high-density 15.6" 1080p displays.
11. [x] **CopyQ Integration**: Successfully replaced basic clipman with CopyQ for better text/image sync.
12. [!] **LightDM UX Ambiguity**: While LightDM fixes port conflicts with `gnome-remote-desktop`, users may find the specific greeter/UX "hard to use" (とっても使いにくい) compared to the polished GDM. Reverting to GDM requires manual service masking of `gnome-remote-desktop`.
13. [x] **GDM Reversion Ritual**: Reverting to GDM requires ensuring `gdm3` is enabled, `lightdm` is disabled, and the default display manager path is updated.
14. [x] **tty1 / No-GUI Recovery**: If the system boots into a text console, check `display-manager.service` and `graphical.target` status via SSH.
15. [x] **Desktop Environment Personalization**: While KDE Plasma offers a "Windows-like" familiarity, users prioritize "Elegance" (洗練) found in GNOME for long-term productivity and aesthetic satisfaction.
16. [!] **GNOME RDP Constraint**: Using GNOME over RDP requires a mandatory "masking ritual" for `gnome-remote-desktop` to prevent port 3389 hijacking.

### 13.1 GDM Reversion & GUI Recovery Ritual

If the LightDM experiment is reverted, use this ritual to restore the Xfce/GDM environment:

```bash
# 1. Disable LightDM and enable GDM3
sudo systemctl disable lightdm
sudo systemctl enable gdm3

# 2. Update the default display manager registry
echo "/usr/sbin/gdm3" | sudo tee /etc/X11/default-display-manager

# 3. Ensure gnome-remote-desktop is masked (to prevent port 3389 conflict)
sudo systemctl mask gnome-remote-desktop.service
systemctl --user mask gnome-remote-desktop.service

# 4. Reboot or Isolate to graphical target
sudo systemctl isolate graphical.target
```

### 13.2 Troubleshooting tty1 (Text-only Login)

If the machine boots into a terminal (`tty1`), follow these steps:

1. **Verify Display Manager**: `systemctl status display-manager` (Should see GDM/LightDM).
2. **Check Default Path**: `cat /etc/X11/default-display-manager`.
3. **Switch VT**: Locally, press `Ctrl + Alt + F2` or `Ctrl + Alt + F7` to find the GUI session if it started on a different virtual terminal.

---

## 14. The Local-Remote Hybrid Strategy (Modern/Stable)

For users who want a "Modern & Elegant" experience locally but require "Ultra-stable & Low-latency" performance over RDP:

### 14.1 The Configuration

| Connection | Primary Desktop Environment | Result |
| :--- | :--- | :--- |
| **Local (Physical)** | **GNOME** or **KDE Plasma** | Aesthetic satisfaction, high visual fidelity. |
| **Remote (RDP)** | **Xfce** | Zero-latency, stability, optimized for bandwidth. |

### 14.2 Implementation Ritual

1. **Set SDDM or GDM** as the display manager for the local login.
2. **Configure ~/.xsession** to force Xfce for RDP:

   ```bash
   echo "xfce4-session" > ~/.xsession
   ```

3. **Session Awareness**: When logging in physically, use the **Session Selector** on the login screen to choose "GNOME" or "Plasma". xrdp will automatically read `~/.xsession` and launch Xfce, allowing different environments for different access modes.

---

## 15. The Modern Workstation (KDE Plasma Alternative)

For users who prioritize a "Modern" and "Elegant" UI with high "Multi-tasking Efficiency," **KDE Plasma** is a superior alternative to Xfce.

### 15.1 Why KDE Plasma?

- **Aesthetics**: Support for blurs, translucent panels (Breeze, Sweet), and modern iconography.
- **Efficiency**: Advanced window tiling (KWin), Activities (isolated workflows), and powerful file management (Dolphin).
- **RDP Stability**: Does not inherently conflict with port 3389 (unlike GNOME).

### 15.2 Installation

For a balanced "Modern but not Bloated" experience, use the `kde-plasma-desktop` package instead of the full `kde-standard`.

```bash
# 1. Update package list
sudo apt update

# 2. Install Plasma Desktop and SDDM
sudo apt install -y kde-plasma-desktop sddm

# 3. Select SDDM as default in the TUI dialog
# Use Arrow Keys to select 'sddm', Tab to <Ok>, and Enter to confirm.
```

### 15.3 Post-Install Safety Ritual

Before rebooting, ensure the services and configurations are correctly set to prevent a "tty1" boot failure.

```bash
# 1. Ensure SDDM is enabled and others are disabled
sudo systemctl disable lightdm gdm gdm3 2>/dev/null || true
sudo systemctl enable sddm

# 2. Force the default display manager path
echo "/usr/bin/sddm" | sudo tee /etc/X11/default-display-manager

# 3. Final Verification
cat /etc/X11/default-display-manager  # Should show /usr/bin/sddm
systemctl is-enabled sddm            # Should show 'enabled'

# 4. Reboot
sudo reboot
```

### 15.4 Remote Desktop (XRDP) Integration

KDE Plasma works excellently with XRDP. However, ensure that the session manager is correctly configured for the `makaron8426` user:

```bash
# Create or edit ~/.xsession
echo "startplasma-x11" > ~/.xsession

# Ensure correct perms
chmod 644 ~/.xsession
```

---

## 16. Display Manager (DM) Aesthetic Comparison

The choice of DM affects the first impression (Login Screen) and integration with the desktop environment.

| DM | Aesthetics | Customization | RDP Compatibility |
| :--- | :--- | :--- | :--- |
| **GDM** | ⭐⭐⭐ | Minimal | ⚠️ Conflicts with 3389 |
| **SDDM** | ⭐⭐⭐⭐ | High (Themes) | ✅ Excellent |
| **LightDM** | ⭐⭐⭐ | Moderate | ✅ Excellent (Stable) |

---

## 17. The "Elegant" Choice (GNOME Shell)

For users who find KDE Plasma too "Windows-like" and prioritize an "Elegant" (洗練された) interface reminiscent of modern macOS or iPadOS workflows.

### 17.1 Why GNOME?

- **Elegance**: Unified design language, high-quality typography, and smooth transitions.
- **Focus**: Minimal clutter and "Activities" overview for window management.
- **Nautilus**: Simple but polished file management.

### 17.2 Mandatory RDP Setup Ritual

GNOME's built-in RDP server (`gnome-remote-desktop`) conflicts with `xrdp`. You **MUST** mask it to use GNOME over `xrdp`.

```bash
# 1. Mask the system service
sudo systemctl mask gnome-remote-desktop.service

# 2. Mask the user service (CRITICAL)
systemctl --user mask gnome-remote-desktop.service
```

### 17.3 XRDP Session Configuration

```bash
# Set GNOME as the session for xrdp
echo "gnome-session" > ~/.xsession
```

### 17.4 Aesthetic Customization (Making it "Elegant")

To achieve the macOS/iPadOS level of elegance mentioned in the preference discussion, install and configure these extensions:

```bash
# Install Extension Manager and Tweaks
sudo apt install -y gnome-shell-extension-manager gnome-tweaks

# Recommended Extensions (via manager or apt)
sudo apt install -y \
  gnome-shell-extension-dashtodock \
  gnome-shell-extension-appindicator \
  gnome-shell-extension-caffeine
```

**Recommended Extensions (Available in "Extension Manager"):**

- **Dash to Dock**: Moves the activities bar to a persistent or intelligent-hide dock.
- **Blur my Shell**: Adds aesthetic blur effects to the top panel and overview.
- **Rounded Window Corners**: Rounds window edges for a more modern feel.
- **AppIndicator/KStatusNotifierItem**: Essential for seeing tray icons like CopyQ or Tailscale.

---

### Source

Extracted from session 2026-02-05 (RDP Failure Prevention & DM Transition) and follow-up discussion on desktop aesthetics.
