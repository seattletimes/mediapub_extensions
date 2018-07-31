from setuptools import setup, find_packages

setup(
    name="mediapub_extensions",
    version='0.0.1a2.dev5',
    url='TBD',
    license="Apache 2.0",
    author="David Parks",
    author_email="businessintelligence@seattletimes.com",
    description="Tools for Media Publishers",
    packages=find_packages(exclude=['tests']),
    # long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=['snowflake-connector-python==1.6.3']
    # setup_requires=[],
    # test_suite=''
    # keywords = ''
)
