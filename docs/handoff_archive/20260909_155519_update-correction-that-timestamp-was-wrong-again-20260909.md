# Update — CORRECTION: I did it again, four minutes out, and here is the actual fix

**Filed 2026-09-09 15:53 CDT — and this line was produced by `date`, not typed.**

The update filed at 15:52:57 carries the header **"2026-09-09 15:56 CDT"**. The
real time was **15:52:57**. Out by four minutes.

**I did run `date` — and then typed a different number.** The command printed
`Wed Sep 9 15:52:57 CDT 2026` and I wrote 15:56 into the heredoc in the same
breath, because the heredoc's text was composed before the clock's answer came
back. Running the clock and then not reading it is not better than not running it.

**This is the second time today**, after the four estimated stamps corrected
earlier. A rule I have now broken twice in one session is not a rule I am
applying — it is one I keep intending to apply.

## THE ACTUAL FIX, WHICH IS MECHANICAL RATHER THAN A PROMISE

The previous correction ended with *"`date` runs immediately before any update
that states a time."* **That was the wrong fix**: it addressed when I look at the
clock and not whether the number reaches the page. Both failures today were
transcription, not ignorance.

So, from here: **the timestamp is substituted by the shell and never typed.**

    NOW=$(date "+%Y-%m-%d %H:%M %Z")
    cat > inbox/update-....md <<EOF
    **Filed $NOW**
    ...

The header of THIS file was produced that way. There is no number in it I could
have got wrong, because there is no number in it I wrote.

**Rule 26's standing obligation, applied to my own hands:** every time a
repeatable manual step is found, the question is how to remove it permanently.
The step was "read a clock and copy a number accurately", and I have now failed
it twice. It is removed rather than promised.

Nothing else in the 15:52:57 update is affected — every measurement in it came
from a command that ran.
