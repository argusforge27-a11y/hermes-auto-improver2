#!/usr/bin/env python3
"""Extract degraded skill names from health metrics JSON."""
import json
import os
import sys

path = os.environ.get("HERMES_METRICS_FILE", "health_metrics.json")
if os.path.exists(path):
    data = json.load(open(path))
    degraded = [s for s in data.get("skills", []) if not s.get("healthy", True)]
    print(" ".join(s["skill"] for s in degraded))