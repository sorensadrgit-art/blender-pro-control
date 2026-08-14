#!/usr/bin/env bash
set -euo pipefail

GROUP=blender-pro-agent
ROOT=/srv/blender-pro

if ! getent group "$GROUP" >/dev/null; then
  groupadd --system "$GROUP"
fi

if id hermes >/dev/null 2>&1; then
  usermod -a -G "$GROUP" hermes
fi

# Published assets are immutable to agents but must remain readable/traversable
# for linked-library verification and rendering. SGID preserves the agent group
# on future published versions without granting agents write access.
install -d -o root -g "$GROUP" -m 2750 "$ROOT/assets/published"
chgrp -R "$GROUP" "$ROOT/assets/published"
find "$ROOT/assets/published" -type d -exec chmod 2750 {} +
find "$ROOT/assets/published" -type f -exec chmod 0640 {} +

for dir in jobs previews renders; do
  install -d -o root -g "$GROUP" -m 2770 "$ROOT/$dir"
  chgrp -R "$GROUP" "$ROOT/$dir"
done

find "$ROOT/jobs" -type d -exec chmod 2770 {} +
find "$ROOT/jobs" -type f -name '*.json' -exec chmod 0660 {} +
find "$ROOT/previews" -type d -exec chmod 2770 {} +
find "$ROOT/previews" -type f -exec chmod 0640 {} +
find "$ROOT/renders" -type d -exec chmod 2770 {} +
find "$ROOT/renders" -type f -exec chmod 0640 {} +
