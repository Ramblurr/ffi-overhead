import os
import strconv

#flag -I.
#include "newplus/plus.c"

fn C.plusone(int) int
fn C.current_timestamp() i64

fn run(count int) i64 {
  mut x := 0
  start := C.current_timestamp()

  for x < count {
    x = C.plusone(x)
  }

  end := C.current_timestamp()

  // Prevent optimization using a side effect
  if x == -1 { // Will never be true but compiler can't prove it
    println('impossible')
  }

  return end - start
}

fn main() {
  if os.args.len == 0 {
    println("First arg (0 - 2000000000) is required.")
    return
  }

  count := strconv.atoi(os.args[1]) or {
    println("Must be a positive number not exceeding 2 billion.")
    return
  }

  println(run(count))
}
