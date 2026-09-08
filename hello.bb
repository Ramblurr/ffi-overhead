#!/usr/bin/env bb

(require '[babashka.ffi :as ffi]
         '[cheshire.core :as json])

(def library (ffi/load-library "./newplus/libnewplus.so"))
(def plusone (ffi/cfn library "plusone" [:int] :int))
(def current-timestamp (ffi/cfn library "current_timestamp" [] :long))

(defn parse-count [args]
  (when-not (= 1 (count args))
    (binding [*out* *err*]
      (println "Exactly one count (1 - 2000000000) is required."))
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

(defn measure [f inputs]
  (let [start (current-timestamp)]
    (run! f inputs)
    (- (current-timestamp) start)))

(defn run [count]
  (let [inputs     (range count)
        control    identity
        foreign    plusone
        control-ms (measure control inputs)
        ffi-ms     (measure foreign inputs)]
    {:count      count
     :control_ms control-ms
     :ffi_ms     ffi-ms}))

(println (json/generate-string (run (parse-count *command-line-args*))))
