This is not really a debian package, just a script to call make-kpkg to build
the ev3dev kernel and modules.

It is for building official releases. If you just want to compile the kernel,
see <https://github.com/ev3dev/ev3dev-buildscripts>.

Depends on: `kernel-package devscripts code-sourcery-toolchain-arm-2011.03`

Kernel version 3.15+ requires kernel-package 13+ (from jessie/utopic)
