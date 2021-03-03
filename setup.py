from setuptools import setup, find_packages

__version__ = '0.3.1'


def read(filename):
    with open(filename, "r", encoding="utf-8") as fh:
        return fh.read()


setup(
    name='cst-micro-chassis',
    version=__version__,
    author='cst',
    license='MIT',
    author_email='tech@nicuzs.com',  # i had to add a "real" email
    url='https://test.pypi.org/project/cst-micro-chassis/',
    description='Will explain later ... ',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'flask==1.1.*',
        'flask-restful==0.3.*',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
