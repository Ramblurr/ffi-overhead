#!/usr/bin/env bb

(require '[babashka.ffi :as ffi])

(def library (ffi/load-library "./newplus/libnewplus.so"))
(def plusone (ffi/cfn library "plusone" [:int] :int))
(def current-timestamp (ffi/cfn library "current_timestamp" [] :long))

(defn parse-count [args]
  (when-not (= 1 (count args))
    (binding [*out* *err*]
      (println "First arg (0 - 2000000000) is required."))
    (System/exit 1))
  (let [count (try
                (Long/parseLong (first args))
                (catch NumberFormatException _
                  nil))]
    (when-not (and count (pos? count) (<= count 2000000000))
      (binding [*out* *err*]
        (println "Must be a positive number not exceeding 2 billion."))
      (System/exit 1))
    count))

(defn run [count]
  (let [start (current-timestamp)]
    (loop [x 0]
      (if (< x count)
        (recur (plusone x))
        (println (- (current-timestamp) start))))))

(run (parse-count *command-line-args*))
