"""
Hermes skill entry point for concat-ai-agent.
Exposes `concat_edit(instruction)` for natural language video editing.
"""
from typing import Any, Dict

from .concat_ai_agent import ConcatAIAgent


# Skill metadata for Hermes
def skill_info() -> Dict[str, Any]:
    return {
        "name": "concat-ai-agent",
        "description": "Drive Concat video editor via MCP from natural language",
        "version": "0.1.0",
        "author": "Argus",
        "license": "AGPL-3.0-or-later",
        "tools": ["concat_edit"],
    }


def concat_edit(instruction: str, concat_binary: str = None) -> Dict[str, Any]:
    """
    Edit video using natural language instructions.
    
    Examples:
    - "Create a 30s Short from ~/Videos/clips/*.mp4 with auto-captions, punch-in at 5s, export 1080p"
    - "Split podcast.mp4 into 60s chapters with titles"
    - "Take screen_recording.mov, zoom 2x at 12.5s, add callout 'Click here', export"
    
    Args:
        instruction: Natural language editing instruction
        concat_binary: Optional path to concat binary (auto-detected if omitted)
    
    Returns:
        Dict with output_path, preview_frames, and status
    """
    # Default to DMG mount if available, otherwise auto-detect
    if concat_binary is None:
        import os
        dmg_binary = "/Volumes/Concat/Concat.app/Contents/MacOS/concat"
        if os.path.exists(dmg_binary):
            concat_binary = dmg_binary
    try:
        with ConcatAIAgent(concat_binary=concat_binary) as agent:
            output = agent.parse_and_execute(instruction)
        return {
            "success": True,
            "output_path": output,
            "message": f"✅ Done! Output: {output}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"❌ Failed: {e}",
        }


# For direct testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = concat_edit(" ".join(sys.argv[1:]))
        print(result["message"])
        if result["success"]:
            print(f"Output: {result['output_path']}")
