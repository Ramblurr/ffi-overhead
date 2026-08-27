(ns ffi-overhead.panama
  (:import
   [java.lang.foreign Arena FunctionDescriptor Linker Linker$Option MemoryLayout SymbolLookup ValueLayout]
   [java.lang.invoke MethodHandle MethodHandleProxies]
   [java.util Optional]
   [java.util.function IntUnaryOperator LongSupplier]))

(set! *warn-on-reflection* true)

(def ^Linker linker (Linker/nativeLinker))
(def ^SymbolLookup symbol-lookup
  (SymbolLookup/libraryLookup
   (.toPath (.getCanonicalFile (java.io.File. "./newplus/libnewplus.so")))
   (Arena/global)))
(def linker-options (make-array Linker$Option 0))

(defn downcall-handle [symbol descriptor]
  (.downcallHandle
   linker
   (.orElseThrow ^Optional (.find symbol-lookup symbol))
   descriptor
   linker-options))

(def ^IntUnaryOperator plusone
  (MethodHandleProxies/asInterfaceInstance
   IntUnaryOperator
   ^MethodHandle
   (downcall-handle
    "plusone"
    (FunctionDescriptor/of
     ValueLayout/JAVA_INT
     (into-array MemoryLayout [ValueLayout/JAVA_INT])))))

(def ^LongSupplier current-timestamp
  (MethodHandleProxies/asInterfaceInstance
   LongSupplier
   ^MethodHandle
   (downcall-handle
    "current_timestamp"
    (FunctionDescriptor/of
     ValueLayout/JAVA_LONG
     (make-array MemoryLayout 0)))))

(defn parse-count [args]
  (when-not (= 1 (count args))
    (throw (ex-info "Count must be specified once." {})))
  (let [count (try
                (Long/parseLong (first args))
                (catch NumberFormatException _
                  nil))]
    (when-not (and count (pos? count) (<= count 2000000000))
      (throw (ex-info "Count must be one positive integer not exceeding 2 billion." {})))
    count))

(defn run [count]
  (.applyAsInt plusone (unchecked-int (.getAsLong current-timestamp)))
  (let [start (.getAsLong current-timestamp)]
    (loop [x 0]
      (if (< x count)
        (recur (.applyAsInt plusone (int x)))
        (println (- (.getAsLong current-timestamp) start))))))

(run (parse-count *command-line-args*))
