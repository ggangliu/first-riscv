# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'first-riscv'
copyright = '2024, ggangliu'
author = 'ggangliu'
release = '0.01'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme' #'alabaster'
html_static_path = ['_static']

simplepdf_vars = {
    'primary': '#FA2323',
    'secondary': '#379683',
    'cover': '#ffffff',
    'white': '#ffffff',
    'links': 'FA2323',
    'cover-bg': 'url(cover-bg.jpg) no-repeat center',
    'cover-overlay': 'rgba(250, 35, 35, 0.5)',
    'top-left-content': 'counter(page)',
    'bottom-center-content': '"Custom footer content"',
}

# conf.py
extensions = ['sphinx_simplepdf', 'rst2pdf.pdfbuilder']
pdf_documents = [('index', u'rst2pdf', u'Sample rst2pdf doc', u'ggangliu'),]