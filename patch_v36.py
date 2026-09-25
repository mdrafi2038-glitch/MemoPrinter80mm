from pathlib import Path
p=Path('app/src/main/java/com/memoprinter/eighty/MainActivity.java'); s=p.read_text(encoding='utf-8')
def rep(old,new,label):
 global s
 if old not in s: raise SystemExit('anchor missing: '+label)
 s=s.replace(old,new,1)
rep('EditText customer,address; TextView totalView, countView, dateView; Switch autoPrint; double discountAmount=0; String manualDate="";', 'EditText customer,address; TextView totalView, countView, dateView, timeView; Switch autoPrint; double discountAmount=0; String manualDate="", manualTime=""; int editingMemoNo=0; int editingHistoryIndex=-1;','fields')
rep('static class Memo { int no; String date,name,address;', 'static class Memo { int no; String date,time,name,address;','memo class')
rep('if(wasNewScreen){ items.clear(); discountAmount=0; manualDate=""; }','if(wasNewScreen && editingMemoNo<=0){ items.clear(); discountAmount=0; manualDate=""; manualTime=""; editingMemoNo=0; editingHistoryIndex=-1; }','reset')
rep('memoNo=nextMemoNoForDate(displayMemoDate());\n        shell("নতুন তৈরি করুন","মেমো নং "+memoLabel(memoNo)+" • তারিখ পরিবর্তন করা যাবে",true);','if(editingMemoNo<=0) memoNo=nextMemoNoForDate(displayMemoDate());\n        shell("নতুন তৈরি করুন",(editingMemoNo>0?"মেমো নং "+memoLabel(editingMemoNo)+" • Edit mode":"মেমো নং "+memoLabel(memoNo))+" • তারিখ/সময় পরিবর্তন করা যাবে",true);','number')
old='''        LinearLayout dateCard=card();
        LinearLayout dateRow=new LinearLayout(this); dateRow.setGravity(Gravity.CENTER_VERTICAL);
        LinearLayout dateInfo=new LinearLayout(this); dateInfo.setOrientation(LinearLayout.VERTICAL);
        dateInfo.addView(tv("মেমোর তারিখ",13,MUTED));
        dateView=tv(displayMemoDate(),18,TEXT); dateView.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        dateInfo.addView(dateView);
        dateRow.addView(dateInfo,new LinearLayout.LayoutParams(0,dp(56),1));
        Button editDate=lightAction("✎  Edit Date"); editDate.setOnClickListener(v->dateDialog());
        dateRow.addView(editDate,new LinearLayout.LayoutParams(dp(120),dp(50)));
        dateCard.addView(dateRow);
        c.addView(dateCard); c.addView(gap(12));'''
new='''        LinearLayout dateCard=card();
        LinearLayout dateRow=new LinearLayout(this); dateRow.setGravity(Gravity.CENTER_VERTICAL);
        LinearLayout dateInfo=new LinearLayout(this); dateInfo.setOrientation(LinearLayout.VERTICAL);
        dateInfo.addView(tv("মেমোর তারিখ",13,MUTED));
        dateView=tv(displayMemoDate(),18,TEXT); dateView.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        dateInfo.addView(dateView);
        dateRow.addView(dateInfo,new LinearLayout.LayoutParams(0,dp(56),1));
        Button editDate=lightAction("✎  Edit Date"); editDate.setOnClickListener(v->dateDialog());
        dateRow.addView(editDate,new LinearLayout.LayoutParams(dp(120),dp(50)));
        LinearLayout timeInfo=new LinearLayout(this); timeInfo.setOrientation(LinearLayout.VERTICAL); timeInfo.addView(tv("সময়",13,MUTED));
        timeView=tv(displayMemoTime(),18,TEXT); timeView.setTypeface(Typeface.DEFAULT,Typeface.BOLD); timeInfo.addView(timeView);
        dateRow.addView(timeInfo,new LinearLayout.LayoutParams(dp(110),dp(56)));
        Button editTime=lightAction("Edit Time"); editTime.setOnClickListener(v->timeDialog());
        dateRow.addView(editTime,new LinearLayout.LayoutParams(dp(105),dp(50)));
        dateCard.addView(dateRow); c.addView(dateCard); c.addView(gap(12));'''
rep(old,new,'date card')
rep('''        dlg.setTitle("মেমোর তারিখ");
        dlg.setButton(DialogInterface.BUTTON_NEUTRAL,"পরের দিনের তারিখ",(d,w)->{ manualDate=""; if(dateView!=null)dateView.setText(displayMemoDate()); updateLivePreview(); });
        dlg.show();''','''        dlg.setTitle("Custom Date");
        dlg.show();''','date dialog')
rep('''    String displayMemoDate(){ return manualDate==null||manualDate.trim().isEmpty()?memoDate():manualDate; }

    void automaticInput(){''','''    String todayDate(){return new SimpleDateFormat("dd/MM/yyyy",Locale.getDefault()).format(new Date());}
    String plusDaysDate(int days){Calendar c=Calendar.getInstance();c.add(Calendar.DAY_OF_YEAR,days);return new SimpleDateFormat("dd/MM/yyyy",Locale.getDefault()).format(c.getTime());}
    String currentTime(){return new SimpleDateFormat("hh:mm a",Locale.getDefault()).format(new Date());}
    String displayMemoDate(){ return manualDate==null||manualDate.trim().isEmpty()?todayDate():manualDate; }
    String displayMemoTime(){ return manualTime==null||manualTime.trim().isEmpty()?currentTime():manualTime; }
    void timeDialog(){Calendar c=Calendar.getInstance();try{c.setTime(new SimpleDateFormat("hh:mm a",Locale.getDefault()).parse(displayMemoTime()));}catch(Exception ignored){} TimePickerDialog dlg=new TimePickerDialog(this,(v,h,m)->{Calendar x=Calendar.getInstance();x.set(Calendar.HOUR_OF_DAY,h);x.set(Calendar.MINUTE,m);manualTime=new SimpleDateFormat("hh:mm a",Locale.getDefault()).format(x.getTime());if(timeView!=null)timeView.setText(manualTime);updateLivePreview();},c.get(Calendar.HOUR_OF_DAY),c.get(Calendar.MINUTE),false);dlg.setTitle("Edit Time");dlg.show();}

    void automaticInput(){''','helpers')
rep('Memo readMemo(){ Memo m=new Memo(); m.date=displayMemoDate(); m.no=nextMemoNoForDate(m.date);','Memo readMemo(){ Memo m=new Memo(); m.date=displayMemoDate(); m.time=displayMemoTime(); m.no=editingMemoNo>0?editingMemoNo:nextMemoNoForDate(m.date);','read')
rep('''    void persistMemo(Memo m){ saveMemo(m); memoNo=nextMemoNoForDate(m.date); getPreferences(0).edit().putInt("memo",memoNo).apply(); }
    void saveMemo(Memo m){ history.removeIf(x->x.no==m.no && x.date.equals(m.date)); history.add(0,m); while(history.size()>100)history.remove(history.size()-1); saveHistory(); }''','''    void persistMemo(Memo m){
        if(editingMemoNo>0 && editingHistoryIndex>=0 && editingHistoryIndex<history.size()){
            history.set(editingHistoryIndex,m); saveHistory(); editingMemoNo=0; editingHistoryIndex=-1; return;
        }
        saveMemo(m); memoNo=nextMemoNoForDate(m.date); getPreferences(0).edit().putInt("memo",memoNo).apply();
    }
    void saveMemo(Memo m){ history.removeIf(x->x.no==m.no && x.date.equals(m.date)); history.add(0,m); while(history.size()>100)history.remove(history.size()-1); saveHistory(); }''','persist')
rep('Collections.sort(visible,(a,b)->Integer.compare(a.no,b.no));','Collections.sort(visible,(a,b)->Integer.compare(b.no,a.no));','order')
rep('r.addView(tv(m.date+"  •  "+(m.name.isEmpty()?"No customer":m.name),13,MUTED));','r.addView(tv(m.date+"  •  "+(m.time==null||m.time.isEmpty()?"সময় নেই":m.time)+"  •  "+(m.name.isEmpty()?"No customer":m.name),13,MUTED));','time')
old='''            Button view=lightAction("View");
            view.setOnClickListener(v->showSaved(m));
            Button print=action("Print");
            print.setOnClickListener(v->printMemo(m));

            a.addView(view,new LinearLayout.LayoutParams(0,50,1));
            LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(0,50,1);
            pp.setMargins(8,0,0,0);
            a.addView(print,pp);'''
new='''            Button view=lightAction("View");
            view.setOnClickListener(v->showSaved(m));
            Button editMemo=lightAction("Edit");
            editMemo.setOnClickListener(v->editSavedMemo(m));
            Button print=action("Print");
            print.setOnClickListener(v->printMemo(m));

            a.addView(view,new LinearLayout.LayoutParams(0,50,1));
            LinearLayout.LayoutParams ep=new LinearLayout.LayoutParams(0,50,1); ep.setMargins(6,0,0,0); a.addView(editMemo,ep);
            LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(0,50,1); pp.setMargins(6,0,0,0); a.addView(print,pp);'''
rep(old,new,'button')
rep('    void showSaved(Memo m){','''    void editSavedMemo(Memo m){editingMemoNo=m.no;editingHistoryIndex=history.indexOf(m);items.clear();for(Item x:m.items)items.add(new Item(x.name,x.qty,x.price,x.amount));discountAmount=m.discount;manualDate=m.date;manualTime=(m.time==null?"":m.time);newMemo();if(customer!=null)customer.setText(m.name);if(address!=null)address.setText(m.address);if(dateView!=null)dateView.setText(displayMemoDate());if(timeView!=null)timeView.setText(displayMemoTime());refreshProducts();}
    void showSaved(Memo m){''','edit')
rep('o.put("date",m.date);o.put("name",m.name);','o.put("date",m.date);o.put("time",m.time==null?"":m.time);o.put("name",m.name);','save time')
rep('m.date=o.optString("date");m.name=o.optString("name");','m.date=o.optString("date");m.time=o.optString("time","");m.name=o.optString("name");','load time')
rep('m.no=0;m.date=memoDate();m.name="TEST";','m.no=0;m.date=memoDate();m.time=currentTime();m.name="TEST";','sample')
p.write_text(s,encoding='utf-8')