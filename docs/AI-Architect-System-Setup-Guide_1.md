# AI Architect System — Full Setup Guide (Detailed)

This assumes you're on Windows. Every step tells you exactly what to click or type — nothing is assumed.

---

## Part 0 — Two things you'll use constantly

**File Explorer** — the folder/file browser (the icon that looks like a folder in your taskbar).

**PowerShell** — a black/blue window where you type commands. To open it:
- Click the **Start button** (Windows icon, bottom left)
- Type `PowerShell`
- Click **Windows PowerShell** when it appears in the list

Keep that window open as you go — you'll type commands into it throughout this guide.

---

## Part 1 — Install Ollama

1. Open a web browser, go to **https://ollama.com**
2. Click the **Download** button, then **Download for Windows**
3. Open the downloaded file (usually in your **Downloads** folder — double-click it)
4. Click through the installer (Next → Install → Finish). No settings to change.
5. Open PowerShell (see Part 0 if you need a reminder).
6. Type this exactly, then press **Enter**:

```powershell
ollama pull qwen3:14b
```

Wait for it to finish downloading (you'll see a progress bar in the PowerShell window). This can take a while — the file is several gigabytes.

7. Once that finishes, type this and press **Enter**:

```powershell
ollama pull qwen3-coder:30b-a3b
```

8. Once that finishes, type this and press **Enter**:

```powershell
ollama pull qwen2.5:7b
```

9. When all three are done, type this and press **Enter** to confirm they installed:

```powershell
ollama list
```

You should see all three names listed. If you do, Part 1 is complete.

---

## Part 2 — Create your project folder

1. Open **File Explorer**.
2. Click on **Documents** in the left sidebar.
3. Right-click in the empty white space on the right → **New** → **Folder**.
4. Type a name for it: `AIArchitectSystem`, then press **Enter**.
5. Double-click that new folder to open it. You should now be looking at an empty folder. Keep this window open.

---

## Part 3 — Put the docker-compose.yml file into that folder

1. Find the **docker-compose.yml** file I gave you earlier (it's likely in your **Downloads** folder — open File Explorer, click **Downloads** in the left sidebar to check).
2. Click once on the file to select it.
3. Press **Ctrl+X** on your keyboard (this "cuts" it, ready to move).
4. Go back to the **AIArchitectSystem** folder window from Part 2.
5. Press **Ctrl+V** (this pastes/moves the file into that folder).
6. Confirm you now see `docker-compose.yml` sitting inside the `AIArchitectSystem` folder.

Do the exact same thing for **mcpo-config.json** later, in Part 7 — for now, just docker-compose.yml.

---

## Part 4 — Edit one line in docker-compose.yml

1. Right-click on `docker-compose.yml` (inside the AIArchitectSystem folder).
2. Click **Open with** → **Notepad**. (If Notepad isn't listed, click "Choose another app" and pick Notepad.)
3. Find the line that says:

```
WEBUI_SECRET_KEY=change-this-to-a-long-random-string
```

4. Replace `change-this-to-a-long-random-string` with any long random text of your own — for example a random sentence with no spaces, like `myPurpleServer2026DoesNotSleep`. It doesn't need to be memorable, just long and only used here.
5. Press **Ctrl+S** to save. Close Notepad.

---

## Part 5 — Install Docker Desktop

1. Go to **https://www.docker.com/products/docker-desktop** in your browser.
2. Click **Download for Windows**.
3. Open the downloaded installer file, click through it (Next → Install), leave every checkbox at its default setting.
4. It will ask you to restart your computer — do that.
5. After restarting, Docker Desktop should open on its own (a whale icon appears in your system tray, bottom-right near the clock). If it doesn't open automatically, click Start, type `Docker Desktop`, and open it.
6. Wait until the whale icon stops animating — that means Docker is fully started.
7. Click the **gear icon** (Settings) inside Docker Desktop.
8. Click **General** on the left.
9. Make sure **"Start Docker Desktop when you log in"** is checked (turned on).
10. Click **Apply & Restart** if it asks you to.

---

## Part 6 — Launch Open WebUI

1. Open PowerShell (Part 0 reminder: Start → type PowerShell → Enter).
2. You need to move into your project folder. Type this exactly, then press **Enter**:

```powershell
cd "$env:USERPROFILE\Documents\AIArchitectSystem"
```

3. Now type this and press **Enter** — this reads your docker-compose.yml file and starts everything it describes:

```powershell
docker compose up -d
```

4. You'll see some text scroll by (this is normal — it's downloading the Open WebUI program the first time, which can take several minutes).
5. When it finishes and gives you your PowerShell prompt back (a blinking cursor, no more scrolling text), open your web browser and go to:

```
http://localhost:3000
```

6. Open WebUI should load in your browser. The first time, it will ask you to create an account (name, email, password) — this account is just for your own computer, it doesn't go anywhere online. Create it and log in.

**If the page doesn't load:** wait 30 seconds and refresh — the container can take a moment to finish starting after the command finishes.

---

## Part 7 — Connect the filesystem tool

1. In File Explorer, go to your **Downloads** folder, find **mcpo-config.json**.
2. Cut it (Ctrl+X) and paste it (Ctrl+V) into your `AIArchitectSystem` folder — same move as Part 3.
3. Right-click `mcpo-config.json` → **Open with** → **Notepad**.
4. Find this line:

```
"C:\\Users\\YOUR_USERNAME\\Documents\\CitizenCompass"
```

5. Replace `YOUR_USERNAME` with your actual Windows username. (Not sure what it is? In PowerShell, type `whoami` and press Enter — it shows `computername\yourusername`, use the part after the backslash.)
6. Replace `CitizenCompass` with the actual folder name of your website project, or leave it if that's already correct.
7. Save (Ctrl+S) and close Notepad.
8. Install Node.js: go to **https://nodejs.org**, click the button for the **LTS** version, run the installer, click through it (Next → Install), restart your computer once it's done.
9. Open a **new** PowerShell window (close the old one, open a fresh one so it recognizes the new install).
10. Type this and press Enter to install a small tool called `uv`:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

11. Close that PowerShell window, open a new one again.
12. Move into your project folder again:

```powershell
cd "$env:USERPROFILE\Documents\AIArchitectSystem"
```

13. Start the tool server:

```powershell
uvx mcpo --port 8100 --config mcpo-config.json
```

14. Leave this PowerShell window **open and running** — don't close it, it needs to stay active. (Later, we can set this up to start automatically, but for now just leave the window open whenever you want file access to work.)
15. Go back to your Open WebUI browser tab. Click your profile icon (bottom-left) → **Admin Panel** → **Settings** → **External Tools**.
16. Click the **+** button to add a server.
17. Set **Type** to `OpenAPI`, set **URL** to `http://localhost:8100`.
18. Click **Save**.

---

## What "done" looks like right now

- Typing `ollama list` in PowerShell shows your 3 models
- `http://localhost:3000` loads Open WebUI and you can log in
- A PowerShell window is running `uvx mcpo...` and Open WebUI's External Tools shows it connected

Once you've confirmed all three of those, tell me and I'll walk you through Part 8 onward (Blender, the coding worker, and getting your phone connected) with this same level of detail.
