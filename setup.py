#! /usr/bin/env python

from setuptools import setup

deps = []

setup(
    name="csrtool",
    version="0.1.0",
    description="Generate and sign CSRs",
    author="Release Engineers",
    author_email="release+python@mozilla.com",
    py_modules=["ssl"],
    test_suite='tests',
    zip_safe=False,
    license="MPL 2.0",
    install_requires=deps,
    entry_points={
        'console_scripts': [
            'csrtool = csrtool:main'
        ],
    },
    # include files listed in MANIFEST.in
    include_package_data=True,
    classifiers=(
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ),
)
