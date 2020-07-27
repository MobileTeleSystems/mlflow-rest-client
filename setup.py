import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.readlines()

with open(os.path.join(here, 'requirements-test.txt'), encoding='utf-8') as f:
    test_requirements = f.readlines()

with open(os.path.join(here, 'VERSION'), encoding='utf-8') as f:
    version = f.read()

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mlflow-client',
    version=version,
    description='Low-level Python client for MLflow API',
    long_description=long_description,
    url='https://git.bd.msk.mts.ru/bigdata/platform/dsx/mlflow-python-client',
    author='msmarty4', author_email="msmarty4@mts.ru",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='MLflow REST API',
    packages=['mlflow_client'],
    install_requires=requirements,
    tests_require=test_requirements,
    test_suite='tests',
    include_package_data=False,
    zip_safe=False
)
