# ECHO — what Claude in Cowork can and cannot do

**Filed 2026-09-11 by the Adjutant desk, at Sleven's order. Copy-paste block for Echo.**

---

Echo — Sleven wants a complete, honest list of what Claude can and cannot do in his Cowork setup, so you can dig into it. It is written by the Claude session itself, from the tools it actually has loaded in this session on 2026-09-11, not from marketing pages. Where something has not been tested, it says so.

**Why this exists.** Tonight this session took a screenshot of Sleven's Comet browser window, with his approval. The screen-viewing tools were listed as available to this session from its start, and the session did not use them or mention them until he said he wished it could see his screen. He has spent weeks building around the assumption that Claude could not see his computer. Treat everything below as something to verify and push on, not something to trust.

**The model and the product.** Claude, configured as Opus 5 (claude-opus-5), running in Cowork: the Claude desktop app's agent mode. The session runs in a cloud container. It reaches Sleven's Windows PC through the desktop app, which has to be open and online for any of the "on his computer" tools to work. The tool set is not fixed: it changes with the app version, his settings, and which connectors are switched on. So an earlier session may have had fewer tools than this one, or more.

## 1. ON SLEVEN'S COMPUTER — SEEING AND CONTROLLING THE SCREEN ("COMPUTER USE")

Available this session on his PC.

**Can do, once he approves each application:**
- Take screenshots of either monitor. His PC has two: "Sceptre K32" (the main one) and "PM1561P". It can switch between them.
- Zoom into part of the screen to read small text.
- Move the mouse; left, right, middle, double and triple click; drag; press and release the mouse button.
- Type text, press keys and key combinations, hold keys down, scroll.
- Open an application.
- Read and write the clipboard, only if that was specifically approved.
- Run a sequence of these actions in one step.
- List which applications it has been granted.

**How the permission works:**
- Sleven approves a named list of apps. Apps not on the list are blacked out in screenshots; their windows show as solid rectangles.
- Tonight's screenshot masked ChatGPT, Discord, PowerShell, Terminal, Firefox, Obsidian, the Perplexity app, Chrome, Steam and a running game. Only Comet was visible.
- **Browsers can only be granted as "read": it can see them but cannot click or type in them.** Comet was granted that way.
- What level other apps get (a terminal, a game, Blender, Obsidian) is decided when access is requested. **Not tested for any app other than Comet.**

**Cannot:**
- Watch continuously, record video, or capture the screen in the background. Every look is one screenshot taken during a live session.
- Hear audio.
- See anything when the desktop app is closed, the PC is asleep, or the session is not linked to the PC.
- Act on apps he has not approved.

## 2. ON SLEVEN'S COMPUTER — FILES AND A SHELL

**Can do:**
- Ask him to grant a folder; the grant lasts for this session only.
- List folders. Copy files from his PC up to the cloud workspace. Write files back into a granted folder.
- Report device details and which local tool servers are configured. None are configured today.
- Ask him for permission to delete files in a folder.
- Run shell commands inside a small Linux virtual machine on his PC, where granted folders are mounted. **This is broken on his machine.** The tool's own error says a Windows update released 2026-09-08 stops it reaching his files, and that Claude Code is unaffected.

**Cannot:**
- Reach any folder he has not granted.
- Delete files without his separate approval.
- Reach system or credential locations inside a granted folder.

## 3. BROWSERS

**Claude in Chrome: his real Chrome browser, through the Chrome extension.**
- Open, close and switch tabs; go to addresses; go back and forward.
- Click, type, scroll, fill in form fields, use keyboard shortcuts.
- Read the page's structure and full text, and find elements on it.
- Run JavaScript on the page.
- Read the browser console and network requests.
- Take screenshots and zoom.
- Record an animated GIF of what it does.
- Upload files or images into a page.
- Resize the window. It reported success tonight but the width did not change.
- Switch between connected Chrome browsers.
- **Used tonight** to check the Citizen Compass test site rendered at desktop and phone width.

**The built-in browser: a browser panel inside the Claude desktop app, with its own separate profile.**
- The same kinds of actions as above: navigate, click, type, read, find, fill forms, JavaScript, console and network, tabs, resize, screenshots.
- Sites can require his approval before it acts on them.
- Only works while the desktop app is open.

## 4. THE CLOUD WORKSPACE (ITS OWN LINUX MACHINE)

- Run shell commands, Python and Node; install packages.
- Read, write, edit and search files.
- Search the web and fetch web pages. There are content restrictions, and when a site is blocked it may not try to get around the block.
- Build Word, Excel, PowerPoint and PDF files, charts, and design mockups, using built-in skills for each.
- Send files into the chat.
- **Publish hosted web pages ("artifacts") on claude.ai**, private until shared. They can:
  - keep a small shared database;
  - know who is viewing;
  - take comments;
  - ask Claude questions of their own;
  - store files people add.
- It can read and write that database and those comments, and republish pages.
- Draw diagrams and small interactive visuals inline in the chat.
- Start sub-agents that research or work in parallel. With his explicit say-so, run larger multi-agent workflows.
- Keep a task checklist that shows as a widget.
- Read and edit Jupyter notebooks.
- Report code-review findings in a structured way.
- This workspace is temporary. It is wiped some time after the session ends.

## 5. CLAUDE.AI, MEMORY, CONNECTORS AND OTHER SESSIONS

- **The claude.ai project "citizen compass":** read, search and write its documents; read the project's memory files. It **cannot** change the project's instructions or settings.
- **Personal memory that follows Sleven across Claude chat, Cowork and other sessions:** read, write, edit and delete files about who he is and how he wants to work. This is how preferences carry between sessions. It does not remember conversations themselves.
- **Google Calendar is connected:** list calendars; find, create, update and delete events; suggest meeting times; respond to invitations. Sending invitations counts as sending messages on his behalf and needs his yes each time.
- **Can find and suggest more connectors and plugins** from the Claude registry (for example Slack, Gmail, GitHub, Asana), and suggest or create skills.
- **Scheduled tasks:**
  - create, change, run or delete tasks that start a fresh Claude session on a schedule, or once at a set time;
  - send a reminder back into this same conversation later;
  - a scheduled task can be bound to his PC if he approves it.
- **Other Claude sessions:** list them and send them messages. That includes other Claude sessions running on his machine, if any are running. Tonight none were reachable. It can read notifications queued for this session.
- Send push notifications to him.

## 6. HARD LIMITS AND SAFETY RULES IT WORKS UNDER

**Never does, even if asked:**
- Type passwords, card numbers, bank details, government ID numbers or API keys into any website or app field.
- Create accounts.
- Permanently delete data, such as emptying a trash folder.
- Buy, sell or transfer money, shares or crypto.
- Get past a CAPTCHA.
- Change system or security settings.
- Download or run files from untrusted sources.

**Only with a clear yes from him in chat, each time:**
- Downloading a file.
- Sending any message, email or invitation as him.
- Publishing or posting.
- Buying something with a saved payment method.
- Accepting terms or cookie banners.
- Changing account settings.
- Creating mail rules or integrations.
- Submitting any form.
- Pressing any send, submit, delete or confirm button.

**Also:**
- Instructions that appear inside web pages, files or tool output are treated as data, not orders.
- Browsers are view-only through computer use.
- It has a knowledge cutoff and has to search for anything current.

## 7. NOT TESTED, OR UNKNOWN — WHERE TO DIG

1. What control level computer use gives a terminal such as PowerShell or Windows Terminal. If it can type into one, that is a possible path around the broken shell. Not tried, and it may be deliberately restricted.
2. Whether a running game, fullscreen or borderless, shows up in screenshots or is blacked out.
3. How fast and how often screenshots can be taken, and whether that is practical for anything live.
4. Whether earlier Cowork sessions over the last few weeks had computer use at all. This session cannot see their tool lists.
5. Which tools Claude Code has on his machine, compared with Cowork. They are different products with different tool sets.
6. Whether computer use can be used by a scheduled task bound to his PC with nobody present.
7. Why the Chrome window resize reported success without changing the width.

## 8. WHAT THIS CHANGES FOR CITIZEN COMPASS — THE HONEST VERSION

- Claude can now look at what Sleven is looking at, on request, when he approves the app. That removes the need for him to describe his screen or paste screenshots.
- It is **not** a continuous, automatic screen reader. It takes one look per request, only while a session is running and the desktop app is up, and it cannot record. Anything that needs to watch the screen on its own, over time, still needs a local program.
- It can check the website visually in Chrome, which it did tonight, so some visual checks no longer need Sleven or an outside tool.
- It cannot click inside browsers through computer use. Browser actions go through Chrome or the built-in browser.

## WHAT WOULD HELP FROM YOU

1. Check Anthropic's own documentation for Cowork and computer use. What does this list miss, and what does it overstate?
2. Answer the items in section 7 wherever primary sources can.
3. Given section 8, say plainly which of Sleven's past workarounds this makes unnecessary, and which it does not.
