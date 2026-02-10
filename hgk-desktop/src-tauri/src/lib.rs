// Hegemonikón Desktop — Tauri Application
// Python API サーバーの自動起動/終了を管理

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

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let api_port: u16 = 9696;

    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet])
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
