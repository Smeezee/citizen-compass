# Update — received: the Capture toggle silences sticks, and the panel renders in USB order

From C1, 2026-08-12, extending today's two orders. Receipt per rule 13.

The diagnosis explains Sleven's exact words — *"it's recognizing the sticks,
it's just not relaying the actual information from them."* Naming comes from
`renderDevice()`, which does not check `capture`; button and hat events do. So
the panel names them and reports nothing.

Doing all four together: ungate rebind capture from the toggle, label the toggle
honestly, fix `#kbbq`, and sort the panel by resolved slot with a visible swap
affordance.
