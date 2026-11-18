#!/bin/bash
# Installs or upgrades the Pi Bell Slapper. Run from the repo: sudo ./install.sh [--defaults]
set -euo pipefail

APP_DIR=/opt/bell-slapper
SERVICE=bell-slapper.service

die() { echo "Error: $*" >&2; exit 1; }

# --defaults skips prompts and uses the default choices.
DEFAULTS=false
for arg in "$@"; do
  case "$arg" in
    --defaults) DEFAULTS=true ;;
    *) die "unknown option '$arg' (usage: sudo ./install.sh [--defaults])" ;;
  esac
done

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
# Skip refreshing package lists if this script did it in the last 10 minutes.
stamp=/var/cache/bell-slapper-apt-update
if [ -z "$(find "$stamp" -mmin -10 2>/dev/null)" ]; then
  apt-get update -q
  touch "$stamp"
fi
apt-get install -y -q python3 python3-rpi-lgpio ffmpeg alsa-utils

echo "Installing app to $APP_DIR..."
rm -rf "$APP_DIR"
install -d "$APP_DIR/web"
install -m 755 server.py "$APP_DIR/"
install -m 644 ding.wav "$APP_DIR/"
install -m 644 web/* "$APP_DIR/web/"

# Choose the default audio output, preferring USB; ask if there's more than one.
mapfile -t cards < <(sed -n 's/^ *[0-9]* \[\([^ ]*\) *\]: \(.*\)$/\1|\2/p' /proc/asound/cards 2>/dev/null)
if [ ${#cards[@]} -gt 0 ]; then
  choice=0
  for i in "${!cards[@]}"; do
    if [[ ${cards[$i]} == *"|USB-Audio"* ]]; then choice=$i; break; fi
  done
  if [ ${#cards[@]} -gt 1 ] && [ -t 0 ] && [ "$DEFAULTS" = false ]; then
    echo "Audio outputs:"
    for i in "${!cards[@]}"; do echo "  $((i + 1))) ${cards[$i]#*|}"; done
    read -rp "Play sounds through which output? [$((choice + 1))]: " answer
    if [[ $answer =~ ^[0-9]+$ ]] && [ "$answer" -ge 1 ] && [ "$answer" -le ${#cards[@]} ]; then
      choice=$((answer - 1))
    fi
  fi
  card=${cards[$choice]%%|*}
  echo "Using audio output: ${cards[$choice]#*|}"

  if [ -f /etc/asound.conf ] && ! grep -q 'pi-bell-slapper' /etc/asound.conf; then
    cp /etc/asound.conf "/etc/asound-backup-$(date +%F).conf"
  fi
  cat > /etc/asound.conf <<EOF
# Written by pi-bell-slapper install.sh.
pcm.!default {
        type plug
        slave.pcm "hw:CARD=$card,DEV=0"
}

ctl.!default {
        type hw
        card $card
}
EOF
else
  echo "Warning: no sound cards found; sounds won't play." >&2
fi

echo "Starting $SERVICE..."
# Reloading systemd is slow on a Pi Zero, so only do it when the unit changed.
if ! cmp -s "$SERVICE" "/etc/systemd/system/$SERVICE"; then
  install -m 644 "$SERVICE" /etc/systemd/system/
  systemctl daemon-reload
fi
systemctl is-enabled --quiet "$SERVICE" || systemctl enable --no-reload "$SERVICE"
systemctl restart "$SERVICE"

sleep 2
systemctl is-active --quiet "$SERVICE" || die "service failed to start; check: journalctl -u $SERVICE"
echo "Done! Visit http://$(hostname).local/"
