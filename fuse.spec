%define major                   2
%define libname                 %mklibname %{name} %{major}
%define libnamedev              %mklibname %{name} %{major} -d
%define libnamestaticdev        %mklibname %{name} %{major} -d -s

Summary:        Interface for userspace programs to export a virtual filesystem to the kernel
Name:           fuse
Version:        2.6.4
Release:        %mkrel 1
Epoch:          0
License:        GPL
Group:          System/Libraries
URL:            http://sourceforge.net/projects/fuse/
Source0:        http://ovh.dl.sourceforge.net/fuse/fuse-%{version}.tar.gz
Source1:        fuse.init
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRequires:  kernel-source
BuildRequires:  libtool
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
FUSE (Filesystem in USErspace) is a simple interface for userspace
programs to export a virtual filesystem to the linux kernel.  FUSE
also aims to provide a secure method for non privileged users to
create and mount their own filesystem implementations.

%package -n %{libnamedev}
Summary:        Header files and development libraries for libfuse2
Group:          Development/C
Provides:       lib%{name}-devel = %{version}-%{release} %{name}-devel = %{version}-%{release}
Provides:       %{_lib}fuse-devel
Requires:       %{libname} = %{version}

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
Provides:       libfuse-static-devel = %{version}-%{release}
Provides:       %{_lib}fuse-static-devel

%description -n %{libnamestaticdev}
Static libraries for fuse.

%package -n     dkms-%{name}
Summary:        Linux kernel module for FUSE (Filesystem in Userspace)
Group:          System/Kernel and hardware
Requires(post): dkms
Requires(preun): dkms

%description -n dkms-%{name}
FUSE (Filesystem in USErspace) is a simple interface for userspace
programs to export a virtual filesystem to the linux kernel.  FUSE
also aims to provide a secure method for non privileged users to
create and mount their own filesystem implementations.

This package provides the kernel module part.

%prep
%setup -q
%{__rm} util/init_script
%{__cp} -a %{SOURCE1} util/init_script

%build
%{__perl} -pi -e 's|INIT_D_PATH=.*|INIT_D_PATH=%{_initrddir}|' configure.in
%{__autoconf}
%{__libtoolize} --copy --force
%{configure2_5x} --disable-kernel-module
%{__make} LIBTOOL=%{_bindir}/libtool

%install
%{__rm} -rf %{buildroot}

# make install tries to mknod which will of course fail as a user.
# This works around that as it tests if the file exists.
%{__mkdir_p} %{buildroot}/dev/fuse

%{makeinstall_std} LIBTOOL=%{_bindir}/libtool

%{__mkdir_p} %{buildroot}%{_usrsrc}
%{__cp} -a kernel %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}

%{__cat} > %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/dkms.conf << EOF
PACKAGE_VERSION="%{version}-%{release}"

PACKAGE_NAME="%{name}"
MAKE[0]="./configure --enable-kernel-module && %{__make}"
CLEAN="test -f Makefile && %{__make} clean || :"

BUILT_MODULE_NAME[0]="\$PACKAGE_NAME"
DEST_MODULE_LOCATION[0]="/kernel/fs/\$PACKAGE_NAME/"

AUTOINSTALL=yes
REMAKE_INITRD=no
EOF

%clean
%{__rm} -rf %{buildroot}

%post
%_post_service fuse

%preun
%_preun_service fuse

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%post -n dkms-%{name}
%{_sbindir}/dkms add -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
%{_sbindir}/dkms build -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
%{_sbindir}/dkms install -m %{name} -v %{version}-%{release} --rpm_safe_upgrade

if [ $1 = 1 ]; then
  %{__grep} '[^#]*%{name}' %{_sysconfdir}/modprobe.preload || /bin/echo %{name} >> %{_sysconfdir}/modprobe.preload
  /sbin/modprobe %{name}
fi

%preun -n dkms-%{name}
%{_sbindir}/dkms remove -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --all ||:

%postun -n dkms-%{name}
if [ $1 = 0 ]; then
  %{__sed} -i '/.*%{name}/d' %{_sysconfdir}/modprobe.preload
fi

%files
%defattr(0644,root,root,0755)
%doc AUTHORS COPYING COPYING.LIB ChangeLog FAQ Filesystems INSTALL NEWS README README.NFS
%defattr(-,root,root,0755)
%{_bindir}/fusermount
%config(noreplace) %{_sysconfdir}/udev/rules.d/99-fuse.rules
/sbin/mount.fuse
%attr(0755,root,root) %{_initrddir}/fuse
%{_bindir}/ulockmgr_server
%exclude %{_libdir}/libulockmgr.a
%exclude %{_libdir}/libulockmgr.la

%files -n %{libname}
%defattr(-,root,root,0755)
%{_libdir}/*.so.*

%files -n %{libnamedev}
%defattr(-,root,root,0755)
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*

%files -n %{libnamestaticdev}
%defattr(-,root,root,0755)
%{_libdir}/libfuse.la
%{_libdir}/libfuse.a

%files -n dkms-%{name}
%defattr(-,root,root,0755)
%{_usrsrc}/%{name}-%{version}-%{release}


