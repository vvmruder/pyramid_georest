# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class ExternalDocumentation(object):
    url = attr.ib(metadata={"schema_property_name": "url"})
    description = attr.ib(default=None, metadata={"schema_property_name": "description"})
