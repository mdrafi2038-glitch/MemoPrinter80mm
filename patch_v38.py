from pathlib import Path
p=Path("app/src/main/java/com/memoprinter/eighty/MainActivity.java")
s=p.read_text(encoding="utf-8")
old="        final int w=576;"
new="""        // Keep a small safety margin on both sides for real 80mm ESC/POS printers.
        // The old template size is preserved, but the printable bitmap is limited
        // to 560 dots so common 80mm mechanisms do not clip the edges.
        final int w=560;"""
if old not in s: raise SystemExit("render width anchor missing")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
