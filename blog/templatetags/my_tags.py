from django import template
from django.template.base import VariableNode
from django.contrib.auth import get_user_model
from urllib import parse
from django import template

register = template.Library()

@register.filter(name='ga_url')
def ga_url(url, option):
    if not isinstance(url, str) or not isinstance(option, str):
        return url
    parsed_qs = parse.parse_qs(option)
    parsed_url = parse.urlparse(url).__dict__
    options = dict(parse.parse_qs(parsed_url['query']))

    new_qs = {}
    for key, value in parsed_qs.items():
        new_qs['utm_' + key] = value
    options.update(new_qs)

    parsed_url['query'] = parse.urlencode(options, doseq='&')

    return parse.urlunparse(parsed_url.values())

@register.tag(name='addnim')
def add_nim(parser, token):
    nodelist = parser.parse(('end_add_nim'),)
    parser.delete_first_token()
    return NimNode(nodelist)

class NimNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
        self.user_class = get_user_model()

    def render(self, context):
        outputs = []
        for node in self.nodelist:
            if not isinstance(node, VariableNode):
                outputs.append(node.render(context))
                continue
            obj = node.filter_expression.resolve(context)
            if not isinstance(obj, self.user_class):
                outputs.append(node.render(context))
                continue
            outputs.append('{}님'.format(node.render(context)))

        return ''.join(outputs)