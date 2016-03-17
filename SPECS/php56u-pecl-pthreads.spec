# IUS spec file for php56u-pecl-pthreads, forked from:
#
# spec file for php-pecl-pthreads
#
# Copyright (c) 2013-2015 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%global pecl_name pthreads
%global ini_name  40-%{pecl_name}.ini
%define php_base php56u

Summary:        Threading API
Name:           %{php_base}-pecl-pthreads
Version:        2.0.10
Release:        3.ius%{?dist}
License:        PHP
Group:          Development/Languages
URL:            http://pecl.php.net/package/%{pecl_name}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRequires:  %{php_base}-zts-devel
BuildRequires:  %{php_base}-pear

Requires(post): %{php_base}-pear
Requires(postun): %{php_base}-pear
Requires:      %{php_base}(zend-abi) = %{php_zend_api}
Requires:      %{php_base}(api) = %{php_core_api}

# provide the stock name
Provides:     php-pecl-%{pecl_name} = %{version}
Provides:     php-pecl-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides:     php-%{pecl_name} = %{version}
Provides:     php-%{pecl_name}%{?_isa} = %{version}
Provides:     %{php_base}-%{pecl_name} = %{version}
Provides:     %{php_base}-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides:     php-pecl(%{pecl_name}) = %{version}
Provides:     php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:     %{php_base}-pecl(%{pecl_name}) = %{version}
Provides:     %{php_base}-pecl(%{pecl_name})%{?_isa} = %{version}

# conflict with the stock name
Conflicts:    php-pecl-%{pecl_name} < %{version}

# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
# RPM 4.9
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


%description
A compatible Threading API for PHP5.3+

Documentation: http://php.net/pthreads

This extension is only available for PHP in ZTS mode.


%prep
%setup -q -c

# Don't install/register tests
sed -e 's/role="test"/role="src"/' -i package.xml

cd %{pecl_name}-%{version}

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_PTHREADS_VERSION/{s/.* "//;s/".*$//;p}' php_pthreads.h)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}.
   exit 1
fi
cd ..

# Create configuration file
cat > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF


%build
cd %{pecl_name}-%{version}
%{_bindir}/zts-phpize
%configure \
    --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}


%install
make -C %{pecl_name}-%{version} \
     install INSTALL_ROOT=%{buildroot}

# install config file
install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

# Documentation
cd %{pecl_name}-%{version}
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do sed -e 's/\r//' -i $i
   install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%post
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%check
cd %{pecl_name}-%{version}

: Minimal load test for ZTS extension
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

: Upstream test suite  for ZTS extension
TEST_PHP_EXECUTABLE=%{_bindir}/zts-php \
TEST_PHP_ARGS="-n -d extension=$PWD/modules/%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{_bindir}/zts-php -n run-tests.php


%files
%{?_licensedir:%license %{pecl_name}-%{version}/LICENSE}
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{pecl_name}.xml

%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so


%changelog
* Thu Mar 17 2016 Carl George <carl.george@rackspace.com> - 2.0.10-3.ius
- Clean up provides
- Clean up filters
- Install package.xml as %%{pecl_name}.xml, not %%{name}.xml
- Explictly require IUS pear package for %%post and %%postun

* Mon Jun 01 2015 Ben Harper <ben.harper@rackspace.com> - 2.0.10-2.ius
- porting from Remi's github repo https://github.com/remicollet/remirepo/blob/b748aa3aa58473258b7ec2012bd74c5105b7b862/php/pecl/php-pecl-pthreads/php-pecl-pthreads.spec

* Wed Oct 01 2014 Remi Collet <remi@fedoraproject.org> - 2.0.10-1
- Update to 2.0.10 (stable)

* Wed Sep 24 2014 Remi Collet <remi@fedoraproject.org> - 2.0.9-1
- Update to 2.0.9 (stable)

* Mon Sep 15 2014 Remi Collet <remi@fedoraproject.org> - 2.0.8-1
- Update to 2.0.8 (stable)

* Sun May 11 2014 Remi Collet <remi@fedoraproject.org> - 2.0.7-1
- Update to 2.0.7 (stable)

* Sat May 10 2014 Remi Collet <remi@fedoraproject.org> - 2.0.5-1
- Update to 2.0.5 (stable)
- add numerical prefix to extension configuration file

* Sun Mar 30 2014 Remi Collet <remi@fedoraproject.org> - 2.0.4-1
- Update to 2.0.4 (stable)

* Thu Mar 27 2014 Remi Collet <remi@fedoraproject.org> - 2.0.3-1
- Update to 2.0.3 (stable)
- allow SCL build, even if php54 and php55 don't have ZTS

* Fri Mar 21 2014 Remi Collet <remi@fedoraproject.org> - 2.0.2-1
- Update to 2.0.2 (stable)

* Mon Mar 17 2014 Remi Collet <remi@fedoraproject.org> - 2.0.1-1
- Update to 2.0.1 (stable)
- open https://github.com/krakjoe/pthreads/issues/262
  segfault in test suite

* Fri Mar 14 2014 Remi Collet <remi@fedoraproject.org> - 2.0.0-1
- Update to 2.0.0 (stable)
- open https://github.com/krakjoe/pthreads/issues/258
  tests/pools.phpt use PHP 5.5 syntax

* Sun Mar 09 2014 Remi Collet <remi@fedoraproject.org> - 1.0.1-1
- Update to 1.0.1 (stable)
- open https://github.com/krakjoe/pthreads/pull/251
  fix build + fix warnings

* Fri Mar 07 2014 Remi Collet <remi@fedoraproject.org> - 1.0.0-2
- rebuild with new sources :(
- open https://github.com/krakjoe/pthreads/pull/249
  fix test suite for PHP 5.4, and clean build warnings

* Fri Mar 07 2014 Remi Collet <remi@fedoraproject.org> - 1.0.0-1
- Update to 1.0.0 (stable)

* Sat Jan 18 2014 Remi Collet <remi@fedoraproject.org> - 0.1.0-1
- Update to 0.1.0 (stable)

* Sat Oct 26 2013 Remi Collet <remi@fedoraproject.org> - 0.0.45-1
- initial package, version 0.0.45 (stable)
  open https://github.com/krakjoe/pthreads/pull/193
