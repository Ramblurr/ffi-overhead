(ns ffi-overhead.coffi
  (:gen-class)
  (:require
   [coffi.ffi :as ffi :refer [defcfn]]
   [coffi.mem :as mem]
   [criterium.core :as crit]))

(ffi/load-library "../newplus/libnewplus.so")

(defcfn plusone
  "Increment a number by one."
  plusone [::mem/int] ::mem/int)

(defmacro time-millis
  "Evaluates expr and returns the time it took in integer milliseconds"
  [expr]
  `(let [start# (. System (nanoTime))]
     ~expr
     (long (/ (double (- (. System (nanoTime)) start#)) 1000000.0))))

(defn run-benchmark [count print?]
  (let [res (time-millis
             (loop [x 0]
               (if (< x count)
                 (recur (plusone x))
                 nil)))]
    (when print?
      (println res))))

(def s-to-ns (* 1000 1000 1000)) ; in ns

(defmacro warmup [expr]
  `(crit/warmup-for-jit (* 10 crit/s-to-ns) (fn [] ~expr)))

(defn -main [& args]
  (if (empty? args)
    (do
      (println "First arg is required")
      (System/exit 1)))

  (let [count-str (first args)
        count (try (Long/parseLong count-str)
                   (catch NumberFormatException _ nil))]
    (cond
      (not count)
      (do
        (println "Must be a positive number not exceeding 2 billion.")
        (System/exit 1))

      (or (<= count 0) (> count 2000000000))
      (do
        (println "Must be a positive number not exceeding 2 billion.")
        (System/exit 1)))

    (crit/force-gc)
    (warmup (run-benchmark 1000000 false))
    (run-benchmark count true)))
