"""Shared helpers for the long-form scripts: load script.json, flatten chapters into one line list, friendly errors."""
import json, re, sys
from pathlib import Path


def die(msg, code=2):
    print(f'ERROR: {msg}', file=sys.stderr)
    sys.exit(code)


def load_script(P):
    """Read <project>/script.json. Explains the problem (file, line, column) instead of printing a traceback."""
    f = Path(P) / 'script.json'
    if not f.exists():
        die(f'{f} not found. Run from inside the project folder (or pass it), or create one with scripts/new_video.sh <name>.')
    try:
        S = json.loads(f.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        ctx = f.read_text(encoding='utf-8').splitlines()
        near = ctx[e.lineno - 1].strip()[:100] if 0 < e.lineno <= len(ctx) else ''
        die(f'script.json is not valid JSON: {e.msg} at line {e.lineno}, column {e.colno}. Near: "{near}". '
            'Typical causes: a missing comma, a trailing comma, a straight " quote inside a text value (use \\" or a curly quote).')
    if not isinstance(S, dict):
        die('script.json must be a JSON object ({ "title": ..., "chapters": [...] }).')
    if not (S.get('chapters') or S.get('lines')):
        die('script.json needs "chapters": [ { "title": "...", "lines": [ { "text": "..." } ] } ].')
    return S


def flatten(S):
    """script.json (chapters[].lines[] or a plain lines[]) -> (chapters, flat_lines). Each flat line gets ch (chapter index) and first (first line of its chapter)."""
    chapters = S.get('chapters') or [{'title': S.get('title', 'Video'), 'lines': S['lines']}]
    flat = []
    for ci, c in enumerate(chapters):
        if not isinstance(c, dict) or not isinstance(c.get('lines'), list) or not c['lines']:
            die(f'chapter {ci} ("{c.get("title") if isinstance(c, dict) else c}") has no "lines" list.')
        for k, ln in enumerate(c['lines']):
            if not isinstance(ln, dict) or not isinstance(ln.get('text'), str) or not words_of(ln['text']):
                die(f'chapter {ci} line {k}: every line needs a non-empty "text" string with at least one word (got {json.dumps(ln)[:80]}).')
            flat.append({**ln, 'ch': ci, 'first': k == 0})
    return chapters, flat


def words_of(text):
    return [w for w in re.sub(r'\*', '', text).split() if re.search(r'[A-Za-z0-9]', w)]


def speakable(text, pronounce=None):
    """The text the voice reads: rich-text stars removed, quotes/dashes normalised, and the script's "pronounce" respellings applied
    (the captions keep the original spelling; only the voice hears the respelling)."""
    t = text.replace('*', '')
    t = t.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')
    t = re.sub(r'\s*\u2014\s*', ', ', t).replace('\u2013', '-').replace('\u2026', '...').replace('\u00a0', ' ')
    t = re.sub(r'\s*&\s*', ' and ', t)
    for word, said in (pronounce or {}).items():
        t = re.sub(r'(?<![A-Za-z0-9])' + re.escape(word) + r'(?![A-Za-z0-9])', said, t)
    return re.sub(r'\s+', ' ', t).strip()
