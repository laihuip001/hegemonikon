# Hegemonikón RDP + Xfce 最適化マニュアル

> **対象**: Debian 13 + Xfce + xrdp  
> **更新日**: 2026-02-06

---

## 🎯 構成概要

| 接続方法 | デスクトップ環境 | 用途 |
| :--- | :--- | :--- |
| **ローカル** | KDE Plasma / GNOME | モダン UI |
| **RDP** | Xfce（最適化済み） | 軽量・安定 |

---

## 📋 適用済み設定

### 1. モダンテーマ

```bash
sudo apt install -y arc-theme papirus-icon-theme
```

**GUI 設定**:

- 設定 → 外観 → スタイル: **Arc-Dark**
- 設定 → 外観 → アイコン: **Papirus-Dark**

---

### 2. パフォーマンス最適化

```bash
# コンポジティング無効化（RDP 遅延軽減）
xfconf-query -c xfwm4 -p /general/use_compositing -s false

# DPMS/スクリーンセーバー無効化（黒画面防止）
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-enabled -s false
xfconf-query -c xfce4-screensaver -p /saver/enabled -s false
```

---

### 3. タスク切り替え（ウィンドウボタン）

1. パネル右クリック → **パネル** → **アイテムの追加**
2. **「ウィンドウボタン」**を追加
3. 位置を調整

---

### 4. クリップボード管理 (CopyQ)

```bash
# CopyQ 自動起動設定済み
copyq &
```

**GUI 操作 / ショートカット**:

- **履歴表示**: `Ctrl + Shift + V` または `Super + V`
- **コマンド**: `copyq show`
- **監視の一時停止/再開**: `copyq disable` / `copyq enable`

**重要 (xrdp の制限)**:

- **テキスト**: 共有可能（Windows ↔ Debian）
- **画像（スクショ）**: **標準では共有不可**（CopyQ を入れてもプロトコル制限により不可）
- **回避策 (ShareX + Syncthing)**:
    1. Windows に **ShareX** をインストール (`winget install ShareX.ShareX`)。
    2. ShareX の「アプリケーション設定」→「パス」で、**「カスタムスクリーンショットフォルダを使用」**にチェックを入れ、Syncthing 同期フォルダ（例: `C:\Users\makar\Hegemonikon\screenshots`）を指定する。
    3. Windows でスクショ (PrintScreen) を撮ると、自動的に保存され、Debian の `~/Sync/screenshots/` に即座に同期される。
- **画像共有に対応した代替手段**:
  - **RustDesk**: 簡単、画像クリップボード対応。
  - **TigerVNC**: 古典的だが堅牢。
  - **GNOME Remote Desktop**: GNOME 環境なら画像共有もスムーズ。
  - **Parsec**: 高速・低遅延だがゲーム寄り。

---

### 5. スクリーンショット (Screenshooter)

```bash
# インストール
sudo apt install -y xfce4-screenshooter
```

**使用方法**:

- **Print Screen キー**: 全画面キャプチャ
- **コマンド**: `xfce4-screenshooter`
- **出力先**: クリップボードへコピー または ファイル保存

---

## 🔧 xrdp + Xfce 設定

### ~/.xsession

```bash
echo "startxfce4" > ~/.xsession
```

これで RDP ログイン時に自動的に Xfce が起動。

---

## 🛡️ gnome-remote-desktop 競合対策

GNOME がインストールされている場合、3389 ポートの競合を防ぐ:

```bash
sudo systemctl mask gnome-remote-desktop.service
systemctl --user mask gnome-remote-desktop.service
```

---

## 🔍 トラブルシューティング

### 黒画面になる

```bash
# ローカルセッションをログアウト
ssh makaron8426@100.80.253.2 \
  'sid=$(loginctl list-sessions --no-legend | awk '\''$4=="seat0"{print $1; exit}'\''); \
   [ -n "$sid" ] && sudo loginctl terminate-session "$sid"'
```

### xrdp が起動しない

```bash
# ポート確認
sudo ss -ltnp | grep :3389

# gnome-remote-desktop が占有している場合
sudo systemctl stop gnome-remote-desktop
sudo systemctl mask gnome-remote-desktop
sudo systemctl restart xrdp
```

### 日本語入力ができない

```bash
# Fcitx5 再起動
fcitx5 -dr
```

### パネルが消えた / 操作できない

```bash
# 1. パネルの再起動試行
xfce4-panel --restart &

# 2. 設定リセット（すべて消えるので注意）
xfconf-query -c xfce4-panel -p /panels -r -R
xfconf-query -c xfce4-panel -p /plugins -r -R
xfce4-panel &

# 3. パッケージ再インストール（設定項目にパネルがない場合の決定打）
sudo apt install --reinstall -y xfce4-panel xfce4-panel-profiles
```

### クリップボードが同期しない（特に Windows → Debian が不可）

xrdp のクリップボード管理プロセス (`xrdp-chansrv`) の不具合、依存パッケージの不足、または Debian 側のクリップボードマネージャ (CopyQ 等) との競合が原因の場合があります。

1. **基本パッケージの導入**: `xclip` と `xsel` が必要です。

   ```bash
   sudo apt install -y xclip xsel
   ```

2. **chansrv の再起動**: ターミナルで `killall xrdp-chansrv` を実行。プロセスは自動で再起動されます（再接続不要）。
3. **クライアント設定の確認**: Windows 側の「リモートデスクトップ接続」→「ローカルリソース」タブで「クリップボード」にチェックが入っているか確認。
4. **CopyQ の一時停止**: `copyq disable` を実行して共有が復活するか確認してください（その後 `copyq enable` で戻す）。
5. **プロセス確認**: `pgrep -a xrdp-chansrv` でプロセスが動いているか確認。
6. **Windows Win+V の制限**: RDP 側からのコピーは Windows の `Win+V` 履歴には自動的に入りません。直接ペーストは可能ですが、履歴に残したい場合は Windows 側で一度ペーストしてから再コピーしてください。

---

## 📡 接続情報

| 項目 | 値 |
| :--- | :--- |
| **Tailscale IP** | `100.80.253.2` |
| **ポート** | `3389` |
| **ユーザー名** | `makaron8426` |
| **デスクトップ** | Xfce4 |

---

## ✅ チェックリスト

- [ ] テーマ適用（Arc-Dark + Papirus-Dark）
- [ ] ウィンドウボタン追加
- [ ] コンポジティング無効化確認
- [ ] DPMS 無効化確認
- [ ] RDP 接続テスト

---

Last updated: 2026-02-06
