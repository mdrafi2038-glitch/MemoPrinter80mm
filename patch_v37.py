from pathlib import Path
root=Path('.')
main=root/'app/src/main/java/com/memoprinter/eighty/MainActivity.java'
s=main.read_text(encoding='utf-8')
if "UpdateActivity" in s:
    main.write_text(s,encoding="utf-8")
    raise SystemExit(0)
anchor='''        c.addView(r4,new LinearLayout.LayoutParams(-1,dp(142)));
        c.addView(gap(10));

        LinearLayout info=card();'''
insert='''        c.addView(r4,new LinearLayout.LayoutParams(-1,dp(142)));
        c.addView(gap(10));

        LinearLayout r5=new LinearLayout(this); r5.setOrientation(LinearLayout.HORIZONTAL);
        homeCard(r5,"⬆","Update APK","ZIP/APK দিয়ে app update",v->{startActivity(new Intent(this,UpdateActivity.class));});
        c.addView(r5,new LinearLayout.LayoutParams(-1,dp(142)));
        c.addView(gap(10));

        LinearLayout info=card();'''
if anchor in s:
    s=s.replace(anchor,insert,1)
main.write_text(s,encoding='utf-8')

(root/'app/src/main/java/com/memoprinter/eighty/UpdateActivity.java').write_text(r'''package com.memoprinter.eighty;
import android.app.Activity;
import android.os.Bundle;
import android.os.Build;
import android.provider.Settings;
import android.content.*;
import android.content.pm.PackageInfo;
import android.net.Uri;
import android.widget.*;
import androidx.core.content.FileProvider;
import java.io.*;
import java.util.zip.*;

public class UpdateActivity extends Activity {
    static final int PICK=9001;
    TextView status;
    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setPadding(32,40,32,32);
        TextView title=new TextView(this); title.setText("Update APK"); title.setTextSize(24); title.setTypeface(null,1); root.addView(title);
        status=new TextView(this); status.setText("একটি update ZIP বা APK নির্বাচন করুন।\nZIP-এর ভিতরে APK থাকলে সেটি নিজে থেকেই বের করবে।"); status.setTextSize(16); status.setPadding(0,24,0,24); root.addView(status);
        Button pick=new Button(this); pick.setText("Select Update ZIP / APK"); pick.setOnClickListener(v->pickFile()); root.addView(pick,new LinearLayout.LayoutParams(-1,60));
        setContentView(root);
    }
    void pickFile(){
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT); i.addCategory(Intent.CATEGORY_OPENABLE); i.setType("*/*");
        i.putExtra(Intent.EXTRA_MIME_TYPES,new String[]{"application/zip","application/x-zip-compressed","application/vnd.android.package-archive","application/octet-stream"});
        startActivityForResult(i,PICK);
    }
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
        super.onActivityResult(requestCode,resultCode,data);
        if(requestCode!=PICK || resultCode!=RESULT_OK || data==null || data.getData()==null) return;
        try{
            File apk=prepareApk(data.getData()); if(apk==null) throw new Exception("APK পাওয়া যায়নি");
            PackageInfo pi=getPackageManager().getPackageArchiveInfo(apk.getAbsolutePath(),0);
            if(pi==null || !getPackageName().equals(pi.packageName)) throw new Exception("এটি Memo Printer-এর APK নয়");
            PackageInfo cur=getPackageManager().getPackageInfo(getPackageName(),0);
            long current=Build.VERSION.SDK_INT>=28?cur.getLongVersionCode():cur.versionCode;
            long incoming=Build.VERSION.SDK_INT>=28?pi.getLongVersionCode():pi.versionCode;
            if(incoming<=current) throw new Exception("Update APK-এর version পুরোনোটার চেয়ে নতুন হতে হবে");
            installApk(apk);
        }catch(Exception e){ status.setText("Update failed: "+e.getMessage()); }
    }
    File prepareApk(Uri uri) throws Exception{
        String name=new CursorHolder(this,uri).name; File dir=new File(getCacheDir(),"updates"); if(!dir.exists()) dir.mkdirs();
        if(name!=null && name.toLowerCase().endsWith(".apk")) return copyUri(uri,new File(dir,"update.apk"));
        File zipFile=copyUri(uri,new File(dir,"update.zip")); ZipInputStream zis=new ZipInputStream(new BufferedInputStream(new FileInputStream(zipFile)));
        ZipEntry e; File out=null;
        while((e=zis.getNextEntry())!=null){
            if(e.isDirectory()) continue; String n=e.getName().toLowerCase();
            if(n.endsWith(".apk") && (out==null || n.endsWith("app-release.apk"))){
                out=new File(dir,"update.apk"); FileOutputStream fos=new FileOutputStream(out); byte[] buf=new byte[8192]; int len;
                while((len=zis.read(buf))>0) fos.write(buf,0,len); fos.close(); if(n.endsWith("app-release.apk")) break;
            }
        }
        zis.close(); return out;
    }
    File copyUri(Uri uri,File out) throws Exception{
        InputStream in=getContentResolver().openInputStream(uri); if(in==null) throw new Exception("File open করা যায়নি");
        FileOutputStream fos=new FileOutputStream(out); byte[] b=new byte[8192]; int n; while((n=in.read(b))>0) fos.write(b,0,n); in.close(); fos.close(); return out;
    }
    void installApk(File apk) throws Exception{
        if(Build.VERSION.SDK_INT>=26 && !getPackageManager().canRequestPackageInstalls()){
            status.setText("প্রথমবার 'Install unknown apps' permission দিন, তারপর আবার Update চাপুন।");
            startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,Uri.parse("package:"+getPackageName()))); return;
        }
        Uri uri=FileProvider.getUriForFile(this,"com.memoprinter.eighty.fileprovider",apk);
        Intent i=new Intent(Intent.ACTION_VIEW); i.setDataAndType(uri,"application/vnd.android.package-archive");
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_ACTIVITY_NEW_TASK); startActivity(i);
    }
    static class CursorHolder{
        String name;
        CursorHolder(Context c,Uri u){android.database.Cursor cur=null; try{cur=c.getContentResolver().query(u,new String[]{android.provider.OpenableColumns.DISPLAY_NAME},null,null,null); if(cur!=null&&cur.moveToFirst())name=cur.getString(0);}catch(Exception ignored){}finally{if(cur!=null)cur.close();}}
    }
}
''',encoding='utf-8')

manifest=root/'app/src/main/AndroidManifest.xml'
ms=manifest.read_text(encoding='utf-8')
if 'android.permission.REQUEST_INSTALL_PACKAGES' not in ms:
    close=ms.find('>'); ms=ms[:close+1]+'\n    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />'+ms[close+1:]
if '.UpdateActivity' not in ms:
    ms=ms.replace('    </application>', '''        <activity android:name=".UpdateActivity" android:exported="false" />
        <provider android:name="androidx.core.content.FileProvider"
            android:authorities="com.memoprinter.eighty.fileprovider"
            android:exported="false" android:grantUriPermissions="true">
            <meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/file_paths" />
        </provider>
    </application>''')
manifest.write_text(ms,encoding='utf-8')
xml=root/'app/src/main/res/xml/file_paths.xml'; xml.parent.mkdir(parents=True,exist_ok=True)
xml.write_text('''<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android"><cache-path name="updates" path="updates/" /></paths>
''',encoding='utf-8')
