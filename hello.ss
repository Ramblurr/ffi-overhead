(import (chezscheme))

(load-shared-object "./newplus/libnewplus.so")

(define plusone
  (foreign-procedure "plusone" (int) int))
(define current-timestamp
  (foreign-procedure "current_timestamp" () integer-64))

(define (fail message)
  (fprintf (current-error-port) "~a\n" message)
  (exit 1))

(let ([args (cdr (command-line))])
  (unless (= (length args) 1)
    (fail "Count must be specified once."))
  (let ([count (string->number (car args))])
    (unless (and (integer? count)
                 (exact? count)
                 (> count 0)
                 (<= count 2000000000))
      (fail "Count must be one positive integer not exceeding 2 billion."))
    (plusone 0)
    (let ([start (current-timestamp)])
      (let loop ([x 0])
        (if (< x count)
            (loop (plusone x))
            (printf "~d\n" (- (current-timestamp) start)))))))
