# ECHO — what actually stops a runaway. Outside research, 2026-09-10.

    source     Echo, an outside AI with no mailbox. Carried in by Sleven.
    asked for  what real systems use to stop a runaway, and which controls
               experienced operators reach for FIRST. Practice, not theory.
    status     NOT ADOPTED. Verbatim below. Architecture tears into it.
    labels     Echo's own: ESTABLISHED = primary-source doc or reported operating
               practice. INFERENCE = its recommendation from that evidence.
               GUESS = unmeasured prediction or initial tuning value.

---

## ECHO'S REPLY, VERBATIM

Sir, **the practical first controls are admission limits, bounded executions, and an
independently operable stop switch.** Circuit breakers come later: they usually detect
failures or overload, while your most dangerous runaway can remain completely
successful.

**Your main gap is aggregate allowance protection.** Twenty capped runs are not
necessarily affordable runs. Without a trustworthy relationship between each run's
limit and subscription allowance consumption, the current controls reduce risk but
cannot guarantee that the account lasts through the day.

### 1. THE CONTROLS THEMSELVES

All examples are **established implementations**, not recommendations to install those
systems.

**Admission control and aggregate quotas** — Kubernetes rejects resource creation that
would violate quota: *"the control plane rejects that request"*. Stops work entering
when its declared demand exceeds the shared allowance.

**Concurrency limits and bulkheads** — Resilience4j semaphore and thread-pool
bulkheads *"limit the number of concurrent execution"*. Stops too many simultaneous
operations, and one workload occupying all capacity.

**Reserved capacity** — Lambda reserved concurrency *"acts as both a lower and upper
bound"*. Stops other workloads consuming reserved capacity; also caps the reserved
workload.

**Token-bucket rate limiting** — API Gateway *"throttles requests … using the token
bucket algorithm"*. Stops excess sustained rate while permitting a burst.

**Leaky-bucket limiting** — NGINX uses the *"leaky bucket"* method, delaying excess and
rejecting overflow. Stops bursts arriving faster than a service can process.

**Circuit breakers** — Resilience4j opens after configured failure or slow-call rates,
then permits limited recovery probes. **Does not inherently detect successful,
pointless repetition.**

**Retry budgets and adaptive throttling** — AWS SDKs limit retries with a quota;
adaptive mode also rate-limits initial requests. Stops retry amplification.

**Load shedding and priority** — Google documents rejecting lower-criticality requests
first as resources become scarce.

**Absolute deadlines and attempt limits** — Kubernetes Jobs use `activeDeadlineSeconds`
and `backoffLimit`; **the deadline takes precedence over retries.**

**Internal iteration limits** — Claude Code's `--max-turns` limits agentic turns in
print mode and exits with an error. Stops one session reading and reasoning forever
without handing off.

**Causal-chain limits** — Lambda tracks invocations from the same event and stops a
recursive chain after ~16. **Stops a loop whose individual executions are all valid and
successful.**

**Poison-message isolation** — SQS `maxReceiveCount` before dead-letter handling.

**Kill switches and operational flags** — LaunchDarkly calls these *"permanent safety
mechanisms"*. **Stops new activity through paths that check the flag. A flag alone does
not terminate existing work.**

**Watchdog / dead-man monitoring** — kube-prometheus ships an always-firing Watchdog
alert to prove *"the entire alerting pipeline is functional"*. **Its disappearance is
the failure signal.** Automatic stopping requires an attached action.

**Preventive budget caps** — BigQuery checks estimated bytes against a per-query
maximum before execution; an oversized query fails without charge.

**Budget-triggered automatic actions** — AWS Budgets can apply restrictions after a
threshold — subject to reporting and action delays.

#### THE CAVEAT ECHO PUTS ON ALL OF IT

**The name does not establish the guarantee.** API Gateway says its throttles and
quotas are **best-effort targets**. BigQuery says its aggregate custom quotas are
**approximate**. AWS Budgets warns usage can exceed the threshold before notification.

#### THREE IT SAYS WE ARE MISSING

    duplicate-start suppression   repeated observation of the same pending visit
                                  must not start another session
    bounded pending work          stop admitting when backlog exceeds what can be
                                  serviced; preserve existing letters
    an allowance schedule         a daily quota limits total starts and reserves
                                  nothing for the afternoon

### 2. WHAT OPERATORS ACTUALLY DEPLOY FIRST

**Established limitation, and it refused the question as asked:** *"I found
implementation defaults and first-hand operating descriptions, not a representative
survey. There is no defensible '90% of teams' or '90% of protection' figure here."*

    ROUTINE FOUNDATIONS        timeouts, max attempts, concurrency limits, rate
                               limits — built into ordinary SDKs and job runtimes
    SHARED-SERVICE FOUNDATIONS aggregate quotas, reservations, admission control,
                               priority shedding
    DEPENDENCY-SPECIFIC        circuit breakers, adaptive throttling — need signal,
                               volume and tuning
    WORKLOAD-SPECIFIC          recursion limits, poison-message handling, semantic
                               progress checks

**Direct evidence of what an operator reaches for during a real runaway:** AWS's Lambda
guidance says to **reduce available concurrency to zero** and disable the triggering
source. **That is stopping admission, before diagnosing the loop.**

**Its ranked build order:**

    1  make stopping reliable      a global automatic-session limit, initially ONE,
                                   and an independent emergency stop that TERMINATES
                                   running sessions
    2  protect the allowance       reserve capacity for the Owner and for already-
                                   admitted work before allowing another run
    3  bound each execution        keep the existing caps; add a turn limit, an
                                   absolute deadline, and a small retry allowance

#### WHICH CONTROLS GET SWITCHED OFF AFTER FIRING ON HONEST WORK

It would not put numbers on this either. The documented tuning hazards:

**Circuit breakers** — failure classification and minimum sample size matter; a large
minimum may never fire at our volume. **Timeouts** — Google notes short deadlines make
expensive requests fail consistently. **Adaptive throttling** — AWS warns a shared
client can make one resource's throttling slow unrelated requests. **Burst limits** —
NGINX provides a dry-run mode that counts excess without restricting, so you can
observe before enforcing.

**And the one aimed straight at us:** *"automatic semantic 'no progress' detectors are
especially vulnerable to being distrusted here, because they must distinguish
legitimate investigation from repetition. Use them as advisory evidence; retain
deterministic ceilings underneath."*

### 3. THE LOOP THAT IS LEGAL AT EVERY STEP

**Lambda's recursion protection is the relevant prior art.** It propagates event
lineage and an invocation count. **The decisive condition is repeated execution within
the same originating chain — not whether each invocation reported an error.**

**Our permanent job number and delivery ceiling are already the inexpensive
equivalent.**

**A legal loop evades:** error-rate circuit breakers; retry budgets, if each handoff
counts as fresh successful work; idle watchdogs, if it keeps producing output;
short-window limits, if it circulates slowly; poison-message handling, if every message
processes successfully.

**Its answer to the question I actually asked:** *"Yes: without an independently
checkable definition of progress, a hard cumulative ceiling is the dependable detector.
It detects excessive repetition, not whether the repetition was intellectually
justified."*

**Three places the ceiling has to apply:**

    between desks under one job    cumulative deliveries — we have this
    inside one session             agentic turns, total runtime, per-run cap
    across fresh or resumed jobs   aggregate allowance; derived work must not get
                                   unlimited fresh entitlement

**And the trap:** *"Do not let 'successful completion' replenish the cumulative job
allowance. That would make a success-producing loop self-funding."*

### 4. RATE VERSUS TOTAL

**Real systems use both.** API Gateway usage plans combine request throttling with
aggregate quotas, as separate settings, because they protect different dimensions.

    daily total only        permits spending the whole day's entitlement at once
    short-window rate only  permits continuing at that rate indefinitely
    concurrency only        permits serial consumption forever
    per-run cap only        permits many permitted runs exhausting the resource

**On our own numbers:** five starts per fifteen minutes is a burst allowance, not a
day-long pacing policy. **Twenty starts can be admitted in four batches a little over
fifteen minutes apart — roughly 45 minutes from first batch to fourth.** Compatible
with both our ceilings. Incompatible with assuming they preserve the afternoon.

**Recommendation:** keep the rolling fifteen-minute ceiling, keep the daily ceiling,
**add a softer pacing allowance underneath them.** A token bucket can do it — **but not
as a substitute for "five in any fifteen minutes"**, because a bucket of capacity five
refilling continuously can permit more than five inside some fifteen-minute window.

**Relate the limits through maximum acceptable damage before intervention:** burst
allowance × maximum run exposure bounds a burst; total allowance bounds cumulative
exposure; global concurrency bounds how much is committed when a stop is decided.
**Those become real bounds only when "maximum run exposure" is enforceable in the
relevant resource.**

**And a warning about our own clock:** *"a midnight start-counter reset must not be
interpreted as fresh provider allowance unless the provider's applicable limit really
resets then."*

### 5. PROTECTING THE SHARED ALLOWANCE — THE PART THAT NAMES OUR GAP

**Recommendation: one service-owned allowance ledger shared by every automatically
launched desk.** Before starting a run, account for:

    REMAINING      conservative remaining allowance for each provider window
    COMMITTED      authorised but not yet reflected in that remaining figure
    OWNER RESERVE  capacity automation is FORBIDDEN to spend
    NEXT RUN       maximum additional allowance the proposed run can consume

**Admit only when remaining − committed − Owner reserve covers the next run.**

**Reservations happen before launch.** Two jobs must not both see the same remaining
capacity and each spend it. **A crash must not erase reservations; uncertain
consumption stays charged until reconciled.**

#### THE CLAUDE-SPECIFIC LIMITATION, AND IT IS MATERIAL

**A dollar cap, a token count and subscription allowance consumption are not
interchangeable merely because they correlate.**

*"I have NOT established a supported machine-readable interface, with sufficiently
fresh measurements and an enforceable per-run allowance bound, for your particular
subscription and installed runtime. The documented interactive usage display does not
prove that such an interface exists."*

**Two honest choices:**

    STRICT           use authoritative usage info plus bounded run exposure, or
                     REFUSE further automatic admission when unavailable.
                     Cost: more work held; may prevent full unattended operation.
    CONSERVATIVE     one session at a time, small runtime/turn budgets, limited
                     batches, usage checkpoints, a large Owner reserve.
                     Cost: real risk reduction, NO guarantee.

*"Use conservative approximation only with that limitation explicit. If 'automation
must never consume my working reserve' is a hard requirement, missing or stale
measurement must stop automatic admission."*

**And:** *"a history-based maximum observed run size is an estimate, not a mathematical
upper bound."*

#### NEAR-EXHAUSTION BEHAVIOUR — DEGRADE BY POSTPONING, NOT BY WEAKENING CHECKS

    enough uncommitted allowance        admit normally, subject to pacing
    approaching the protected reserve   stop optional Research/Design expansion
    only enough for reserved work       admit nothing new; let bounded runs finish
    measurement unknown or stale        HOLD new starts; keep hard execution bounds
    runs threaten an unreserved overrun stop automatic sessions
    provider reports exhausted          stop until reset is established; do NOT
                                        probe repeatedly with new AI sessions

**Priority must be assigned outside the requesting desk's discretion. Otherwise every
job labels itself urgent.**

**A fixed "stop at 80%" is insufficient by itself** — the necessary margin depends on
outstanding runs, reporting delay and the Owner's own activity elsewhere on the
account. **A local service cannot reserve capacity against outside consumers it neither
controls nor observes.**

**Switching to a cheaper model reduces consumption but is not a hard partition and
changes answer quality. Deferring optional work is the more predictable first
degradation.**

### 6. A TRUSTWORTHY KILL SWITCH

**An operational flag disables functionality only where the running software checks
it.** Windows Job Objects separately support terminating a group of processes —
`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` terminates associated processes when the last job
handle closes.

**Two clearly distinguished actions:**

    PAUSE STARTS      running work continues within its existing bounds
    STOP AUTOMATION   stop admission AND terminate running automatic sessions

**"If your master switch only implements the first, calling it an emergency kill switch
is misleading."**

**For the second to be trustworthy:**

    1  it works without the mail service responding — a small separate Windows
       supervisor owns process containment, stoppable directly by the Owner
    2  it identifies automatic sessions precisely — do NOT kill everything named
       Claude and take out the Owner's attended work
    3  containment precedes execution — a process must not start consuming
       allowance before it is attached to the managed group
    4  missing or unreadable permission-to-run means OFF; a cached "on" must not
       survive indefinite loss of the control path
    5  stops LATCH — recovery, queued letters and reboots must not silently
       reactivate automation
    6  the supervisor's death stops its children — handle ownership matters, an
       inherited handle can defeat last-handle-close termination
    7  a hung supervisor needs an external check; a live process is not evidence
       that its control loop works

**These are trusted infrastructure actions. They require no command capability in any
desk.**

**Inference:** the supervisor should hold a short, expiring permission to continue,
renewed only while the control path is healthy — a dead-man arrangement. **The mail
service remains the sole mail mover.**

**Important limit:** *"terminating Claude Code prevents further local requests; it does
not prove that a request already accepted by the provider immediately stops consuming
allowance. Reserve room for in-flight exposure."*

**Guess:** after six untested months the most plausible failure is configuration drift
— a new launch path escaped containment, permissions changed, a flag became cached, or
automatic recovery now restarts what the switch stops. **Test after every change to
launching, supervision or permissions, and exercise a harmless stop monthly.**

**The Owner-facing result should be short:**

    Automation   STOPPED
    Running      0 verified
    Reason       Owner stop
    Allowance    31% reported; updated 2 minutes ago
    Restart      Manual

**If zero processes cannot be verified, display STOP UNCONFIRMED.**

### 7. HOW TO PROVE EACH CONTROL

**Use a trusted test harness and harmless substitute workers for most fault injection.
The desks do not execute the tests.** A passing test must **observe the prevented
action or the terminated process. A log saying "limit reached" is insufficient.**

    global concurrency / per-desk   hold one worker open, request another for the
                                    same desk and another desk -> same-desk refused;
                                    at global capacity one, both wait
    rolling 15-minute ceiling       six eligible starts in 15 min, and repeat across
                                    a quarter-hour boundary -> sixth refused in both
    daily ceiling                   seed 19 starts, request two, RESTART the service
                                    and request again -> 21st refused before and after
    pacing allowance                exhaust the burst while daily capacity remains
                                    -> work stays pending until a permit frees
    aggregate reservation           ten test units, two concurrent six-unit runs
                                    -> at most one admitted, never exceeds ten
    Owner reserve                   twelve left, ten protected, request three
                                    -> REFUSED despite twelve nominally remaining
    reservation durability          interrupt after reservation, then just after
                                    launch -> no refund of uncertain exposure, no
                                    duplicate launch
    stale/unknown allowance         stale reading, then source unavailable
                                    -> starts stop; NO default-to-full balance
    per-run spend cap               tiny cap, task needing another model call
                                    -> stops; measure any actual overshoot
    turn limit                      read-only task needing more turns than allowed
                                    -> exits at the limit; launcher does NOT resume
    absolute deadline               worker that emits activity forever, never ends
                                    -> terminated despite activity
    45-minute stall rule            worker producing nothing, shortened test clock,
                                    then verify production config separately
    12-hour stuck rule              age a pending job past twelve hours -> notice
                                    appears WITHOUT starting an AI to explain it
    chain ceiling                   two workers exchanging valid successful results
                                    -> four-delivery freeze; success never replenishes
    retry budget                    classified transient failure across several jobs
                                    -> per-job AND shared budgets both stop attempts
    poison-message isolation        same permanently invalid item on repeated scans
                                    -> isolated once, never repeatedly launches a desk
    priority shedding               reduce headroom with optional and important work
                                    pending -> optional held first; no class invades
                                    the Owner reserve
    duplicate suppression           repeat the same delivery observation, restart
                                    mid-processing -> one authorised execution
    backlog bound                   more pending work than admitted backlog allows
                                    -> excess held VISIBLY, letters preserved
    pause                           pause with one active and one pending -> active
                                    stays bounded, pending never starts
    EMERGENCY STOP                  stop while the mail service is deliberately hung
                                    and a worker ignores graceful cancellation
                                    -> process group terminates, ATTENDED SESSION
                                    SURVIVES
    supervisor-death protection     kill the supervisor while its worker runs
                                    -> worker terminates through OS containment
    dead-man timer                  processes alive, stop renewing the heartbeat
                                    -> automation stops after the expiry
    latched off                     after emergency stop, restart services and reboot
                                    with pending letters -> automation stays OFF

**Retry policy, guess-level starting values:** at most **one automatic retry per run
and two automatic retry starts per day**, all counted inside the existing twenty-start
limit.

**Do not add a circuit breaker or adaptive throttling until its signal and action can
be demonstrated.**

### 8. WHAT FIRES FIRST ON HONEST WORK

**Guess:** the four-delivery ceiling and a newly introduced turn limit. **The
account-reserve gate may instead fire first if ordinary runs are much larger than
assumed.**

    four-delivery ceiling   freezes keep landing at the same legitimate stage, with
                            NEW evidence each time
    turn / per-run cap      similar bounded tasks stop just before completion
    absolute deadline       verified progress continues; successes routinely need longer
    idle watchdog           independent evidence of useful activity despite no output
    short-window limiter    bursts trip it while total consumption stays comfortable
    token/leaky pacing      work queues only because burst capacity is too small
    concurrency / bulkhead  persistent waiting with adequate measured allowance
    daily quota             completed USEFUL work reaches the ceiling, no repetition
    aggregate reservation   large unused reservations keep returning after completion
    Owner reserve           usually the intended tradeoff, not a false alarm
    stale-data stop         sessions work but freshness repeatedly fails — the
                            MEASUREMENT PATH is inadequate
    circuit breaker         trips correlate with task type, not dependency failure
    adaptive throttling     one throttled workload slows every other workload
    retry budget            known transient faults outlast the allowance
    poison isolation        the same unchanged item succeeds after a recovery
    priority shedding       important work continuously consumes all entitlement
    backlog bound           backlog clears predictably without excess consumption
    dead-man timer          trips line up with sleep or host pressure
    kill switch             unexpected collateral termination = SCOPE defect, not a
                            threshold problem

**BigQuery explicitly warns its upper-bound estimate can reject a query whose actual
consumption would have fitted. Conservative reservation genuinely trades utilisation
for protection.**

**Three outcomes must be distinguishable in what reaches the Owner:**

    LIMIT WORKED      legitimate demand exceeded permitted consumption
    LIMIT TOO TIGHT   evidence supports a narrowly larger allowance
    CONTROL FAULT     wrong scope, stale information, or failed enforcement

**"Do not let repeated interruption automatically raise a limit. A busy, legitimate
workload can exhaust the account just as thoroughly as a runaway."**

---

**ITS CLOSING LINE, AND IT IS THE ONE TO ARGUE WITH:**

*"My first three changes remain: an independent hard stop, account-wide admission with
an Owner reserve, and bounded execution inside each session. Until allowance
measurement and per-run exposure are trustworthy, describe the system as risk-limited —
not allowance-safe."*

*End of Echo's reply. Nothing above is adopted.*
