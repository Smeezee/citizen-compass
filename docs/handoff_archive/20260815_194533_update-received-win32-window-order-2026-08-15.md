# Update: received the order to drop WebView2 for a plain Win32 window

Sleven's decision after tonight's live test, chosen from five options with the
requirement "future proof for the next twenty years".

**I agree with the decision.** Four defects today trace to one root, and the
scaffolding around WebView2 - the black box, the dead bridge, the 12s timeout,
the browser fallback, the parity check - are all costs of the engine rather than
features. The bridge fails on his machine WITH a runtime present, so the 162 MB
payload would not have saved him either.

Starting now. Build alongside WebView2, per the order; deletion waits on his test.
