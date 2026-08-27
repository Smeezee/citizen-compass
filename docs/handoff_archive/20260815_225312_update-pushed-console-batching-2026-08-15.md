# Update: pushed `33a9c6a`. No release cut.

`2e1589d..33a9c6a`. `origin/main` is now `33a9c6a`, nothing unpushed.

Checked before pushing: the commit touches **no** `releases/` path. Confirmed
after, over the network - the published feed still reads **0.3.2**, and the tags
are unchanged. **Nothing reaches Sleven's wife or his friend.** They stay on
0.3.2, which is the build before tonight's console fix, the batched send and the
WebView2 removal.

That gap is now meaningful and worth stating plainly: **the published 0.3.2 is a
CONSOLE build.** Anyone who installs it gets the black box, and closing it kills
their collector. Cutting 0.3.3 is the thing that fixes that for them, and it has
not been asked for.
