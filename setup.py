import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "requirements.txt")) as f:
    requirements = f.readlines()

with open(os.path.join(here, "README.rst")) as f:
    long_description = f.read()

setup(
    name="mlflow-client",
    version_config={
        "template": "{tag}",
        "dev_template": "{tag}.dev{ccount}",
        "dirty_template": "{tag}",
        "version_file": os.path.join(here, "mlflow_client", "VERSION"),
        "count_commits_from_version_file": True,
    },
    description="Python client for MLflow API",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="Apache License 2.0",
    license_files=("LICENSE.txt",),
    url="https://github.com/MobileTeleSystems/mlflow-client",
    author="MTS DSX Team",
    author_email="dsx-team@mts.ru",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    project_urls={
        "Documentation": "https://mlflow-client.readthedocs.io/en/stable/",
        "Source": "https://github.com/MobileTeleSystems/mlflow-client",
        "CI/CD": "https://github.com/MobileTeleSystems/mlflow-client/actions",
        "Tracker": "https://github.com/MobileTeleSystems/mlflow-client/issues",
    },
    keywords="MLflow REST API",
    packages=find_packages(exclude=["docs", "docs.*", "tests", "tests.*", "samples", "samples.*"]),
    python_requires=">=3.7",
    install_requires=requirements,
    setup_requires=["setuptools-git-versioning>=1.8.1"],
    test_suite="tests",
    include_package_data=True,
    zip_safe=False,
)
