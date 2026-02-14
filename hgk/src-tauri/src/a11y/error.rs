// AT-SPI2 Error Types
//
// Unified error type for all accessibility operations.
// Converts from zbus, atspi, and IO errors automatically.

use thiserror::Error;

#[derive(Debug, Error)]
pub enum A11yError {
    #[error("AT-SPI2 connection failed: {0}")]
    Connection(String),

    #[error("Element not found: {bus}:{path}")]
    ElementNotFound { bus: String, path: String },

    #[error("Action failed: {0}")]
    ActionFailed(String),

    #[error("xdotool execution failed: {0}")]
    XdotoolFailed(String),

    #[error("Bytebot API error: {0}")]
    BytebotError(String),

    #[error("D-Bus error: {0}")]
    DBus(#[from] zbus::Error),

    #[error("AT-SPI error: {0}")]
    Atspi(#[from] atspi::AtspiError),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}

// Tauri commands need String errors — provide easy conversion
impl From<A11yError> for String {
    fn from(e: A11yError) -> String {
        e.to_string()
    }
}

pub type A11yResult<T> = Result<T, A11yError>;
