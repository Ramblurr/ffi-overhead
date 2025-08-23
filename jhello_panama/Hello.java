package jhello_panama;

import java.lang.foreign.*;
import java.lang.invoke.MethodHandle;
import java.nio.file.Path;

public final class Hello
{
    private static final Linker linker = Linker.nativeLinker();
    private static final SymbolLookup symbolLookup;
    private static final MethodHandle plusone;
    private static final MethodHandle currentTimestamp;
    
    static {
        try {
            // Load the shared library
            java.io.File currentDir = new java.io.File(".").getCanonicalFile();
            System.load(currentDir.getPath() + "/newplus/libnewplus.so");
            symbolLookup = SymbolLookup.loaderLookup();
            
            // Define function signatures
            FunctionDescriptor plusoneDesc = FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT);
            FunctionDescriptor timestampDesc = FunctionDescriptor.of(ValueLayout.JAVA_LONG);
            
            // Get method handles
            plusone = linker.downcallHandle(
                symbolLookup.find("plusone").orElseThrow(),
                plusoneDesc
            );
            
            currentTimestamp = linker.downcallHandle(
                symbolLookup.find("current_timestamp").orElseThrow(),
                timestampDesc
            );
        } catch (Exception e) {
            throw new RuntimeException("Failed to initialize native bindings", e);
        }
    }
    
    public static int plusone(int x) {
        try {
            return (int) plusone.invokeExact(x);
        } catch (Throwable t) {
            throw new RuntimeException(t);
        }
    }
    
    public static long current_timestamp() {
        try {
            return (long) currentTimestamp.invokeExact();
        } catch (Throwable t) {
            throw new RuntimeException(t);
        }
    }
    
    static void run(int count) {
        final long start = current_timestamp();
        
        int x = 0;
        while (x < count)
            x = plusone(x);
        
        System.out.println(current_timestamp() - start);
    }
    
    public static void main(String[] args) throws Exception {
        if (args.length == 0) {
            System.err.println("First arg (0 - 2000000000) is required.");
            return;
        }
        
        int count = Integer.parseInt(args[0]);
        if (count <= 0 || count > 2000000000) {
            System.err.println("Must be a positive number not exceeding 2 billion.");
            return;
        }
        
        // Warmup
        plusone((int)current_timestamp());
        
        // Run benchmark
        run(count);
    }
}