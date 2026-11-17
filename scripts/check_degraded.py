#!/usr/bin/env python3
"""Check health metrics and output degraded skills to GITHUB_OUTPUT."""
import json
import os
import sys

path = os.environ.get("HERMES_METRICS_FILE", "health_metrics.json")
if os.path.exists(path):
    data = json.load(open(path))
    degraded = [s for s in data.get("skills", []) if not s.get("healthy", True)]
    print(f"degraded={len(degraded)}")
    print("skills=" + " ".join(s["skill"] for s in degraded))
else:
    print("degraded=0")
    print("skills=")