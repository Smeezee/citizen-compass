# ECHO — the routing and escalation process. Outside research, 2026-09-10.

    source     Echo, an outside AI with no mailbox. Carried in by Sleven.
    asked for  the most thorough, reliable process for the chain
               Owner -> Architecture -> Build -> Architecture -> Owner,
               grounded in how real systems solve it rather than invented.
    status     NOT ADOPTED. Verbatim below. Architecture tears into it first.
    labels     Echo's own: ESTABLISHED = supported by the linked primary source.
               RECOMMENDATION = its application of that practice to this system.
               FORECAST = an unmeasured prediction.

---

## ECHO'S REPLY, VERBATIM

Sir, my recommendation is **an enforced state machine in the mail service, a
separate watchdog, and a service-owned history that desks cannot rewrite**. Those
are established mechanisms that fit a single-machine, file-based system.

There is no credible basis for claiming a measured frequency ranking for this
particular arrangement. I distinguish documented failure mechanisms from my
forecast below.

**Labels:** **Established** means supported by the linked primary source.
**Recommendation** means my application of that practice to your system.
**Forecast** means an unmeasured prediction.

### 1. PRIOR ART — WHAT GENUINELY APPLIES

**Supervision trees — Erlang/OTP.** Starts, monitors and restarts processes.
`one_for_one` restarts the failed child; other strategies restart dependent groups.
Restart intensity limits prevent endless crash/restart cycles. *Applies to service
and session failures. It does not decide whether Architecture's answer is useful or
whether another Build attempt makes sense. Restarting a process and revising a plan
must remain separate decisions.*

**Retry budgets, backoff and jitter — AWS SDKs.** Retries selected transient
failures, spaces attempts apart, limits retry traffic. *Applies to temporary
execution failures. It does not justify repeatedly asking an AI to solve the same
unresolved problem. Jitter has relatively little value with one active desk; a retry
budget still matters.*

**Dead-letter handling — Amazon SQS.** Removes repeatedly unsuccessful messages from
ordinary processing so they can be examined and deliberately returned. *Applies
directly as an exception tray. You are adopting the handling policy, without
adopting SQS or a broker.*

**Explicit state machines — W3C SCXML.** Defines which events can cause which
transitions, subject to conditions. *The closest fit. A destination is permitted
only when the current state, sender, outcome and evidence permit that transition.*

**Durable workflows — Temporal.** Separates workflow progress from individual
activity attempts, records state, supports incoming decisions, uses timeouts to
detect missing completion. *Borrow the semantics: persistent state, separate attempt
identities, bounded activity execution, durable human decisions. A small file
service does not automatically inherit Temporal's durability or recovery
guarantees.*

**Task scheduling — Apache Airflow.** Tracks dependencies and distinct task states,
including queued, running, retrying and waiting for human input. Detects tasks left
"running" after their worker has disappeared. *Borrow the operational states and
reconciliation. Its DAG model is a less natural fit for recurring Architecture–Build
revision loops. Installing Airflow would add machinery without removing your core
routing problem.*

**Business workflows and incidents — Camunda.** Stops at human tasks; creates
incidents when execution cannot advance; resumes after intervention. *Very close to
the desired escalation model. A blocked job remains blocked until an explicit
intervention occurs. Clearing an incident is not evidence that its cause was fixed.*

**Escalation policies — PagerDuty.** Finds someone who will respond, using elapsed
acknowledgement time and successive responders. *Borrow acknowledgement and
reminders. It solves "nobody has taken responsibility," not "the responsible
person's solution is correct." You have one final human, so a multi-person paging
ladder adds little.*

**Ticket workflows and SLA clocks — Jira / Jira Service Management.** Restricts
transitions and measures time under explicit start, pause and stop conditions.
*Applies directly. Ownership, permitted status changes and waiting-on-human time
should be explicit. A ticket's reassignment history alone does not establish
progress.*

**Sagas and compensation.** Handles partially completed operations by executing
business-specific compensating actions. *Mostly does not apply to mail circulation.
Sending work back to Architecture is rework, not compensation. It becomes relevant
when an attended Build operation changes something that may need reversal.*

#### THE PRIMARY-SOURCE LINES

    OTP        "If a child process terminates, only that process is restarted."
               erlang.org/doc/system/sup_princ.html
    AWS        "Standard mode retries failed requests using exponential backoff
               with jitter."
               docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html
    SQS        "isolate unconsumed messages to determine why processing did not
               succeed."
               docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/
               sqs-dead-letter-queues.html
    SCXML      "Transitions between states are triggered by events and
               conditionalized via guard conditions."   w3.org/TR/scxml/
    Temporal   "Instead, retry failed Activities within the Workflow."
               docs.temporal.io/encyclopedia/retry-policies
               docs.temporal.io/encyclopedia/workflow-message-passing
    Airflow    tasks "may get stuck in a `running` state despite their associated
               jobs being inactive."
               airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html
    Camunda    "The process instance stops at this point and waits until the user
               task instance is completed."
               docs.camunda.io/docs/components/modeler/bpmn/user-tasks/
    PagerDuty  "Acknowledgment does not resolve the incident".
               support.pagerduty.com/main/docs/escalation-policies
    Jira       "Validators check that any input made to the transition is valid
               before the transition is performed."
               support.atlassian.com/jira-cloud-administration/docs/
               configure-advanced-issue-workflows/
    Compensat. "A compensating transaction is application specific."
               learn.microsoft.com/en-us/azure/architecture/patterns/
               compensating-transaction

**Recommendation, ranked:** adopt state-machine enforcement first; durable
attempt/history tracking second; independent supervision third; selective retries
fourth. Treat compensation as a Build concern when an actual operation needs it.

### 2. FAILURE MODES — FREQUENCY AND DETECTORS

**Established limitation:** these sources document mechanisms and controls, but do
not provide comparable occurrence rates for your four failures. Giving you an
empirical first-to-fourth ranking would be invented.

The following is a **forecast for early operation**, ranked by expected encounter
frequency, not severity.

**1. An incomplete or unusable handoff** — ambiguous instruction, missing evidence,
wrong destination, malformed completion. *Workflow validators reject missing or
invalid transition inputs.* **Cheapest detector:** check required completion evidence
and permitted destination before accepting the handoff. A present file is
insufficient.

**2. Quiet noncompletion** — session never starts properly, exits without a valid
reply, or remains alive but produces nothing usable. *Workflow engines distinguish
queue delay, execution timeout and missing heartbeat.* **Cheapest detector:** record
launch time and process exit. An exit without an accepted reply fails immediately; no
accepted output by 45 minutes becomes stalled.

**3. Legal ping-pong without progress.** *Transition history reveals cycles;
meaningful outcomes require domain-specific checks. A legal state machine can still
contain an endless legal cycle.* **Cheapest detector:** on a return to Build, require
an identified change and a check that could distinguish the new attempt from the
previous one. Count failed correction rounds.

**4. Retry conceals a persistent fault.** *Attempt histories and internal error
metrics reveal failures hidden behind eventual success.* **Cheapest detector:**
preserve the original error and every retry. A successful retry does not erase
"recovered after failure." Repeated identical unresolved failure stops automatic
retries.

**5. False completion** — a confident reply mistaken for verified success. *Separate
execution outcome from acceptance/verification.* **Cheapest detector:** "resolved but
not verified" cannot become "complete" without Audit evidence against the relevant
artifact version.

**6. Human clears the block without changing its cause.** *Incident systems retain
recurrence and intervention history.* **Cheapest detector:** a restart must name what
changed or explicitly record a one-attempt override. Recurrence of the same
unresolved blocker is shown immediately.

**7. Duplicate start or stale reply after recovery.** *Durable execution systems
correlate attempts and reject duplicate or obsolete completions.* **Cheapest
detector:** one active writer per job; service-assigned attempt identity; accept
completion only from the current attempt.

**8. The mail service itself silently stops making progress.** *Independent
monitoring checks externally visible progress.* **Cheapest detector:** a separately
scheduled checker verifies a recent completed mail scan and overdue work. "Process
exists" does not pass the check.

Ranks 1–4 could readily change once you have operating data. Rank 6 will be uncommon
if the Owner is rarely asked to intervene, but frequent interventions create more
opportunities for it.

**Activity is not progress.** A new timestamp, another paragraph or a successful
session exit proves activity. It does not prove a requirement was satisfied.

**A deterministic detector cannot reliably recognize that two differently worded
explanations mean the same thing.** Use exact blocker references, attempt history and
evidence identifiers. The round limit catches the cases that evade exact matching.
**Do not add another AI judge and call that enforcement.**

Google explicitly discusses "failures masked by retries" and warns that frequent
noisy alerts lead people to skim or ignore them.
*sre.google/sre-book/monitoring-distributed-systems/*

For an actual frequency ranking after launch, count **jobs affected and underlying
incidents**, alongside attempts. Ten retries of one fault must not look like ten
independent faults.

### 3. THE STATE MACHINE — WORK STATE AND EXECUTION STATE

**Recommendation:** keep two separate descriptions of each job. **Work state:** what
must happen next. **Execution state:** whether its current desk visit is waiting,
running, failed or finished. This prevents "the process exited successfully" from
becoming "the job is complete."

**Anything absent from the tables below is prohibited.** Desks request changes; the
mail service validates and records them.

#### WORK STATES AND LEGAL TRANSITIONS

    FILED                        -> Architecture review        Owner
                                    valid first filing, unique permanent job number

    ARCHITECTURE REVIEW          -> Build ready                Architecture
                                    decision/spec, bounded task, acceptance check
                                 -> Specialist review          Architecture
                                    named Design or Research desk, specific question
                                 -> Waiting on Owner           Architecture
                                    explicit unresolved decision + escalation packet

    SPECIALIST REVIEW            -> Architecture review        the assigned desk
                                    answer or explicit inability; sources if relevant

    BUILD READY                  -> Waiting for attended Build Build / capability check
                                    execution needs capabilities an auto session lacks
                                 -> Architecture review        Build
                                    spec defect, missing prerequisite, cannot proceed

    WAITING FOR ATTENDED BUILD   -> Build executing            Owner-controlled start
                                    job-specific authorisation, real attended start

    BUILD EXECUTING              -> Architecture review        Build
                                    failed check or blocker, what was tried, evidence
                                 -> Resolved but not verified  Build
                                    exact changed artifact/revision + evidence

    RESOLVED BUT NOT VERIFIED    -> Audit review               service, approved route
                                    fixed review target, acceptance criteria

    AUDIT REVIEW                 -> Verified, awaiting closure Audit
                                    findings vs the identified revision, each criterion
                                 -> Architecture review        Audit
                                    failed or indeterminate criterion + evidence

    VERIFIED, AWAITING CLOSURE   -> Complete                   Architecture
                                    audit passed; reviewed artifact still current
                                 -> Architecture review        Architecture
                                    new conflicting evidence or artifact changed

    WAITING ON OWNER             -> Architecture review        Owner
                                    explicit decision, permitted next attempt,
                                    permanent restart record where applicable

    ANY NONTERMINAL              -> Waiting on Owner           service
                                    delivery ceiling, exhausted budget, exception
                                 -> Superseded                 Owner
                                    replacement job number + why the old one is dead
                                 -> Abandoned                  Owner
                                    explicit stop + disposition of unfinished effects

**Complete, superseded and abandoned are terminal for automation.** They never
restart because a desk edits `Status:`. To reopen, the Owner must explicitly return
the same job to Architecture under a recorded restart. Supersession links must also
be reconciled; both jobs must not silently become authoritative. Architecture can
recommend superseding or abandoning; final authority stays with the Owner.

#### EXECUTION STATES AND LEGAL TRANSITIONS

    READY               -> Starting                    service reserves a start,
                                                       checks limits, assigns the visit
    STARTING            -> Running                     service observes the process
                        -> Attempt failed              launch failure or unresolved
                                                       outcome (ambiguous first goes
                                                       to recovery inspection)
    RUNNING             -> Reply awaiting validation   desk produces its one completion
                        -> Attempt failed              exits without acceptable output
                        -> Stalled                     45-minute deadline, no output
    REPLY AWAITING VAL. -> Visit finished              service validates attempt, stamp,
                                                       outcome and evidence
                        -> Quarantined                 invalid, conflicting, stale or
                                                       prohibited completion
    ATTEMPT FAILED      -> Retry waiting               eligible transient failure and
                                                       remaining retry allowance
    RETRY WAITING       -> Starting                    backoff elapsed, old writer gone,
                                                       all launch limits still pass
    ATTEMPT FAILED
      or STALLED        -> Exception held              retry unsafe, unavailable or spent
    EXCEPTION HELD      -> Ready                       authorised recovery, previous
                                                       custody safely closed
    QUARANTINED         -> Ready for Architecture      Owner-authorised release after the
                                                       integrity/route problem is fixed
    ANY NONTERMINAL     -> Recovery inspection         service restart, or uncertainty
                                                       about file, process or custody
    RECOVERY INSPECTION -> Reconstructed prior state   service can prove the state
                        -> Exception held              state cannot be proved
    READY / RETRY WAIT. -> Launch held                 global ceiling or unsafe service
    LAUNCH HELD         -> previous waiting state      hold cleared and limits permit

"Stuck for 12 hours" is **a condition attached to a nonterminal job**, not evidence of
a cause. It might mean queued, awaiting an Owner answer, or waiting for attended
Build. Preserve the underlying state.

#### THREE CONSEQUENCES

**First: automatic Build cannot build.** Under your permissions it can review
instructions and write a letter. Actual execution needs an attended Build session.
The process can remove manual startup for eligible desks; **it cannot honestly remove
human attendance from command execution.**

**Second: Audit needs a narrowly defined correspondence exception.** "Read-only and
holds no files" must mean no ownership or modification of project artifacts, while
still permitting the required review letter. Otherwise Audit cannot participate.

**Third: your stamp rule does not yet support failed visits.** A desk that dies
before stamping leaves one outstanding punch. Another delivery creates two. The
recovery transition marked "previous custody safely closed" is therefore **not
implementable under the literal current rule.**

### 4. THE ESCALATION RULE — COUNT FAILED CORRECTION ROUNDS

**Established:** real systems count different things because they protect against
different failures.

    Attempts / restarts (OTP, Temporal)   detects repeated execution failure
                                          but a "successful" process can produce
                                          useless work indefinitely
    Receipts / deliveries (SQS)           detects repeated unsuccessful handling
                                          but legitimate multi-step work spends
                                          the same allowance
    Elapsed execution time                detects silent or over-long attempts
                                          but fast useless cycles remain possible
    Time without acknowledgement          detects nobody taking responsibility
      (PagerDuty)                         but acknowledgement is not repair
    Time under ticket states (Jira)       detects waiting and service delay
                                          but pausing the wrong clock hides age
    Distinct participants                 detects unexpected spread
                                          but two can loop forever, and several
                                          can make legitimate progress

Temporal separates individual execution time from total time across retries. Airflow
documents an overall timeout that retries do not reset. Jira permits SLA pauses while
waiting for a customer.

**Recommendation: independent triggers; whichever fires first wins.**

    Build's first substantive failure          -> back to Architecture, never Owner
    Architecture cannot identify a materially
      different next attempt                   -> escalate immediately
    Two failed correction rounds               -> freeze for Owner
    Same unresolved blocker returns after a
      correction, no changed prerequisite      -> freeze early, do not spend a round
    Four-delivery ceiling                      -> freeze per the existing hard rule
    45 min without accepted output             -> attempt stalled, stop further writing
    12 h without accepted work progress        -> stuck, notify with the real reason
    Next start exceeds either global ceiling   -> refuse, hold, notify Owner

A **correction round** begins when Architecture answers an identified Build failure
with a revised approach, and ends when Build reports the result of attempting that
revision. The initial failed Build attempt is not a correction round. Research
consultation is not a new round. A renamed blocker does not erase prior rounds.

**Two rounds is a proposed policy, not an industry-standard number.**

#### THE DELIVERY ARITHMETIC — AND IT IS UNAVOIDABLE

    delivery 1   Architecture
    delivery 2   Build
    delivery 3   Architecture, after Build's problem
    delivery 4   Build, after Architecture's correction

If freezing happens immediately on the fourth delivery, the corrected Build attempt
cannot run. If the fourth recipient may finish first, its result still cannot return
to Architecture without a fifth delivery.

**Even the straightforward route Owner → Architecture → Build → Audit → Architecture
reaches delivery four before Architecture closes the job.**

**Your four-delivery limit is defensible as a strict human checkpoint. It is a poor
substitute for a failed-round budget.** Its cost is routine Owner involvement in
otherwise healthy work.

Define the freeze boundary explicitly: "fourth delivery received" and "fourth visit
completed" are different policies. The literal, stricter interpretation is freezing
on receipt.

An Owner restart needs a new **allowance period**, while lifetime deliveries and
restarts remain permanent. Otherwise a job already at four immediately freezes again.
That allowance accounting must not erase repeated-blocker history or global start
usage.

For session failures: **one automatic retry only for an identified transient cause**,
delayed 60–90 seconds, honouring a longer provider-requested delay. A starting
setting, not a sourced optimum. Unknown failures, permission failures, invalid
letters and substantive Build failures get no automatic retry. Exponential backoff
becomes useful only if you later permit several retries.

#### WHAT GOES BEFORE THE OWNER

Display requirements, not a mail format.

    Job                 number and short title
    Stopped because     one concrete sentence
    Tried               up to two short attempt/result lines
    Still missing       one prerequisite or decision
    Decision needed     one sentence
    Recommended action  one action and its main cost
    Alternative         one action and its main cost
    After your answer   next desk and permitted attempt
    History             restart count and direct evidence references

"Unknown" is valid for the cause. **The service must not invent Architecture's
diagnosis when Architecture itself is stalled.**

**Separate acknowledge, decide and restart.** "I saw this" cannot restart it. For
voice input, show the recognized job and action before accepting a restart; an
ambiguous "yes" must not release multiple jobs.

A human may knowingly allow another attempt without a proven repair, but record it as
an **override**, not "fixed." Show that override when the blocker returns.

### 5. ENFORCEMENT VERSUS CONVENTION

**The mail service is the correct place to enforce routing. You are wrong only in
saying it is the *only* place enforcement can live.** Three boundaries:

    the mail service      decides legal transitions and custody
    the session launcher  no desk starts without valid authorisation and budget
    permissions           desks cannot bypass the other two by changing protected
                          state or writing into other trays

If those can be bypassed, the route remains a convention.

#### WHAT THE LEGAL-TRANSITION CHECK MUST ESTABLISH

    1  the job exists and its permanent identity is unambiguous
    2  the sender is the session actually assigned this visit
    3  the completion belongs to the current attempt
    4  the recorded current state permits that outcome and destination
    5  required evidence exists and refers to the correct work
    6  the current visit has finished or been explicitly cancelled through a
       supported recovery path
    7  delivery and escalation limits permit the transition
    8  the change can be recorded durably BEFORE a new desk is started

**`From:` is a claim, not authentication.** The service must already know which desk
it launched and which job that session could edit. Permission to write anywhere in a
common inbox does not prove one-letter ownership or stop modification of another job.

**A punch count cannot authenticate routing.** A file can be moved illicitly while its
count stays unchanged. A copied stamp can make totals look normal. The arithmetic is a
useful consistency check, but **"anything else proves unauthorised movement" is
false** — partial writes or interrupted service operations can also break it. And a
passing count does not prove lawful movement.

#### THE UNSTAMPED-VISIT PROBLEM REQUIRES AN EXPLICIT DECISION

    delivered once      punches 1, stamps 0
    desk dies
    service re-routes   punches 2, stamps 0

No illegal actor was involved, yet the invariant fails. Two honest approaches:

**Keep the literal rule** — a failed unstamped visit cannot be handed onward. Hold the
original in place and let the Owner inspect it. Recovery may require the same visit
eventually producing a genuine stamp.

**Add explicit service-recorded cancellation of a visit** — a dead visit can be closed
as failed and routed onward, and cancellation stays distinguishable from successful
desk completion.

**I recommend the second. It is a change to an already-decided rule, and I am
identifying it as such.** Without it, general crash recovery is impossible. **Do not
solve this by forging a desk stamp or deleting a punch.**

The same issue arises if the four-delivery freeze tries to move a newly delivered,
unstamped job immediately into the Owner's tray.

#### WHAT HAPPENS TO AN ILLEGAL LETTER

    do not deliver to the requested destination
    preserve the submitted content and the rejection reason
    quarantine the job; prevent further desk starts for it
    notify Architecture through an authorised exception notice for a route error
    notify the Owner directly for identity/history integrity problems, or when
      Architecture is unavailable
    do NOT automatically bounce it to its sender for unlimited correction

An exception notice does not create another work item with a fresh budget. The
original job keeps its number and accumulated history.

#### CRASH RECOVERY WITH FILES

A move, a punch update and a history update are **not one indivisible operation
merely because they occur on one machine.**

Use a service-owned, append-only journal in ordinary files. Record the intended
transition, perform it, then record confirmation. On startup, reconcile incomplete
transitions against the actual file and process state. **Reprocessing the same
transition must not create another delivery or session.**

*aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/*

**Do not promise exactly-once session execution.** A crash between launching a process
and recording that launch creates uncertainty. Reserve the attempt first, identify the
process afterwards, hold on ambiguity. **The achievable target is one accepted
completion and no overlapping authorised writers.**

Windows also caches writes; a completed write is not automatically evidence that it
survived power loss.
*learn.microsoft.com/en-us/windows/win32/fileio/file-caching*

#### REDUCING THE CONCENTRATION RISK

Keep **one mail mover.** Add a **separate, small watchdog**, started independently by
Windows scheduling or service management. Its job is limited:

    check a full mail-service scan completed recently
    check overdue starts, stalled sessions and stuck jobs independently
    alert WITHOUT depending on the mail-routing loop
    never move mail, never automatically override custody

Use bounded Windows service recovery for a crashed mail service; the independent
checker is still needed for a live but hung process.
*learn.microsoft.com/en-us/windows/win32/api/winsvc/ns-winsvc-service_failure_actionsw*

Start with a check every minute and flag two missed completed scans. Proposed
operating values.

**One machine remains one machine.** This removes a process-level monitoring
dependency. It cannot detect or report a total machine or power failure while that
machine is off. **Under your constraints the reliable outcome is safe stoppage and
recoverable history, not continuous availability.**

### 6. THE RECORD

**Preserve authoritative events and the evidence used for decisions. Do not rely on
the latest edited memo to preserve its own past.**

    KEEP
      permanent job identity and filing event
      every accepted AND rejected transition
      previous state, requested state and accepted state
      assigned desk, visit and session attempt
      launch reservation, observed start, exit, timeout and cancellation
      punches, stamps and exceptional custody closures
      original failure, correction attempted, observed result
      delivery counts, correction counts, lifetime restarts
      Owner acknowledgement, decision and override SEPARATELY
      artifact versions and retained evidence used in verification
      route-policy and permission-profile versions
      service recovery actions and unresolved uncertainty
      notification creation and acknowledgement

**A hash alone cannot reconstruct overwritten text. A reference to a mutable file
cannot establish what Audit saw.** Preserve the relevant version or content as well.

    SAFE TO LEAVE OUT
      token-by-token model output
      claimed internal reasoning
      identical directory-scan results
      repeated "still waiting" entries
      full source trees copied on every visit
      secrets and credentials
      a separate alert for every retry of the same incident

**Do not let desk-authored prose revise service history.** An inbox write restriction
alone does not protect history embedded in a file the desk can edit.

For launch ceilings, **record reservations durably BEFORE launching.** The sixth start
in a rolling fifteen minutes and the twenty-first in the defined day must be refused
rather than started and noticed afterwards. Count retries too. Define the day's
timezone, and never reset usage simply because the service restarted.

### 7. WHAT BREAKS FIRST

**Forecast:** the first practical failure will be the boundary between **"a letter
exists" and "a complete, valid handoff exists."** A desk will leave partial output,
exit without a usable completion, or produce an otherwise valid letter that cannot
legally advance. A directory event may arrive while editing is still underway.

**Established:** Windows documents notification-loss cases and instructs applications
to recover by enumerating the directory — "compute the changes by enumerating the
directory or subtree." **A watcher notification is therefore a prompt to inspect, not
an authoritative work record.**
*learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-readdirectorychangesw*

**Cheapest control:** a complete scan at startup and periodically thereafter; launch
only from a validated, completed handoff whose writer has finished. **At your start
ceilings, begin with one active automatic session at a time.** That costs throughput
but makes ownership and recovery much easier to verify.

**Second forecast:** the four-delivery checkpoint produces more Owner interruptions
than expected, especially when Audit or Research is involved. **Record whether each
freeze was caused by failed progress or simply by legitimate route length.**

#### RANKED OPERATING RECOMMENDATIONS

    1  enforce state, sender, attempt and destination before movement
    2  resolve failed-visit custody and retain protected history
    3  validate completed handoffs; reconcile with periodic scans
    4  independent watchdog with an independent alert path
    5  separate acknowledgement, restart and verified repair
    6  selective retry and correction-round budgets

Before enabling unattended starts, demonstrate these outcomes with controlled
failures: an illegal route is refused; a dead desk leaves no false completion; a
duplicate event starts nothing twice; a stale reply is rejected; a service restart
preserves limits; and a silent mail-service failure produces an independent alert.

**The release condition should be observable recovery from those failures, not
another successful unattended reply.**

---

*End of Echo's reply. Nothing above is adopted.*
