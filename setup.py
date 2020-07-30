import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'requirements.txt'), 'r') as f:
    requirements = f.readlines()

with open(os.path.join(here, 'requirements-test.txt'), 'r') as f:
    test_requirements = f.readlines()

with open(os.path.join(here, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='mlflow-client',
    version_config={
        "template": "{tag}",
        "dev_template": "{tag}.dev{ccount}",
        "dirty_template": "{tag}",
        "starting_version": "0.0.1"
    },
    description='Low-level Python client for MLflow API',
    long_description=long_description,
    long_description_content_type="text/markdown",
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
    setup_requires=['setuptools-git-versioning'],
    test_suite='tests',
    include_package_data=False,
    zip_safe=False
)
