package org.townledger.vale;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.charset.CodingErrorAction;
import java.nio.ByteBuffer;

/** Bounded UTF-8 archive transport, independent of Activity and document providers. */
final class ArchiveIO {
    static final int LIMIT = 8 * 1024 * 1024;
    private ArchiveIO() {}
    static byte[] encode(String text) throws IOException {
        if (text == null || text.length() > LIMIT) throw new IOException("Archive exceeds 8 MB");
        int size=0;
        for(int i=0;i<text.length();i++) {
            char c=text.charAt(i);
            if(Character.isHighSurrogate(c)) {
                if(i+1>=text.length()||!Character.isLowSurrogate(text.charAt(++i)))throw new IOException("Invalid Unicode archive");
                size+=4;
            }else if(Character.isLowSurrogate(c))throw new IOException("Invalid Unicode archive");
            else size+=c<0x80?1:c<0x800?2:3;
            if(size>LIMIT)throw new IOException("Archive exceeds 8 MB");
        }
        return text.getBytes(StandardCharsets.UTF_8);
    }
    static String decode(byte[] bytes) throws IOException {
        String text=StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes)).toString();
        return text.startsWith("\ufeff")?text.substring(1):text;
    }
    static boolean pendingName(String name) {
        return name!=null&&name.matches("pending-town-export-[0-9a-f-]+\\.json");
    }
    static byte[] read(InputStream in) throws IOException {
        if (in == null) throw new IOException("No document source");
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        byte[] buffer = new byte[8192];
        int n;
        while ((n = in.read(buffer)) != -1) {
            if (bytes.size() + n > LIMIT) throw new IOException("Archive exceeds 8 MB");
            bytes.write(buffer, 0, n);
        }
        return bytes.toByteArray();
    }
    static void write(OutputStream out, byte[] bytes) throws IOException {
        if (out == null) throw new IOException("No document destination");
        if (bytes.length > LIMIT) throw new IOException("Archive exceeds 8 MB");
        out.write(bytes);
        out.flush();
    }
}
