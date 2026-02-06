import ast, sys
try:
    with open("app.py", "r", encoding="utf-8") as f:
        source = f.read()
    ast.parse(source)
    print("OK - no syntax errors")
except SyntaxError as e:
    print(f"SyntaxError at line {e.lineno}: {e.msg}")
    print(f"Text: {e.text}")
    # Show context
    lines = source.split("\n")
    start = max(0, e.lineno - 5)
    for i in range(start, min(len(lines), e.lineno + 3)):
        marker = ">>>" if i + 1 == e.lineno else "   "
        print(f"{marker} {i+1}: {lines[i][:100]}")
