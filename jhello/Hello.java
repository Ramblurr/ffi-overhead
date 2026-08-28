package jhello;

import java.lang.management.CompilationMXBean;
import java.lang.management.ManagementFactory;

public final class Hello
{
    private static final long WARMUP_NANOS = 10_000_000_000L;
    private static final int WARMUP_COUNT = 1_000_000;
    private static final int STABLE_JIT_CHECKS = 3;

    public static native int plus(int x, int y);
    public static native int plusone(int x);
    public static native long current_timestamp();

    private static void loadNative() throws Exception
    {
        java.io.File file = new java.io.File("."), 
            jhello = new java.io.File(file, "jhello");
        
        if (jhello.exists())
            file = jhello;
        
        String currentDir = file.getCanonicalPath();
    
        System.load(currentDir + "/libjhello.so");
    }
    
    static int runLoop(int count)
    {
        int x = 0;
        while (x < count)
            x = plusone(x);

        return x;
    }

    static void warmup()
    {
        final CompilationMXBean compiler = ManagementFactory.getCompilationMXBean();
        final long start = System.nanoTime();
        long loadedClasses = ManagementFactory.getClassLoadingMXBean().getTotalLoadedClassCount();
        long compilationTime = compiler.getTotalCompilationTime();
        int stableChecks = 0;

        do
        {
            runLoop(WARMUP_COUNT);

            final long newLoadedClasses = ManagementFactory.getClassLoadingMXBean().getTotalLoadedClassCount();
            final long newCompilationTime = compiler.getTotalCompilationTime();
            if (loadedClasses == newLoadedClasses && compilationTime == newCompilationTime)
                stableChecks++;
            else
                stableChecks = 0;

            loadedClasses = newLoadedClasses;
            compilationTime = newCompilationTime;
        }
        while (System.nanoTime() - start < WARMUP_NANOS || stableChecks < STABLE_JIT_CHECKS);
    }

    static void run(int count)
    {
        final long start = current_timestamp();
        runLoop(count);
        System.out.println(current_timestamp() - start);
    }

    public static void main(String[] args) throws Exception
    {
        if (args.length == 0)
        {
            System.err.println("First arg (0 - 2000000000) is required.");
            return;
        }
        
        int count = Integer.parseInt(args[0]);
        if (count <= 0 || count > 2000000000)
        {
            System.err.println("Must be a positive number not exceeding 2 billion.");
            return;
        }
        
        // load
        loadNative();
        System.gc();
        warmup();
        
        // start
        run(count);
    }
}
