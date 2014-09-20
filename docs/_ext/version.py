import re
from sphinx import addnodes, roles
from sphinx.util.console import bold
from sphinx.util.compat import Directive
from sphinx.writers.html import SmartyPantsHTMLTranslator

# RE for option descriptions without a '--' prefix
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
    app.add_directive('versionadded', VersionDirective)
    app.add_directive('versionchanged', VersionDirective)
    app.add_crossref_type(
        directivename="release",
        rolename="release",
        indextemplate="pair: %s; release",
    )

class DjangoHTMLTranslator(SmartyPantsHTMLTranslator):
    """
    Django-specific reST to HTML tweaks.
    """

    # Don't use border=1, which docutils does by default.
    def visit_table(self, node):
        self.context.append(self.compact_p)
        self.compact_p = True
        self._table_row_index = 0  # Needed by Sphinx
        self.body.append(self.starttag(node, 'table', CLASS='docutils'))

    def depart_table(self, node):
        self.compact_p = self.context.pop()
        self.body.append('</table>\n')

    def visit_desc_parameterlist(self, node):
        self.body.append('(')  # by default sphinx puts <big> around the "("
        self.first_param = 1
        self.optional_param_level = 0
        self.param_separator = node.child_text_separator
        self.required_params_left = sum([isinstance(c, addnodes.desc_parameter)
                                         for c in node.children])

    def depart_desc_parameterlist(self, node):
        self.body.append(')')


    version_text = {
        'deprecated': 'Deprecated in Django-Concurrency %s',
        'versionchanged': 'Changed in Django-Concurrency %s',
        'versionadded': 'New in Django-Concurrency %s',
    }

    def visit_versionmodified(self, node):
        self.body.append(
            self.starttag(node, 'div', CLASS=node['type'])
        )
        version_text = self.version_text.get(node['type'])
        if version_text:
            title = "%s%s" % (
                version_text % node['version'],
                ":" if len(node) else "."
            )
            self.body.append('<span class="title">%s</span> ' % title)

    def depart_versionmodified(self, node):
        self.body.append("</div>\n")

    # Give each section a unique ID -- nice for custom CSS hooks
    def visit_section(self, node):
        old_ids = node.get('ids', [])
        node['ids'] = ['s-' + i for i in old_ids]
        node['ids'].extend(old_ids)
        SmartyPantsHTMLTranslator.visit_section(self, node)
        node['ids'] = old_ids



class VersionDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        if len(self.arguments) > 1:
            msg = """Only one argument accepted for directive '{directive_name}::'.
            Comments should be provided as content,
            not as an extra argument.""".format(directive_name=self.name)
            raise self.error(msg)

        env = self.state.document.settings.env
        ret = []
        node = addnodes.versionmodified()
        ret.append(node)

        if self.arguments[0] == env.config.next_version:
            node['version'] = "Development version"
        else:
            node['version'] = self.arguments[0]

        node['type'] = self.name
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, node)
        env.note_versionchange(node['type'], node['version'], node, self.lineno)
        return ret
