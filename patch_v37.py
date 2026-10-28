from pathlib import Path
p=Path('app/src/main/java/com/memoprinter/eighty/MainActivity.java')
s=p.read_text(encoding='utf-8')
old='while(history.size()>100)history.remove(history.size()-1);'
if old not in s:
    raise SystemExit('Saved Memos limit anchor missing; refusing to build with an unpatched limit')
s=s.replace(old, '', 1)
p.write_text(s, encoding='utf-8')
print('Saved Memos limit removed: memos remain until manually deleted.')
