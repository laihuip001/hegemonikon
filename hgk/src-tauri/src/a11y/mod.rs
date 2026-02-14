// AT-SPI2 + Bytebot VLM Desktop Accessibility Module
// A-path: AT-SPI2 structured tree (fast, free, GTK/Qt)
// B-path: Bytebot VLM screenshot (universal, API cost)

mod tree;
mod bytebot;
pub mod router;

// Re-export types for Tauri commands
pub use tree::{A11yWindow, A11yNode, list_accessible_windows, get_accessible_tree, perform_action, list_actions, set_text, ElementExtents, get_element_extents, focus_element, click_at_element, type_at_element};
pub use router::{DesktopElement, ActionResult, RoutePath};
