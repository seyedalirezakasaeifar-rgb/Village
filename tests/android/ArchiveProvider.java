package org.townledger.vale;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import java.io.File;
import java.io.FileNotFoundException;

/** Test-only external provider. No provider is added to the production manifest. */
public final class ArchiveProvider extends ContentProvider {
    public boolean onCreate(){return true;}
    public String getType(Uri uri){return "application/json";}
    public Cursor query(Uri uri,String[] projection,String selection,String[] args,String order){return null;}
    public Uri insert(Uri uri,ContentValues values){throw new UnsupportedOperationException();}
    public int delete(Uri uri,String where,String[] args){throw new UnsupportedOperationException();}
    public int update(Uri uri,ContentValues values,String where,String[] args){throw new UnsupportedOperationException();}
    public ParcelFileDescriptor openFile(Uri uri,String mode)throws FileNotFoundException{
        if(!"archive".equals(uri.getLastPathSegment()))throw new FileNotFoundException("Unknown private test document");
        return ParcelFileDescriptor.open(new File(getContext().getCacheDir(),"qa-document.json"),ParcelFileDescriptor.parseMode(mode));
    }
}
