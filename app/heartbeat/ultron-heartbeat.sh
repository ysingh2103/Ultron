#!/usr/bin/env bash
# Ultron heartbeat: logs basic health of linuxot every 30 seconds
while true; do
  disk=$(df --output=pcent / | tail -1 | tr -d ' %')
  load=$(cut -d' ' -f1 /proc/loadavg)
  for svc in tomcat10 docker k3s; do
    state=$(systemctl is-active "$svc")
    [ "$state" = "active" ] || echo "WARN $svc is $state"
  done
  echo "heartbeat disk=${disk}% load=${load}"
  sleep 30
done
