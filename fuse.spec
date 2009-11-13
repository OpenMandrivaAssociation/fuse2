%define major                   2
%define libname                 %mklibname %{name} %{major}
%define libnamedev              %mklibname %{name} -d
%define libnamestaticdev        %mklibname %{name} -d -s
%define ulock_major		1

Summary:        Interface for userspace programs to export a virtual filesystem to the kernel
Name:           fuse
Version:        2.8.1
Release:        %mkrel 2
Epoch:          0
License:        GPL
Group:          System/Libraries
URL:            http://sourceforge.net/projects/fuse/
Source0:        http://ovh.dl.sourceforge.net/sourceforge/%{name}/%{name}-%{version}.tar.gz
Source2:        fuse-makedev.d-fuse
Patch0:		fuse-2.8.0-fix-str-fmt.patch
Requires(post): makedev
Requires(post): rpm-helper
Requires(preun): rpm-helper
Obsoletes:      dkms-fuse <= 0:2.7.4-1mdv2009.0
BuildRequires:	libtool
BuildRequires:	gettext-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
FUSE (Filesystem in USErspace) is a simple interface for userspace
programs to export a virtual filesystem to the linux kernel.  FUSE
also aims to provide a secure method for non privileged users to
create and mount their own filesystem implementations.

%package -n %{libnamedev}
Summary:        Header files and development libraries for libfuse2
Group:          Development/C
Provides:       %{name}-devel = %{epoch}:%{version}-%{release}
Requires:       %{libname} = %{epoch}:%{version}-%{release}
Obsoletes:	%libname-devel

%description -n %{libnamedev}
Header files and development libraries for fuse.

%package -n %{libname}
Summary:        Libraries for fuse
Group:          Development/C

%description -n %{libname}
Libraries for fuse.

%package -n %{libnamestaticdev}
Summary:        Static libraries for fuse
Group:          Development/C
Provides:       %{name}-static-devel = %{epoch}:%{version}-%{release}
Requires:       %{libnamedev} = %{epoch}:%{version}-%{release}
Obsoletes:	%libname-static-devel

%description -n %{libnamestaticdev}
Static libraries for fuse.

%prep

%setup -q
%patch0 -p0
%{__sed} -i 's|mknod|/bin/echo Disabled: mknod |g' util/Makefile.in
%{__perl} -pi -e 's|INIT_D_PATH=.*|INIT_D_PATH=%{_initrddir}|' configure*

%build
#libtoolize --copy --force; aclocal; autoconf; automake

%configure2_5x \
    --libdir=/%{_lib} \
    --bindir=/bin \
    --exec-prefix=/

%make

%install
%{__rm} -rf %{buildroot}

%makeinstall_std

%{__mkdir_p} %{buildroot}%{_sysconfdir}/makedev.d
%{__cp} -a %{SOURCE2} %{buildroot}%{_sysconfdir}/makedev.d/z-fuse

%{__mkdir_p} %{buildroot}%{_libdir}
%{__mv} %{buildroot}/%{_lib}/pkgconfig %{buildroot}%{_libdir}

%{__mkdir_p} %{buildroot}%{_bindir}
pushd %{buildroot}%{_bindir}
%{__ln_s} /bin/fusermount fusermount
%{__ln_s} /bin/ulockmgr_server ulockmgr_server
popd

rm -fr %{buildroot}%{_sysconfdir}/rc.d/init.d %{buildroot}%{_sysconfdir}/udev/rules.d


%preun
if [ -f %{_sysconfdir}/rc.d/init.d/fuse ]; then
  chkconfig --del fuse
fi


%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
%doc AUTHORS COPYING COPYING.LIB ChangeLog FAQ Filesystems INSTALL NEWS README README.NFS
%attr(0755,root,root) /sbin/mount.fuse
%attr(4755,root,root) /bin/fusermount
%attr(0755,root,root) /bin/ulockmgr_server
%config(noreplace) %{_sysconfdir}/makedev.d/z-fuse
%{_bindir}/fusermount
%{_bindir}/ulockmgr_server
%exclude /%{_lib}/libulockmgr.a
%exclude /%{_lib}/libulockmgr.la

%files -n %{libname}
%defattr(-,root,root,0755)
/%{_lib}/libfuse.so.%{major}*
/%{_lib}/libulockmgr.so.%{ulock_major}*

%files -n %{libnamedev}
%defattr(-,root,root,0755)
%{_includedir}/*
/%{_lib}/libfuse.la
/%{_lib}/*.so
%{_libdir}/pkgconfig/*

%files -n %{libnamestaticdev}
%defattr(0644,root,root,0755)
/%{_lib}/libfuse.a
