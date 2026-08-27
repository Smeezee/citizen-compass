# ALERT — GitHub will limit the project account on 2026-09-30 unless 2FA is enabled. Enabling it will ALSO break every stored git password on the machines, and that is the part nobody will see coming.

    from      C3 (Cowork), 2026-08-16
    for       C1 -> Code, and Sleven
    source    email to Sleven from "GitHub", received 2026-08-16 12:14, read from
              a screenshot he provided. Transcribed in §5.
    deadline  2026-09-30 00:00 UTC - 45 days from the email
    account   the GitHub handle addressed is "Smeezee"

---

## 1. What the email says

GitHub has begun requiring two-factor authentication for accounts that contribute
code. Sleven's account meets the criteria. He has **45 days, until 2026-09-30
00:00 UTC**. After that, *"your access to GitHub.com will be limited until you
enroll in 2FA."*

Offered methods, in the email's own order: **TOTP apps and SMS first, then
passkeys and the GitHub Mobile app.**

## 2. VERIFY IT FROM GITHUB, NOT FROM THE EMAIL

**I cannot confirm this email is genuine from a screenshot, and a 2FA notice with
an enrolment link is the exact shape a phishing message takes.** The policy is
real — GitHub has been rolling this out to contributing accounts — but that does
not make any individual email real.

**Do not click the link in the email.** Type the address in directly:

    github.com/settings/security

**If the requirement is real it will be stated there, on the account's own
settings page, with the same deadline.** If it is not there, the email was not
from GitHub and nothing needs doing.

This costs thirty seconds and it settles it.

## 3. THE PART THAT WILL BREAK THIS PROJECT — read this before enrolling

**Turning on 2FA immediately invalidates password authentication for git over
HTTPS.** Any machine that pushes using a stored GitHub *password* stops working
the moment 2FA is switched on. Not on the deadline — **the moment it is enabled.**

This project pushes from at least Sleven's machine, and the collector's releases
are published to GitHub. **A push that starts failing mid-session, right after an
unrelated settings change, is a genuinely confusing failure**, and it will look
like a git problem rather than an auth problem.

**So the order matters:**

    1. confirm the requirement on github.com/settings/security
    2. create a Personal Access Token, or switch the remote to SSH
    3. update the stored credential on every machine that pushes
    4. THEN enable 2FA
    5. test one push before assuming it is done

**Doing step 4 first turns a scheduled task into an emergency.**

## 4. What is NOT affected

**The collector's update feed and public downloads are unaffected.** Those are
anonymous reads of a public release — no login, no token. Contributors who
downloaded the collector will keep getting updates whatever happens to the
account.

**The live site is unaffected.** It deploys from Netlify.

**The risk is confined to pushing, publishing releases, and anything that
authenticates as the account.**

## 5. Transcription, for the record

> Hey Smeezee!
>
> We're reaching out to let you know that, as announced last year, we have
> officially begun requiring users who contribute code on GitHub.com to have
> two-factor authentication (2FA) enabled.
>
> Your account meets this criteria, and you will need to enroll in 2FA within 45
> days, by September 30th, 2026 at 00:00 (UTC). After this date, your access to
> GitHub.com will be limited until you enroll in 2FA. Enrolling is easy, and we
> support several options, starting with TOTP apps and text messages (SMS) and
> then adding on passkeys and the GitHub Mobile app.
>
> Making the software supply chain more secure is a team effort, and we can't do
> it without you. [...] To see this and other security events for your account,
> visit your account security audit log.
>
> Thanks,
> The GitHub Team

## 6. One recommendation, and it is Sleven's call

**Prefer a TOTP app or a passkey over SMS.** SMS 2FA can be defeated by a SIM
swap, and this account can publish software that other people download and run —
his wife's machine and his friend's machine already run it. **The account is a
software distribution channel now, not just a code store**, and that raises what
a takeover would cost.

**Also worth doing while he is in there: save the recovery codes somewhere that is
not the same phone.** Losing the second factor with no recovery codes locks the
account out permanently, and every release the collector auto-updates from lives
behind it.

## 7. What I checked and what I did not

**Checked:** nothing. **This is a transcription of a screenshot plus the known
consequences of enabling 2FA on a git remote.**

**Did NOT check:**
- **Whether the email is genuine.** §2. Nobody should act on it without loading
  github.com directly.
- **Which machines have a stored GitHub credential, or whether they use HTTPS or
  SSH.** That determines how much of §3 applies and it needs someone at the
  machines. **If the remotes are already SSH, §3 is a non-issue** — worth
  establishing before anyone plans work around it.
- Whether the account has any other collaborators who would also be affected.
