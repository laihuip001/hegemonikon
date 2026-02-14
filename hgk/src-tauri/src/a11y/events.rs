// AT-SPI2 event monitoring — reactive desktop awareness
// Provides snapshot-based change detection (polling approach)
// Full event streaming can be added once atspi-0.29 API is stabilized

use super::tree;
use serde::Serialize;

/// Desktop state change detected by polling
#[derive(Debug, Clone, Serialize)]
#[serde(tag = "type")]
pub enum DesktopChange {
    /// New window appeared
    WindowAppeared { app_name: String, bus_name: String },
    /// Window disappeared
    WindowDisappeared { app_name: String, bus_name: String },
    /// No changes detected
    NoChange,
}

/// Compare current window list against a previous snapshot
/// Returns a list of changes (new windows, disappeared windows)
pub async fn detect_changes(
    previous: &[tree::A11yWindow],
) -> Result<Vec<DesktopChange>, String> {
    let current = tree::list_accessible_windows().await?;
    let mut changes = Vec::new();

    // Find new windows
    for w in &current {
        if !previous.iter().any(|p| p.bus_name == w.bus_name) {
            changes.push(DesktopChange::WindowAppeared {
                app_name: w.app_name.clone(),
                bus_name: w.bus_name.clone(),
            });
        }
    }

    // Find disappeared windows
    for p in previous {
        if !current.iter().any(|w| w.bus_name == p.bus_name) {
            changes.push(DesktopChange::WindowDisappeared {
                app_name: p.app_name.clone(),
                bus_name: p.bus_name.clone(),
            });
        }
    }

    if changes.is_empty() {
        changes.push(DesktopChange::NoChange);
    }

    Ok(changes)
}

/// Take a snapshot of current windows for future comparison
pub async fn take_snapshot() -> Result<Vec<tree::A11yWindow>, String> {
    tree::list_accessible_windows().await
}
