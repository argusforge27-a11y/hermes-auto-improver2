"""Stub: Gemini engine not configured. Local engine path never calls these."""
def is_youtube(*a, **k):
    return False


def upload_file(*a, **k):
    raise SystemExit("Gemini upload unavailable (no API key)")


def ask(*a, **k):
    raise SystemExit("Gemini ask unavailable (no API key)")


def delete_file(*a, **k):
    return None