from setuptools import setup, find_packages

setup(
    name="mediapub_extensions",
    version='1.1.beta',
    url='TBD',
    license="Apache 2.0",
    author="David Parks",
    author_email="businessintelligence@seattletimes.com",
    description="Tools for Media Publishers",
    packages=find_packages(exclude=['tests']),
    # long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=['snowflake-connector-python==2.4.2',
                      'google-api-python-client==1.12.8',
                      'google-cloud==0.34.0',
                      'oauth2client==4.1.3',
                      'pyodbc==4.0.30',
                      'googleads==26.0.0',
                      'google-cloud-bigquery==2.13.1',
                      'google-cloud-storage==1.37.1',
                      'pandas==1.2.1',
                      'pyarrow==3.0.0',
                      'google-cloud-bigquery-storage==2.3.0'
                      ]
    # setup_requires=[],
    # test_suite=''
    # keywords = ''
)
