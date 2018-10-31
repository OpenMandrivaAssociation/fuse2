%define	major 2
%define	ulmajor 1
%define	libname %mklibname fuse %{major}
%define	libulm %mklibname ulockmgr %{ulmajor}
%define	devname %mklibname %{name} -d
%define	static %mklibname %{name} -d -s

Summary:	Interface for userspace programs to export a virtual filesystem to the kernel
Name:		fuse2
Version:	2.9.7
Release:	2
License:	GPLv2+
Group:		System/Base
Url:		https://github.com/libfuse/libfuse
Source0:	https://github.com/libfuse/libfuse/releases/download/fuse_2_9_5/fuse-%{version}.tar.gz
Patch0:		mount-readlink-hang-workaround.patch
Patch1:		fuse-2.9.2-namespace-conflict-fix.patch
Patch2:		fuse-0001-More-parentheses.patch

BuildRequires:	libtool
BuildRequires:	gettext-devel
Requires:	which
Requires(preun):	rpm-helper

%description
FUSE (Filesystem in USErspace) is a simple interface for userspace
programs to export a virtual filesystem to the linux kernel.  FUSE
also aims to provide a secure method for non privileged users to
create and mount their own filesystem implementations.

%package -n	%{libname}
Summary:	Libraries for fuse
Group:		System/Libraries
License:	LGPLv2+

%description -n	%{libname}
Libraries for fuse.

%package -n	%{libulm}
Summary:	libulockmgr for fuse
Group:		System/Libraries
License:	LGPLv2+
Conflicts:	%{libname} < 2.9.2-1

%description -n	%{libulm}
Libraries for fuse.

%package -n	%{devname}
Summary:	Header files and development libraries for libfuse2
Group:		Development/C
License:	LGPLv2+
Provides:	%{name}-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}
Requires:	%{libulm} = %{EVRD}

%description -n	%{devname}
Header files and development libraries for fuse.

%package -n	%{static}
Summary:	Static libraries for fuse
Group:		Development/C
License:	LGPLv2+
Provides:	%{name}-static-devel = %{EVRD}
Requires:	%{devname} = %{EVRD}

%description -n	%{static}
Static libraries for fuse.

%prep
%setup -qn fuse-%{version}
%apply_patches

sed -e 's|mknod|/bin/echo Disabled: mknod |g' -i util/Makefile.in
sed -i -e 's|INIT_D_PATH=.*|INIT_D_PATH=%{_initrddir}|' configure*

%build
%configure \
    CC="gcc -fuse-ld=bfd" \
    LD="ld.bfd" \
    --bindir=/bin \
    --exec-prefix=/ \
    --enable-static \
    --enable-util \
    --enable-lib \
    --disable-mtab

%make

%install
%makeinstall_std

install -d %{buildroot}/%{_lib}
for l in libfuse.so libulockmgr.so; do
    rm %{buildroot}%{_libdir}/${l}
    mv %{buildroot}%{_libdir}/${l}.*.* %{buildroot}/%{_lib}
    ln -sr %{buildroot}/%{_lib}/${l}.*.* %{buildroot}%{_libdir}/${l}
done

# XXX: have a hard time believing that these symlinks are actually needed,,,
mkdir -p %{buildroot}%{_bindir}
ln -s /bin/fusermount %{buildroot}%{_bindir}/fusermount
ln -s /bin/ulockmgr_server %{buildroot}%{_bindir}/ulockmgr_server

rm -rf %{buildroot}%{_sysconfdir}/rc.d/init.d %{buildroot}%{_sysconfdir}/udev/rules.d

%preun
if [ -f %{_sysconfdir}/rc.d/init.d/fuse ]; then
    chkconfig --del fuse
fi

%files
%doc AUTHORS ChangeLog NEWS README.NFS
%attr(0755,root,root) /sbin/mount.fuse
%attr(4755,root,root) /bin/fusermount
%attr(0755,root,root) /bin/ulockmgr_server
%{_bindir}/fusermount
%{_bindir}/ulockmgr_server
%{_mandir}/man1/fusermount.1.*
%{_mandir}/man1/ulockmgr_server.1.*
%{_mandir}/man8/mount.fuse.8.*

%files -n %{libname}
/%{_lib}/libfuse.so.%{major}*

%files -n %{libulm}
/%{_lib}/libulockmgr.so.%{ulmajor}*

%files -n %{devname}
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*

%files -n %{static}
%{_libdir}/*.a
