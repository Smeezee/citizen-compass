"""
Citizen Compass — Ask Engine

Core logic for the desktop overlay: takes a typed question, tries to
answer it from your own project files first, falls back to a web search
if nothing local looks relevant, then asks the local Ollama model
(qwen3:14b) to produce a plain-English answer grounded in whatever
context was found.

This module has NO GUI and NO hotkey code in it on purpose — it's the
"brain" only, so it can be tested headlessly (see the __main__ block)
before being wired into the actual overlay window. overlay_app.py (the
Windows GUI + hotkey shell) imports and calls ask_question() from here.

SEARCH STRATEGY (local-first, matching your stated preference):
  1. Grep-style keyword search across docs/, tests/testing-site/ships/,
     and data-layer/ for anything matching words in the question.
  2. If that turns up file content, hand it to qwen3:14b as context and
     ask it to answer using ONLY that context.
  3. If nothing local matches (or the model says it can't answer from
     what was found), fall back to a web search, hand THOSE results to
     qwen3:14b instead, and say clearly that the answer came from the web.

Every answer says where it came from (local files vs. web) so you're
never unsure whether you're looking at your own project data or
something pulled from the internet.
"""

import json
import re
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# ---- CONFIG -----------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
SEARCH_DIRS = [
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "tests" / "testing-site" / "ships",
    PROJECT_ROOT / "data-layer",
]
SEARCHABLE_EXTENSIONS = (".md", ".json", ".txt")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:14b"
OLLAMA_TIMEOUT_SECONDS = 60

MAX_LOCAL_FILES_AS_CONTEXT = 5
MAX_CHARS_PER_FILE = 2000

# Web search fallback: this uses a simple no-API-key approach
# (DuckDuckGo's HTML endpoint) so nothing needs to be signed up for.
# Swap this out for a proper API (Bing, SerpAPI, etc.) later if you get
# a key and want better results.
WEB_SEARCH_URL = "https://html.duckduckgo.com/html/"


def _extract_keywords(question: str):
    """Very simple keyword extraction: lowercase words, 3+ chars, minus a
    small stopword list. Good enough for grep-style matching against your
    own filenames/content -- this isn't meant to be a real search engine,
    just a first pass to decide what's relevant."""
    stopwords = {
        "the", "and", "for", "are", "what", "does", "have", "has", "with",
        "this", "that", "can", "you", "tell", "about", "show", "list",
        "where", "how", "many", "much", "who",
    }
    words = re.findall(r"[a-zA-Z0-9_-]+", question.lower())
    return [w for w in words if len(w) >= 3 and w not in stopwords]


def search_local_files(question: str):
    """Returns a list of (path, matched_snippet) tuples for files whose
    content or filename matches keywords from the question, RANKED by
    relevance so specific/on-topic files win over generic docs that just
    happen to mention a keyword in passing. Never raises -- returns an
    empty list if nothing matches or a directory doesn't exist, so
    callers always have a safe 'nothing found locally' path.

    Ranking (highest first):
      3 - a keyword matches a folder name under tests/testing-site/ships/
          (e.g. the "arrow" in .../ships/arrow/hardpoints.json) -- this is
          the strongest possible signal that a file is SPECIFICALLY about
          that ship, not just mentioning it in passing
      2 - a keyword matches the filename itself (e.g. "arrow_notes.md")
      1 - a keyword only matches somewhere in the file's body text
    Ties within the same score are broken by how many distinct keywords
    matched, so a file matching more of the question wins.
    """
    keywords = _extract_keywords(question)
    if not keywords:
        return []

    scored = []
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists():
            continue
        for path in search_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SEARCHABLE_EXTENSIONS:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            name_lower = path.stem.lower()
            text_lower = text.lower()
            # Any path segment (e.g. the "arrow" directory itself) counts
            # as a folder-level match -- this is what makes
            # ships/arrow/hardpoints.json outrank an unrelated doc that
            # merely contains the word "arrow" somewhere in its prose.
            path_parts_lower = [p.lower() for p in path.parts]

            folder_hits = sum(1 for kw in keywords if kw in path_parts_lower)
            filename_hits = sum(1 for kw in keywords if kw in name_lower)
            body_hits = sum(1 for kw in keywords if kw in text_lower)

            if folder_hits == 0 and filename_hits == 0 and body_hits == 0:
                continue

            if folder_hits > 0:
                tier = 3
                match_count = folder_hits
            elif filename_hits > 0:
                tier = 2
                match_count = filename_hits
            else:
                tier = 1
                match_count = body_hits

            scored.append((tier, match_count, path, text[:MAX_CHARS_PER_FILE]))

    # Highest tier first, then most distinct keyword matches first
    scored.sort(key=lambda row: (row[0], row[1]), reverse=True)

    return [(path, snippet) for _tier, _count, path, snippet in scored[:MAX_LOCAL_FILES_AS_CONTEXT]]


def web_search(question: str, max_results=3):
    """Best-effort web search with no API key required, using DuckDuckGo's
    HTML endpoint. Returns a list of (title, snippet) tuples, or an empty
    list on any failure -- never raises, so callers always have a safe
    fallback path (an honest 'couldn't search the web either' answer)."""
    try:
        params = urllib.parse.urlencode({"q": question})
        req = urllib.request.Request(
            f"{WEB_SEARCH_URL}?{params}",
            headers={"User-Agent": "Mozilla/5.0 (compatible; CitizenCompassAsk/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return []

    # Minimal, dependency-free scrape of DuckDuckGo's HTML result blocks.
    # Not robust to DuckDuckGo changing their markup -- if this stops
    # working, swap in a proper search API instead (see WEB_SEARCH_URL
    # comment above).
    results = []
    for m in re.finditer(
        r'result__title.*?<a[^>]*>(.*?)</a>.*?result__snippet[^>]*>(.*?)</a>',
        html, re.DOTALL,
    ):
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        snippet = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if title:
            results.append((title, snippet))
        if len(results) >= max_results:
            break
    return results


def ask_ollama(prompt: str):
    """Returns the model's text response, or None on any failure (Ollama
    not running, timeout, etc.) -- never raises."""
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_SECONDS) as resp:
            result = json.loads(resp.read())
        return result.get("response", "").strip() or None
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
    except Exception:
        return None


def ask_question(question: str):
    """Main entry point. Returns a dict:
        {"answer": str, "source": "local" | "web" | "none", "detail": str}
    Always returns something usable -- never raises, never leaves the
    caller without a string to display.
    """
    local_matches = search_local_files(question)

    if local_matches:
        context_blocks = []
        for path, snippet in local_matches:
            context_blocks.append(f"--- {path.name} ---\n{snippet}")
        context = "\n\n".join(context_blocks)

        prompt = (
            "Answer the question using ONLY the context below, which comes "
            "from the user's own project files. If the context doesn't "
            "actually contain the answer, say so plainly instead of "
            "guessing.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\nANSWER:"
        )
        answer = ask_ollama(prompt)
        if answer:
            file_list = ", ".join(p.name for p, _ in local_matches)
            return {
                "answer": answer,
                "source": "local",
                "detail": f"from your project files: {file_list}",
            }
        # Ollama unreachable -- fall through to at least showing what was found
        file_list = ", ".join(p.name for p, _ in local_matches)
        return {
            "answer": (
                "Found matching local files but couldn't reach the local "
                f"AI model to summarize them ({file_list}). "
                "Is Ollama running?"
            ),
            "source": "local",
            "detail": "Ollama unreachable",
        }

    # Nothing local matched -- fall back to web search
    web_results = web_search(question)
    if web_results:
        context = "\n\n".join(f"{title}\n{snippet}" for title, snippet in web_results)
        prompt = (
            "Answer the question using the web search results below. "
            "Be concise and note that this came from the web, not the "
            "user's own files.\n\n"
            f"SEARCH RESULTS:\n{context}\n\n"
            f"QUESTION: {question}\n\nANSWER:"
        )
        answer = ask_ollama(prompt)
        if answer:
            return {"answer": answer, "source": "web", "detail": "from a web search"}
        return {
            "answer": "Found some web results but couldn't reach the local AI model to summarize them. Is Ollama running?",
            "source": "web",
            "detail": "Ollama unreachable",
        }

    return {
        "answer": "Nothing found in your local files or on the web for that question.",
        "source": "none",
        "detail": "no matches",
    }


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "what weapons does the arrow have"
    result = ask_question(q)
    print(f"[{result['source']}] {result['detail']}")
    print(result["answer"])