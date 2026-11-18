"""
High-level AI agent for Concat video editing.
Parses natural language → plans MCP tool calls → executes.
"""
import os
import re
import glob
from pathlib import Path
from typing import Any, Dict, List, Optional

from .concat_mcp_client import ConcatMCPClient


class ConcatAIAgent:
    """Natural language → Concat MCP workflows."""

    def __init__(self, concat_binary: Optional[str] = None):
        self.client = ConcatMCPClient(binary=concat_binary)
        self.project_path: Optional[str] = None

    def __enter__(self):
        self.client.start()
        return self

    def __exit__(self, *args):
        self.client.stop()

    # ─── High-level workflows ───

    def create_shorts(
        self,
        input_pattern: str,
        duration: float = 30,
        add_captions: bool = True,
        punch_in_times: List[float] = None,
        export_resolution: str = "1080p",
        output_name: str = "short.mp4",
    ) -> str:
        """Create a Short/Reel/TikTok from clips."""
        # Create project
        project = self.client.call("project_create", {"name": "AI Shorts"})
        self.project_path = project["path"]
        
        # Import media (expand glob)
        files = sorted(glob.glob(os.path.expanduser(input_pattern)))
        if not files:
            raise ValueError(f"No files match {input_pattern}")
        for f in files:
            self.client.call("media_import", {"path": self.project_path, "file": f})
        
        # Add all clips to timeline in sequence
        self.client.call("clips_add_sequence", {"path": self.project_path, "lane": 0})
        
        # Trim to target duration
        timeline = self.client.call("timeline_read", {"path": self.project_path})
        total_dur = timeline.get("duration", 0)
        if total_dur > duration:
            self.client.call("clip_trim", {
                "path": self.project_path,
                "clip_id": timeline["clips"][-1]["id"],
                "end": duration,
            })
        
        # Add captions (local Whisper)
        if add_captions:
            self.client.call("captions_add", {"path": self.project_path, "lane": 1})
        
        # Punch-in keyframes (zoom)
        if punch_in_times:
            clips = self.client.call("timeline_read", {"path": self.project_path})["clips"]
            for t in punch_in_times:
                # Find clip at time t
                clip = next((c for c in clips if c["start"] <= t < c["end"]), None)
                if clip:
                    rel = (t - clip["start"]) / (clip["end"] - clip["start"])
                    self.client.call("keyframe_set", {
                        "path": self.project_path,
                        "clip_id": clip["id"],
                        "property": "scale",
                        "position": rel,
                        "value": 1.5,  # 1.5x zoom
                    })
                    # Return to 1.0 shortly after
                    self.client.call("keyframe_set", {
                        "path": self.project_path,
                        "clip_id": clip["id"],
                        "property": "scale",
                        "position": min(rel + 0.1, 0.99),
                        "value": 1.0,
                    })
        
        # Export
        export = self.client.call("export_start", {
            "path": self.project_path,
            "output": output_name,
            "preset": export_resolution,
        })
        result = self.client.call("export_wait", {"path": self.project_path, "id": export["id"]})
        return result["output"]

    def split_podcast(
        self,
        input_file: str,
        chapter_duration: float = 60,
        add_titles: bool = True,
    ) -> List[str]:
        """Split long video into chapters."""
        outputs = []
        project = self.client.call("project_create", {"name": "Podcast Chapters"})
        self.project_path = project["path"]
        
        self.client.call("media_import", {"path": self.project_path, "file": os.path.expanduser(input_file)})
        self.client.call("clips_add_sequence", {"path": self.project_path, "lane": 0})
        
        timeline = self.client.call("timeline_read", {"path": self.project_path})
        total = timeline.get("duration", 0)
        clips = timeline["clips"]
        
        chapter = 1
        pos = 0.0
        while pos < total:
            end = min(pos + chapter_duration, total)
            # Create chapter project
            ch_project = self.client.call("project_create", {"name": f"Chapter {chapter}"})
            ch_path = ch_project["path"]
            
            # Copy clip segment (simplified - would need clip_split in real impl)
            # For now, export segment from main timeline
            export = self.client.call("export_start", {
                "path": self.project_path,
                "output": f"chapter_{chapter}.mp4",
                "preset": "1080p",
                "range": [pos, end],  # hypothetical
            })
            result = self.client.call("export_wait", {"path": self.project_path, "id": export["id"]})
            outputs.append(result["output"])
            
            pos = end
            chapter += 1
        return outputs

    def tutorial_zoom_callout(
        self,
        input_file: str,
        zoom_times: List[Dict],  # [{time: 12.5, scale: 2.0, duration: 2.0}, ...]
        callouts: List[Dict],    # [{time: 12.5, text: "Click here", position: [0.5, 0.3]}, ...]
        output_name: str = "tutorial.mp4",
    ) -> str:
        """Screen recording with zoom punch-ins and callout text."""
        project = self.client.call("project_create", {"name": "Tutorial"})
        self.project_path = project["path"]
        
        self.client.call("media_import", {"path": self.project_path, "file": os.path.expanduser(input_file)})
        self.client.call("clips_add_sequence", {"path": self.project_path, "lane": 0})
        
        timeline = self.client.call("timeline_read", {"path": self.project_path})
        clips = timeline["clips"]
        
        # Zoom keyframes
        for z in zoom_times:
            clip = next((c for c in clips if c["start"] <= z["time"] < c["end"]), None)
            if clip:
                rel = (z["time"] - clip["start"]) / (clip["end"] - clip["start"])
                self.client.call("keyframe_set", {
                    "path": self.project_path,
                    "clip_id": clip["id"],
                    "property": "scale",
                    "position": rel,
                    "value": z.get("scale", 2.0),
                })
                end_rel = min(rel + z.get("duration", 1.0) / (clip["end"] - clip["start"]), 0.99)
                self.client.call("keyframe_set", {
                    "path": self.project_path,
                    "clip_id": clip["id"],
                    "property": "scale",
                    "position": end_rel,
                    "value": 1.0,
                })
        
        # Callout titles
        for c in callouts:
            clip = next((cl for cl in clips if cl["start"] <= c["time"] < cl["end"]), None)
            if clip:
                rel = (c["time"] - clip["start"]) / (clip["end"] - clip["start"])
                self.client.call("title_add", {
                    "path": self.project_path,
                    "lane": 1,
                    "start": c["time"],
                    "duration": c.get("duration", 3.0),
                    "text": c["text"],
                    "position": c.get("position", [0.5, 0.2]),
                    "size": c.get("size", 0.08),
                    "color": c.get("color", "#ffffff"),
                })
        
        export = self.client.call("export_start", {
            "path": self.project_path,
            "output": output_name,
            "preset": "1080p",
        })
        result = self.client.call("export_wait", {"path": self.project_path, "id": export["id"]})
        return result["output"]

    # ─── Natural language parser (simplified) ───

    def parse_and_execute(self, instruction: str) -> str:
        """Parse natural language and run appropriate workflow."""
        instr = instruction.lower()
        
        # Shorts/Reel/TikTok
        if any(kw in instr for kw in ["short", "reel", "tiktok", "vertical"]):
            # Extract duration
            dur_match = re.search(r"(\d+)\s*[sS]?(?:econd)?", instr)
            duration = float(dur_match.group(1)) if dur_match else 30
            
            # Extract input pattern
            pattern_match = re.search(r"from\s+([^\s,]+)", instr)
            pattern = pattern_match.group(1) if pattern_match else "~/Videos/*.mp4"
            
            # Punch-in times
            punch_times = []
            for m in re.finditer(r"(?:punch|zoom).*?(\d+(?:\.\d+)?)\s*[sS]", instr):
                punch_times.append(float(m.group(1)))
            
            return self.create_shorts(
                input_pattern=pattern,
                duration=duration,
                punch_in_times=punch_times or None,
            )
        
        # Podcast chapters
        if "podcast" in instr or "chapter" in instr:
            file_match = re.search(r"(\S+\.mp4)", instr)
            if file_match:
                return self.split_podcast(file_match.group(1))
        
        # Tutorial with zoom/callout
        if "tutorial" in instr or "screen" in instr or "zoom" in instr:
            file_match = re.search(r"(\S+\.(?:mov|mp4))", instr)
            if file_match:
                # Simplified - would need better NLP
                return self.tutorial_zoom_callout(file_match.group(1), [], [])
        
        # Simple project + title fallback
        if "project" in instr or "title" in instr:
            import os
            home = os.path.expanduser('~')
            project = self.client.call('project_create', {
                'location': home,
                'name': 'AI Project',
                'video': {'width': 1920, 'height': 1080, 'rateNum': 30, 'rateDen': 1}
            })
            path = os.path.join(home, 'AI Project')
            title_text = "Hello World"
            for word in ["title", "text", "saying"]:
                if word in instr:
                    idx = instr.index(word)
                    after = instr[idx + len(word):].strip()
                    if after:
                        title_text = after.split()[0] if after.split() else title_text
                        break
            self.client.call('title_add', {
                'path': path,
                'lane': 0,
                'start': 0.0,
                'duration': 3.0,
                'text': title_text,
                'position': [0.5, 0.5],
                'size': 0.1,
                'color': '#ffffff'
            })
            self.client.call('project_save', {'path': path})
            return path
        
        raise ValueError(f"Could not parse instruction: {instruction}")
