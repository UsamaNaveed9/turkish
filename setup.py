# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in turkish/__init__.py
from turkish import __version__ as version

setup(
	name='turkish',
	version=version,
	description='invoice',
	author='usama',
	author_email='usama@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
