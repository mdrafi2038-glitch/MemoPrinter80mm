from pathlib import Path

p=Path("app/src/main/java/com/memoprinter/eighty/MainActivity.java")
s=p.read_text(encoding="utf-8")
old="""        Bitmap src=BitmapFactory.decodeResource(getResources(), R.drawable.memo_template);
        if(src==null) throw new IllegalStateException("Memo template could not be loaded");
        // Keep a small safety margin on both sides for real 80mm ESC/POS printers.
        // The old template size is preserved, but the printable bitmap is limited
        // to 560 dots so common 80mm mechanisms do not clip the edges.
        final int w=560;
        final float sx=w/(float)src.getWidth();
        final int h=Math.round(src.getHeight()*sx);
        Bitmap b=Bitmap.createScaledBitmap(src,w,h,true).copy(Bitmap.Config.ARGB_8888,true);"""
new="""        // Decode the template close to the final print width. This avoids loading
        // a very large memo image into memory, which can make Preview fail.
        final int w=560;
        android.graphics.BitmapFactory.Options bounds=new android.graphics.BitmapFactory.Options();
        bounds.inJustDecodeBounds=true;
        BitmapFactory.decodeResource(getResources(),R.drawable.memo_template,bounds);
        if(bounds.outWidth<=0 || bounds.outHeight<=0)
            throw new IllegalStateException("Memo template could not be loaded");
        android.graphics.BitmapFactory.Options opts=new android.graphics.BitmapFactory.Options();
        opts.inPreferredConfig=Bitmap.Config.ARGB_8888;
        int sample=1;
        while((bounds.outWidth/sample)>w*2) sample*=2;
        opts.inSampleSize=sample;
        Bitmap src=BitmapFactory.decodeResource(getResources(),R.drawable.memo_template,opts);
        if(src==null) throw new IllegalStateException("Memo template could not be decoded");
        final float sx=w/(float)src.getWidth();
        final int h=Math.max(1,Math.round(src.getHeight()*sx));
        Bitmap b=Bitmap.createScaledBitmap(src,w,h,true).copy(Bitmap.Config.ARGB_8888,true);
        if(b==null) throw new IllegalStateException("Memo bitmap could not be created");"""
if old not in s: raise SystemExit("render anchor not found")
p.write_text(s.replace(old,new,1),encoding="utf-8")
