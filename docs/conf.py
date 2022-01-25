# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import sys
import subprocess
from pathlib import Path

from packaging.version import Version

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

setup_py = Path(__file__).parent.parent.joinpath("setup.py").absolute()
ver = Version(
    subprocess.check_output(  # nosec
        f"{sys.executable} {setup_py} --version",
        shell=True,
    )
    .decode("utf-8")
    .strip()
)

# -- Project information -----------------------------------------------------

project = "mlflow-rest-client"
copyright = "2022, MTS (Mobile Telesystems)"
author = "MTS DSX Team"

# The short X.Y version
version = ver.base_version
# The full version, including alpha/beta/rc tags
release = ver.public


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx_autodoc_typehints",
    "changelog",
    "numpydoc",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumds.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_title = f"mlflow-rest-client {version}"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named 'default.css' will overwrite the builtin 'default.css'.
# html_static_path = ['_static']

extlinks = {
    "github-user": ("https://github.com/%s", "@%s"),
}

changelog_sections = [
    "general",
    "client",
    "artifact",
    "experiment",
    "model",
    "page",
    "run",
    "tag",
    "dependency",
    "docs",
    "samples",
    "ci",
    "tests",
    "dev",
]

changelog_caption_class = ""

changelog_inner_tag_sort = ["breaking", "deprecated", "feature", "bug", "refactor"]
changelog_hive_sections_from_tags = True

changelog_render_ticket = {
    "default": "https://github.com/MobileTeleSystems/mlflow-rest-client/issues/%s",
    "DSX": "https://jira.bd.msk.mts.ru/browse/DSX-%s",
    "SCRR": "https://jira.bd.msk.mts.ru/browse/SCRR-%s",
}
changelog_render_pullreq = {
    "default": "https://github.com/MobileTeleSystems/mlflow-rest-client/pull/%s",
    "gitlab": "https://gitlab.services.mts.ru/bigdata/platform/dsx/mlflow-client/-/merge_requests/%s",
}
changelog_render_changeset = "https://github.com/MobileTeleSystems/mlflow-rest-client/commit/%s"

language = "en"

default_role = "any"
todo_include_todos = False

numpydoc_show_class_members = False
pygments_style = "sphinx"

autoclass_content = "both"
