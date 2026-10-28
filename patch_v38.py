from pathlib import Path

p = Path('app/src/main/java/com/memoprinter/eighty/MainActivity.java')
s = p.read_text(encoding='utf-8')

field = '    final ArrayList<Memo> history=new ArrayList<>();'
field_new = field + '\n    // Render Saved Memos thumbnails off the UI thread, one at a time.\n    final java.util.concurrent.ExecutorService memoPreviewExecutor = java.util.concurrent.Executors.newSingleThreadExecutor();'
if field in s:
    s = s.replace(field, field_new, 1)
elif 'memoPreviewExecutor' not in s:
    raise SystemExit('Memo history field not found; refusing unsafe patch')

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
new = '''            ImageView thumb=new ImageView(this);
            thumb.setAdjustViewBounds(true);
            thumb.setScaleType(ImageView.ScaleType.FIT_CENTER);
            thumb.setBackgroundColor(WHITE);
            thumb.setContentDescription("Saved memo preview");
            LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(-1,dp(260));
            tp.setMargins(0,dp(8),0,dp(8));
            r.addView(thumb,tp);
            thumb.setOnClickListener(v->showSaved(m));
            // Preserve the existing thumbnail UI, but render its bitmap in the
            // background so opening Saved Memos does not freeze the screen.
            memoPreviewExecutor.execute(() -> {
                Bitmap preview = renderMemo(m);
                runOnUiThread(() -> {
                    if (thumb.getParent() != null) thumb.setImageBitmap(preview);
                    else if (preview != null && !preview.isRecycled()) preview.recycle();
                });
            });
'''
if old in s:
    s = s.replace(old, new, 1)
elif 'memoPreviewExecutor.execute(() -> {' not in s:
    raise SystemExit('Saved Memos thumbnail block not found; refusing unsafe patch')
p.write_text(s, encoding='utf-8')
print('Saved Memos optimized: preserved thumbnail UI and renders previews in the background.')
