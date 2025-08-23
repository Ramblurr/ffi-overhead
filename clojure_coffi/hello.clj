(require '[coffi.mem :as mem])
(require '[coffi.ffi :as ffi :refer [defcfn]])

;; Load our newplus library
(ffi/load-library "../newplus/libnewplus.so")

;; Define the functions from our C library
(defcfn plusone
  "Increment a number by one."
  plusone [::mem/int] ::mem/int)

(defcfn current_timestamp
  "Get current timestamp in milliseconds."
  current_timestamp [] ::mem/long)

(defn run-benchmark [count]
  (let [start (current_timestamp)]
    (loop [x 0]
      (if (< x count)
        (recur (plusone x))
        (println (- (current_timestamp) start))))))

;; Get command line argument
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
    
    ;; Start benchmark immediately
    (run-benchmark count)))

;; If running as script, call -main with command line args
(apply -main *command-line-args*)
