// AT-SPI2 Tree Walker — using atspi crate's high-level AccessibleProxy API
// Queries the accessibility tree via D-Bus to enumerate windows and UI elements
// Uses AccessibilityConnection to connect to the AT-SPI2 dedicated bus

use atspi::proxy::accessible::{AccessibleProxy, ObjectRefExt};
use atspi::AccessibilityConnection;
use serde::Serialize;
use zbus::Connection;

use super::error::{A11yError, A11yResult};

/// A desktop window discovered via AT-SPI2
#[derive(Debug, Clone, Serialize)]
pub struct A11yWindow {
    /// Application name
    pub app_name: String,
    /// D-Bus bus name (e.g. ":1.42")
    pub bus_name: String,
    /// D-Bus object path
    pub path: String,
    /// Role name
    pub role: String,
    /// Number of child elements (top-level)
    pub child_count: i32,
}

/// A UI element in the accessibility tree
#[derive(Debug, Clone, Serialize)]
pub struct A11yNode {
    /// Role name (e.g. "push button", "text", "frame")
    pub role: String,
    /// Name / label
    pub name: String,
    /// D-Bus bus name
    pub bus_name: String,
    /// D-Bus object path for this element
    pub path: String,
    /// Child nodes
    pub children: Vec<A11yNode>,
}

/// List all accessible windows on the desktop via AT-SPI2 Registry
pub async fn list_accessible_windows() -> A11yResult<Vec<A11yWindow>> {
    let a11y_conn = AccessibilityConnection::new().await?;
    let conn = a11y_conn.connection();

    // The AT-SPI2 Registry root object lists all accessible applications
    let registry = AccessibleProxy::builder(&conn)
        .destination("org.a11y.atspi.Registry")?
        .path("/org/a11y/atspi/accessible/root")?
        .cache_properties(zbus::proxy::CacheProperties::No)
        .build()
        .await?;

    // Get all children (= all accessible applications)
    let children = registry.get_children().await?;

    let mut windows = Vec::new();

    for child_ref in children {
        // Convert ObjectRefOwned to AccessibleProxy
        let child_proxy = match child_ref.as_accessible_proxy(&conn).await {
            Ok(p) => p,
            Err(_) => continue,
        };

        let app_name = child_proxy.name().await.unwrap_or_default();
        let role = child_proxy
            .get_role()
            .await
            .map(|r| r.name().to_string())
            .unwrap_or_else(|_| "unknown".to_string());
        let child_count = child_proxy.child_count().await.unwrap_or(0);

        // Extract bus name and path from the proxy
        let bus_name = child_proxy
            .inner()
            .destination()
            .to_string();
        let path = child_proxy
            .inner()
            .path()
            .to_string();

        windows.push(A11yWindow {
            app_name,
            bus_name,
            path,
            role,
            child_count,
        });
    }

    Ok(windows)
}

/// Get the accessibility tree for a specific application
/// Uses cache if available (TTL-based, see cache.rs)
pub async fn get_accessible_tree(
    bus_name: &str,
    path: &str,
    max_depth: u32,
) -> A11yResult<Vec<A11yNode>> {
    // Check cache first
    if let Some(cached) = super::cache::get(bus_name, path, max_depth) {
        return Ok(cached);
    }

    let a11y_conn = AccessibilityConnection::new().await?;
    let conn = a11y_conn.connection();

    let proxy = AccessibleProxy::builder(&conn)
        .destination(bus_name.to_string())?
        .path(path.to_string())?
        .cache_properties(zbus::proxy::CacheProperties::No)
        .build()
        .await?;

    let name = proxy.name().await.unwrap_or_default();
    let role = proxy
        .get_role()
        .await
        .map(|r| r.name().to_string())
        .unwrap_or_else(|_| "unknown".to_string());

    let children = if max_depth > 0 {
        walk_children(&conn, &proxy, max_depth - 1).await
    } else {
        Vec::new()
    };

    let result = vec![A11yNode {
        role,
        name,
        bus_name: bus_name.to_string(),
        path: path.to_string(),
        children,
    }];

    // Store in cache
    super::cache::put(bus_name, path, max_depth, result.clone());

    Ok(result)
}

/// Recursively walk child nodes
fn walk_children<'a>(
    conn: &'a Connection,
    parent: &'a AccessibleProxy<'_>,
    remaining_depth: u32,
) -> std::pin::Pin<Box<dyn std::future::Future<Output = Vec<A11yNode>> + Send + 'a>> {
    Box::pin(async move {
        let children_refs = match parent.get_children().await {
            Ok(c) => c,
            Err(_) => return Vec::new(),
        };

        let mut nodes = Vec::new();

        for child_ref in children_refs {
            let child_proxy = match child_ref.as_accessible_proxy(conn).await {
                Ok(p) => p,
                Err(_) => continue,
            };

            let name = child_proxy.name().await.unwrap_or_default();
            let role = child_proxy
                .get_role()
                .await
                .map(|r| r.name().to_string())
                .unwrap_or_else(|_| "unknown".to_string());

            let bus_name = child_proxy.inner().destination().to_string();
            let path = child_proxy.inner().path().to_string();

            let grandchildren = if remaining_depth > 0 {
                walk_children(conn, &child_proxy, remaining_depth - 1).await
            } else {
                Vec::new()
            };

            nodes.push(A11yNode {
                role,
                name,
                bus_name,
                path,
                children: grandchildren,
            });
        }

        nodes
    })
}

/// Perform the default action on an AT-SPI element (e.g. click a button)
/// Returns: (success, action_name)
pub async fn perform_action(
    bus_name: &str,
    path: &str,
    action_index: i32,
) -> A11yResult<(bool, String)> {
    let a11y_conn = AccessibilityConnection::new().await?;
    let conn = a11y_conn.connection();

    use atspi::proxy::action::ActionProxy;

    let action_proxy = ActionProxy::builder(&conn)
        .destination(bus_name.to_string())?
        .path(path.to_string())?
        .cache_properties(zbus::proxy::CacheProperties::No)
        .build()
        .await?;

    // Get the action name for reporting
    let action_name = action_proxy
        .get_name(action_index)
        .await
        .unwrap_or_else(|_| format!("action_{}", action_index));

    let result = action_proxy.do_action(action_index).await?;

    Ok((result, action_name))
}

/// List available actions on an AT-SPI element
pub async fn list_actions(
    bus_name: &str,
    path: &str,
) -> A11yResult<Vec<String>> {
    let a11y_conn = AccessibilityConnection::new().await?;
    let conn = a11y_conn.connection();

    use atspi::proxy::action::ActionProxy;

    let action_proxy = ActionProxy::builder(&conn)
        .destination(bus_name.to_string())?
        .path(path.to_string())?
        .cache_properties(zbus::proxy::CacheProperties::No)
        .build()
        .await?;

    let n = action_proxy.nactions().await?;

    let mut names = Vec::new();
    for i in 0..n {
        if let Ok(name) = action_proxy.get_name(i).await {
            names.push(name);
        }
    }

    Ok(names)
}

/// Set text content on an AT-SPI editable text element
pub async fn set_text(
    bus_name: &str,
    path: &str,
    text: &str,
) -> A11yResult<bool> {
    let a11y_conn = AccessibilityConnection::new().await?;
    let conn = a11y_conn.connection();

    use atspi::proxy::editable_text::EditableTextProxy;

    let text_proxy = EditableTextProxy::builder(&conn)
        .destination(bus_name.to_string())?
        .path(path.to_string())?
        .cache_properties(zbus::proxy::CacheProperties::No)
        .build()
        .await?;

    text_proxy.set_text_contents(text).await?;
    Ok(true)
}

/// Element position and size on screen (from AT-SPI Component interface)
#[derive(Debug, Clone, Serialize)]
pub struct ElementExtents {
    pub x: i32,
    pub y: i32,
    pub width: i32,
    pub height: i32,
}

/// Get the screen position and size of an AT-SPI element
pub async fn get_element_extents(
    bus_name: &str,
    path: &str,
) -> A11yResult<ElementExtents> {
    let a11y_conn = AccessibilityConnection::new().await?;
    let conn = a11y_conn.connection();

    use atspi::proxy::component::ComponentProxy;
    use atspi::CoordType;

    let comp_proxy = ComponentProxy::builder(&conn)
        .destination(bus_name.to_string())?
        .path(path.to_string())?
        .cache_properties(zbus::proxy::CacheProperties::No)
        .build()
        .await?;

    let (x, y, w, h) = comp_proxy.get_extents(CoordType::Screen).await?;

    Ok(ElementExtents { x, y, width: w, height: h })
}

/// Focus an AT-SPI element (bring it to front / keyboard focus)
pub async fn focus_element(
    bus_name: &str,
    path: &str,
) -> A11yResult<bool> {
    let a11y_conn = AccessibilityConnection::new().await?;
    let conn = a11y_conn.connection();

    use atspi::proxy::component::ComponentProxy;

    let comp_proxy = ComponentProxy::builder(&conn)
        .destination(bus_name.to_string())?
        .path(path.to_string())?
        .cache_properties(zbus::proxy::CacheProperties::No)
        .build()
        .await?;

    Ok(comp_proxy.grab_focus().await?)
}

/// Click at the center of an AT-SPI element using xdotool
/// This is the A-path click: get_extents → center → xdotool click
pub async fn click_at_element(
    bus_name: &str,
    path: &str,
) -> A11yResult<(bool, i32, i32)> {
    let ext = get_element_extents(bus_name, path).await?;

    if ext.width == 0 && ext.height == 0 {
        return Err(A11yError::ActionFailed("Element has zero size (not visible)".to_string()));
    }

    let center_x = ext.x + ext.width / 2;
    let center_y = ext.y + ext.height / 2;

    // Focus first, then click
    let _ = focus_element(bus_name, path).await;

    let output = std::process::Command::new("xdotool")
        .args(["mousemove", "--sync",
               &center_x.to_string(), &center_y.to_string(),
               "click", "1"])
        .output()
        .map_err(|e| A11yError::XdotoolFailed(e.to_string()))?;

    Ok((output.status.success(), center_x, center_y))
}

/// Type text at the focused element using xdotool
/// Combines focus_element + xdotool type
pub async fn type_at_element(
    bus_name: &str,
    path: &str,
    text: &str,
) -> A11yResult<bool> {
    // Try EditableText first (pure AT-SPI)
    if let Ok(success) = set_text(bus_name, path, text).await {
        if success {
            return Ok(true);
        }
    }

    // Fallback: focus + xdotool type
    let _ = focus_element(bus_name, path).await;

    let output = std::process::Command::new("xdotool")
        .args(["type", "--clearmodifiers", text])
        .output()
        .map_err(|e| A11yError::XdotoolFailed(e.to_string()))?;

    Ok(output.status.success())
}
