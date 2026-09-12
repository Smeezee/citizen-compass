# DESIGN — the easiest keybinding setup, for a keyboard, a pad or two sticks

    from    C3, 2026-09-06
    status  PLAN ONLY. Nothing built. Sleven asked for the plan first so the
            flaws can be found before any code exists.
            "I wanna take the key binding process that is Star Citizen and make
            it so much simpler and easier for other users like myself. No matter
            if they're playing with just mouse and keyboard, an Xbox controller,
            or flight sticks. I wanna make it the easiest key binding setup ever."
    built   The keyboard half exists as a mockup ("Keyboard First"). This plan
            covers all three device types and the binding flow itself.
    on disk 2026-09-12. Existed only in the claude.ai project until then.

> **READ §2 AGAINST THE SURVEY.** `docs/CIC_survey-keybind-tools-and-the-gap-2026-09-06.md`
> withdraws §2 as a differentiator the same day — press-to-find is Star Binder's
> Finder mode and already exists. It survives as a requirement, never as the
> reason to build. The reason to build is the check-up in that document's §5.

---

## 1. WHY IT IS HARD TODAY

Not because binding a key is hard. Because of six things around it.

**Finding the action.** 691 actions in nested categories. You scroll.

**Not knowing what is free.** Nothing shows you an empty key until you have
already taken one.

**Not knowing what you broke.** Bind something and it silently comes off
whatever had it. You find out in a fight.

**Doing it more than once.** Keyboard, then pad, then sticks. Same work three
times, in three places, with no shared view.

**No record.** Nothing tells you what you changed from the default, so nothing
tells you what to undo when it feels wrong.

**Getting it into the game.** A file, in a folder, with a name.

**The game will still be complicated.** It has 691 actions and it should. The
goal is not to hide that. It is to stop the tool adding difficulty on top of it.

---

## 2. THE ONE IDEA

**You never look up a key. You press it.**

Every interaction in this design runs in one of two directions, and both are the
same gesture:

    I HAVE AN ACTION, WHERE DOES IT GO   search it, then press the input
    I HAVE AN INPUT, WHAT IS ON IT       press it, and the page tells you

The second direction is the one nothing else offers, and it is the one that
actually matches how people think when they are sat at the desk. You do not
wonder "where is Boost." You press a key and wonder what it does.

**And it is device-blind.** Pressing a key, pressing a pad button and pressing a
stick trigger are the same gesture to the page. That is what lets one design
serve all three without the user learning three tools.

> **WITHDRAWN AS A DIFFERENTIATOR the same day.** "The one nothing else offers"
> is wrong: Star Binder's Finder mode does exactly this, free, in a browser.
> The sentence stands as a requirement and not as a claim.

---

## 3. THE RULES

**One board, and the board is your hardware.** Keyboard shows a keyboard. Pad
shows a pad. Two sticks show two sticks. Same colours, same card, same
gestures. Nothing is a list unless the user asks for a list.

**Binding is always "press it".** Never a dropdown of key names, never typing
`np_5`. Press the thing you want. It is the only method that works identically
on hardware nobody has anticipated.

**Show the cost before it is paid.** Never silently steal. Before a rebind
lands: *"this takes Boost off Left Shift"* with a yes or a cancel. The single
most common frustration in the game's own menu, removed.

**Same key, different mode, is NOT a conflict.** W is throttle in flight and
walk forward on foot, and that is correct. A real conflict is the same input,
same mode, same layer, twice. Most tools cry wolf here. This one must not.

**Start from a profile, never from zero.** Nobody binds 691 actions. They take a
starting point and change twenty things. So the first screen is a choice of
starting point, and everything after that is a diff.

**Every change is recorded and reversible.** A short list of what you changed
from your starting point. That list is the thing worth sharing, and the thing to
read when something feels wrong.

---

## 4. THE SHAPE — four screens, and only the second one matters

**Screen 1 — What are you flying with.**
Detects what is plugged in. Keyboard and mouse, a pad, one stick, two sticks, a
stick and a throttle, pedals, any combination. It asks nothing it can work out
itself, and it lets you say "I want to plan for a stick I do not own yet."

**Screen 2 — The board.** This is the product. Everything below happens here.

**Screen 3 — What you changed.** The diff from your starting point, in plain
sentences. Undo any line.

**Screen 4 — Put it in the game.** Export, and exactly where the file goes.
Import to start from what you already fly with.

---

## 5. THE BOARD, IN DETAIL

**The picture is your hardware, at rest, with everything on it visible.**

Every input carries the name of what it does, coloured by mode. Nothing is
hidden behind a click. You can read the whole layout without touching anything.

**Four things you can do on it, and that is all:**

**Look.** Hover or press any input. It lights, and a card opens showing
everything on it, grouped by mode.

**Filter.** Switch mode — flight, on foot, EVA, vehicle, camera. The board
recolours. Hold a modifier — shift, alt, the stick's pinky lever — and the board
shows that layer. **You explore layers by holding them, not by choosing them
from a menu.**

**Find.** Type an action. The board dims and the input holding it lights up. If
nothing holds it, the board shows you the free inputs instead.

**Change.** Covered in §6.

**And one honest state that nothing else shows:** an input that is empty in the
mode you are looking at, but busy in another, says so. *"Nothing here. 30 in
Camera."* An empty-looking key that is actually loaded is the single most
confusing thing on a board and it costs one line to fix.

---

## 6. THE REBIND FLOW — per entry, never per input

**Sleven's correction, 2026-09-06, and it is the right one.** One input can
carry several actions across modes. Rebinding must act on the LINE you picked,
not on the whole key.

    press or click an input
      -> card opens, one line per action on it, grouped by mode
         FLIGHT     Strafe up (abs.)        [change] [clear]
         ON FOOT    Lean right              [change] [clear]
         EVA        Boost up                [change] [clear]
         + one line for every mode it is empty in, greyed, with [add]

    press [change] on the on-foot line
      -> "press the input you want for Lean right"
      -> you press it
      -> if it is taken IN THAT MODE AND LAYER:
           "That takes Crouch off C. Swap, or pick another?"
         if it is taken in a different mode: no warning, it is fine
      -> done, and the change lands in the What You Changed list

**Two extra beats that cost nothing and save a lot:**

**A modifier is part of the press.** Hold shift and press the key, and it binds
to the shift layer. You never choose a layer from a menu — you perform it.

**Press type is a second, optional question**, and only when it applies. Tap,
hold, long press, double tap. Default to whatever the action already used, and
never ask when there is only one sensible answer.

---

## 7. WHAT CHANGES PER DEVICE, AND WHAT DOES NOT

**Everything in §5 and §6 is identical on all three. What differs is only the
picture and three device facts.**

**Keyboard and mouse.** Many inputs, so most actions get their own key and
layers are optional. Modifiers are keys you already have. Mouse buttons and
wheel are inputs like any other. This half is already built.

**Xbox pad.** The hard one, and the one everybody does badly. There are not
enough buttons — about fifteen against 691 actions — so **layers stop being
optional and become the whole design.** Hold a bumper, the board changes, that
is a second full set. The design should say plainly on screen: *"you have 15
buttons and 4 layers, so 60 slots."* Analog triggers and sticks are axes, not
buttons, and need the axis treatment below.

**Flight sticks.** Many buttons, hats with four or eight directions, and usually
two devices at once. Two grips side by side, and the pinky lever is the natural
layer key. This is where the earlier stick panel work joins in: the picture is a
real drawing of the stick with every control in its real place.

> **2026-09-12: the stick picture is now our own photographs only** (Sleven,
> 2026-09-08), **and no control's identity may come from its HID button number**
> (Architecture, 2026-09-10). Shift state means one control reports several
> numbers, so there is no table to store. The pilot's press supplies the mapping.

**The three device facts that need their own handling:**

**Axes are not buttons.** A stick, a trigger, a pedal, a throttle. They need
direction, deadzone, curve and invert — not a keypress. The card for an axis is
a different card, with a curve you can see and a live dot riding it.

**Hats are one input with four or eight faces**, and each face binds separately.
Drawn as a cluster, treated as a group.

**Two devices are not one.** With two sticks, the same button number exists on
both. The page must always say which device, and never merge them.

---

## 8. THE THING THAT MAKES IT ACTUALLY EASIER — the starter set

**691 actions is the real enemy.** Showing all of them is honest and useless.

So there are three depths, and you choose one:

**Essentials.** The forty or so things you need to leave a hangar and come back
alive. Throttle, strafe, look, fire, landing gear, quantum, ping, exit seat.
**Somebody has to write this list by hand and it is the most valuable thing in
the whole design** — it is the difference between a tool and a spreadsheet.

**Common.** Add the things a working pilot uses weekly. Salvage, mining,
cargo, targeting depth, power triangle.

**Everything.** All 691. Always reachable, never the default.

**And the depth is a filter, not a wall.** It only changes what the board
highlights and what search ranks first. Nothing is ever hidden from someone
looking for it.

---

## 9. FLAWS AND OPEN QUESTIONS — the point of writing this first

**1. The essentials list is hand-written and nobody has written it.** It is
opinion, not data. It will be argued with. It should probably be a starting
point that the user can edit, and it should say who wrote it.
**Still true 2026-09-12. Nobody has written it.**

**2. Detecting a pad and a stick reliably is not proven here.** The browser can
see them, and the earlier stick work established exactly what it can and cannot
tell — identity yes, physical layout no. **A pad has the advantage of a standard
layout the browser does report; sticks do not.** That asymmetry is not yet
designed around.

**3. "Press the input you want" competes with the page's own keyboard.** While
capturing, every key must be swallowed — including Escape, Tab and F-keys — with
a clear way out that is not a key. Small, but easy to get wrong and infuriating
when it is wrong.

**4. Some inputs cannot be pressed on demand.** A pedal at full travel, a
throttle detent, a hat direction on a stick that is not plugged in. There has to
be a manual fallback, and it must not become the main path.

**5. The game's own file format for pads and sticks has not been read.** The
keyboard side is understood. Whether a pad binding and a stick binding sit in
the same profile file, and how devices are identified inside it, is NOT CHECKED
and is the largest unknown in this plan.
**Still NOT CHECKED 2026-09-12, and still the largest unknown. Two of the three
device types in the brief rest on it.**

**6. Layers are the best feature and the easiest to make confusing.** Holding a
modifier changes the whole board, which is powerful and disorienting. It needs a
permanent, obvious indicator of which layer you are looking at.

**7. Undo needs to be per change, not a global reset.** Easy to say, and it
means every change carries enough information to be reversed on its own.

**8. Nothing here is designed for a phone.** Not once.

---

## 10. WHAT IS DELIBERATELY NOT IN THIS

**No account, no cloud, no sharing.** Sleven's machine and Sleven's file.
Sharing profiles is an obvious later idea and it is not this.

**No recommendations.** The tool does not tell you where Boost should go. It
shows you what is free and what you would break, and you decide.

**No macros, no scripting, no automation.** Binding only.

**No claim about what other tools do.** Nothing was surveyed for this document.
**Surveyed the same day — see `docs/CIC_survey-keybind-tools-and-the-gap-2026-09-06.md`.**

---

## Checked / not checked

**CHECKED:** the 691-action dataset, its categories and modes, and that the
keyboard board works against it — that is the existing mockup, tested key by key
across both numlock states and every mode and layer.

**NOT CHECKED:** the game's profile file format for pads and sticks; how Star
Citizen's own binding menu behaves today; whether a browser can reliably tell
one connected stick from another when two of the same model are plugged in;
anything about effort, cost or build order.

**Plan only. Not a work order. Nothing authorised.**
