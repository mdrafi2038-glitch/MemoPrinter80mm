from pathlib import Path

p = Path('app/src/main/java/com/memoprinter/eighty/MainActivity.java')
s = p.read_text(encoding='utf-8')

old = '''            ImageView thumb=new ImageView(this);
            thumb.setImageBitmap(renderMemo(m));
            thumb.setAdjustViewBounds(true);
            thumb.setScaleType(ImageView.ScaleType.FIT_CENTER);
            thumb.setBackgroundColor(WHITE);
            thumb.setContentDescription("Saved memo preview");
            LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(-1,dp(260));
            tp.setMargins(0,dp(8),0,dp(8));
            r.addView(thumb,tp);
            thumb.setOnClickListener(v->showSaved(m));
'''
new = '''            // Keep Saved Memos responsive: do not render a full-size memo bitmap
            // synchronously for every history row. Preview is generated only when
            // the user taps View (showSaved), while the list stays lightweight.
            TextView previewHint=tv("📄 Memo preview • View চাপুন",12,MUTED);
            previewHint.setGravity(Gravity.CENTER);
            previewHint.setBackground(shape(0xFFF8FAFC,12));
            LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(-1,dp(44));
            tp.setMargins(0,dp(8),0,dp(8));
            r.addView(previewHint,tp);
            previewHint.setOnClickListener(v->showSaved(m));
'''
if old not in s:
    raise SystemExit('Saved Memos thumbnail block not found; refusing unsafe patch')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('Saved Memos optimized: removed synchronous full memo rendering from every list row.')
