from flask import url_for

import CloudFlare

def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.index)


# TODO: move this to a better home
def register_subdomain(subdomain, target):
    """
    :subdomain is the the subdomain name
    :target is the aliased url
    """
    cf = CloudFlare.CloudFlare(Config.CF_API_EMAIL, Config.CF_API_KEY)

    dns_record = {
        'type': 'CNAME',
        'name': subdomain,
        'content': target,
    }

    cf.zones.dns_records.post(Config.CF_ZONE_ID, data=dns_record)
