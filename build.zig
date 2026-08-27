const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "zig_hello",
        .root_module = b.createModule(.{
            .root_source_file = b.path("hello.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    exe.root_module.addIncludePath(b.path("."));
    exe.root_module.link_libc = true;
    exe.root_module.addCSourceFile(.{
        .file = b.path("newplus/plus.c"),
        .flags = &.{},
    });

    const install_exe = b.addInstallArtifact(exe, .{
        .dest_dir = .{ .override = .{ .custom = "zig_hello" } },
    });

    b.getInstallStep().dependOn(&install_exe.step);
}
