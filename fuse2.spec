# LTO should be disabled due to compiling bug on 86_64 and i686 https://bugs.gentoo.org/663518 (penguin)
%define _disable_lto 1

%define major 2
%define ulmajor 1
%define libname %mklibname fuse %{major}
%define libulm %mklibname ulockmgr %{ulmajor}
%define devname %mklibname %{name} -d
%define static %mklibname %{name} -d -s

Summary:	Interface for userspace programs to export a virtual filesystem to the kernel
Name:		fuse2
Version:	2.9.9
Release:	3
License:	GPLv2+
Group:		System/Base
Url:		https://github.com/libfuse/libfuse
Source0:	https://github.com/libfuse/libfuse/releases/download/fuse_2_9_5/fuse-%{version}.tar.gz
Patch0:		mount-readlink-hang-workaround.patch
Patch1:		fuse-0001-More-parentheses.patch
Patch2:		https://gitweb.gentoo.org/repo/gentoo.git/plain/sys-fs/fuse/files/fuse-2.9.3-kernel-types.patch
Patch3:		https://gitweb.gentoo.org/repo/gentoo.git/plain/sys-fs/fuse/files/fuse-2.9.9-avoid-calling-umount.patch
Patch4:		https://gitweb.gentoo.org/repo/gentoo.git/plain/sys-fs/fuse/files/fuse-2.9.9-closefrom-glibc-2-34.patch
BuildRequires:	libtool
BuildRequires:	gettext-devel

%description
FUSE (Filesystem in USErspace) is a simple interface for userspace
programs to export a virtual filesystem to the linux kernel.  FUSE
also aims to provide a secure method for non privileged users to
create and mount their own filesystem implementations.

%package -n %{libname}
Summary:	Libraries for fuse
Group:		System/Libraries
License:	LGPLv2+

%description -n	%{libname}
Libraries for fuse.

%package -n %{libulm}
Summary:	libulockmgr for fuse
Group:		System/Libraries
License:	LGPLv2+
Conflicts:	%{libname} < 2.9.2-1

%description -n %{libulm}
Libraries for fuse.

%package -n %{devname}
Summary:	Header files and development libraries for libfuse2
Group:		Development/C
License:	LGPLv2+
Provides:	%{name}-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}
Requires:	%{libulm} = %{EVRD}

%description -n %{devname}
Header files and development libraries for fuse.

%package -n %{static}
Summary:	Static libraries for fuse
Group:		Development/C
License:	LGPLv2+
Provides:	%{name}-static-devel = %{EVRD}
Requires:	%{devname} = %{EVRD}

%description -n %{static}
Static libraries for fuse.

%prep
%autosetup -n fuse-%{version} -p1

sed -e 's|mknod|/bin/echo Disabled: mknod |g' -i util/Makefile.in
sed -i -e 's|INIT_D_PATH=.*|INIT_D_PATH=%{_initrddir}|' configure*

%build
export MOUNT_FUSE_PATH="%{_sbindir}"
%configure \
    CC="gcc -fuse-ld=bfd" \
    LD="ld.bfd" \
    --enable-static \
    --enable-util \
    --enable-lib \
    --disable-mtab

%make_build

%install
%make_install

# XXX: have a hard time believing that these symlinks are actually needed,,,
mkdir -p %{buildroot}/{bin,sbin}
ln -s %{_bindir}/fusermount %{buildroot}/bin/fusermount
ln -s %{_bindir}/ulockmgr_server %{buildroot}/bin/ulockmgr_server
ln -s %{_sbindir}/mount.fuse %{buildroot}/sbin/mount.fuse
rm -rf %{buildroot}%{_sysconfdir}/rc.d/init.d %{buildroot}%{_sysconfdir}/udev/rules.d

%files
%doc AUTHORS ChangeLog NEWS README.NFS
%attr(0755,root,root) %{_sbindir}/mount.fuse
%attr(4755,root,root) %{_bindir}/fusermount
%attr(0755,root,root) %{_bindir}/ulockmgr_server
/sbin/mount.fuse
/bin/fusermount
/bin/ulockmgr_server
%doc %{_mandir}/man1/fusermount.1.*
%doc %{_mandir}/man1/ulockmgr_server.1.*
%doc %{_mandir}/man8/mount.fuse.8.*

%files -n %{libname}
%{_libdir}/libfuse.so.%{major}*

%files -n %{libulm}
%{_libdir}/libulockmgr.so.%{ulmajor}*

%files -n %{devname}
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*

%files -n %{static}
%{_libdir}/*.a
