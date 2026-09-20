from pathlib import Path

p=Path("app/src/main/java/com/memoprinter/eighty/MainActivity.java")
s=p.read_text(encoding="utf-8")

old_num='''    double num(String s){if(s==null)return 0;s=s.trim();StringBuilder b=new StringBuilder();for(char ch:s.toCharArray()){if(ch>='০'&&ch<='৯')b.append((char)('0'+ch-'০'));else if(ch==','||ch==' '||ch=='৳'){}else b.append(ch);}try{return Double.parseDouble(b.toString());}catch(Exception e){return 0;}}'''
new_num='''    double num(String s){
        if(s==null)return 0;
        s=s.trim();
        StringBuilder b=new StringBuilder();
        for(char ch:s.toCharArray()){
            if(ch>='০'&&ch<='৯') b.append((char)('0'+ch-'০'));
            else if(ch==','||ch==' '||ch=='৳') {}
            else b.append(ch);
        }
        String z=b.toString().trim();
        // Allow carton notation such as 1/c or 2/C. For calculations the
        // numeric carton count is used, while the original text is preserved
        // in the memo quantity column.
        if(z.matches("^\\\\d+(?:\\\\.\\\\d+)?\\\\s*/\\\\s*[cC]$")){
            int slash=z.indexOf('/');
            z=z.substring(0,slash).trim();
        }
        try{return Double.parseDouble(z);}catch(Exception e){return 0;}
    }'''
if(!s.includes(old_num)) throw new Error("num anchor missing");
s=s.replace(old_num,new_num,1);

const oldHint='final EditText n=input("পণ্যের নাম"); final EditText q=input("পরিমাণ — ২ / 2"); final EditText p=input("প্রতি পিস দাম — ২৫ / 25");';
const newHint='final EditText n=input("পণ্যের নাম"); final EditText q=input("পরিমাণ — ২ / 2 / 1/c"); final EditText p=input("প্রতি পিস দাম — ২৫ / 25");';
if(!s.includes(oldHint)) throw new Error("quantity hint anchor missing");
s=s.replace(oldHint,newHint,1);

const oldItem='Item item=new Item(name,bn(formatNumber(qty)),bn(formatNumber(price)),bn(formatNumber(qty*price)));';
const newItem='String qtyRaw=q.getText().toString().trim(); String qtyDisplay=isCartonQty(qtyRaw)?qtyRaw:bn(formatNumber(qty)); Item item=new Item(name,qtyDisplay,bn(formatNumber(price)),bn(formatNumber(qty*price)));';
if(!s.includes(oldItem)) throw new Error("item anchor missing");
s=s.replace(oldItem,newItem,1);

const oldFind='    Double findPrice(String name){ if(name==null)return null;';
const helper='    boolean isCartonQty(String s){ if(s==null)return false; String z=s.trim(); return z.matches("^[0-9০-৯]+(?:[.][0-9]+)?\\\\s*/\\\\s*[cC]$") || z.matches("^[0-9০-৯]+(?:[.][0-9]+)?\\\\s*কা$" ) || z.matches("^[0-9০-৯]+(?:[.][0-9]+)?\\s*কা$"); }\n';
if(!s.includes(oldFind)) throw new Error("findPrice anchor missing");
s=s.replace(oldFind,helper+oldFind,1);

p.write_text(s,encoding="utf-8")
