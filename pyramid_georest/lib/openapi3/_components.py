# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class Components(object):
    callbacks = attr.ib(default=None, metadata={"schema_property_name": "callbacks"})
    examples = attr.ib(default=None, metadata={"schema_property_name": "examples"})
    headers = attr.ib(default=None, metadata={"schema_property_name": "headers"})
    links = attr.ib(default=None, metadata={"schema_property_name": "links"})
    parameters = attr.ib(default=None, metadata={"schema_property_name": "parameters"})
    request_bodies = attr.ib(default=None, metadata={"schema_property_name": "requestBodies"})
    responses = attr.ib(default=None, metadata={"schema_property_name": "responses"})
    schemas = attr.ib(default=None, metadata={"schema_property_name": "schemas"})
    security_schemes = attr.ib(default=None, metadata={"schema_property_name": "securitySchemes"})
