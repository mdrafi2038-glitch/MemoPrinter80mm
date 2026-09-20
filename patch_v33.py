from pathlib import Path
p=Path("app/src/main/java/com/memoprinter/eighty/MainActivity.java")
s=p.read_text(encoding="utf-8")

# Editing state for an existing saved order.
s=s.replace('String currentScreen="home";',
            'String currentScreen="home";\n    int editingMemoNo=-1; String editingMemoDate="";',1)

# Preserve the existing memo number when editing; new memos still get the next number for that date.
old='Memo readMemo(){ Memo m=new Memo(); m.date=displayMemoDate(); m.no=nextMemoNoForDate(m.date);'
new='Memo readMemo(){ Memo m=new Memo(); m.date=displayMemoDate(); m.no=(editingMemoNo>0 && m.date.equals(editingMemoDate))?editingMemoNo:nextMemoNoForDate(m.date);'
if old not in s: raise SystemExit("readMemo anchor missing")
s=s.replace(old,new,1)

# Replace persist logic so editing updates the same order instead of creating a new one.
old='void persistMemo(Memo m){ saveMemo(m); memoNo=nextMemoNoForDate(m.date); getPreferences(0).edit().putInt("memo",memoNo).apply(); }'
new='void persistMemo(Memo m){ saveMemo(m); memoNo=nextMemoNoForDate(m.date); getPreferences(0).edit().putInt("memo",memoNo).apply(); editingMemoNo=-1; editingMemoDate=""; }'
if old not in s: raise SystemExit("persistMemo anchor missing")
s=s.replace(old,new,1)

# Add Update Order action to each saved memo card.
old='''            Button view=lightAction("View");
            view.setOnClickListener(v->showSaved(m));
            Button print=action("Print");
            print.setOnClickListener(v->printMemo(m));

            a.addView(view,new LinearLayout.LayoutParams(0,50,1));
            LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(0,50,1);
            pp.setMargins(8,0,0,0);
            a.addView(print,pp);
            r.addView(a);'''
new='''            Button update=lightAction("✎  Update Order");
            update.setOnClickListener(v->editSavedMemo(m));
            Button view=lightAction("View");
            view.setOnClickListener(v->showSaved(m));
            Button print=action("Print");
            print.setOnClickListener(v->printMemo(m));

            a.addView(update,new LinearLayout.LayoutParams(0,50,1));
            LinearLayout.LayoutParams vp=new LinearLayout.LayoutParams(0,50,1);
            vp.setMargins(6,0,6,0);
            a.addView(view,vp);
            a.addView(print,new LinearLayout.LayoutParams(0,50,1));
            r.addView(a);'''
if old not in s: raise SystemExit("card buttons anchor missing")
s=s.replace(old,new,1)

# Insert editor method before showSaved.
marker='    void showSaved(Memo m){'
method=r'''    void editSavedMemo(Memo m){
        editingMemoNo=m.no;
        editingMemoDate=m.date;
        manualDate=m.date;
        items.clear();
        for(Item x:m.items) items.add(new Item(x.name,x.qty,x.price,x.amount));
        discountAmount=m.discount;

        newMemo();
        editingMemoNo=m.no;
        editingMemoDate=m.date;
        manualDate=m.date;
        if(dateView!=null) dateView.setText(m.date);
        if(customer!=null) customer.setText(m.name);
        if(address!=null) address.setText(m.address);
        items.clear();
        for(Item x:m.items) items.add(new Item(x.name,x.qty,x.price,x.amount));
        discountAmount=m.discount;
        memoNo=m.no;
        refreshProducts();
        updateLivePreview();
        toast("Order update mode চালু হয়েছে — পরিবর্তন করে Save Memo দিন");
    }

'''
if marker not in s: raise SystemExit("showSaved marker missing")
s=s.replace(marker,method+marker,1)

p.write_text(s,encoding="utf-8")
