package main

// ui_js_selftest.go - the check that would have caught tonight's dead window.
//
// # WHAT HAPPENED
//
// A text splice into the page's script left one extra "});" behind. The Go code
// compiled, vet was clean, the binary ran - and the window came up permanently
// stuck on "starting" with every button dead, because one syntax error stops a
// browser parsing the WHOLE script.
//
// Nothing in this project could have seen that. The UI is a Go string. The
// compiler checks Go, not the JavaScript inside a string literal, so a broken
// page is indistinguishable from a working one right up until somebody opens
// the window.
//
// # WHAT THIS CHECKS
//
// Not that the page works - that needs a browser. Only that its braces,
// brackets and parentheses balance, and that every element the script reaches
// for actually exists in the HTML. Those two are where splices go wrong, and
// both are checkable without rendering anything.

import (
	"regexp"
	"strings"
)

var reUIGetElem = regexp.MustCompile(`getElementById\('([A-Za-z0-9_-]+)'\)`)
var reUIHasID = regexp.MustCompile(`id="([A-Za-z0-9_-]+)"`)

// balanceUIScript walks the script ignoring string and comment content, and
// reports the first place the nesting goes wrong.
func balanceUIScript(js string) (string, bool) {
	var stack []rune
	pairs := map[rune]rune{')': '(', ']': '[', '}': '{'}
	line := 1
	inLine, inBlock := false, false
	var quote rune

	rs := []rune(js)
	for i := 0; i < len(rs); i++ {
		c := rs[i]
		if c == '\n' {
			line++
			inLine = false
			continue
		}
		switch {
		case inLine:
			continue
		case inBlock:
			if c == '*' && i+1 < len(rs) && rs[i+1] == '/' {
				inBlock = false
				i++
			}
			continue
		case quote != 0:
			if c == '\\' {
				i++
			} else if c == quote {
				quote = 0
			}
			continue
		}
		switch c {
		case '/':
			if i+1 < len(rs) && rs[i+1] == '/' {
				inLine = true
				i++
			} else if i+1 < len(rs) && rs[i+1] == '*' {
				inBlock = true
				i++
			}
		case '\'', '"', '`':
			quote = c
		case '(', '[', '{':
			stack = append(stack, c)
		case ')', ']', '}':
			if len(stack) == 0 {
				return "line " + itoaSmall(line) + ": a closing " + string(c) +
					" with nothing open - this is the shape a bad splice leaves", false
			}
			if stack[len(stack)-1] != pairs[c] {
				return "line " + itoaSmall(line) + ": " + string(c) + " does not match " +
					string(stack[len(stack)-1]), false
			}
			stack = stack[:len(stack)-1]
		}
	}
	if len(stack) != 0 {
		return itoaSmall(len(stack)) + " unclosed bracket(s) at the end of the script", false
	}
	return "", true
}

func runUIScriptSelftest(check func(name string, ok bool, detail string)) {
	a := strings.Index(uiHTML, "<script>")
	b := strings.Index(uiHTML, "</script>")
	if a < 0 || b < a {
		check("ui: the page has a script block", false, "no <script> found in uiHTML")
		return
	}
	js := uiHTML[a+len("<script>") : b]

	why, ok := balanceUIScript(js)
	check("ui: the page script is balanced", ok, why+
		" - one stray brace stops the browser parsing the WHOLE script, so every "+
		"button dies and the window sits on 'starting' forever")

	// NEGATIVE CONTROL. Without this, a balance checker that always returned
	// true would pass the check above and catch nothing.
	if _, badOK := balanceUIScript("function f() { if (a) { b(); }"); badOK {
		check("NEGATIVE CONTROL: the balance checker catches an unclosed brace",
			false, "it accepted obviously broken script")
	} else {
		check("NEGATIVE CONTROL: the balance checker catches an unclosed brace",
			true, "and one with a stray closer")
	}
	if _, badOK := balanceUIScript("f(); });"); badOK {
		check("NEGATIVE CONTROL: it catches a stray closing brace specifically",
			false, "that is the exact defect from 2026-08-08")
	} else {
		check("NEGATIVE CONTROL: it catches a stray closing brace specifically",
			true, "the exact defect from 2026-08-08")
	}

	// Every element the script reaches for must exist, or a rename silently
	// makes a button do nothing.
	ids := map[string]bool{}
	for _, m := range reUIHasID.FindAllStringSubmatch(uiHTML, -1) {
		ids[m[1]] = true
	}
	var missing []string
	for _, m := range reUIGetElem.FindAllStringSubmatch(js, -1) {
		if !ids[m[1]] {
			missing = append(missing, m[1])
		}
	}
	check("ui: every element the script reaches for exists in the page",
		len(missing) == 0,
		"missing: "+strings.Join(missing, ", "))

	// NEGATIVE CONTROL for that one too.
	check("NEGATIVE CONTROL: the page really does declare ids",
		len(ids) > 3, "found "+itoaSmall(len(ids))+" ids - if this were 0 the check above would pass for free")
}
