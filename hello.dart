import 'dart:ffi' as ffi;
import 'dart:io' show File;

typedef _PlusOneNative = ffi.Int Function(ffi.Int);
typedef _PlusOne = int Function(int);
typedef _CurrentTimestampNative = ffi.LongLong Function();
typedef _CurrentTimestamp = int Function();

final _newplus = ffi.DynamicLibrary.open(
  File('newplus/libnewplus.so').absolute.path,
);
final _plusone = _newplus.lookupFunction<_PlusOneNative, _PlusOne>('plusone');
final _currentTimestamp = _newplus
    .lookupFunction<_CurrentTimestampNative, _CurrentTimestamp>(
      'current_timestamp',
    );

void run(int count) {
  // start
  var start = _currentTimestamp();

  int x = 0;
  while (x < count) {
    x = _plusone(x);
  }

  print(_currentTimestamp() - start);
}

void main(List<String> args) {
  if (args.isEmpty) {
    print("First arg (0 - 2000000000) is required.");
    return;
  }

  var count = int.parse(args[0]);
  if (count <= 0 || count > 2000000000) {
    print("Must be a positive number not exceeding 2 billion.");
    return;
  }

  _plusone(_currentTimestamp() == 0 ? 1 : 2);
  run(count);
}
