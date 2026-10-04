from pathlib import Path
p=Path('app/src/main/java/com/memoprinter/eighty/MainActivity.java')
s=p.read_text(encoding='utf-8')
start=s.find('    void previewMemo(){')
if start<0: raise SystemExit('previewMemo not found')
depth=0; endpos=None
for i in range(start,len(s)):
    if s[i]=='{': depth+=1
    elif s[i]=='}':
        depth-=1
        if depth==0: endpos=i+1; break
if endpos is None: raise SystemExit('previewMemo end not found')
new='''    void previewMemo(){
        try {
            final Memo m=readMemo();
            ScrollView sv=new ScrollView(this);
            sv.setFillViewport(true);
            LinearLayout box=new LinearLayout(this);
            box.setOrientation(LinearLayout.VERTICAL);
            box.setPadding(dp(8),dp(8),dp(8),dp(8));
            ImageView image=new ImageView(this);
            image.setAdjustViewBounds(true);
            image.setScaleType(ImageView.ScaleType.FIT_CENTER);
            image.setBackgroundColor(WHITE);
            image.setContentDescription("80mm memo preview");
            image.setImageBitmap(renderMemo(m));
            box.addView(image,new LinearLayout.LayoutParams(-1,-2));
            sv.addView(box);
            AlertDialog dlg=new AlertDialog.Builder(this)
                    .setTitle("Print Preview • 80mm")
                    .setView(sv)
                    .setNegativeButton("Close",null)
                    .setPositiveButton("🖨 Print",null)
                    .create();
            dlg.setOnShowListener(v -> {
                Button print=dlg.getButton(AlertDialog.BUTTON_POSITIVE);
                print.setOnClickListener(x -> {
                    try { printMemo(m); dlg.dismiss(); }
                    catch(Throwable e){ Toast.makeText(MainActivity.this,"Print error: "+e.getMessage(),Toast.LENGTH_LONG).show(); }
                });
            });
            dlg.show();
        } catch(Throwable e) {
            Toast.makeText(this,"Preview error: "+(e.getMessage()==null?"Unable to create preview":e.getMessage()),Toast.LENGTH_LONG).show();
        }
    }'''
s=s[:start]+new+s[endpos:]
p.write_text(s,encoding='utf-8')
