#!/bin/bash
# Installs or upgrades the Pi Bell Slapper. Run from the repo: sudo ./install.sh
set -euo pipefail

APP_DIR=/opt/bell-slapper
SERVICE=bell-slapper.service

die() { echo "Error: $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run with sudo."
cd "$(dirname "$0")"

# Only Raspberry Pi OS Bookworm or Trixie is supported.
[ -f /etc/rpi-issue ] || die "this doesn't look like Raspberry Pi OS."
# shellcheck source=/dev/null
. /etc/os-release
case "${VERSION_CODENAME:-}" in
  bookworm|trixie) ;;
  *) die "Raspberry Pi OS ${VERSION_CODENAME:-unknown} is not supported (use Trixie or Bookworm)." ;;
esac

echo "Installing packages..."
apt-get update -q
apt-get install -y -q python3 python3-rpi-lgpio ffmpeg alsa-utils

echo "Installing app to $APP_DIR..."
rm -rf "$APP_DIR"
install -d "$APP_DIR/web"
install -m 755 server.py "$APP_DIR/"
install -m 644 ding.wav "$APP_DIR/"
install -m 644 web/* "$APP_DIR/web/"

# Default to the first USB sound card, if there is one and ALSA isn't configured yet.
card=$(awk '$2 == "snd_usb_audio" {print $1; exit}' /proc/asound/modules 2>/dev/null || true)
if [ -n "$card" ] && [ ! -f /etc/asound.conf ]; then
  echo "Setting USB sound card $card as the default audio output..."
  cat > /etc/asound.conf <<EOF
pcm.!default {
        type plug
        slave.pcm "hw:$card,0"
}

ctl.!default {
        type hw
        card $card
}
EOF
fi

echo "Starting $SERVICE..."
install -m 644 "$SERVICE" /etc/systemd/system/
systemctl daemon-reload
systemctl enable "$SERVICE"
systemctl restart "$SERVICE"

sleep 2
systemctl is-active --quiet "$SERVICE" || die "service failed to start; check: journalctl -u $SERVICE"
echo "Done! Visit http://$(hostname).local/"
