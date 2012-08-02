#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='rubber',
    version='0.1',
    description='Elasticsearch client with Django support.',
    author='Stéphane JAIS',
    author_email='stephane@cantinasoftware.com',
    long_description=open('README.md', 'r').read(),
    url='https://github.com/cantinasoftware/rubber',
    packages=[
        'rubber',
        'tests'
    ],
    package_data={
        'rubber': []
    },
    test_suite='tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
