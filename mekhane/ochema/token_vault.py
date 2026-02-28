# PROOF: [L2/インフラ] <- mekhane/ochema/ A0→多アカウント OAuth トークン管理
# PURPOSE: TokenVault — 複数 Google OAuth アカウントのトークンを管理・切替する
"""TokenVault — Multi-account OAuth token management.

Manages multiple Google OAuth refresh tokens for Cortex API access.
Each account has independent credentials and can be used simultaneously.

Usage:
    from mekhane.ochema.token_vault import TokenVault

    vault = TokenVault()
    token = vault.get_token("default")    # Default gemini-cli account
    token = vault.get_token("work")       # Work account

    vault.add_account("work", Path("~/.gemini/oauth_creds_work.json"))
    vault.list_accounts()
    vault.set_default("work")

Storage:
    ~/.config/ochema/
    ├── vault.json          # Account registry + metadata
    └── tokens/
        ├── default.json    # Default (gemini-cli) credentials
        └── work.json       # Additional account credentials
"""

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# --- Constants ---

_VAULT_DIR = Path.home() / ".config" / "ochema"
_VAULT_FILE = _VAULT_DIR / "vault.json"
_TOKENS_DIR = _VAULT_DIR / "tokens"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_OAUTH_CONFIG = Path.home() / ".config" / "cortex" / "oauth.json"
_GEMINI_CLI_CREDS = Path.home() / ".gemini" / "oauth_creds.json"
_TOKEN_TTL = 3300  # 55 minutes


# --- Exceptions ---


class VaultError(Exception):
    """TokenVault error."""
    pass


class VaultAuthError(VaultError):
    """Authentication error for a specific account."""
    pass


# --- TokenVault ---


class TokenVault:
    """Multi-account OAuth token manager.

    Stores refresh tokens for multiple Google accounts and provides
    access tokens with caching and auto-refresh.

    Thread-safe for concurrent access to different accounts.
    Not thread-safe for mutations (add/remove/set_default).
    """

    def __init__(self) -> None:
        """Initialize vault. Creates directory structure if needed."""
        self._cache: dict[str, tuple[str, float]] = {}  # account -> (token, expiry)
        self._vault_data: Optional[dict[str, Any]] = None
        self._oauth_config: Optional[tuple[str, str]] = None

    # --- Public API ---

    def get_token(self, account: str = "default") -> str:
        """Get a valid access token for the given account.

        Args:
            account: Account name ("default", "work", etc.)

        Returns:
            Valid OAuth access token (ya29.*)

        Raises:
            VaultError: Account not found
            VaultAuthError: Token refresh failed
        """
        # Check cache
        if account in self._cache:
            token, expiry = self._cache[account]
            if time.time() < expiry:
                return token

        # Get refresh token for account
        vault = self._load_vault()
        acct_info = vault.get("accounts", {}).get(account)
        if not acct_info:
            # Auto-import default from gemini-cli if not registered
            if account == "default" and _GEMINI_CLI_CREDS.exists():
                self._auto_import_default()
                vault = self._load_vault(force=True)
                acct_info = vault.get("accounts", {}).get(account)

            if not acct_info:
                raise VaultError(
                    f"アカウント '{account}' が見つかりません。\n"
                    f"登録方法: vault.add_account('{account}', Path('/path/to/creds.json'))"
                )

        creds_file = _TOKENS_DIR / acct_info["creds_file"]
        if not creds_file.exists():
            raise VaultError(
                f"認証ファイルが見つかりません: {creds_file}"
            )

        try:
            creds = json.loads(creds_file.read_text())
            refresh_token = creds["refresh_token"]
        except (json.JSONDecodeError, KeyError) as e:
            raise VaultAuthError(f"認証ファイル解析エラー ({account}): {e}")

        # Refresh access token
        token = self._refresh_token(refresh_token)
        self._cache[account] = (token, time.time() + _TOKEN_TTL)
        return token

    def add_account(
        self,
        name: str,
        creds_path: Path,
        email: str = "",
    ) -> dict[str, str]:
        """Add a new account to the vault.

        Args:
            name: Account name (e.g. "work", "personal")
            creds_path: Path to OAuth credentials file (with refresh_token)
            email: Optional email for display

        Returns:
            Account info dict

        Raises:
            VaultError: If account already exists or creds invalid
        """
        vault = self._load_vault()

        if name in vault.get("accounts", {}):
            raise VaultError(f"アカウント '{name}' は既に存在します")

        # Validate creds
        creds_path = Path(creds_path).expanduser()
        if not creds_path.exists():
            raise VaultError(f"認証ファイルが見つかりません: {creds_path}")

        try:
            creds = json.loads(creds_path.read_text())
            if "refresh_token" not in creds:
                raise VaultError("refresh_token が含まれていません")
        except json.JSONDecodeError as e:
            raise VaultError(f"認証ファイル解析エラー: {e}")

        # Copy creds to vault
        _TOKENS_DIR.mkdir(parents=True, exist_ok=True)
        dest = _TOKENS_DIR / f"{name}.json"
        dest.write_text(json.dumps(creds, indent=2))
        dest.chmod(0o600)

        # Detect email from creds if not provided
        if not email:
            email = creds.get("email", creds.get("account", ""))

        # Update vault
        acct_info = {
            "email": email,
            "source": "manual",
            "creds_file": f"{name}.json",
            "added_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        vault.setdefault("accounts", {})[name] = acct_info
        if not vault.get("default_account"):
            vault["default_account"] = name
        self._save_vault(vault)

        logger.info("Account added: %s (email=%s)", name, email or "?")
        return acct_info

    def remove_account(self, name: str) -> None:
        """Remove an account from the vault.

        Args:
            name: Account name to remove

        Raises:
            VaultError: If account doesn't exist or is the default
        """
        vault = self._load_vault()
        if name not in vault.get("accounts", {}):
            raise VaultError(f"アカウント '{name}' が見つかりません")

        if vault.get("default_account") == name:
            raise VaultError(
                f"デフォルトアカウント '{name}' は削除できません。"
                "先に set_default() で別のアカウントをデフォルトに設定してください。"
            )

        # Remove creds file
        creds_file = _TOKENS_DIR / vault["accounts"][name]["creds_file"]
        if creds_file.exists():
            creds_file.unlink()

        del vault["accounts"][name]
        self._save_vault(vault)

        # Clear cache
        self._cache.pop(name, None)
        logger.info("Account removed: %s", name)

    def list_accounts(self) -> list[dict[str, Any]]:
        """List all registered accounts.

        Returns:
            List of account info dicts with name, email, is_default
        """
        vault = self._load_vault()
        default = vault.get("default_account", "")
        result = []
        for name, info in vault.get("accounts", {}).items():
            result.append({
                "name": name,
                "email": info.get("email", ""),
                "source": info.get("source", "unknown"),
                "is_default": name == default,
                "added_at": info.get("added_at", ""),
            })
        return result

    def set_default(self, name: str) -> None:
        """Set the default account.

        Args:
            name: Account name to set as default
        """
        vault = self._load_vault()
        if name not in vault.get("accounts", {}):
            raise VaultError(f"アカウント '{name}' が見つかりません")

        vault["default_account"] = name
        self._save_vault(vault)
        logger.info("Default account set: %s", name)

    def get_default_account(self) -> str:
        """Get the name of the default account."""
        vault = self._load_vault()
        return vault.get("default_account", "default")

    def get_token_with_failover(
        self,
        primary: str = "default",
    ) -> tuple[str, str]:
        """Get token with automatic failover to other accounts.

        Tries the primary account first. If it fails, iterates through
        all other registered accounts.

        Args:
            primary: Preferred account name

        Returns:
            (token, account_name) tuple — the token and which account provided it

        Raises:
            VaultError: If no account can provide a valid token
        """
        # Try primary first
        try:
            token = self.get_token(primary)
            return token, primary
        except (VaultError, VaultAuthError) as e:
            logger.warning("Primary account '%s' failed: %s", primary, e)

        # Failover: try all other accounts
        vault = self._load_vault()
        for name in vault.get("accounts", {}):
            if name == primary:
                continue
            try:
                token = self.get_token(name)
                logger.info("Failover: using account '%s' instead of '%s'", name, primary)
                return token, name
            except (VaultError, VaultAuthError) as e:
                logger.debug("Failover account '%s' also failed: %s", name, e)
                continue

        raise VaultError(
            f"全アカウントでトークン取得に失敗しました。"
            f"Primary: '{primary}', Total accounts: {len(vault.get('accounts', {}))}"
        )

    def get_project(self, account: str = "default") -> Optional[str]:
        """Get the project ID for an account (if cached)."""
        vault = self._load_vault()
        acct = vault.get("accounts", {}).get(account, {})
        return acct.get("project")

    def set_project(self, account: str, project: str) -> None:
        """Cache the project ID for an account."""
        vault = self._load_vault()
        if account in vault.get("accounts", {}):
            vault["accounts"][account]["project"] = project
            self._save_vault(vault)

    # --- Private Methods ---

    def _load_vault(self, force: bool = False) -> dict[str, Any]:
        """Load vault data from disk (cached)."""
        if self._vault_data is not None and not force:
            return self._vault_data

        if _VAULT_FILE.exists():
            try:
                self._vault_data = json.loads(_VAULT_FILE.read_text())
            except json.JSONDecodeError:
                logger.warning("vault.json 破損 — 初期化します")
                self._vault_data = {"default_account": "default", "accounts": {}}
        else:
            self._vault_data = {"default_account": "default", "accounts": {}}

        return self._vault_data

    def _save_vault(self, data: dict[str, Any]) -> None:
        """Save vault data to disk."""
        _VAULT_DIR.mkdir(parents=True, exist_ok=True)
        _VAULT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        _VAULT_FILE.chmod(0o600)
        self._vault_data = data

    def _auto_import_default(self) -> None:
        """Auto-import gemini-cli credentials as 'default' account."""
        if not _GEMINI_CLI_CREDS.exists():
            return

        try:
            creds = json.loads(_GEMINI_CLI_CREDS.read_text())
            if "refresh_token" not in creds:
                return
        except json.JSONDecodeError:
            return

        # Copy to vault
        _TOKENS_DIR.mkdir(parents=True, exist_ok=True)
        dest = _TOKENS_DIR / "default.json"
        if not dest.exists():
            dest.write_text(json.dumps(creds, indent=2))
            dest.chmod(0o600)

        # Register in vault
        vault = self._load_vault()
        vault.setdefault("accounts", {})["default"] = {
            "email": creds.get("email", creds.get("account", "")),
            "source": "gemini-cli (auto-imported)",
            "creds_file": "default.json",
            "added_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        vault["default_account"] = "default"
        self._save_vault(vault)
        logger.info("Auto-imported gemini-cli credentials as 'default' account")

    def _refresh_token(self, refresh_token: str) -> str:
        """Refresh an access token using the refresh token."""
        client_id, client_secret = self._get_oauth_config()

        data = urllib.parse.urlencode({
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }).encode("utf-8")

        try:
            req = urllib.request.Request(_TOKEN_URL, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["access_token"]
        except (urllib.error.HTTPError, KeyError, json.JSONDecodeError) as e:
            raise VaultAuthError(f"Token refresh 失敗: {e}")

    def _get_oauth_config(self) -> tuple[str, str]:
        """Load OAuth client_id and client_secret (cached)."""
        if self._oauth_config:
            return self._oauth_config

        if not _OAUTH_CONFIG.exists():
            raise VaultError(
                f"OAuth 設定が見つかりません: {_OAUTH_CONFIG}\n"
                "作成方法: mkdir -p ~/.config/cortex && "
                'echo \'{"client_id":"...","client_secret":"..."}\' > ~/.config/cortex/oauth.json'
            )

        data = json.loads(_OAUTH_CONFIG.read_text())
        self._oauth_config = (data["client_id"], data["client_secret"])
        return self._oauth_config

    def status(self) -> dict[str, Any]:
        """Get token health status for all accounts.

        Returns:
            {
                "accounts": {
                    "account_name": {
                        "cached": bool,
                        "ttl_seconds": int or None,
                        "expires_at": str or None,
                        "healthy": bool,
                    },
                    ...
                },
                "default_account": str,
                "total_accounts": int,
            }
        """
        vault = self._load_vault()
        now = time.time()
        result: dict[str, Any] = {}

        for name in vault.get("accounts", {}):
            if name in self._cache:
                _token, expiry = self._cache[name]
                ttl = max(0, int(expiry - now))
                result[name] = {
                    "cached": True,
                    "ttl_seconds": ttl,
                    "expires_at": time.strftime(
                        "%Y-%m-%dT%H:%M:%S", time.localtime(expiry)
                    ),
                    "healthy": ttl > 300,  # > 5 min remaining
                }
            else:
                result[name] = {
                    "cached": False,
                    "ttl_seconds": None,
                    "expires_at": None,
                    "healthy": None,  # unknown until first use
                }

        return {
            "accounts": result,
            "default_account": vault.get("default_account", "default"),
            "total_accounts": len(result),
        }

    def __repr__(self) -> str:
        vault = self._load_vault()
        n = len(vault.get("accounts", {}))
        default = vault.get("default_account", "?")
        return f"TokenVault(accounts={n}, default={default!r})"
