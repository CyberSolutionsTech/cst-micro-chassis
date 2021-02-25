import io
import os
import re

from setuptools import setup, find_packages

__version__ = '0.2.3'


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


setup(
    name='cst-micro-chassis',
    version=__version__,
    author='cst',
    license=read('LICENSE'),
    author_email='nicolae.natrapeiu@cyber-solutions.com',
    url='https://test.pypi.org/project/cst-micro-chassis/',
    description='Microservices chassis pattern library',
    long_description=read('README.md'),
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'flask==1.1.*',
        'flask-restful==0.3.*',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha'
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython'
        'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.7',
)
