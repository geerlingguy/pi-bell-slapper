#!/bin/bash
# Installs or upgrades the Pi Bell Slapper. Run from the repo: sudo ./install.sh [--defaults]
set -euo pipefail

APP_DIR=/opt/bell-slapper
SERVICE=bell-slapper.service
EMAIL_SERVICE=bell-slapper-email.service
EMAIL_CONFIG=/etc/bell-slapper/email.yml

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

PACKAGES=(python3 python3-rpi-lgpio ffmpeg alsa-utils python3-imapclient python3-yaml)
installed=$(dpkg-query -W -f='${db:Status-Abbrev}\n' "${PACKAGES[@]}" 2>/dev/null | grep -c '^ii' || true)
if [ "$installed" -ne ${#PACKAGES[@]} ]; then
  echo "Installing packages..."
  # Skip refreshing package lists if they changed in the last 10 minutes (same check as Ansible's apt module).
  if [ -z "$(find /var/lib/apt/lists -maxdepth 0 -mmin -10)" ]; then
    apt-get update -q
  fi
  apt-get install -y -q "${PACKAGES[@]}"
fi

echo "Installing app to $APP_DIR..."
rm -rf "$APP_DIR"
install -d "$APP_DIR/web"
install -m 755 server.py email_check.py "$APP_DIR/"
install -m 644 ding.wav "$APP_DIR/"
install -m 644 web/* "$APP_DIR/web/"

# Choose the default audio output, preferring USB; ask if there's more than one.
cards=()
for dir in /proc/asound/card[0-9]*; do
  [ -f "$dir/id" ] || continue
  label=$(<"$dir/id")
  [ -e "$dir/usbid" ] && label="$label (USB)"
  cards+=("$label")
done
if [ ${#cards[@]} -gt 0 ]; then
  choice=0
  for i in "${!cards[@]}"; do
    if [[ ${cards[$i]} == *" (USB)" ]]; then choice=$i; break; fi
  done
  if [ ${#cards[@]} -gt 1 ] && [ -t 0 ] && [ "$DEFAULTS" = false ]; then
    echo "Audio outputs:"
    for i in "${!cards[@]}"; do echo "  $((i + 1))) ${cards[$i]}"; done
    read -rp "Play sounds through which output? [$((choice + 1))]: " answer
    if [[ $answer =~ ^[0-9]+$ ]] && [ "$answer" -ge 1 ] && [ "$answer" -le ${#cards[@]} ]; then
      choice=$((answer - 1))
    fi
  fi
  card=${cards[$choice]% (USB)}
  [ -e "/proc/asound/$card" ] || die "sound card '$card' not found."
  echo "Using audio output: ${cards[$choice]}"

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

# Reloading systemd is slow on a Pi Zero, so only do it when a unit changed.
# A new email unit gets enabled; an existing one that was disabled stays off.
[ -f "/etc/systemd/system/$EMAIL_SERVICE" ] && email_new=false || email_new=true
reload=false
for unit in "$SERVICE" "$EMAIL_SERVICE"; do
  if ! cmp -s "$unit" "/etc/systemd/system/$unit"; then
    install -m 644 "$unit" /etc/systemd/system/
    reload=true
  fi
done
[ "$reload" = false ] || systemctl daemon-reload

start() {
  echo "Starting $1..."
  systemctl is-enabled --quiet "$1" || systemctl enable --quiet "$1"
  systemctl restart "$1"
  sleep 2
  systemctl is-active --quiet "$1" || die "$1 failed to start; check: journalctl -u $1"
}

start "$SERVICE"
if [ -f "$EMAIL_CONFIG" ]; then
  chmod 600 "$EMAIL_CONFIG"
  if [ "$email_new" = true ] || systemctl is-enabled --quiet "$EMAIL_SERVICE"; then
    start "$EMAIL_SERVICE"
  else
    echo "$EMAIL_SERVICE is disabled. To turn it on: sudo systemctl enable --now $EMAIL_SERVICE"
  fi
else
  echo "To ring the bell for emails, copy email.example.yml to $EMAIL_CONFIG, edit it, and run this again."
fi
echo "Done! Visit http://$(hostname).local/"
