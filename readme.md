This is not really a debian package, just a script to call make-kpkg to build
the ev3dev kernel and modules.

It is for building official releases. If you just want to compile the kernel,
see <https://github.com/ev3dev/ev3dev-buildscripts>.

**IMPORTANT**: Requires patched version of `kernel-package` due to
<https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=890817>. This is available
in the ev3dev tool PPA for Ubuntu 18.04.


Build depends: `kernel-package devscripts module-assistant  gcc-linaro-arm-linux-gnueabihf-6.4 `

Toolchain package is in ev3dev PPA:

```
sudo add-apt-repository ppa:ev3dev/tools
```
