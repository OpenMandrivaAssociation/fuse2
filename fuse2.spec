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
Release:	5
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

rm -rf %{buildroot}%{_sysconfdir}/rc.d/init.d %{buildroot}%{_sysconfdir}/udev/rules.d

# (tpg) strip LTO from "LLVM IR bitcode" files
check_convert_bitcode() {
    printf '%s\n' "Checking for LLVM IR bitcode"
    llvm_file_name=$(realpath ${1})
    llvm_file_type=$(file ${llvm_file_name})

    if printf '%s\n' "${llvm_file_type}" | grep -q "LLVM IR bitcode"; then
# recompile without LTO
    clang %{optflags} -fno-lto -Wno-unused-command-line-argument -x ir ${llvm_file_name} -c -o ${llvm_file_name}
    elif printf '%s\n' "${llvm_file_type}" | grep -q "current ar archive"; then
    printf '%s\n' "Unpacking ar archive ${llvm_file_name} to check for LLVM bitcode components."
# create archive stage for objects
    archive_stage=$(mktemp -d)
    archive=${llvm_file_name}
    cd ${archive_stage}
    ar x ${archive}
    for archived_file in $(find -not -type d); do
        check_convert_bitcode ${archived_file}
        printf '%s\n' "Repacking ${archived_file} into ${archive}."
        ar r ${archive} ${archived_file}
    done
    ranlib ${archive}
    cd ..
    fi
}

for i in $(find %{buildroot} -type f -name "*.[ao]"); do
    check_convert_bitcode ${i}
done

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
