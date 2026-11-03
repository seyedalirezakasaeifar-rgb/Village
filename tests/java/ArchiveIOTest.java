package org.townledger.vale;
import java.io.*;
import java.util.*;
import java.nio.charset.StandardCharsets;
public final class ArchiveIOTest {
    interface Action {void run() throws Exception;}
    static void reject(Action action) throws Exception {try{action.run();throw new AssertionError("Expected rejection");}catch(IOException expected){}}
    static void check(boolean value){if(!value)throw new AssertionError();}
    public static void main(String[] args) throws Exception {
        String text="{\"town\":\"Oak · آبادی 🌲\"}";byte[] bytes=ArchiveIO.encode(text);
        check(ArchiveIO.decode(ArchiveIO.read(new ByteArrayInputStream(bytes))).equals(text));
        check(ArchiveIO.decode(("\ufeff"+text).getBytes(StandardCharsets.UTF_8)).equals(text));
        ByteArrayOutputStream out=new ByteArrayOutputStream();ArchiveIO.write(out,bytes);check(Arrays.equals(bytes,out.toByteArray()));
        byte[] exact=new byte[ArchiveIO.LIMIT];Arrays.fill(exact,(byte)'a');check(ArchiveIO.read(new ByteArrayInputStream(exact)).length==ArchiveIO.LIMIT);
        check(ArchiveIO.encode(new String(exact,StandardCharsets.US_ASCII)).length==ArchiveIO.LIMIT);
        reject(()->ArchiveIO.read(new ByteArrayInputStream(new byte[ArchiveIO.LIMIT+1])));
        reject(()->ArchiveIO.write(new ByteArrayOutputStream(),new byte[ArchiveIO.LIMIT+1]));
        char[] unicode=new char[ArchiveIO.LIMIT/3+1];Arrays.fill(unicode,'\u20ac');reject(()->ArchiveIO.encode(new String(unicode)));
        reject(()->ArchiveIO.encode("\ud800"));reject(()->ArchiveIO.decode(new byte[]{(byte)0xc3,(byte)0x28}));
        reject(()->ArchiveIO.read(null));reject(()->ArchiveIO.write(null,bytes));reject(()->ArchiveIO.encode(null));
        reject(()->ArchiveIO.read(new InputStream(){public int read() throws IOException{throw new IOException("Provider failed");}}));
        reject(()->ArchiveIO.write(new OutputStream(){public void write(int b) throws IOException{throw new IOException("Provider failed");}},bytes));
        check(ArchiveIO.pendingName("pending-town-export-123e4567-e89b-12d3-a456-426614174000.json"));
        check(!ArchiveIO.pendingName("../town.json")&&!ArchiveIO.pendingName(null)&&!ArchiveIO.pendingName("pending-town-export-x.json"));
        System.out.println("PASS Unicode/BOM round trip, exact 8 MB boundary, byte-based limits, malformed Unicode, bounded/provider errors and private pending filenames");
    }
}
