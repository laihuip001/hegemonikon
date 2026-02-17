# Syncthing 4-Node Mesh Configuration (Oikos Convergence)

This artifact documents the specific device IDs and functional roles within the current Hegemonikón mesh topology as of 2026-02-06.

## 1. Node Topology

| Device Name | Device ID | Functional Role |
| :--- | :--- | :--- |
| **Debian Host** | `AUPKMPX-MMJPX7A-QVW6EOC-UVRCIIV-APR4QPY-UE4NA7A-XELPJO4-NQD7RAF` | **Creative Core (Soul Hub)** |
| **Windows Laptop** | `SPNLWTT-WVQNH3E-MSL4BDX-KIFPJOY-CTL4F65-IHBP6U3-XQHJC7F-ILGLFAN` | **Execution/Implementation Surface** |
| **OPPO PAD 3** | `TMOAL3G-AFNXSG6-RYJ2BV7-KQ4TN6N-2UDABTL-MEMWB74-TKGN4ES-XHM2WQ6` | **Reference/Static Intelligence** |
| **Pixel 9a** | `CJR6XXV-NLLMGR7-B7CLZIR-QWJMUDN-J6P7ZDG-5IJPPAF-TYW7HZL-GZTXEQH` | **Mobile/Dynamic Intervention** |

## 2. Shared Folder: "Sync"

- **Folder Path (Debian)**: `~/Sync`
- **Folder ID**: `sync`
- **Sharing**: Active across all 4 nodes.

## 3. Configuration Protocol (Debian CLI)

To replicate this setup on the Debian core:

```bash
# Register Devices
syncthing cli config devices add --device-id "CJR6XXV-NLLMGR7-B7CLZIR-QWJMUDN-J6P7ZDG-5IJPPAF-TYW7HZL-GZTXEQH" --name "Pixel 9a"
syncthing cli config devices add --device-id "TMOAL3G-AFNXSG6-RYJ2BV7-KQ4TN6N-2UDABTL-MEMWB74-TKGN4ES-XHM2WQ6" --name "OPPO PAD 3"
syncthing cli config devices add --device-id "SPNLWTT-WVQNH3E-MSL4BDX-KIFPJOY-CTL4F65-IHBP6U3-XQHJC7F-ILGLFAN" --name "Windows Laptop"

# Create and Link Folder
syncthing cli config folders add --id "sync" --label "Sync" --path "/home/makaron8426/Sync"
syncthing cli config folders "sync" devices add --device-id "CJR6XXV-NLLMGR7-B7CLZIR-QWJMUDN-J6P7ZDG-5IJPPAF-TYW7HZL-GZTXEQH"
syncthing cli config folders "sync" devices add --device-id "TMOAL3G-AFNXSG6-RYJ2BV7-KQ4TN6N-2UDABTL-MEMWB74-TKGN4ES-XHM2WQ6"
syncthing cli config folders "sync" devices add --device-id "SPNLWTT-WVQNH3E-MSL4BDX-KIFPJOY-CTL4F65-IHBP6U3-XQHJC7F-ILGLFAN"
```

## 4. Status & Verification

### Check Online Connections

Use the following command to see which devices are currently connected to the Debian hub:

```bash
curl -s http://localhost:8384/rest/system/connections | python3 -c "import sys,json; d=json.load(sys.stdin)['connections']; print('=== 接続状況 ==='); [print(f'{k[:7]}...: 接続済み' if v.get('connected') else f'{k[:7]}...: 未接続') for k,v in d.items()]"
```

### Sync Verification Test

1. Create a file on Debian: `echo \"Hello\" > ~/Sync/test.txt`
2. Check for existence on other devices.
3. Confirm version numbers (e.g., v2.0.11 or v2.0.14) match across the mesh for best stability.

## 5. Troubleshooting & Findings

### Windows "Hidden Folder" Issue

If the `Sync` folder is created but not visible in Windows Explorer:

- Check for hidden items (View -> Hidden Items).
- Verify the path in Syncthing Web UI (Settings -> Edit Folder -> General).
- Ensure the user has permissions for the parent directory.

### Path Configuration Warning

When adding the folder on Windows, ensure the **Folder Path** points exactly to a dedicated subfolder (e.g., `C:\Users\makar\Hegemonikon` or `...\Sync`) rather than the entire user root (`C:\Users\makar`). This prevents the accidental synchronization of sensitive profile data (e.g., `AppData`, `Documents`) to all nodes in the mesh.

### Accidental Root Sync Recovery (The "Zombie Sync" Ritual)

If a node (e.g., Windows Laptop) accidentally syncs its entire profile root (`C:\Users\makar`) instead of a subfolder, the data will rapidly propagate to all other connected nodes (Pixel, OPPO). Simply deleting on Debian is insufficient as mobile nodes will treat the deletion as a "missing file" and re-upload the profile data (Zombie Sync).

**The Mesh-Wide Purge Ritual:**

1. **Isolate the Source**: Correct the path on the offending node (Windows) to a dedicated folder (e.g., `C:\Users\makar\Hegemonikón`).
2. **Activate Master Mode (Debian)**: Set the Debian folder to **Send Only** to prevent it from accepting re-uploads from mobile devices.

    **Refined CLI (v1.29+):**

    ```bash
    # Method A: Nested CLI
    syncthing cli config folders "sync" type set sendonly

    # Method B: REST API (Most Robust)
    curl -X PATCH http://localhost:8384/rest/config/folders/sync \
         -H "Content-Type: application/json" \
         -d '{"type":"sendonly"}'
    ```

3. **Manual Cleanup on Mobile**: Delete the unwanted profile folders (`AppData`, `Downloads`, etc.) on the Pixel and OPPO devices to clear their local cache.
4. **Debian Purge**: Delete the folders from the Debian `~/Sync` directory.
5. **Revert to Sync Mode**: Once the mesh is clean, set Debian back to **Send & Receive**:

    ```bash
    syncthing cli config folders "sync" type set sendreceive
    ```

```bash
# Debian side cleanup sequence
# Verified on Syncthing v1.29.5 (2026-02-07)
syncthing cli config folders "sync" type set sendonly

cd ~/Sync
# NOTE: Using sudo is often required because Windows-originated files (shortcuts, etc.) 
# may create permission issues on the Linux filesystem.
sudo rm -rf AppData Documents Downloads Favorites Links Music OneDrive "Saved Games" Searches Videos .ssh

# Revert to Send & Receive
syncthing cli config folders "sync" type set sendreceive
```

**Verification (2026-02-07)**:
The cleanup of `~/Sync/AppData` (548KB) was successfully completed using the above sequence. The folder state was verified to be `sendreceive` after the ritual.

### Manual Sharing Fallback

If the "New Folder" notification does not appear:

1. Open Web UI (<http://localhost:8384>).
2. Click **Add Folder**.
3. Use the matching **Folder ID** (`sync`).
4. Select the **Sharing** tab and check the Debian host.

### Connectivity Check

If devices are not showing as "Connected" (e.g., in a 4-node mesh):

- Ensure Tailscale is active on both nodes.
- Restart the Syncthing user service: `systemctl --user restart syncthing`.

---

## 6. Verification Patterns

### Standard README Test

Creating a `README.md` with the following structure helps verify that all nodes can read the current topology:

```markdown
# 🔄 Hegemonikón Sync Folder
| Device | Role | Status (2026-02-06) |
|:---|:---|:---|
| Debian | Hub | 🟢 Active |
| Windows | Execution | 🔴 Offline/Disconnected |
| Pixel 9a | Mobile | 🔴 Offline/Disconnected |
| OPPO PAD 3| Reference | 🔴 Offline/Disconnected |
```

## 7. 2026-02-06 Verification Log

- **Active Mesh**: All 4 nodes registered successfully.
- **Hub Status**: Debian host (AUPKMPX) confirmed as the "Soul Hub".
- **Connectivity**: Observed use of Relays due to NAT-PMP refusal at the router (192.168.1.1).
- **Cleanup**: Identified `~/Sync/AppData` (548KB) as residual "Zombie Sync" data to be purged.

## 8. 2026-02-07 Verification Log

- **Cleanup Success**: The "Purge Ritual" was executed. `~/Sync/AppData` and other Windows-specific residues were successfully removed from the Debian hub.
- **CLI Confirmation**: Confirmed that `syncthing cli config folders sync type set [sendonly|sendreceive]` is the correct syntax for Syncthing v1.29.5 on Debian.
- **Mesh Integrity**: The folder state was returned to `sendreceive` successfully, and the mesh is ready for the "Content Strategy" design phase.

---

Last Synchronized/Verified: 2026-02-07 (Zombie Sync Cleared & v1.29.5 CLI Verified)
