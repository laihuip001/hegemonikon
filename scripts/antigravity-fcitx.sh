#!/bin/bash
# Wrapper to launch Antigravity with proper Japanese input support
# Fcitx5 integration for Electron apps

export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx

# Start fcitx5 if not running
pgrep -x fcitx5 > /dev/null || fcitx5 -d

# Launch Antigravity with Wayland/X11 IME support flags
exec /usr/share/antigravity/antigravity \
    --enable-wayland-ime \
    --enable-features=UseOzonePlatform,WaylandWindowDecorations \
    --ozone-platform-hint=auto \
    --gtk-version=4 \
    "$@"
