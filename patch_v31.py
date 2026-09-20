from pathlib import Path
import re

p=Path("app/src/main/java/com/memoprinter/eighty/MainActivity.java")
s=p.read_text(encoding="utf-8")

# Per-date serials.
s=s.replace('shell("নতুন তৈরি করুন","মেমো নং "+memoLabel(memoNo)+" • তারিখ পরিবর্তন করা যাবে",true);',
            'memoNo=nextMemoNoForDate(displayMemoDate());\n        shell("নতুন তৈরি করুন","মেমো নং "+memoLabel(memoNo)+" • তারিখ পরিবর্তন করা যাবে",true);',1)
s=s.replace('Memo readMemo(){ Memo m=new Memo(); m.no=memoNo; m.date=displayMemoDate();',
            'Memo readMemo(){ Memo m=new Memo(); m.date=displayMemoDate(); m.no=nextMemoNoForDate(m.date);',1)
s=s.replace('void persistMemo(Memo m){ boolean isNew=(m.no==memoNo); saveMemo(m); if(isNew){getPreferences(0).edit().putInt("memo",memoNo+1).apply();memoNo++;} }',
            'void persistMemo(Memo m){ saveMemo(m); memoNo=nextMemoNoForDate(m.date); getPreferences(0).edit().putInt("memo",memoNo).apply(); }',1)
s=s.replace('history.removeIf(x->x.no==m.no); history.add(0,m);',
            'history.removeIf(x->x.no==m.no && x.date.equals(m.date)); history.add(0,m);',1)

# Rename the existing V30 list renderer; a new outer renderer will show date folders.
s=s.replace('    void savedMemos(){\n        openScreen("saved");',
            '    void savedMemosList(String date){\n        openScreen("savedList");',1)

# Insert the date-folder screen immediately before the renamed list renderer.
marker='    void savedMemosList(String date){'
folder=r'''    void savedMemos(){
        openScreen("saved");
        shell("Saved Memos","Date-wise folders • local history",true);
        ScrollView sv=scroll(); LinearLayout c=content(sv);
        if(history.isEmpty()){ c.addView(tv("কোনো saved memo নেই",15,MUTED)); return; }
        ArrayList<String> dates=new ArrayList<>();
        for(Memo m:history) if(m.date!=null && !dates.contains(m.date)) dates.add(m.date);
        Collections.sort(dates,(a,b)->compareMemoDates(b,a));
        for(String date:dates){
            int count=countMemosForDate(date);
            LinearLayout f=card(); f.setOrientation(LinearLayout.HORIZONTAL); f.setGravity(Gravity.CENTER_VERTICAL);
            TextView i=tv("📁",30,TEXT); i.setGravity(Gravity.CENTER); f.addView(i,new LinearLayout.LayoutParams(dp(52),dp(64)));
            LinearLayout info=new LinearLayout(this); info.setOrientation(LinearLayout.VERTICAL);
            TextView t=tv(date,17,TEXT); t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            info.addView(t,new LinearLayout.LayoutParams(-1,dp(32)));
            info.addView(tv(bn(String.valueOf(count))+"টি Memo",13,MUTED),new LinearLayout.LayoutParams(-1,dp(25)));
            f.addView(info,new LinearLayout.LayoutParams(0,dp(70),1));
            TextView a=tv("›",30,BLUE); a.setGravity(Gravity.CENTER); f.addView(a,new LinearLayout.LayoutParams(dp(40),dp(70)));
            f.setOnClickListener(v->savedMemosList(date));
            c.addView(f,new LinearLayout.LayoutParams(-1,dp(90))); c.addView(gap(10));
        }
    }

    int countMemosForDate(String date){ int n=0; for(Memo m:history) if(date.equals(m.date)) n++; return n; }
    int nextMemoNoForDate(String date){ int max=0; for(Memo m:history) if(date!=null && date.equals(m.date)) max=Math.max(max,m.no); return max+1; }
    void renumberDate(String date){
        ArrayList<Memo> list=new ArrayList<>(); for(Memo m:history) if(date.equals(m.date)) list.add(m);
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
        }catch(Exception e){ return a.compareTo(b); }
    }

'''
if marker not in s: raise SystemExit("savedMemos marker missing")
s=s.replace(marker,folder+marker,1)

# Make the existing list screen show only the selected date, while keeping its V30 cards.
start=s.index('    void savedMemosList(String date){')
end=s.index('    void showSaved(Memo m)',start)
block=s[start:end]
block=block.replace('shell("Saved Memos","Local history • mark any memos and print together",true);',
                    'shell(date,"Saved Memos • "+bn(String.valueOf(countMemosForDate(date)))+"টি",true);',1)
block=block.replace('if(history.isEmpty()){', 'if(history.isEmpty()){',1)
# Every list/selection operation in this method should use only this date.
needle='        if(history.isEmpty()){\n            c.addView(tv("কোনো saved memo নেই",15,MUTED));\n            return;\n        }'
if needle in block:
    block=block.replace(needle,needle+'\n        ArrayList<Memo> visible=new ArrayList<>(); for(Memo z:history) if(date.equals(z.date)) visible.add(z); Collections.sort(visible,(a,b)->Integer.compare(a.no,b.no));',1)
block=block.replace('!history.isEmpty() && marked.size()==history.size()','!visible.isEmpty() && marked.size()==visible.size()')
block=block.replace('for(int i=0;i<history.size();i++){','for(int i=0;i<visible.size();i++){')
block=block.replace('marked.add(history.get(i));','marked.add(visible.get(i));')
block=block.replace('for(Memo m:history){','for(Memo m:visible){')
block=block.replace('history.removeAll(marked);\n                    marked.clear();\n                    saveHistory();',
                    'history.removeAll(marked);\n                    renumberDate(date);\n                    marked.clear();\n                    saveHistory();')
s=s[:start]+block+s[end:]

# Back navigation support for the new folder detail screen.
s=s.replace('else if("saved".equals(name)) savedMemos();',
            'else if("saved".equals(name)) savedMemos();\n        else if("savedList".equals(name)) savedMemos();',1)

# Fix the detail-screen route: savedMemos() above opens folders, while the list needs its date.
# Use a small field so Back can restore the selected folder.
s=s.replace('String currentScreen="home";',
            'String currentScreen="home";\n    String savedFolderDate="";',1)
s=s.replace('f.setOnClickListener(v->savedMemosList(date));',
            'f.setOnClickListener(v->{ savedFolderDate=date; savedMemosList(date); });',1)
s=s.replace('else if("savedList".equals(name)) savedMemos();',
            'else if("savedList".equals(name)) savedMemosList(savedFolderDate);',1)

# Normalize legacy V30 data on first load.
old='''    void loadHistory(){String raw=getPreferences(0).getString("history","[]");try{JSONArray a=new JSONArray(raw);for(int i=0;i<a.length();i++){JSONObject o=a.getJSONObject(i);Memo m=new Memo();m.no=o.optInt("no");m.date=o.optString("date");m.name=o.optString("name");m.address=o.optString("address");m.subtotal=o.optDouble("subtotal",o.optDouble("total"));m.discount=o.optDouble("discount",0);m.total=o.optDouble("total",m.subtotal-m.discount);JSONArray q=o.optJSONArray("items");if(q!=null)for(int j=0;j<q.length();j++){JSONObject x=q.getJSONObject(j);m.items.add(new Item(x.optString("name"),x.optString("qty"),x.optString("price"),x.optString("amount")));}history.add(m);}}catch(Exception ignored){}}'''
new='''    void loadHistory(){String raw=getPreferences(0).getString("history","[]");try{JSONArray a=new JSONArray(raw);for(int i=0;i<a.length();i++){JSONObject o=a.getJSONObject(i);Memo m=new Memo();m.no=o.optInt("no");m.date=o.optString("date");m.name=o.optString("name");m.address=o.optString("address");m.subtotal=o.optDouble("subtotal",o.optDouble("total"));m.discount=o.optDouble("discount",0);m.total=o.optDouble("total",m.subtotal-m.discount);JSONArray q=o.optJSONArray("items");if(q!=null)for(int j=0;j<q.length();j++){JSONObject x=q.getJSONObject(j);m.items.add(new Item(x.optString("name"),x.optString("qty"),x.optString("price"),x.optString("amount")));}history.add(m);} normalizeHistorySerials(); }catch(Exception ignored){}}\n    void normalizeHistorySerials(){ ArrayList<String> dates=new ArrayList<>(); for(Memo m:history) if(m.date!=null&&!dates.contains(m.date)) dates.add(m.date); for(String d:dates) renumberDate(d); saveHistory(); }'''
if old not in s: raise SystemExit("loadHistory anchor missing")
s=s.replace(old,new,1)

p.write_text(s,encoding="utf-8")
