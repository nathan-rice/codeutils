"""
Created on Nov 14, 2011

@author: Administrator
"""

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="UNC-ITS-RC Code Utilities",
    version="0.1",
    author="Nathan Rice",
    author_email="nathan_rice@unc.edu",
    long_description=read("README"),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    packages=["codeutils"],
    test_suite="test"
)
