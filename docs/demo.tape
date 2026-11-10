# The demo recording: the test suite, then three questions to the MCP server, one per screen (no model is called).
# Sized to stay readable when embedded about 740 px wide. Regenerate: vhs docs/demo.tape   (needs vhs and ttyd)
Output docs/demo.mp4
Set Shell "bash"
Set FontSize 32
Set Width 1280
Set Height 720
Set Padding 40
Set TypingSpeed 45ms
Set Theme "Builtin Dark"

Hide
Type `unset UV_NATIVE_TLS; export PS1='$ '; ask(){ uv run python scripts/demo.py --brief "$1"; }; clear` Enter
Sleep 1s
Show

Type "# Verified Canadian planning figures." Enter
Type "# First, the tests:" Enter
Sleep 500ms
Type "uv run pytest -q" Enter
Sleep 7s
Type "clear; ask 1" Enter
Sleep 7s
Type "clear; ask 2" Enter
Sleep 8s
Type "clear; ask 3" Enter
Sleep 7s
