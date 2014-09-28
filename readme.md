This is not really a debian package, just a script to call make-kpkg to build
the ev3dev kernel and modules.

It is for building official releases. If you just want to compile the kernel,
see <https://github.com/ev3dev/ev3dev-buildscripts>.

Build depends: `kernel-package devscripts module-assistant code-sourcery-toolchain-arm-2011.03`

`code-sourcery-toolchain-arm-2011.03` package is in the ev3dev.org package repository.

Kernel version 3.15+ requires `kernel-package` version 13+ (availible in offical jessie or utopic repositories)
