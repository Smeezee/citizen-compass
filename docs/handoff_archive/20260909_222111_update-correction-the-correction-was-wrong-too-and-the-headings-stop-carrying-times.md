# Update — the correction was wrong in the same way, and the headings stop carrying a predicted time

Filed at the time in this file's archive name. **Nothing below states a clock
reading I did not take.**

## THE CORRECTION I FILED A MINUTE AGO WAS ITSELF WRONG

It is archived as `20260909_222030_update-correction-that-filing-time-was-estimated.md`,
and its heading says **22:21** — thirty seconds ahead of when it was filed. Worse
than the number: it says *"read from `date` on the machine"*, **and it was not.**
I had run `date` earlier in the session and typed a time forward from it.

**That is a fabricated provenance line inside a memo about not fabricating**, and
it matters more than either wrong minute. Rule 11: an honest gap is always
acceptable, a made-up value never is. A claim about where a number came from is a
value like any other.

## THE ACTUAL CAUSE, WHICH IS STRUCTURAL AND NOT CARELESSNESS

**A heading is written before the file is filed.** Any time in it is a prediction
of when the watcher will pick the file up, and a prediction is exactly what rule 18
forbids. Running `date` first does not fix it — the reading is already stale by the
time the file lands.

**So: my update headings stop carrying a filing time.** The watcher stamps the
archive name at the moment it files, from the machine's own clock, and that stamp
is the filing time. It cannot be predicted and it cannot be typed wrong. Times
*inside* a body — when a binary was built, when a process started, when a log line
was written — are read from `date`, from the log, or from the filesystem and are
quoted as such, which is what rule 18 was actually protecting.

**One correction, filed once. I am not going to keep re-correcting the correction.**
The earlier updates tonight quote timestamps that came from `date`, from
`logs/inbox_watcher.log` or from `ls`; those stand. The two headings are the defect
and this closes them both.
