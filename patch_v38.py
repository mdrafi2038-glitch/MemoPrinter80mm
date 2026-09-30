from pathlib import Path
root=Path(".")
main=root/"app/src/main/java/com/memoprinter/eighty/MainActivity.java"
manifest=root/"app/src/main/AndroidManifest.xml"
if not main.exists() or not manifest.exists(): raise SystemExit("Memo Printer Android source files not found")
updater=r'''package com.memoprinter.eighty;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.Settings;
import androidx.core.content.FileProvider;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.regex.*;
public final class AppUpdater {
 private static final String RELEASES_URL="https://api.github.com/repos/mdrafi2038-glitch/MemoPrinter80mm/releases/latest";
 private static final String APK_NAME="MemoPrinter80mm-update.apk";
 private static File pendingApk; private final Activity activity;
 public AppUpdater(Activity a){activity=a;}
 public void check(boolean manual){new Thread(()->{HttpURLConnection c=null;try{
  c=(HttpURLConnection)new URL(RELEASES_URL).openConnection();c.setConnectTimeout(10000);c.setReadTimeout(15000);
  c.setRequestProperty("Accept","application/vnd.github+json");c.setRequestProperty("User-Agent","MemoPrinter80mm-Updater");
  if(c.getResponseCode()<200||c.getResponseCode()>=300)throw new IOException();
  JSONObject r=new JSONObject(readAll(c.getInputStream()));int remote=versionFromTag(r.optString("tag_name",""));
  JSONArray as=r.optJSONArray("assets");String apkUrl=null;if(as!=null)for(int i=0;i<as.length();i++){JSONObject a=as.optJSONObject(i);if(a!=null&&a.optString("name","").toLowerCase().endsWith(".apk")){apkUrl=a.optString("browser_download_url",null);break;}}
  int local=activity.getPackageManager().getPackageInfo(activity.getPackageName(),0).versionCode;
  if(remote<=local||apkUrl==null){if(manual)toast("আপনার Memo Printer সর্বশেষ ভার্সনে আছে ✓");return;}
  final int v=remote;final String u=apkUrl;activity.runOnUiThread(()->new AlertDialog.Builder(activity).setTitle("নতুন আপডেট পাওয়া গেছে").setMessage("Build "+v+" পাওয়া গেছে। এখন আপডেট করবেন?").setNegativeButton("পরে",null).setPositiveButton("আপডেট",(d,w)->download(u)).show());
 }catch(Throwable e){if(manual)toast("Update check করা যায়নি");}finally{if(c!=null)c.disconnect();}},"memo-updater-check").start();}
 private void download(String url){new Thread(()->{HttpURLConnection c=null;InputStream in=null;OutputStream out=null;try{
  c=(HttpURLConnection)new URL(url).openConnection();c.setConnectTimeout(15000);c.setReadTimeout(30000);c.setInstanceFollowRedirects(true);c.setRequestProperty("User-Agent","MemoPrinter80mm-Updater");
  if(c.getResponseCode()<200||c.getResponseCode()>=300)throw new IOException();File dir=activity.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);if(dir==null)dir=activity.getCacheDir();if(!dir.exists())dir.mkdirs();
  File apk=new File(dir,APK_NAME);if(apk.exists())apk.delete();in=c.getInputStream();out=new FileOutputStream(apk);byte[] b=new byte[8192];int n;long total=0;while((n=in.read(b))!=-1){out.write(b,0,n);total+=n;}out.flush();if(total<10000)throw new IOException();
  final File f=apk;activity.runOnUiThread(()->install(f));
 }catch(Throwable e){toast("Update download ব্যর্থ হয়েছে");}finally{try{if(in!=null)in.close();}catch(Exception ignored){}try{if(out!=null)out.close();}catch(Exception ignored){}if(c!=null)c.disconnect();}},"memo-updater-download").start();}
 private void install(File apk){if(Build.VERSION.SDK_INT>=26&&!activity.getPackageManager().canRequestPackageInstalls()){pendingApk=apk;try{activity.startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,Uri.parse("package:"+activity.getPackageName())));toast("Install permission দিন, তারপর অ্যাপে ফিরে আসুন");}catch(Throwable e){toast("Install permission settings খোলা যায়নি");}return;}
  try{Uri u=FileProvider.getUriForFile(activity,activity.getPackageName()+".fileprovider",apk);Intent i=new Intent(Intent.ACTION_VIEW);i.setDataAndType(u,"application/vnd.android.package-archive");i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_ACTIVITY_NEW_TASK);activity.startActivity(i);}catch(Throwable e){toast("APK install শুরু করা যায়নি");}}
 public static void onResume(Activity a){if(pendingApk!=null&&Build.VERSION.SDK_INT>=26&&a.getPackageManager().canRequestPackageInstalls()){File f=pendingApk;pendingApk=null;try{Uri u=FileProvider.getUriForFile(a,a.getPackageName()+".fileprovider",f);Intent i=new Intent(Intent.ACTION_VIEW);i.setDataAndType(u,"application/vnd.android.package-archive");i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_ACTIVITY_NEW_TASK);a.startActivity(i);}catch(Throwable ignored){}}}
 private static int versionFromTag(String s){Matcher m=Pattern.compile("build[-_](\\d+)$",Pattern.CASE_INSENSITIVE).matcher(s==null?"":s.trim());return m.find()?Integer.parseInt(m.group(1)):0;}
 private static String readAll(InputStream in)throws IOException{StringBuilder s=new StringBuilder();byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1)s.append(new String(b,0,n,"UTF-8"));return s.toString();}
 private void toast(String s){activity.runOnUiThread(()->android.widget.Toast.makeText(activity,s,android.widget.Toast.LENGTH_SHORT).show());}
}
'''
(root/"app/src/main/java/com/memoprinter/eighty/AppUpdater.java").write_text(updater,encoding="utf-8")
x=root/"app/src/main/res/xml/file_paths.xml";x.parent.mkdir(parents=True,exist_ok=True)
x.write_text('''<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
 <external-files-path name="updates" path="Download/" />
 <cache-path name="cache" path="." />
</paths>
''',encoding="utf-8")
m=manifest.read_text(encoding="utf-8")
if "android.permission.INTERNET" not in m:m=m.replace('<manifest xmlns:android="http://schemas.android.com/apk/res/android">','<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n <uses-permission android:name="android.permission.INTERNET"/>\n <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES"/>',1)
if "androidx.core.content.FileProvider" not in m:
 provider=''' <provider android:name="androidx.core.content.FileProvider" android:authorities="com.memoprinter.eighty.fileprovider" android:exported="false" android:grantUriPermissions="true">
  <meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/file_paths"/>
 </provider>
'''
 m=m.replace("    </application>",provider+"    </application>",1)
manifest.write_text(m,encoding="utf-8")
s=main.read_text(encoding="utf-8")
anchor='memoNo=getPreferences(0).getInt("memo",1); if(memoNo<1 || memoNo>999999){ memoNo=1; } loadPrices(); loadHistory(); loadPrinter(); home();'
if "new AppUpdater(this).check(false);" not in s:
 if anchor not in s:raise SystemExit("onCreate updater anchor missing")
 s=s.replace(anchor,anchor+'\n        new AppUpdater(this).check(false);',1)
if "AppUpdater.onResume(this);" not in s:s=s.replace('    @Override public void onBackPressed(){','    @Override protected void onResume(){ super.onResume(); AppUpdater.onResume(this); }\n\n    @Override public void onBackPressed(){',1)
main.write_text(s,encoding="utf-8")
print("updater patch applied")
