import os

try:
    from setuptools import setup, find_packages, Command
    from setuptools.command.test import test
    from setuptools.command.install import install
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command
    from setuptools.command.test import test
    from setuptools.command.install import install

setup(
    name='chai',
    version='0.1.0',
    author="Vitaly Babiy, Aaron Westendorf",
    author_email="vbabiy@agoragames.com, aaron@agoragames.com",
    packages = find_packages(),
    url="https://github.com/agoragames/chai",
    description="Easy to use mocking/stub framework.",
    license="MIT License",
    long_description=open('README.rst').read(),
    keywords=['python', 'test', 'mock'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Topic :: Communications",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries'
    ]
)
