#!/usr/bin/env python


import setuptools

setuptools.setup(
    name='cfman',
    version='0.1',
    description='Yet another configuration management and deploy tool',
    license='Apache 2.0',
    author='Anton Schur',
    author_email='tonich.sh@gmail.com',
    packages=[
        'cfman',
        'cfman.cmdbuilder',
        'cfman/cmdbuilder/commands',
        'cfman/joblib',
        'cfman/joblib/require',
        'cfman/executor',
        'cfman/executor/connector',
        'cfman/tests',
        'cfman/tests/commands',
    ],
    install_requires=[
        'paramiko>=2.4',
        'jinja2'
    ],
    entry_points={
        'console_scripts': [
            'cfman = cfman.executor.program:program.run',
        ]
    },
)
