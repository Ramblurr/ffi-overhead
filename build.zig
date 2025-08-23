const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    
    const exe = b.addExecutable(.{
        .name = "zig_hello",
        .root_source_file = b.path("hello.zig"),
        .target = target,
        .optimize = optimize,
    });
    
    exe.addIncludePath(b.path("."));
    exe.linkLibC();
    exe.addCSourceFile(.{
        .file = b.path("newplus/plus.c"),
        .flags = &.{},
    });
    
    exe.addRPath(b.path("newplus"));
    
    const install_exe = b.addInstallArtifact(exe, .{
        .dest_dir = .{ .override = .{ .custom = "zig_hello" } },
    });
    
    b.getInstallStep().dependOn(&install_exe.step);
}
