CITIZEN COLLECTOR
Written for whoever is about to run this, not for the person who built it.


WHAT IS THIS

Star Citizen writes a diary of your session to a file on your computer.
It always has. Nobody reads it.

This program reads it, pulls out the useful facts - what a shop charged,
what ships were nearby, where you went - and keeps them in one tidy file.
When you feel like it, you press a button and it packages that file up so
you can send it to Sleven, who is building a free reference site out of it.

That is the whole thing.


WHAT IT DOES NOT DO

  - It never sends anything on its own. Not on a timer, not in the
    background, not when you are not looking. The only thing that sends
    anything is you pressing the button, and it asks what to include
    before it does.
  - It does not read any window except Star Citizen's. It checks the
    window belongs to the game before it looks.
  - It does not read chat. Not filtered, not scrubbed - never sampled.
  - It does not touch the game. No mods, no injection, no reading the
    game's memory, no pressing keys for you. It only reads a text file the
    game already wrote and takes ordinary screenshots.


THE FIRST TIME YOU RUN IT

It asks. Say no and it exits without reading anything.


HOW TO RUN IT

  1. Unzip it somewhere you will find it again.
  2. Double-click collector.exe.
  3. Play.

There is nothing to install. No runtime, no setup, no admin password.

On most machines it opens its own little window. On some it opens as a tab
in whatever browser you already use instead - same buttons, same everything.
You are not doing anything wrong if you get the tab; it just means Windows
did not have the bit it needed for a window, so it used the browser you
already had. Leave the tab open while you play.

The window can be minimised. It follows the game: when Star Citizen closes,
it stops.

To stop it entirely, close the window. To remove it, delete the folder.
Nothing is installed and nothing is left behind.


SENDING YOUR DATA

Press SEND MY DATA. It tells you what it is about to package - how many
rows, how many screenshots - and gives you three buttons: data only,
data and pictures, or cancel. Cancel writes nothing.

Before anything is packaged:

  - Player names are replaced with anonymous tags. Yours and everyone
    else's. The same person always gets the same tag, so the data still
    makes sense, but the names are gone.
  - Screenshots are NOT included unless you choose them, and they are NOT
    covered by that name-swapping. A picture of your screen shows whatever
    was on your screen - your handle, anyone standing near you, your party
    list. Choose accordingly.
  - There is a README inside the zip listing exactly what is in it.

If a send address has been set up, the same button uploads it and then
tells you it arrived. If it has not, the zip just lands next to the
program and the folder opens - it is yours to send by hand or delete.

Either way nothing is cleared off your disk until the far end has confirmed
it received a byte-for-byte identical copy. If anything goes wrong you keep
everything.


A NOTE ON WHAT IS KEPT LOCALLY

The file on your own disk holds the real names it saw in the game log,
including other players'. That is deliberate - it is how the name-swapping
gets checked and improved. That file never leaves your computer on its own,
and the swapping happens before anything is packaged to go anywhere.


THE ID FILE

collector-install-id.txt holds 16 random bytes. That is all it is. It is
not built from your name, your handle, your Windows account or anything
about your computer, and it cannot be turned back into you.

It exists so that if you and somebody else both report a price of 1,000 for
copper, that counts as two people agreeing rather than one report counted
twice. Delete it any time; a new one gets made.


IF SOMETHING LOOKS WRONG

collector-auto.log, in the same folder, is a plain text diary of what the
program did. It is readable. If something seems off, that file will say so
in words.


WHO TO ASK

Sleven. He built it, he is the only person who gets your file, and he is
the one to tell if you want your contributions removed.


IF IT SAYS THERE IS AN UPDATE

It checks whether a newer version exists and says so in the window. It does
not install anything unless you click the button. When you do, it checks the
download against a fingerprint published alongside it and throws it away if
they do not match.
