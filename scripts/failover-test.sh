#!/usr/bin/env bash
while true; do
  printf '%s  ' "$(date +%T.%3N)"
  docker exec clab-anycast-client curl -s -m 1 http://10.99.99.99 || echo "NO ANSWER"
  sleep 0.5
done
