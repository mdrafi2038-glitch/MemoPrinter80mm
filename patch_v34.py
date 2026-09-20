from pathlib import Path
p=Path("app/src/main/java/com/memoprinter/eighty/MainActivity.java")
s=p.read_text(encoding="utf-8")

# Add a date-level total amount at the very bottom of each Saved Memos date folder.
anchor='''        updateSelection[0].run();
    }

    void showSaved(Memo m){'''
insert='''        updateSelection[0].run();

        // Date-wise total: sum the final total amount of every memo in this folder.
        double dateTotalAmount=0;
        for(Memo mm:visible) dateTotalAmount += mm.total;

        LinearLayout totalCard=card();
        totalCard.setPadding(dp(16),dp(18),dp(16),dp(18));
        TextView totalLabel=tv("এই তারিখের মোট Order Amount",16,MUTED);
        totalLabel.setGravity(Gravity.CENTER);
        totalCard.addView(totalLabel,new LinearLayout.LayoutParams(-1,dp(30)));

        TextView totalAmount=tv("৳"+bn(formatNumber(dateTotalAmount)),23,BLUE_DARK);
        totalAmount.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        totalAmount.setGravity(Gravity.CENTER);
        totalCard.addView(totalAmount,new LinearLayout.LayoutParams(-1,dp(42)));

        LinearLayout.LayoutParams totalLp=new LinearLayout.LayoutParams(-1,dp(96));
        totalLp.setMargins(0,dp(4),0,dp(20));
        c.addView(totalCard,totalLp);
    }

    void showSaved(Memo m){'''
if anchor not in s:
    raise SystemExit("Saved Memos total anchor missing")
s=s.replace(anchor,insert,1)
p.write_text(s,encoding="utf-8")
