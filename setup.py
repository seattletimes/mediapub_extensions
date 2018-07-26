from setuptools import setup, find_packages

setup(
    name="mediapub_extensions",
    version='0.0.1a1.dev1',
    url='TBD',
    license="MIT",
    author="David Parks",
    author_email="businessintelligence@seattletimes.com",
    description="Tools for Media Publishers",
    packages=find_packages(exclude=['tests']),
    # long_description=open('README.md').read(),
    zip_safe=False,
    # setup_requires=[],
    # test_suite=''
)
