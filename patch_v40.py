from pathlib import Path
import re

root=Path(".")
files=list(root.rglob("*.java"))+list(root.rglob("*.kt"))

for p in files:
    s=p.read_text(encoding="utf-8",errors="ignore")
    orig=s

    # A transparent preview bitmap was being shown over the default black
    # ImageView background. Force preview ImageViews to a white paper background
    # immediately before displaying their bitmap.
    s=re.sub(
        r'(?m)^([ \t]*)([A-Za-z_$][\w$]*)\.setImageBitmap\(([^\n;]+)\);',
        lambda m: m.group(1)+m.group(2)+'.setBackgroundColor(android.graphics.Color.WHITE);\n'+m.group(1)+m.group(2)+'.setImageBitmap('+m.group(3)+');',
        s
    )

    # Also prevent preview containers explicitly using black as their background.
    s=re.sub(
        r'(?i)(preview[^\n]{0,160}?\.setBackgroundColor\()android\.graphics\.Color\.BLACK(\))',
        r'\1android.graphics.Color.WHITE\2',
        s
    )

    if s!=orig:
        p.write_text(s,encoding="utf-8")
        print("patched",p)
