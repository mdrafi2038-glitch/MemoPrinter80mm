from pathlib import Path
import re

p = Path("app/src/main/java/com/memoprinter/eighty/MainActivity.java")
s = p.read_text(encoding="utf-8")

# Always calculate the displayed memo number for the currently selected/default date.
s = s.replace(
    'void newMemo(){\n        boolean wasNewScreen = !"newMemo".equals(currentScreen);',
    'void newMemo(){\n        memoNo = nextMemoNoForDate(displayMemoDate());\n        boolean wasNewScreen = !"newMemo".equals(currentScreen);',
    1
)

# Route the date-folder detail screen correctly when navigating/back.
s = s.replace(
    'else if("saved".equals(name)) savedMemos();\n        else if("printer".equals(name))',
    'else if("saved".equals(name)) savedMemos();\n        else if("savedList".equals(name)) savedMemosList(savedFolderDate);\n        else if("printer".equals(name))',
    1
)

# Replace the whole Saved Memos section with a deterministic date-folder implementation.
start = s.find('    void savedMemos(){')
end = s.find('    void showSaved(Memo m)', start)
if start < 0 or end < 0:
    raise SystemExit("Saved Memos section anchors not found")

saved = r'''    void savedMemos(){
        openScreen("saved");
        shell("Saved Memos","Date-wise folders • local history",true);
        ScrollView sv=scroll();
        LinearLayout c=content(sv);

        if(history.isEmpty()){
            c.addView(tv("কোনো saved memo নেই",15,MUTED));
            return;
        }

        ArrayList<String> dates=new ArrayList<>();
        for(Memo m:history){
            if(m.date!=null && !m.date.trim().isEmpty() && !dates.contains(m.date))
                dates.add(m.date);
        }
        Collections.sort(dates,(a,b)->compareMemoDates(b,a));

        TextView hint=tv("প্রতিটি তারিখের মেমো আলাদা folder-এ রাখা হয়েছে",13,MUTED);
        hint.setPadding(dp(2),dp(2),dp(2),dp(12));
        c.addView(hint);

        for(String date:dates){
            int count=countMemosForDate(date);

            LinearLayout folder=card();
            folder.setOrientation(LinearLayout.HORIZONTAL);
            folder.setGravity(Gravity.CENTER_VERTICAL);
            folder.setPadding(dp(14),dp(12),dp(10),dp(12));
            folder.setClickable(true);
            folder.setFocusable(true);

            TextView icon=tv("📁",34,TEXT);
            icon.setGravity(Gravity.CENTER);
            folder.addView(icon,new LinearLayout.LayoutParams(dp(58),dp(76)));

            LinearLayout info=new LinearLayout(this);
            info.setOrientation(LinearLayout.VERTICAL);
            info.setGravity(Gravity.CENTER_VERTICAL);

            TextView title=tv(date,18,TEXT);
            title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            info.addView(title,new LinearLayout.LayoutParams(-1,dp(34)));

            TextView countTv=tv(bn(String.valueOf(count))+"টি Memo",14,MUTED);
            info.addView(countTv,new LinearLayout.LayoutParams(-1,dp(28)));

            folder.addView(info,new LinearLayout.LayoutParams(0,dp(76),1));

            TextView arrow=tv("›",32,BLUE);
            arrow.setGravity(Gravity.CENTER);
            folder.addView(arrow,new LinearLayout.LayoutParams(dp(42),dp(76)));

            folder.setOnClickListener(v->{
                savedFolderDate=date;
                savedMemosList(date);
            });

            c.addView(folder,new LinearLayout.LayoutParams(-1,dp(104)));
            c.addView(gap(10));
        }
    }

    String savedFolderDate="";

    int countMemosForDate(String date){
        int n=0;
        for(Memo m:history) if(date!=null && date.equals(m.date)) n++;
        return n;
    }

    int nextMemoNoForDate(String date){
        int max=0;
        for(Memo m:history){
            if(date!=null && date.equals(m.date)) max=Math.max(max,m.no);
        }
        return max+1;
    }

    void renumberDate(String date){
        ArrayList<Memo> list=new ArrayList<>();
        for(Memo m:history) if(date!=null && date.equals(m.date)) list.add(m);

        Collections.sort(list,(a,b)->Integer.compare(a.no,b.no));
        for(int i=0;i<list.size();i++) list.get(i).no=i+1;

        memoNo=nextMemoNoForDate(date);
        getPreferences(0).edit().putInt("memo",memoNo).apply();
    }

    int compareMemoDates(String a,String b){
        try{
            Date da=new SimpleDateFormat("dd/MM/yyyy",Locale.US).parse(a);
            Date db=new SimpleDateFormat("dd/MM/yyyy",Locale.US).parse(b);
            return da.compareTo(db);
        }catch(Exception e){
            return a.compareTo(b);
        }
    }

    void savedMemosList(String date){
        openScreen("savedList");
        shell(date,"Saved Memos • "+bn(String.valueOf(countMemosForDate(date)))+"টি",true);

        ScrollView sv=scroll();
        LinearLayout c=content(sv);

        ArrayList<Memo> visible=new ArrayList<>();
        for(Memo m:history) if(date!=null && date.equals(m.date)) visible.add(m);
        Collections.sort(visible,(a,b)->Integer.compare(a.no,b.no));

        if(visible.isEmpty()){
            c.addView(tv("এই তারিখে কোনো memo নেই",15,MUTED));
            return;
        }

        // Keep the existing V30 memo-card design inside the selected date folder.
        LinearLayout tools=new LinearLayout(this);
        tools.setOrientation(LinearLayout.VERTICAL);

        final ArrayList<Memo> marked=new ArrayList<>();
        final ArrayList<CheckBox> boxes=new ArrayList<>();

        LinearLayout selectRow=new LinearLayout(this);
        selectRow.setGravity(Gravity.CENTER_VERTICAL);
        TextView selected=tv("০টি selected",14,TEXT);
        selected.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        CheckBox all=new CheckBox(this);
        all.setText("সবগুলো Mark");
        all.setTextSize(13);
        all.setTextColor(TEXT);
        selectRow.addView(selected,new LinearLayout.LayoutParams(0,dp(52),1));
        selectRow.addView(all,new LinearLayout.LayoutParams(dp(125),dp(52)));
        tools.addView(selectRow);

        LinearLayout actionRow=new LinearLayout(this);
        Button bulkPrint=action("🖨  Marked Print");
        Button bulkDelete=lightAction("🗑  Marked Delete");
        actionRow.addView(bulkPrint,new LinearLayout.LayoutParams(0,dp(52),1));
        LinearLayout.LayoutParams deleteLp=new LinearLayout.LayoutParams(0,dp(52),1);
        deleteLp.setMargins(dp(8),0,0,0);
        actionRow.addView(bulkDelete,deleteLp);
        tools.addView(actionRow);

        c.addView(tools);
        c.addView(gap(10));

        final Runnable[] updateSelection=new Runnable[1];
        updateSelection[0]=()->{
            selected.setText(bn(String.valueOf(marked.size()))+"টি selected");
            boolean checked=!visible.isEmpty() && marked.size()==visible.size();
            all.setOnCheckedChangeListener(null);
            all.setChecked(checked);
            all.setOnCheckedChangeListener((button,value)->{
                marked.clear();
                for(int i=0;i<visible.size();i++){
                    CheckBox cb=boxes.get(i);
                    cb.setOnCheckedChangeListener(null);
                    cb.setChecked(value);
                    cb.setOnCheckedChangeListener((b,v)->{
                        Memo mm=(Memo)b.getTag();
                        if(v){ if(!marked.contains(mm)) marked.add(mm); }
                        else marked.remove(mm);
                        updateSelection[0].run();
                    });
                    if(value) marked.add(visible.get(i));
                }
                updateSelection[0].run();
            });
        };

        for(Memo m:visible){
            LinearLayout r=card();

            LinearLayout top=new LinearLayout(this);
            top.setGravity(Gravity.CENTER_VERTICAL);

            CheckBox mark=new CheckBox(this);
            mark.setText("Mark");
            mark.setTextSize(13);
            mark.setTextColor(BLUE_DARK);
            mark.setTag(m);

            TextView h=tv("মেমো নং "+memoLabel(m.no),18,TEXT);
            h.setTypeface(Typeface.DEFAULT,Typeface.BOLD);

            top.addView(mark,new LinearLayout.LayoutParams(dp(75),dp(48)));
            top.addView(h,new LinearLayout.LayoutParams(0,dp(48),1));
            r.addView(top);

            r.addView(tv(m.date+"  •  "+(m.name.isEmpty()?"No customer":m.name),13,MUTED));
            r.addView(tv("পণ্য: "+bn(String.valueOf(m.items.size()))+"   •   মোট: ৳"+bn(formatNumber(m.total)),14,TEXT));

            ImageView thumb=new ImageView(this);
            thumb.setImageBitmap(renderMemo(m));
            thumb.setAdjustViewBounds(true);
            thumb.setScaleType(ImageView.ScaleType.FIT_CENTER);
            thumb.setBackgroundColor(WHITE);
            thumb.setContentDescription("Saved memo preview");

            LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(-1,dp(260));
            tp.setMargins(0,dp(8),0,dp(8));
            r.addView(thumb,tp);
            thumb.setOnClickListener(v->showSaved(m));

            mark.setOnCheckedChangeListener((button,checked)->{
                if(checked){ if(!marked.contains(m)) marked.add(m); }
                else marked.remove(m);
                updateSelection[0].run();
            });

            r.addView(gap(7));

            LinearLayout a=new LinearLayout(this);
            Button view=lightAction("View");
            view.setOnClickListener(v->showSaved(m));
            Button print=action("Print");
            print.setOnClickListener(v->printMemo(m));

            a.addView(view,new LinearLayout.LayoutParams(0,50,1));
            LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(0,50,1);
            pp.setMargins(8,0,0,0);
            a.addView(print,pp);
            r.addView(a);

            c.addView(r);
            c.addView(gap(10));
            boxes.add(mark);
        }

        all.setOnCheckedChangeListener((button,value)->{
            marked.clear();
            for(int i=0;i<visible.size();i++){
                CheckBox cb=boxes.get(i);
                cb.setOnCheckedChangeListener(null);
                cb.setChecked(value);
                cb.setOnCheckedChangeListener((b,v)->{
                    Memo mm=(Memo)b.getTag();
                    if(v){ if(!marked.contains(mm)) marked.add(mm); }
                    else marked.remove(mm);
                    updateSelection[0].run();
                });
                if(value) marked.add(visible.get(i));
            }
            updateSelection[0].run();
        });

        bulkPrint.setOnClickListener(v->{
            if(marked.isEmpty()){
                toast("যে memoগুলো print করতে চান সেগুলো আগে Mark করুন");
                return;
            }
            printMemos(new ArrayList<>(marked));
        });

        bulkDelete.setOnClickListener(v->{
            if(marked.isEmpty()){
                toast("যে memoগুলো delete করতে চান সেগুলো আগে Mark করুন");
                return;
            }
            int count=marked.size();
            new AlertDialog.Builder(this)
                .setTitle("Marked Memo Delete")
                .setMessage(bn(String.valueOf(count))+"টি memo permanently delete করবেন?")
                .setNegativeButton("Cancel",null)
                .setPositiveButton("Delete",(d,w)->{
                    history.removeAll(marked);
                    renumberDate(date);
                    marked.clear();
                    saveHistory();
                    toast("Marked memo delete হয়েছে ✓");
                    savedMemosList(date);
                }).show();
        });

        updateSelection[0].run();
    }

'''
s = s[:start] + saved + s[end:]

p.write_text(s,encoding="utf-8")
