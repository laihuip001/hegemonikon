// AT-SPI2 event listener — reactive desktop awareness
// Subscribes to window focus, creation, and destruction events

use atspi::events::object::{FocusEvent, StateChangedEvent};
use atspi::events::EventInterfaces;
use atspi::AccessibilityConnection;
use futures::StreamExt;
use serde::Serialize;
use std::sync::Arc;
use tokio::sync::broadcast;

/// Desktop event types
#[derive(Debug, Clone, Serialize)]
#[serde(tag = "type")]
pub enum DesktopEvent {
    /// A window gained focus
    FocusChanged {
        app_name: String,
        bus_name: String,
        path: String,
    },
    /// A window state changed (shown/hidden)
    StateChanged {
        app_name: String,
        bus_name: String,
        path: String,
        state: String,
        enabled: bool,
    },
}

/// Event listener handle — drop to stop listening
pub struct EventListenerHandle {
    pub receiver: broadcast::Receiver<DesktopEvent>,
    _cancel: tokio::sync::oneshot::Sender<()>,
}

/// Start listening for AT-SPI desktop events
/// Returns a handle with a broadcast receiver for events
pub async fn start_event_listener() -> Result<EventListenerHandle, String> {
    let a11y = AccessibilityConnection::new()
        .await
        .map_err(|e| format!("AT-SPI2 connection failed: {}", e))?;
    let a11y = Arc::new(a11y);

    // Subscribe to focus and state-changed events
    a11y.register_event::<FocusEvent>()
        .await
        .map_err(|e| format!("Failed to register FocusEvent: {}", e))?;
    a11y.register_event::<StateChangedEvent>()
        .await
        .map_err(|e| format!("Failed to register StateChangedEvent: {}", e))?;

    let (tx, rx) = broadcast::channel::<DesktopEvent>(64);
    let (cancel_tx, mut cancel_rx) = tokio::sync::oneshot::channel::<()>();

    let a11y_clone = a11y.clone();
    tokio::spawn(async move {
        let mut stream = a11y_clone.event_stream();

        loop {
            tokio::select! {
                _ = &mut cancel_rx => break,
                event = stream.next() => {
                    match event {
                        Some(Ok(ev)) => {
                            let desktop_event = match &ev {
                                EventInterfaces::Object(
                                    atspi::events::object::ObjectEvents::Focus(f)
                                ) => {
                                    Some(DesktopEvent::FocusChanged {
                                        app_name: String::new(),
                                        bus_name: f.inner.sender.to_string(),
                                        path: f.inner.path.to_string(),
                                    })
                                }
                                EventInterfaces::Object(
                                    atspi::events::object::ObjectEvents::StateChanged(s)
                                ) => {
                                    Some(DesktopEvent::StateChanged {
                                        app_name: String::new(),
                                        bus_name: s.inner.sender.to_string(),
                                        path: s.inner.path.to_string(),
                                        state: s.state.to_string(),
                                        enabled: s.enabled != 0,
                                    })
                                }
                                _ => None,
                            };

                            if let Some(de) = desktop_event {
                                let _ = tx.send(de);
                            }
                        }
                        Some(Err(_)) => continue,
                        None => break,
                    }
                }
            }
        }
    });

    Ok(EventListenerHandle {
        receiver: rx,
        _cancel: cancel_tx,
    })
}
