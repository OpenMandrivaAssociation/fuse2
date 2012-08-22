%define	major	2
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d
%define	static	%mklibname %{name} -d -s
%define	ulmajor	1

Summary:	Interface for userspace programs to export a virtual filesystem to the kernel
Name:		fuse
Version:	2.9.1
Release:	1
Epoch:		0
License:	GPLv2+
Group:		System/Libraries
URL:		http://sourceforge.net/projects/fuse/
Source0:	http://downloads.sourceforge.net/project/fuse/fuse-2.X/%{version}/%{name}-%{version}.tar.gz
Source2:	fuse-makedev.d-fuse
Patch0:		mount-readlink-hang-workaround.patch
Requires(post):	makedev
Requires(post):	rpm-helper
Requires(preun):rpm-helper
Obsoletes:	dkms-fuse <= 0:2.7.4-1mdv2009.0
BuildRequires:	libtool
BuildRequires:	gettext-devel

%description
FUSE (Filesystem in USErspace) is a simple interface for userspace
programs to export a virtual filesystem to the linux kernel.  FUSE
also aims to provide a secure method for non privileged users to
create and mount their own filesystem implementations.

%package -n	%{libname}
Summary:	Libraries for fuse
Group:		Development/C
License:	LGPLv2+

%description -n	%{libname}
Libraries for fuse.

%package -n	%{devname}
Summary:	Header files and development libraries for libfuse2
Group:		Development/C
License:	LGPLv2+
Provides:	%{name}-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}

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
%patch0 -p1

sed -e 's|mknod|/bin/echo Disabled: mknod |g' -i util/Makefile.in
perl -pi -e 's|INIT_D_PATH=.*|INIT_D_PATH=%{_initrddir}|' configure*

%build
%configure2_5x	--libdir=/%{_lib} \
		--bindir=/bin \
		--exec-prefix=/
%make

%install
%makeinstall_std

install -m644 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/makedev.d/z-fuse

mkdir -p  %{buildroot}%{_libdir}
mv %{buildroot}/%{_lib}/pkgconfig %{buildroot}%{_libdir}

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
%config(noreplace) %{_sysconfdir}/makedev.d/z-fuse
%{_bindir}/fusermount
%{_bindir}/ulockmgr_server
%{_mandir}/man1/fusermount.1.*
%{_mandir}/man1/ulockmgr_server.1.*
%{_mandir}/man8/mount.fuse.8.*

%files -n %{libname}
/%{_lib}/libfuse.so.%{major}*
/%{_lib}/libulockmgr.so.%{ulmajor}*

%files -n %{devname}
%{_includedir}/*
/%{_lib}/*.so
%{_libdir}/pkgconfig/*

%files -n %{static}
/%{_lib}/*.a
