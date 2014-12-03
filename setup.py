try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requirements = [r for r in map(str.strip, open('requirements.txt').readlines())]
exec([v for v in open('chai/__init__.py') if '__version__' in v][0])

setup(
    name='chai',
    version=__version__,
    author='Vitaly Babiy, Aaron Westendorf',
    author_email="vbabiy@agoragames.com, aaron@agoragames.com",
    packages=['chai'],
    url='https://github.com/agoragames/chai',
    license='LICENSE.txt',
    description="Easy to use mocking, stubbing and spying framework.",
    long_description=open('README.rst').read(),
    keywords=['python', 'test', 'mock'],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 6 - Mature',
        'License :: OSI Approved :: BSD License',
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        'Topic :: Software Development :: Libraries',
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
    ],
    test_suite="tests",
)
