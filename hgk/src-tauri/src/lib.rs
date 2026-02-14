// Hegemonikón Desktop — Tauri Application
// Python API サーバーの自動起動/終了を管理

#[cfg(target_os = "linux")]
pub mod a11y;

use std::net::TcpStream;
use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::Manager;
use std::time::{Duration, Instant};

/// Python API サーバーの子プロセスを保持
struct ApiProcess(Mutex<Option<Child>>);

/// ポートが開いているか確認
fn is_port_open(port: u16) -> bool {
    TcpStream::connect(format!("127.0.0.1:{}", port)).is_ok()
}

/// API サーバーが起動するまで待機 (health check)
fn wait_for_api(port: u16, timeout_ms: u64) -> bool {
    let start = Instant::now();
    let timeout = Duration::from_millis(timeout_ms);
    let interval = Duration::from_millis(500);

    while start.elapsed() < timeout {
        if is_port_open(port) {
            return true;
        }
        std::thread::sleep(interval);
    }
    false
}

/// HGK プロジェクトルートを解決
fn resolve_hgk_root() -> String {
    // 1. 環境変数 HGK_ROOT が設定されていればそれを使う
    if let Ok(root) = std::env::var("HGK_ROOT") {
        return root;
    }
    // 2. デフォルト: $HOME/oikos/hegemonikon
    if let Some(home) = dirs::home_dir() {
        return home.join("oikos/hegemonikon").to_string_lossy().to_string();
    }
    // 3. フォールバック
    String::from("/home/makaron8426/oikos/hegemonikon")
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

/// AT-SPI2: List all accessible windows on the desktop
#[cfg(target_os = "linux")]
#[tauri::command]
async fn list_windows() -> Result<Vec<a11y::A11yWindow>, String> {
    a11y::list_accessible_windows().await
}

/// AT-SPI2: Get the accessibility tree for a specific application
#[cfg(target_os = "linux")]
#[tauri::command]
async fn get_element_tree(
    bus_name: String,
    path: String,
    max_depth: Option<u32>,
) -> Result<Vec<a11y::A11yNode>, String> {
    a11y::get_accessible_tree(&bus_name, &path, max_depth.unwrap_or(3)).await
}

/// Unified: List all desktop elements (A/B routed)
#[cfg(target_os = "linux")]
#[tauri::command]
async fn list_desktop() -> Result<Vec<a11y::DesktopElement>, String> {
    a11y::router::list_desktop_elements().await
}

/// Unified: Take a desktop screenshot (B-path)
#[cfg(target_os = "linux")]
#[tauri::command]
async fn desktop_screenshot() -> Result<a11y::ActionResult, String> {
    a11y::router::screenshot_desktop().await
}

/// Unified: Click on a desktop element (A/B routed)
#[cfg(target_os = "linux")]
#[tauri::command]
async fn desktop_click(
    bus_name: Option<String>,
    object_path: Option<String>,
    x: Option<i32>,
    y: Option<i32>,
) -> Result<a11y::ActionResult, String> {
    a11y::router::click_element(bus_name, object_path, x, y).await
}

/// Unified: Type text into a desktop element (A/B routed)
#[cfg(target_os = "linux")]
#[tauri::command]
async fn desktop_type(
    bus_name: Option<String>,
    object_path: Option<String>,
    text: String,
) -> Result<a11y::ActionResult, String> {
    a11y::router::type_into_element(bus_name, object_path, &text).await
}

/// AT-SPI: Perform an action on an element (A-path only)
#[cfg(target_os = "linux")]
#[tauri::command]
async fn desktop_do_action(
    bus_name: String,
    object_path: String,
    action_index: Option<i32>,
) -> Result<a11y::ActionResult, String> {
    let (success, action_name) = a11y::perform_action(&bus_name, &object_path, action_index.unwrap_or(0)).await?;
    Ok(a11y::ActionResult {
        success,
        route: a11y::RoutePath::Atspi,
        message: format!("Action '{}' performed", action_name),
        screenshot: None,
    })
}

/// AT-SPI: List available actions for an element (A-path only)
#[cfg(target_os = "linux")]
#[tauri::command]
async fn desktop_list_actions(
    bus_name: String,
    object_path: String,
) -> Result<Vec<String>, String> {
    a11y::list_actions(&bus_name, &object_path).await
}

/// AT-SPI: Set text on an editable element (A-path only)
#[cfg(target_os = "linux")]
#[tauri::command]
async fn desktop_set_text(
    bus_name: String,
    object_path: String,
    text: String,
) -> Result<a11y::ActionResult, String> {
    let success = a11y::set_text(&bus_name, &object_path, &text).await?;
    Ok(a11y::ActionResult {
        success,
        route: a11y::RoutePath::Atspi,
        message: format!("Text set to '{}'", text),
        screenshot: None,
    })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // GBM/DMA-BUF フォールバック: NVIDIA 環境や RDP セッションで
    // WebKitGTK の GPU バッファ作成が失敗し白画面になる問題を回避。
    // 常に設定する (GBM が使える環境では無視されるため害なし)
    if std::env::var("WEBKIT_DISABLE_DMABUF_RENDERER").is_err() {
        println!("[HGK] Setting WEBKIT_DISABLE_DMABUF_RENDERER=1 (GBM fallback)");
        std::env::set_var("WEBKIT_DISABLE_DMABUF_RENDERER", "1");
    }

    let api_port: u16 = 9696;

    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            #[cfg(target_os = "linux")]
            list_windows,
            #[cfg(target_os = "linux")]
            get_element_tree,
            #[cfg(target_os = "linux")]
            list_desktop,
            #[cfg(target_os = "linux")]
            desktop_screenshot,
            #[cfg(target_os = "linux")]
            desktop_click,
            #[cfg(target_os = "linux")]
            desktop_type,
            #[cfg(target_os = "linux")]
            desktop_do_action,
            #[cfg(target_os = "linux")]
            desktop_list_actions,
            #[cfg(target_os = "linux")]
            desktop_set_text,
        ])
        .setup(move |app| {
            // dev モードならスキップ (既に手動でサーバーが起動している想定)
            if std::env::var("TAURI_ENV").unwrap_or_default() == "dev" {
                println!("[HGK] Dev mode: skipping API server spawn");
                return Ok(());
            }

            // ポートが既に使用中ならスキップ (2重起動防止)
            if is_port_open(api_port) {
                println!("[HGK] Port {} already in use, skipping spawn", api_port);
                app.manage(ApiProcess(Mutex::new(None)));
                return Ok(());
            }

            // Python venv パスを解決
            let hgk_root = resolve_hgk_root();
            let python_path = format!("{}/.venv/bin/python", &hgk_root);

            println!("[HGK] Starting API server...");
            println!("[HGK]   Python: {}", &python_path);
            println!("[HGK]   Root:   {}", &hgk_root);
            println!("[HGK]   Port:   {}", api_port);

            // Python API サーバーを spawn
            match Command::new(&python_path)
                .args(["-m", "mekhane.api.server", "--port", &api_port.to_string()])
                .env("PYTHONPATH", &hgk_root)
                .current_dir(&hgk_root)
                .stdout(std::process::Stdio::null())
                .stderr(std::process::Stdio::piped())
                .spawn()
            {
                Ok(child) => {
                    println!("[HGK] API server spawned (PID: {})", child.id());
                    app.manage(ApiProcess(Mutex::new(Some(child))));

                    // ヘルスチェック待機 (最大 10 秒)
                    if wait_for_api(api_port, 10_000) {
                        println!("[HGK] API server ready on port {}", api_port);
                    } else {
                        eprintln!("[HGK] ⚠ API server did not respond within 10s");
                    }
                }
                Err(e) => {
                    eprintln!("[HGK] ✗ Failed to spawn API server: {}", e);
                    eprintln!("[HGK]   Ensure Python venv exists at: {}", &python_path);
                    app.manage(ApiProcess(Mutex::new(None)));
                }
            }

            Ok(())
        })
        .on_window_event(|_window, event| {
            // ウィンドウ破棄時に Python プロセスを終了
            if let tauri::WindowEvent::Destroyed = event {
                // Note: on_window_event doesn't give us app handle directly,
                // cleanup is handled by Drop trait on app exit
            }
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app, event| {
            // アプリ終了時に Python プロセスを kill + wait
            if let tauri::RunEvent::Exit = event {
                if let Some(api) = app.try_state::<ApiProcess>() {
                    if let Ok(mut guard) = api.0.lock() {
                        if let Some(ref mut child) = *guard {
                            let pid = child.id();
                            println!("[HGK] Shutting down API server (PID: {})...", pid);
                            let _ = child.kill();
                            let _ = child.wait(); // ゾンビプロセス防止
                            println!("[HGK] API server stopped.");
                        }
                    }
                }
            }
        });
}
