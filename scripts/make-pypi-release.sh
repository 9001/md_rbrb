#!/bin/bash
set -e
echo

mode="$1"

[[ "x$mode" == x ]] &&
{
	echo "need argument 1:  (D)ry or (U)pload"
	echo
	exit 1
}

[[ -e md_rbrb.py ]] || cd ..
[[ -e md_rbrb.py ]] ||
{
	echo "run me from within the md_rbrb folder"
	echo
	exit 1
}

# one-time stuff, do this manually through copy/paste
true ||
{
	cat > ~/.pypirc <<EOF
[distutils]
index-servers =
  pypi
  pypitest

[pypi]
username=qwer
password=asdf

[pypitest]
repository: https://test.pypi.org/legacy/
username=qwer
password=asdf
EOF

	# set pypi password
	chmod 600 ~/.pypirc
	sed -ri 's/qwer/username/;s/asdf/password/' ~/.pypirc

	# setup build env
	cd ~/dev/md_rbrb &&
	virtualenv buildenv
	
	# test rst
	pip install docutils
	./setup.py rstconv; ./setup.py --long-description | tee ~/Desktop/rst | rst2html.py > ~/Desktop/rst.html
}

pydir="$(
	which python |
	sed -r 's@[^/]*$@@'
)"

[[ -e "$pydir/activate" ]] &&
{
	echo '`deactivate` your virtualenv'
	exit 1
}

function have() {
	python -c "import $1; $1; $1.__version__"
}

. buildenv/bin/activate
have setuptools
have wheel
have m2r
./setup.py clean2
./setup.py rstconv
./setup.py sdist bdist_wheel --universal
[[ "x$mode" == "xu" ]] &&
	./setup.py sdist bdist_wheel upload -r pypi

cat <<EOF


    all done!
    
    to clean up the source tree:
    
       cd ~/dev/md_rbrb
       ./setup.py clean2
   
EOF

