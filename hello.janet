#!/usr/bin/env janet

# Load the newplus shared library and bind the functions
(ffi/context "newplus/libnewplus.so")
(ffi/defbind plusone :int [x :int])
(ffi/defbind current_timestamp :long [])

(defn run [count]
  (let [start (current_timestamp)]
    (var x 0)
    (while (< x count)
      (set x (plusone x)))
    (print (- (current_timestamp) start))))

(defn main [& args]
  (if (< (length args) 2)
    (do
      (print "First arg is required")
      (os/exit 1)))
  
  (def count-str (get args 1))  # Skip script name, get first actual argument
  (def count (scan-number count-str))
  
  (cond
    (not count)
    (do
      (print "Must be a positive number not exceeding 2 billion.")
      (os/exit 1))
    
    (or (<= count 0) (> count 2000000000))
    (do
      (print "Must be a positive number not exceeding 2 billion.")
      (os/exit 1)))
  
  # start immediately
  (run count))