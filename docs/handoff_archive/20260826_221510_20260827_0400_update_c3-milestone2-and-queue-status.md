# Update — C3 milestone 2, and where the queue stands

**2026-08-27 · Code** — progress update. Still working; not a stop.

## C3 milestone 2 - the definition tables are not where the documented order puts them

Milestone 1 verified `textLength` and located the string region
(44,288,701 - 61,454,626). This milestone tried to find the definition tables.

**First attempt looked like a success and was not.** Reading offset 116 as a
table of 16-byte rows, 97.9% of the first field's values "resolved to a string"
in the text region. That number is worthless: the values were 0, 6, 4, 12, 20 -
landing mid-word inside `TLAWPILOT1_CV_Taunt_IG_008_GeezWheredYou`. **In a
17 MB text region almost any offset resolves to something.**

So the test was made discriminating: a real name offset points at the START of
a string, meaning the byte before it is the previous string's terminator.

    random offsets                          1.75%   <- the baseline
    116, rows of 16 bytes                  13.2%
    116, rows of 32 bytes                  15.8%
    116, rows of 12 / 20 / 24 / 28 bytes   4.0-7.0%

A correct table would score near 100%. **None of these is the table.** Either
the tables do not begin at 116, or their first field is not an offset into this
region.

**What this milestone produces is a tool, not a schema:** a test that separates
a real table from a coincidence, with a measured baseline to judge against.
That is what the next pass should search with.

## Queue status

    1. A1/A2                    DONE   committed 5bdbdc4, deployed
    2. model inheritance        DONE   committed 6e25e27, deployed
    3. A3/A4                    DONE   committed a1b499a, deployed
    4. F3 real-browser control  DONE   committed dbdc538
    5. C5 + C5b                 DONE   committed ac99c7b, 14 assertions
       C6 acquisition           IN FLIGHT - cloning, 969 MB of ~6 GB
    6. C3                       milestone 1 committed 6f755b9, milestone 2 above

**Item 5 is gated on the clone**, which is running in the background with a
watcher on it. Everything else in the queue that can be done without it has
been.

Preconditions for the acquisition were checked before it started, as the
procedure demands: git-lfs 3.7.1 confirmed **before** cloning, 512 GB free,
Defender's scanner present for gate 4.

Still to do when it lands: capture git metadata **before** stripping `.git`,
then the five gates in order, malware scan before the rename out of `.partial`,
re-hash after, and rename only when all five pass. **The new snapshot will not
be promoted** - the site keeps serving `20260801T204744Z` and keeps saying 4.9.

Then C5 runs on the pair. Five weeks between two 4.9 builds should be a small,
boring diff; if it comes back with hundreds of changes or none at all, that is
the tool and not the data, and I will say which before drawing any conclusion.
