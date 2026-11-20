#!/bin/sh
# usage: healthcheck.sh <local ASN>
ASN="$1"
VIP="10.99.99.99/32"
while true; do
  if wget -q -T 1 -O /dev/null http://127.0.0.1/; then
    CMD="network $VIP"
  else
    CMD="no network $VIP"
  fi
  vtysh -c "conf t" -c "router bgp $ASN" -c "address-family ipv4 unicast" -c "$CMD" >/dev/null 2>&1
  sleep 1
done