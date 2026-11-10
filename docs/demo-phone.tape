# The demo recording (tall, for phones): the tests, then three questions to the MCP server, one per screen (no model is called).
# Regenerate: vhs docs/demo-phone.tape   (needs vhs and ttyd). Extra room at the bottom keeps the player's controls off the text.
Output docs/demo-phone.mp4
Set Shell "bash"
Set FontSize 28
Set Width 720
Set Height 760
Set Padding 30
Set TypingSpeed 45ms
Set Theme "Builtin Dark"

Hide
Type `unset UV_NATIVE_TLS; export PS1='$ '; ask(){ uv run python scripts/demo.py --brief "$1" 36; }; clear` Enter
Sleep 1s
Show

Type "# Verified Canadian planning" Enter
Type "# figures. First, the tests:" Enter
Sleep 500ms
Type "uv run pytest -q" Enter
Sleep 7s
Type "clear; ask 1" Enter
Sleep 7s
Type "clear; ask 2" Enter
Sleep 8s
Type "clear; ask 3" Enter
Sleep 7s
