with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

in_triple_double = False
in_triple_single = False
for i, line in enumerate(lines[:485], 1):
    # Count triple-quote occurrences  
    td = line.count('"""')
    ts = line.count("'''")
    if td % 2 == 1:  # odd number means toggle
        in_triple_double = not in_triple_double
        print(f"Line {i}: toggle triple-double-quote -> now {'OPEN' if in_triple_double else 'CLOSED'} | {line.rstrip()[:90]}")
    if ts % 2 == 1:
        in_triple_single = not in_triple_single
        print(f"Line {i}: toggle triple-single-quote -> now {'OPEN' if in_triple_single else 'CLOSED'} | {line.rstrip()[:90]}")

print(f"\nFinal state at line 485: triple-double={'OPEN' if in_triple_double else 'CLOSED'}, triple-single={'OPEN' if in_triple_single else 'CLOSED'}")
