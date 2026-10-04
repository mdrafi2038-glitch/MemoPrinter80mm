from pathlib import Path

p = Path("app/src/main/java/com/memoprinter/eighty/MainActivity.java")
s = p.read_text(encoding="utf-8")

old = """    void previewMemo(){
        if(items.isEmpty()){toast("কমপক্ষে ১টি পণ্য যোগ করুন");return;}
        Memo m=readMemo();
        LinearLayout box=new LinearLayout(this); box.setOrientation(LinearLayout.VERTICAL); box.setPadding(dp(8),dp(8),dp(8),dp(8));
        ImageView image=new ImageView(this); image.setImageBitmap(renderMemo(m)); image.setAdjustViewBounds(true); image.setScaleType(ImageView.ScaleType.FIT_CENTER); image.setBackgroundColor(WHITE); box.addView(image,new LinearLayout.LayoutParams(-1,-2));
        AlertDialog dlg=new AlertDialog.Builder(this).setTitle("Print Preview • 80mm").setView(box).setNegativeButton("Close",null).setPositiveButton("🖨 Print",(d,w)->printMemo(m)).create(); dlg.show();
    }"""

new = """    void previewMemo(){
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
            Bitmap previewBitmap=renderMemo(m);
            image.setImageBitmap(previewBitmap);
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
                    try {
                        printMemo(m);
                        dlg.dismiss();
                    } catch(Throwable e) {
                        Toast.makeText(MainActivity.this,"Print error: "+e.getMessage(),Toast.LENGTH_LONG).show();
                    }
                });
            });
            dlg.show();
        } catch(Throwable e) {
            Toast.makeText(this,"Preview error: "+(e.getMessage()==null?"Unable to create preview":e.getMessage()),Toast.LENGTH_LONG).show();
        }
    }"""

if old not in s:
    raise SystemExit("previewMemo block not found")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
