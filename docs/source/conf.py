# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import sphinx
import datetime

project = 'first-riscv'
copyright = '2024, ggangliu'
author = 'ggangliu'
release = '0.01'
version = "0.01"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme' #'alabaster'
html_static_path = ['_static']

html_css_files = ['_variables.scss']



simplepdf_vars = {
    'cover-overlay': 'rgba(26, 150, 26, 0.7)',
    'primary-opaque': 'rgba(26, 150, 26, 0.7)',
    'cover-bg': 'url(cover-bg.jpg) no-repeat center',
    'primary': '#1a961a',
    'secondary': '#379683',
    'cover': '#ffffff',
    'white': '#ffffff',
    'links': '#1a961a',
    'top-left-content': '"Header left"',
    'top-center-content': '"Header center"',
    'top-right-content': '"Header right"',
    'bottom-left-content': 'counter(page)',
    'bottom-center-content': '"first RISC-V"',
    'bottom-right-content': 'string(heading)',
}

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'restructuredtext',
    '.md': 'markdown',
}


# conf.py
extensions = ['sphinx_simplepdf', 'rst2pdf.pdfbuilder']
pdf_documents = [('index', u'rst2pdf', u'Sample rst2pdf doc', u'ggangliu'),]