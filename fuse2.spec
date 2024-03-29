%define major 2
%define ulmajor 1
%define libname %mklibname fuse %{major}
%define libulm %mklibname ulockmgr %{ulmajor}
%define devname %mklibname %{name} -d
%define static %mklibname %{name} -d -s

Summary:	Interface for userspace programs to export a virtual filesystem to the kernel
Name:		fuse2
Version:	2.9.9
Release:	7
License:	GPLv2+
Group:		System/Base
Url:		https://github.com/libfuse/libfuse
Source0:	https://github.com/libfuse/libfuse/releases/download/fuse-%{version}/fuse-%{version}.tar.gz
Patch0:		mount-readlink-hang-workaround.patch
Patch1:		https://gitweb.gentoo.org/repo/gentoo.git/plain/sys-fs/fuse/files/fuse-2.9.9-avoid-calling-umount.patch
Patch100:	https://src.fedoraproject.org/rpms/fuse/raw/rawhide/f/fuse2-0001-More-parentheses.patch
Patch101:	https://src.fedoraproject.org/rpms/fuse/raw/rawhide/f/fuse2-0002-add-fix-for-namespace-conflict-in-fuse_kernel.h.patch
Patch102:	https://src.fedoraproject.org/rpms/fuse/raw/rawhide/f/fuse2-0003-make-buffer-size-match-kernel-max-transfer-size.patch
Patch103:	https://src.fedoraproject.org/rpms/fuse/raw/rawhide/f/fuse2-0004-Whitelist-SMB2-found-on-some-NAS-devices.patch
Patch104:	https://src.fedoraproject.org/rpms/fuse/raw/rawhide/f/fuse2-0005-Whitelist-UFSD-backport-to-2.9-branch-452.patch
Patch105:	https://src.fedoraproject.org/rpms/fuse/raw/rawhide/f/fuse2-0006-Correct-errno-comparison-571.patch
Patch106:	https://src.fedoraproject.org/rpms/fuse/raw/rawhide/f/fuse2-0007-util-ulockmgr_server.c-conditionally-define-closefro.patch
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
    --enable-static \
    --enable-util \
    --enable-lib \
    --disable-mtab

%make_build

%install
%make_install

rm -rf %{buildroot}%{_sysconfdir}/rc.d/init.d %{buildroot}%{_sysconfdir}/udev/rules.d

%files
%doc AUTHORS ChangeLog NEWS README.NFS
%attr(0755,root,root) %{_sbindir}/mount.fuse
%attr(4755,root,root) %{_bindir}/fusermount
%attr(0755,root,root) %{_bindir}/ulockmgr_server
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
