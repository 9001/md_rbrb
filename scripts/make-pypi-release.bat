cd %~dp0\..
python setup.py clean2
python setup.py sdist bdist_wheel --universal
REM python setup.py sdist upload -r pypi
