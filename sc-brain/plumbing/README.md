# Plumbing

State files, indexes, and tiny local tools that make SC Brain easy to get.

## Tools (free, local, no AI)
| Command | What |
|---|---|
| `python sc-brain/plumbing/ask_sc_brain.py shelves` | List shelves |
| `python sc-brain/plumbing/ask_sc_brain.py recent` | What’s new log |
| `python sc-brain/plumbing/ask_sc_brain.py find WORD` | Search under sc-brain |
| `python sc-brain/plumbing/ask_sc_brain.py tree` | Folder tree |
| `python sc-brain/plumbing/append_index.py SHELF "summary" [ref]` | Append to latest.md |
| `python sc-brain/plumbing/sync_roadmap_pointer.py` | Point roadmap shelf at watcher state |

## Layout
- `indexes/latest.md` — append-only change log
- `state/` — watcher state copies / markers (RSI watcher will use)
