#!/usr/bin/env python3
"""Summarise a failover-test.sh log: who answered, when it changed, and how long
clients went without an answer.

Usage:
  ./scripts/failover-test.sh | tee logs/b1.log     # break something, then Ctrl-C
  python3 scripts/analyze.py logs/b1.log           # outage per event
  python3 scripts/analyze.py logs/b4.log 180       # 2nd argument: baseline in seconds,
                                                   # also prints the gain vs that baseline

Resolution: the probe runs every ~0.5 s and curl waits up to 1 s, so treat
results as accurate to roughly +/- 1 second.
"""
import re
import sys
from datetime import datetime

LINE = re.compile(r"^(\d{2}:\d{2}:\d{2}\.\d{1,6})\s+(.*)$")


def parse(path):
    rows = []
    with open(path) as f:
        for raw in f:
            m = LINE.match(raw.strip())
            if m:
                rows.append((datetime.strptime(m.group(1), "%H:%M:%S.%f"), m.group(2).strip()))
    return rows


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    rows = parse(sys.argv[1])
    if not rows:
        sys.exit("no timestamped lines found; was the log produced by failover-test.sh?")
    baseline = float(sys.argv[2]) if len(sys.argv) > 2 else None

    prev_node = last_good = None
    failed = events = 0
    for t, text in rows:
        if text.startswith("served by"):
            node = text.split()[-1]
            if prev_node and (failed or node != prev_node):
                events += 1
                gap = (t - last_good).total_seconds()
                print(f"event {events}: {prev_node} -> {node}, no answer for ~{gap:.1f} s "
                      f"({failed} failed probes)")
                if baseline and gap > 0:
                    factor = baseline / gap
                    saved = 100 * (baseline - gap) / baseline
                    print(f"  vs baseline {baseline:g} s: {factor:.0f}x faster, {saved:.1f}% less downtime")
            prev_node, last_good, failed = node, t, 0
        else:
            failed += 1

    if failed:
        print(f"log ends with {failed} unanswered probes: the service never came back")
    if not events and not failed:
        print("no failover seen in this log")


if __name__ == "__main__":
    main()
