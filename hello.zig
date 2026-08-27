const std = @import("std");
const c = @cImport({
    // See https://github.com/zig-lang/zig/issues/515
    @cDefine("_NO_CRT_STDIO_INLINE", "1");
    @cInclude("stdio.h");
    @cInclude("newplus/plus.h");
});

pub fn main(init: std.process.Init) !void {
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    if (args.len == 1) {
        _ = c.printf("First arg (0 - 2000000000) is required.\n");
        return;
    }

    const count = try std.fmt.parseInt(i32, args[1], 10);
    if (count <= 0 or count > 2000000000) {
        _ = c.printf("Must be a positive number not exceeding 2 billion.\n");
        return;
    }

    run(count);
}

fn run(count: i32) void {
    const start = c.current_timestamp();

    var x: i32 = 0;
    while (x < count) {
        x = c.plusone(x);
    }

    const elapsed = c.current_timestamp() - start;
    _ = c.printf("%lld\n", elapsed);
}
