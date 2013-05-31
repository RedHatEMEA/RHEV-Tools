Name:		rhev-tools
Version:	0.1.2
Release:	1%{?dist}
Summary:	RHEV utilities for everyday admin tasks

Group:		System Environment/Daemons
License:	GPL
URL:		https://github.com/RedHatEMEA/RHEV-Tools
Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch

BuildRequires:	/bin/tar
Requires:	python, ovirt-engine-sdk
Provides:	rhev-tools = 0.1.2

# disable debug packages and the stripping of the binaries
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%description
RHEV-Tools are a large collection of useful scripts utilizing the RHEV API.
They are intended to simplify administrative tasks from command line, as well
as serve as an example of the RHEV API usage.

%prep
%setup -q 

%build

%install
# Create the directories
mkdir -m 0755 -p $RPM_BUILD_ROOT/etc/rhev-tools
mkdir -m 0755 -p $RPM_BUILD_ROOT/usr/bin

cp -afv etc/rhev-tools/default.conf $RPM_BUILD_ROOT/etc/rhev-tools/default.conf
cp -afv general/events.py $RPM_BUILD_ROOT/usr/bin/
cp -afv general/import_vms.py $RPM_BUILD_ROOT/usr/bin/
cp -afv general/list_all_vms.py $RPM_BUILD_ROOT/usr/bin/
cp -afv general/move_vm.py $RPM_BUILD_ROOT/usr/bin/
cp -afv general/rhevtools.py $RPM_BUILD_ROOT/usr/bin/
cp -afv general/update_preferred_host.py $RPM_BUILD_ROOT/usr/bin/
cp -afv general/vm.py $RPM_BUILD_ROOT/usr/bin/

%clean
rm -rf $RPM_BUILD_ROOT

%pre

%post

%preun

%files
%defattr(-,root,root,-)
%attr(0755,root,root) %{_sysconfdir}/rhev-tools
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/rhev-tools/default.conf
%attr(0755,root,root) %{_bindir}/events.py
%attr(0755,root,root) %{_bindir}/import_vms.py
%attr(0755,root,root) %{_bindir}/list_all_vms.py
%attr(0755,root,root) %{_bindir}/move_vm.py
%attr(0644,root,root) %{_bindir}/rhevtools.py
%attr(0755,root,root) %{_bindir}/update_preferred_host.py
%attr(0755,root,root) %{_bindir}/vm.py
%doc general/import-list-example.csv README LICENSE SERIAL_CONSOLE

%changelog
* Fri May 31 2013 Miguel Perez Colino <mperez@redhat.com> 0.1.2-1
- Initial RPM 
