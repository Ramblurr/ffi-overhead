package jhello_panama;

import java.lang.foreign.*;
import java.lang.management.CompilationMXBean;
import java.lang.management.ManagementFactory;
import java.lang.invoke.MethodHandle;
import java.nio.file.Path;

public final class Hello
{
    private static final long WARMUP_NANOS = 10_000_000_000L;
    private static final int WARMUP_COUNT = 1_000_000;
    private static final int STABLE_JIT_CHECKS = 3;

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
    
    static int runLoop(int count) {
        int x = 0;
        while (x < count)
            x = plusone(x);

        return x;
    }

    static void warmup() {
        final CompilationMXBean compiler = ManagementFactory.getCompilationMXBean();
        final long start = System.nanoTime();
        long loadedClasses = ManagementFactory.getClassLoadingMXBean().getTotalLoadedClassCount();
        long compilationTime = compiler.getTotalCompilationTime();
        int stableChecks = 0;

        do {
            runLoop(WARMUP_COUNT);

            final long newLoadedClasses = ManagementFactory.getClassLoadingMXBean().getTotalLoadedClassCount();
            final long newCompilationTime = compiler.getTotalCompilationTime();
            if (loadedClasses == newLoadedClasses && compilationTime == newCompilationTime)
                stableChecks++;
            else
                stableChecks = 0;

            loadedClasses = newLoadedClasses;
            compilationTime = newCompilationTime;
        } while (System.nanoTime() - start < WARMUP_NANOS || stableChecks < STABLE_JIT_CHECKS);
    }

    static void run(int count) {
        final long start = current_timestamp();
        runLoop(count);
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
        System.gc();
        warmup();
        
        // Run benchmark
        run(count);
    }
}