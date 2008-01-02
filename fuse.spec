%define major                   2
%define libname                 %mklibname %{name} %{major}
%define libnamedev              %mklibname %{name} -d
%define libnamestaticdev        %mklibname %{name} -d -s

Name:           fuse
Version:        2.7.1
Release:        %mkrel 2
Epoch:          0
Summary:        Interface for userspace programs to export a virtual filesystem to the kernel
License:        GPL
Group:          System/Libraries
URL:            http://sourceforge.net/projects/fuse/
Source0:        http://ovh.dl.sourceforge.net/sourceforge/%{name}/%{name}-%{version}.tar.gz
Source1:        fuse-udev.nodes
Source2:        fuse-makedev.d-fuse
Source4:        fuse.init
Patch0:         fuse-udev_rules.patch
Requires(post): makedev
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

%package -n dkms-%{name}
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
%patch0 -p0
%{__rm} util/init_script
%{__cp} -a %{SOURCE4} util/init_script
%{__sed} -i 's|mknod|/bin/echo Disabled: mknod |g' util/Makefile.in

%build
%{__perl} -pi -e 's|INIT_D_PATH=.*|INIT_D_PATH=%{_initrddir}|' configure
%{configure2_5x} --disable-kernel-module \
 --libdir=/%{_lib} \
 --bindir=/bin \
 --exec-prefix=/
%{make}

%install
%{__rm} -rf %{buildroot}
%{makeinstall_std}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/udev/devices.d
%{__cp} -a %{SOURCE1} %{buildroot}%{_sysconfdir}/udev/devices.d/99-fuse.nodes
%{__mkdir_p} %{buildroot}%{_sysconfdir}/makedev.d
%{__cp} -a %{SOURCE2} %{buildroot}%{_sysconfdir}/makedev.d/z-fuse

%{__mkdir_p} %{buildroot}%{_libdir}
%{__mv} %{buildroot}/%{_lib}/pkgconfig %{buildroot}%{_libdir}

%{__mkdir_p} %{buildroot}%{_bindir}
pushd %{buildroot}%{_bindir}
%{__ln_s} /bin/fusermount fusermount
%{__ln_s} /bin/ulockmgr_server ulockmgr_server
popd

%{__mkdir_p} %{buildroot}%{_usrsrc}
%{__cp} -a kernel %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}

%{__cat} > %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/dkms.conf << EOF
PACKAGE_VERSION="%{version}-%{release}"

PACKAGE_NAME="%{name}"
MAKE[0]="./configure --enable-kernel-module && make"
CLEAN="%{_bindir}/test -r Makefile && make clean || :"

BUILT_MODULE_NAME[0]="\$PACKAGE_NAME"
DEST_MODULE_LOCATION[0]="/kernel/fs/\$PACKAGE_NAME/"

AUTOINSTALL=yes
REMAKE_INITRD=no
EOF

%clean
%{__rm} -rf %{buildroot}

%pre
%_pre_groupadd fuse

%preun
%_preun_service fuse

%post
%_post_service fuse

%postun
%_postun_groupdel fuse

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
%attr(0755,root,root) /sbin/mount.fuse
%attr(4755,root,fuse) /bin/fusermount
%attr(0755,root,root) /bin/ulockmgr_server
%attr(0755,root,root) %{_initrddir}/fuse
%config(noreplace) %{_sysconfdir}/makedev.d/z-fuse
%{_bindir}/fusermount
%{_bindir}/ulockmgr_server
%config(noreplace) %{_sysconfdir}/udev/rules.d/99-fuse.rules
%config(noreplace) %{_sysconfdir}/udev/devices.d/99-fuse.nodes
%exclude /%{_lib}/libulockmgr.a
%exclude /%{_lib}/libulockmgr.la

%files -n %{libname}
%defattr(-,root,root,0755)
/%{_lib}/*.so.*

%files -n %{libnamedev}
%defattr(-,root,root,0755)
%{_includedir}/*
/%{_lib}/libfuse.la
/%{_lib}/*.so
%{_libdir}/pkgconfig/*

%files -n %{libnamestaticdev}
%defattr(0644,root,root,0755)
/%{_lib}/libfuse.a

%files -n dkms-%{name}
%defattr(-,root,root,0755)
%{_usrsrc}/%{name}-%{version}-%{release}
