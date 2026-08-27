# Update — starting open item #3, the browser fallback

Item #1 is closed (previous update). Item #2 is blocked on `gh`.

Taking **item #3: the browser fallback has never executed.** The handoff calls
it "the one path with zero real-world evidence" — both machines it has run on
have WebView2, so the fallback has never been reached in anger.

Intent: force the no-WebView2 condition rather than wait to meet a machine
without it, and confirm the fallback actually serves the panel, that its
security gates (token in path, loopback only, `Sec-Fetch-Site`) hold, and that
the nine window actions behave identically across both transports.

Will report what executed and what did not.
