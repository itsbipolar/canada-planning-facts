# The README recording: the test suite, then three questions to the MCP server (no model is called).
# Regenerate: vhs docs/demo.tape   (needs vhs and ttyd)
Output docs/demo.mp4
Set Shell "bash"
Set FontSize 15
Set Width 1640
Set Height 900
Set Padding 24
Set TypingSpeed 40ms
Set Theme "Builtin Dark"

Hide
Type "unset UV_NATIVE_TLS; export PS1='$ '; clear" Enter
Sleep 1s
Show

Type "# canada-planning-facts: hand-verified Canadian planning facts. Education, not advice." Enter
Sleep 1s
Type "uv run pytest -q" Enter
Sleep 9s
Type "clear; uv run python scripts/demo.py" Enter
Sleep 6s
Sleep 6s
