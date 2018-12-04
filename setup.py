from setuptools import setup, find_packages

setup(
    name="mediapub_extensions",
    version='0.0.1a4.dev1',
    url='TBD',
    license="Apache 2.0",
    author="David Parks",
    author_email="businessintelligence@seattletimes.com",
    description="Tools for Media Publishers",
    packages=find_packages(exclude=['tests']),
    # long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=['snowflake-connector-python==1.6.3',
                      'google-api-python-client==1.7.4',
                      'google-cloud==0.27.0',
                      'oauth2client==4.1.2',
                      'googleads==14.1.0'
                      ]
    # setup_requires=[],
    # test_suite=''
    # keywords = ''
)
