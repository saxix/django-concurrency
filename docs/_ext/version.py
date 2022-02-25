import re

from docutils.parsers.rst import Directive, directives
from sphinx import addnodes, roles
from sphinx.errors import ExtensionError
from sphinx.util.console import bold
# RE for option descriptions without a '--' prefix
from sphinx.writers.html import HTMLTranslator

simple_option_desc_re = re.compile(
    r'([-_a-zA-Z0-9]+)(\s*.*?)(?=,\s+(?:/|-|--)|$)')


def setup(app):
    app.add_crossref_type(
        directivename="setting",
        rolename="setting",
        indextemplate="pair: %s; setting",
    )
    app.add_crossref_type(
        directivename="templatetag",
        rolename="ttag",
        indextemplate="pair: %s; template tag"
    )
    app.add_crossref_type(
        directivename="templatefilter",
        rolename="tfilter",
        indextemplate="pair: %s; template filter"
    )
    app.add_crossref_type(
        directivename="fieldlookup",
        rolename="lookup",
        indextemplate="pair: %s; field lookup type",
    )
    app.add_config_value('next_version', '0.0', True)
    app.add_crossref_type(
        directivename="release",
        rolename="release",
        indextemplate="pair: %s; release",
    )
