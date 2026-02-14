// Desktop Action Router — A/B path routing engine
// A-path: AT-SPI2 (fast, structured, free) for GTK/Qt apps
// B-path: Bytebot VLM (slower, visual, API cost) for unsupported apps

use super::bytebot::BytebotClient;
use super::tree;
use serde::{Deserialize, Serialize};

/// Which path was used for the action
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RoutePath {
    /// AT-SPI2 structured accessibility tree
    Atspi,
    /// Bytebot VLM screenshot-based
    Vlm,
    /// No backend available
    Unavailable,
}

/// Unified desktop element info (returned by both paths)
#[derive(Debug, Clone, Serialize)]
pub struct DesktopElement {
    /// Application name
    pub app_name: String,
    /// Element role (button, text, etc.)
    pub role: String,
    /// Element name/label
    pub name: String,
    /// Which path discovered this element
    pub route: RoutePath,
    /// AT-SPI bus name (A-path only)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bus_name: Option<String>,
    /// AT-SPI object path (A-path only)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub object_path: Option<String>,
    /// Child count
    pub child_count: i32,
}

/// Result of a desktop action
#[derive(Debug, Clone, Serialize)]
pub struct ActionResult {
    /// Whether the action succeeded
    pub success: bool,
    /// Which path was used
    pub route: RoutePath,
    /// Human-readable message
    pub message: String,
    /// Screenshot base64 (VLM path only)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub screenshot: Option<String>,
}

/// Route: list all accessible desktop windows
/// Returns unified elements from AT-SPI (A-path) with VLM availability flag
pub async fn list_desktop_elements() -> Result<Vec<DesktopElement>, String> {
    // Try A-path first (AT-SPI2)
    let atspi_result = tree::list_accessible_windows().await;

    match atspi_result {
        Ok(windows) => {
            let elements: Vec<DesktopElement> = windows
                .into_iter()
                .map(|w| DesktopElement {
                    app_name: w.app_name,
                    role: w.role,
                    name: String::new(),
                    route: RoutePath::Atspi,
                    bus_name: Some(w.bus_name),
                    object_path: Some(w.path),
                    child_count: w.child_count,
                })
                .collect();
            Ok(elements)
        }
        Err(atspi_err) => {
            // A-path failed entirely — check if B-path is available
            let bytebot = BytebotClient::new();
            if bytebot.is_available().await {
                Ok(vec![DesktopElement {
                    app_name: "Desktop (VLM)".to_string(),
                    role: "desktop-frame".to_string(),
                    name: "Bytebot VLM fallback".to_string(),
                    route: RoutePath::Vlm,
                    bus_name: None,
                    object_path: None,
                    child_count: 0,
                }])
            } else {
                Err(format!(
                    "Both paths unavailable. AT-SPI: {}. Bytebot: not running.",
                    atspi_err
                ))
            }
        }
    }
}

/// Route: take a screenshot of the desktop
/// Always uses B-path (Bytebot) since AT-SPI doesn't provide visual capture
pub async fn screenshot_desktop() -> Result<ActionResult, String> {
    let bytebot = BytebotClient::new();

    if !bytebot.is_available().await {
        return Err("Bytebot is not running. Start with: docker-compose -f docker/docker-compose.yml up -d".to_string());
    }

    let result = bytebot.screenshot().await?;
    Ok(ActionResult {
        success: result.success,
        route: RoutePath::Vlm,
        message: "Screenshot captured via Bytebot".to_string(),
        screenshot: result.screenshot,
    })
}

/// Route: click on a specific element or coordinate
/// Tries A-path (AT-SPI action) first, falls back to B-path (coordinate click)
pub async fn click_element(
    bus_name: Option<String>,
    object_path: Option<String>,
    x: Option<i32>,
    y: Option<i32>,
) -> Result<ActionResult, String> {
    // A-path: AT-SPI DoAction interface
    if let (Some(bus), Some(path)) = (&bus_name, &object_path) {
        match tree::perform_action(bus, path, 0).await {
            Ok((success, action_name)) => {
                return Ok(ActionResult {
                    success,
                    route: RoutePath::Atspi,
                    message: format!("AT-SPI action '{}' performed (success={})", action_name, success),
                    screenshot: None,
                });
            }
            Err(_) => {
                // A-path failed, fall through to B-path
            }
        }
    }

    // B-path: coordinate-based click via Bytebot
    if let (Some(x), Some(y)) = (x, y) {
        let bytebot = BytebotClient::new();
        if bytebot.is_available().await {
            let result = bytebot.click(x, y).await?;
            return Ok(ActionResult {
                success: result.success,
                route: RoutePath::Vlm,
                message: format!("Clicked at ({}, {}) via Bytebot", x, y),
                screenshot: None,
            });
        }
    }

    Err("No click target: provide AT-SPI path or (x, y) coordinates".to_string())
}

/// Route: type text into an element
pub async fn type_into_element(
    bus_name: Option<String>,
    object_path: Option<String>,
    text: &str,
) -> Result<ActionResult, String> {
    // A-path: AT-SPI EditableText interface
    if let (Some(bus), Some(path)) = (&bus_name, &object_path) {
        match tree::set_text(bus, path, text).await {
            Ok(success) => {
                return Ok(ActionResult {
                    success,
                    route: RoutePath::Atspi,
                    message: format!("AT-SPI set text '{}' (success={})", text, success),
                    screenshot: None,
                });
            }
            Err(_) => {
                // A-path failed, fall through to B-path
            }
        }
    }

    // B-path: type via Bytebot
    let bytebot = BytebotClient::new();
    if bytebot.is_available().await {
        let result = bytebot.type_text(text).await?;
        return Ok(ActionResult {
            success: result.success,
            route: RoutePath::Vlm,
            message: format!("Typed '{}' via Bytebot", text),
            screenshot: None,
        });
    }

    Err("Cannot type: Bytebot is not running".to_string())
}
