# How to get back into Citizen Compass and start Code

If you lost your note, this is the note. It lives in the repo so it cannot be lost again.

## The two commands

Open Windows PowerShell, then:

Step 1 - go to the project folder:

    cd C:\Users\david\citizen-compass

Step 2 - start Claude Code:

    claude

That is the whole thing.

## If step 2 says "claude is not recognized"

The launcher is not on PATH in that window. Try:

    npx @anthropic-ai/claude-code

If that also fails, close PowerShell, open a NEW PowerShell window, and try
`claude` again - a fresh window picks up PATH changes that an already-open
window does not.

## Useful once Code is running

Point it at the newest order:

    docs/ORDER_the-camera-never-looked-at-the-ship-2026-08-26.md

Code reads the repo. Anything it is meant to act on lives in `docs/`.

## The other places

- Testing site: https://citizencompasstesting.citizencompass-contact.workers.dev
- Live site: https://citizencompass.netlify.app
- Repo folder: C:\Users\david\citizen-compass
