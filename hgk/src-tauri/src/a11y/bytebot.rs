// Bytebot REST API client (B-path: VLM fallback)
// Connects to the local Bytebot Docker container for screenshot-based desktop control

use serde::{Deserialize, Serialize};

/// Bytebot server configuration
const DEFAULT_BYTEBOT_URL: &str = "http://localhost:9990";

/// Action types supported by the Bytebot /computer-use endpoint
#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum BytebotAction {
    Screenshot,
    Click,
    Type,
    ScrollUp,
    ScrollDown,
}

/// Request body for the Bytebot /computer-use endpoint
#[derive(Debug, Clone, Serialize)]
pub struct ComputerUseRequest {
    pub action: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub coordinate: Option<[i32; 2]>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text: Option<String>,
}

/// Response from the Bytebot /computer-use endpoint
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ComputerUseResponse {
    /// Base64-encoded screenshot (for screenshot action)
    #[serde(default)]
    pub screenshot: Option<String>,
    /// Action result message
    #[serde(default)]
    pub message: Option<String>,
    /// Whether the action was successful
    #[serde(default = "default_true")]
    pub success: bool,
}

fn default_true() -> bool {
    true
}

/// Bytebot client for VLM-based desktop control
pub struct BytebotClient {
    base_url: String,
}

impl BytebotClient {
    /// Create a new Bytebot client with default URL
    pub fn new() -> Self {
        Self {
            base_url: std::env::var("BYTEBOT_URL")
                .unwrap_or_else(|_| DEFAULT_BYTEBOT_URL.to_string()),
        }
    }

    /// Check if Bytebot is available
    pub async fn is_available(&self) -> bool {
        let url = format!("{}/health", self.base_url);
        let client = reqwest::Client::new();
        client.get(&url).send().await.is_ok()
    }

    /// Take a screenshot via Bytebot
    pub async fn screenshot(&self) -> Result<ComputerUseResponse, String> {
        self.send_action(ComputerUseRequest {
            action: "screenshot".to_string(),
            coordinate: None,
            text: None,
        })
        .await
    }

    /// Click at a specific coordinate
    pub async fn click(&self, x: i32, y: i32) -> Result<ComputerUseResponse, String> {
        self.send_action(ComputerUseRequest {
            action: "click".to_string(),
            coordinate: Some([x, y]),
            text: None,
        })
        .await
    }

    /// Type text
    pub async fn type_text(&self, text: &str) -> Result<ComputerUseResponse, String> {
        self.send_action(ComputerUseRequest {
            action: "type".to_string(),
            coordinate: None,
            text: Some(text.to_string()),
        })
        .await
    }

    /// Send an action to the Bytebot /computer-use endpoint
    async fn send_action(&self, request: ComputerUseRequest) -> Result<ComputerUseResponse, String> {
        let url = format!("{}/computer-use", self.base_url);
        let client = reqwest::Client::new();

        let response = client
            .post(&url)
            .json(&request)
            .send()
            .await
            .map_err(|e| format!("Bytebot request failed: {}", e))?;

        let status = response.status();
        if !status.is_success() {
            let body = response.text().await.unwrap_or_default();
            return Err(format!("Bytebot error ({}): {}", status, body));
        }

        response
            .json::<ComputerUseResponse>()
            .await
            .map_err(|e| format!("Bytebot response parse error: {}", e))
    }
}
