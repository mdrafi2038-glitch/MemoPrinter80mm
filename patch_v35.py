from pathlib import Path

p = Path("app/src/main/java/com/memoprinter/eighty/MainActivity.java")
s = p.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(label + " anchor missing")
    s = s.replace(old, new, 1)

# Carton quantity support + pieces-per-carton settings.
replace_once(
    '    final LinkedHashMap<String,Double> prices=new LinkedHashMap<>();',
    '    final LinkedHashMap<String,Double> prices=new LinkedHashMap<>();\n    final LinkedHashMap<String,Double> cartonPcs=new LinkedHashMap<>();',
    'field'
)

replace_once(
    'loadPrices(); loadHistory(); loadPrinter(); home();',
    'loadPrices(); loadCartonPcs(); loadHistory(); loadPrinter(); home();',
    'startup'
)

old_num = '''    double num(String s){if(s==null)return 0;s=s.trim();StringBuilder b=new StringBuilder();for(char ch:s.toCharArray()){if(ch>='০'&&ch<='৯')b.append((char)('0'+ch-'০'));else if(ch==','||ch==' '||ch=='৳'){}else b.append(ch);}try{return Double.parseDouble(b.toString());}catch(Exception e){return 0;}}'''
new_num = '''    double num(String s){
        if(s==null)return 0;
        s=s.trim();
        StringBuilder b=new StringBuilder();
        for(char ch:s.toCharArray()){
            if(ch>='০'&&ch<='৯') b.append((char)('0'+ch-'০'));
            else if(ch==','||ch==' '||ch=='৳') {}
            else b.append(ch);
        }
        String z=b.toString().trim();
        if(z.matches("^\\\\d+(?:\\\\.\\\\d+)?\\\\s*/\\\\s*[cC]$")) z=z.substring(0,z.indexOf('/')).trim();
        else if(z.matches("^\\\\d+(?:\\\\.\\\\d+)?\\\\s*কা$")) z=z.substring(0,z.length()-2).trim();
        try{return Double.parseDouble(z);}catch(Exception e){return 0;}
    }'''
replace_once(old_num,new_num,'num')

replace_once(
    'final EditText n=input("পণ্যের নাম"); final EditText q=input("পরিমাণ — ২ / 2"); final EditText p=input("প্রতি পিস দাম — ২৫ / 25");',
    'final EditText n=input("পণ্যের নাম"); final EditText q=input("পরিমাণ — ২ / 2 / ১কা / 1/c"); final EditText p=input("প্রতি পিস দাম — ২৫ / 25");',
    'quantity hint'
)

replace_once(
    'Item item=new Item(name,bn(formatNumber(qty)),bn(formatNumber(price)),bn(formatNumber(qty*price)));',
    'String qtyRaw=q.getText().toString().trim(); double calcQty=num(qtyRaw); String qtyDisplay=isCartonQty(qtyRaw)?qtyRaw:bn(formatNumber(qty)); Item item=new Item(name,qtyDisplay,bn(formatNumber(price)),bn(formatNumber(calcQty*price)));',
    'manual item'
)

replace_once(
    'out.items.add(new Item(bnName,bn(formatNumber(qty)),bn(formatNumber(price)),bn(formatNumber(qty*price))));',
    'double calcQty=num(qtyText); String qtyDisplay=isCartonQty(qtyText)?qtyText:bn(formatNumber(qty)); out.items.add(new Item(bnName,qtyDisplay,bn(formatNumber(price)),bn(formatNumber(calcQty*price))));',
    'automatic item'
)

helpers = '''    boolean isCartonQty(String s){
        if(s==null)return false;
        String z=s.trim();
        return z.matches("^[0-9০-৯]+(?:[.][0-9]+)?\\\\s*/\\\\s*[cC]$")
            || z.matches("^[0-9০-৯]+(?:[.][0-9]+)?\\\\s*কা$");
    }
    Double findCartonPcs(String name){
        if(name==null)return null;
        String q=name.trim();
        for(String k:cartonPcs.keySet()) if(k.equalsIgnoreCase(q)) return cartonPcs.get(k);
        return null;
    }
    Double findCartonPcsAny(String raw,String converted){
        Double v=findCartonPcs(raw); if(v!=null)return v;
        return findCartonPcs(converted);
    }
    double quantityInPieces(String product,String qtyText){
        double q=num(qtyText);
        if(!isCartonQty(qtyText)) return q;
        Double pcs=findCartonPcs(product);
        return pcs==null ? -1 : q*pcs;
    }
    double quantityInPiecesAny(String raw,String converted,String qtyText){
        double q=num(qtyText);
        if(!isCartonQty(qtyText)) return q;
        Double pcs=findCartonPcsAny(raw,converted);
        return pcs==null ? -1 : q*pcs;
    }

'''
replace_once('    void loadPrices(){', helpers+'    void loadPrices(){','helpers')

old_save = '''    void savePrices(){try{JSONObject o=new JSONObject();for(String k:prices.keySet())o.put(k,prices.get(k));getPreferences(0).edit().putString("prices",o.toString()).apply();}catch(Exception ignored){}}'''
new_save = '''    void savePrices(){try{JSONObject o=new JSONObject();for(String k:prices.keySet())o.put(k,prices.get(k));getPreferences(0).edit().putString("prices",o.toString()).apply();}catch(Exception ignored){}}
    void loadCartonPcs(){String raw=getPreferences(0).getString("carton_pcs","{}");try{JSONObject o=new JSONObject(raw);Iterator<String>it=o.keys();while(it.hasNext()){String k=it.next();double v=o.optDouble(k,0);if(v>0)cartonPcs.put(k,v);}}catch(Exception ignored){}}
    void saveCartonPcs(){try{JSONObject o=new JSONObject();for(String k:cartonPcs.keySet())o.put(k,cartonPcs.get(k));getPreferences(0).edit().putString("carton_pcs",o.toString()).apply();}catch(Exception ignored){}}'''
replace_once(old_save,new_save,'savePrices')

old_settings = '''void settings(){ openScreen("settings"); shell("Settings","পণ্য ও default price",true);ScrollView sv=scroll();LinearLayout c=content(sv);c.addView(section("Default Product Price"));LinearLayout add=card();EditText n=input("পণ্যের নাম");EditText p=input("ডিফল্ট প্রতি পিস দাম");p.setInputType(android.text.InputType.TYPE_CLASS_TEXT);add.addView(n);add.addView(gap(8));add.addView(p);add.addView(gap(8));Button save=action("＋  Save / Update Price");save.setOnClickListener(v->{String name=n.getText().toString().trim();double val=num(p.getText().toString());if(name.isEmpty()||val<=0){toast("পণ্য ও দাম সঠিকভাবে দিন");return;}prices.put(name,val);savePrices();n.setText("");p.setText("");refreshCurrentScreen();});add.addView(save);c.addView(add);c.addView(gap(14));c.addView(section("Saved Prices"));if(prices.isEmpty())c.addView(tv("কোনো default price save করা নেই",14,MUTED));for(String k:new ArrayList<>(prices.keySet())){LinearLayout r=card();r.setOrientation(LinearLayout.HORIZONTAL);TextView a=tv(k,15,TEXT);a.setTypeface(Typeface.DEFAULT,Typeface.BOLD);TextView b=tv("৳"+bn(formatNumber(prices.get(k))),15,MUTED);b.setGravity(Gravity.RIGHT);Button del=lightAction("Delete");del.setOnClickListener(v->{prices.remove(k);savePrices();refreshCurrentScreen();});r.addView(a,new LinearLayout.LayoutParams(0,dp(50),1));r.addView(b,new LinearLayout.LayoutParams(dp(85),dp(50)));r.addView(del,new LinearLayout.LayoutParams(dp(82),dp(50)));c.addView(r);c.addView(gap(8));}}'''
new_settings = '''void settings(){ openScreen("settings"); shell("Settings","পণ্য, default price ও carton pcs",true);ScrollView sv=scroll();LinearLayout c=content(sv);c.addView(section("Default Product Price + Carton Setting"));LinearLayout add=card();EditText n=input("পণ্যের নাম");EditText p=input("ডিফল্ট প্রতি পিস দাম");EditText cp=input("১ কার্টুনে কত পিস? যেমন ২৪");p.setInputType(android.text.InputType.TYPE_CLASS_TEXT);cp.setInputType(android.text.InputType.TYPE_CLASS_TEXT);add.addView(n);add.addView(gap(8));add.addView(p);add.addView(gap(8));add.addView(cp);add.addView(gap(4));add.addView(tv("যেমন: Pata → ১ কার্টুন = ২৪ pcs. এই সেটিং থাকলে ১কা = ২৪ pcs হিসেবে হিসাব হবে।",12,MUTED));add.addView(gap(8));Button save=action("＋  Save / Update");save.setOnClickListener(v->{String name=n.getText().toString().trim();double val=num(p.getText().toString());String cpRaw=cp.getText().toString().trim();double cpVal=cpRaw.isEmpty()?0:num(cpRaw);if(name.isEmpty()||val<=0){toast("পণ্য ও দাম সঠিকভাবে দিন");return;}prices.put(name,val);if(cpVal>0)cartonPcs.put(name,cpVal);else cartonPcs.remove(name);savePrices();saveCartonPcs();n.setText("");p.setText("");cp.setText("");refreshCurrentScreen();});add.addView(save);c.addView(add);c.addView(gap(14));c.addView(section("Saved Product Settings"));if(prices.isEmpty())c.addView(tv("কোনো product save করা নেই",14,MUTED));for(String k:new ArrayList<>(prices.keySet())){LinearLayout r=card();r.setOrientation(LinearLayout.HORIZONTAL);LinearLayout info=new LinearLayout(this);info.setOrientation(LinearLayout.VERTICAL);TextView a=tv(k,15,TEXT);a.setTypeface(Typeface.DEFAULT,Typeface.BOLD);info.addView(a);Double cpv=cartonPcs.get(k);info.addView(tv("৳"+bn(formatNumber(prices.get(k)))+" / pcs"+(cpv!=null?"   •   ১ carton = "+bn(formatNumber(cpv))+" pcs":"   •   carton setting নেই"),12,MUTED));Button del=lightAction("Delete");del.setOnClickListener(v->{prices.remove(k);cartonPcs.remove(k);savePrices();saveCartonPcs();refreshCurrentScreen();});r.addView(info,new LinearLayout.LayoutParams(0,dp(60),1));r.addView(del,new LinearLayout.LayoutParams(dp(82),dp(60)));c.addView(r);c.addView(gap(8));}}'''
replace_once(old_settings,new_settings,'settings')

# Summary uses pieces, not carton count.
old_summary='double v=num(x.optString("qty"));if(old==null)m.put(n,v);else m.put(old,m.get(old)+v);'
new_summary='double v=quantityInPieces(n,x.optString("qty"));if(v<0)v=0;if(old==null)m.put(n,v);else m.put(old,m.get(old)+v);'
if old_summary in s:
    s=s.replace(old_summary,new_summary,1)

p.write_text(s,encoding="utf-8")
