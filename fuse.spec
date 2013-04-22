%define	major	2
%define	ulmajor	1
%define	libname	%mklibname %{name} %{major}
%define	libulm	%mklibname ulockmgr %{ulmajor}
%define	devname	%mklibname %{name} -d
%define	static	%mklibname %{name} -d -s

%bcond_without	uclibc

Summary:	Interface for userspace programs to export a virtual filesystem to the kernel
Name:		fuse
Version:	2.9.2
Release:	3
License:	GPLv2+
Group:		System/Base
Url:		http://sourceforge.net/projects/fuse/
Source0:	http://ovh.dl.sourceforge.net/sourceforge/%{name}/%{name}-%{version}.tar.gz
Patch0:		mount-readlink-hang-workaround.patch
Patch1:		fuse-2.9.2-automake-1.13.patch

BuildRequires:	libtool
BuildRequires:	gettext-devel
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-16
%endif
Requires(post,preun):	rpm-helper

%description
FUSE (Filesystem in USErspace) is a simple interface for userspace
programs to export a virtual filesystem to the linux kernel.  FUSE
also aims to provide a secure method for non privileged users to
create and mount their own filesystem implementations.

%package -n	uclibc-%{name}
Summary:	uClibc build of fuse
Group:		System/Base

%description -n	uclibc-%{name}
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

%package -n	uclibc-%{libname}
Summary:	Libraries for fuse (uClibc build)
Group:		System/Libraries
License:	LGPLv2+

%description -n	uclibc-%{libname}
Libraries for fuse.

%package -n	%{libulm}
Summary:	libulockmgr for fuse
Group:		System/Libraries
License:	LGPLv2+
Conflicts:	%{libname} < 2.9.2-1

%description -n	%{libulm}
Libraries for fuse.

%package -n	uclibc-%{libulm}
Summary:	libulockmgr for fuse (uClibc build)
Group:		System/Libraries
License:	LGPLv2+

%description -n	uclibc-%{libulm}
Libraries for fuse.

%package -n	%{devname}
Summary:	Header files and development libraries for libfuse2
Group:		Development/C
License:	LGPLv2+
Provides:	%{name}-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}
Requires:	%{libulm} = %{EVRD}
%if %{with uclibc}
Requires:	uclibc-%{libname} = %{version}
Requires:	uclibc-%{libulm} = %{version}
%endif

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
%setup -q
%apply_patches

sed -e 's|mknod|/bin/echo Disabled: mknod |g' -i util/Makefile.in
sed -i -e 's|INIT_D_PATH=.*|INIT_D_PATH=%{_initrddir}|' configure*

%build
CONFIGURE_TOP=$PWD
%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
%uclibc_configure \
	CC="%{uclibc_cc} -fuse-ld=bfd" \
	--bindir=%{uclibc_root}/bin \
	--sbindir=%{uclibc_root}/sbin \
	--exec-prefix=/
%make
popd
%endif

mkdir -p system
pushd system
%configure2_5x \
	CC="gcc -fuse-ld=bfd" \
	--bindir=/bin \
	--exec-prefix=/
%make
popd

%install
%if %{with uclibc}
%makeinstall_std -C uclibc
install -d %{buildroot}%{uclibc_root}/%{_lib}
for l in libfuse.so libulockmgr.so; do
	rm %{buildroot}%{uclibc_root}%{_libdir}/${l}
	mv %{buildroot}%{uclibc_root}%{_libdir}/${l}.*.* %{buildroot}%{uclibc_root}/%{_lib}
	ln -sr %{buildroot}%{uclibc_root}/%{_lib}/${l}.*.* %{buildroot}%{uclibc_root}%{_libdir}/${l}
done
rm -r %{buildroot}%{uclibc_root}%{_libdir}/pkgconfig
%endif

%makeinstall_std -C system
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
%doc AUTHORS ChangeLog FAQ Filesystems NEWS README README.NFS
%attr(0755,root,root) /sbin/mount.fuse
%attr(4755,root,root) /bin/fusermount
%attr(0755,root,root) /bin/ulockmgr_server
%{_bindir}/fusermount
%{_bindir}/ulockmgr_server
%{_mandir}/man1/fusermount.1.*
%{_mandir}/man1/ulockmgr_server.1.*
%{_mandir}/man8/mount.fuse.8.*

%if %{with uclibc}
%files -n uclibc-%{name}
%attr(4755,root,root) %{uclibc_root}/bin/fusermount
%attr(0755,root,root) %{uclibc_root}/bin/ulockmgr_server
%endif

%files -n %{libname}
/%{_lib}/libfuse.so.%{major}*

%if %{with uclibc}
%files -n uclibc-%{libname}
%{uclibc_root}/%{_lib}/libfuse.so.%{major}*
%endif

%files -n %{libulm}
/%{_lib}/libulockmgr.so.%{ulmajor}*

%if %{with uclibc}
%files -n uclibc-%{libulm}
%{uclibc_root}/%{_lib}/libulockmgr.so.%{ulmajor}*
%endif

%files -n %{devname}
%{_includedir}/*
%{_libdir}/*.so
%if %{with uclibc}
%{uclibc_root}%{_libdir}/*.so
%endif
%{_libdir}/pkgconfig/*

%files -n %{static}
%{_libdir}/*.a
%if %{with uclibc}
%{uclibc_root}%{_libdir}/*.a
%endif

