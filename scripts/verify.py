#!/usr/bin/env python3

import json
import subprocess
import sys

PREFIX = "10.99.99.99/32"
NODES = {"n1": "10.0.1.2", "n2": "10.0.2.2", "n3": "10.0.3.2"}


def vtysh(node, cmd):
    out = subprocess.run(
        ["docker", "exec", f"clab-anycast-{node}", "vtysh", "-c", cmd],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)


def main():
    ok = True
    peers = vtysh("rc", "show bgp summary json").get("ipv4Unicast", {}).get("peers", {})
    for node, ip in NODES.items():
        state = peers.get(ip, {}).get("state", "missing")
        good = state == "Established"
        print(f"[{'PASS' if good else 'FAIL'}] rc <-> {node} ({ip}): {state}")
        ok = ok and good

    routes = vtysh("rc", f"show ip route {PREFIX} json").get(PREFIX, [])
    active = next((r for r in routes if r.get("selected")), None)
    if not active:
        print(f"[FAIL] no selected route for {PREFIX}")
        sys.exit(1)

    nh = active["nexthops"][0]["ip"]
    node = next((n for n, ip in NODES.items() if ip == nh), "unknown")
    print(f"[INFO] {PREFIX} is currently routed via {node} ({nh})")
    if len(sys.argv) > 1:
        good = node == sys.argv[1]
        print(f"[{'PASS' if good else 'FAIL'}] expected active node {sys.argv[1]}")
        ok = ok and good
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()