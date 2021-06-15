
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ''

setup(
    long_description=readme,
    name='pipda',
    version='0.2.8',
    description='A framework for data piping in python',
    python_requires='==3.*,>=3.7.0',
    author='pwwang',
    author_email='pwwang@pwwang.com',
    license='MIT',
    packages=['pipda'],
    package_dir={"": "."},
    package_data={},
    install_requires=['executing', 'varname'],
    extras_require={"dev": ["pytest", "pytest-cov"]},
)
