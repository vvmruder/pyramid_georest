# -*- coding: utf-8 -*-

VERSION = '3.0.3'


class Contact(dict):

    def __init__(self, name=None, url=None, email=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#contactObject

        Args:
            name (str or None): see https://spec.openapis.org/oas/v3.0.3
            url (str or None): see https://spec.openapis.org/oas/v3.0.3
            email (str ro None): see https://spec.openapis.org/oas/v3.0.3
        """
        super().__init__()
        if name:
            self['name'] = name
        if url:
            self['url'] = url
        if email:
            self['email'] = email


class License(dict):
    def __init__(self, name=None, url=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#licenseObject

        Args:
            name (str or None): see https://spec.openapis.org/oas/v3.0.3
            url (str or None): see https://spec.openapis.org/oas/v3.0.3
        """
        super().__init__()
        if name:
            self['name'] = name
        if url:
            self['url'] = url


class Info(dict):

    def __init__(self, title, version, description=None, terms_of_service=None, contact=None,
                 api_license=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#infoObject

        Args:
            title (str): see https://spec.openapis.org/oas/v3.0.3#infoObject
            version (str): see https://spec.openapis.org/oas/v3.0.3#infoObject
            description (str or None): see https://spec.openapis.org/oas/v3.0.3#infoObject
            terms_of_service (str or None): see https://spec.openapis.org/oas/v3.0.3#infoObject
            contact (Contact or None): see https://spec.openapis.org/oas/v3.0.3#infoObject
            api_license (License or None): see https://spec.openapis.org/oas/v3.0.3#infoObject
        """
        super().__init__()
        self['title'] = title
        self['version'] = version
        if description:
            self['description'] = description
        if terms_of_service:
            self['termsOfService'] = terms_of_service
        if contact:
            self['contact'] = contact
        if api_license:
            self['license'] = api_license


class ServerVariable(dict):

    def __init__(self, key, default, enum=None, description=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#server-variable-object

        Args:
            key (str): The key which is used then as key for parent elements.
            default (str): see https://spec.openapis.org/oas/v3.0.3#server-variable-object
            enum (list of str or None): see https://spec.openapis.org/oas/v3.0.3#server-variable-object
            description (str or None): see https://spec.openapis.org/oas/v3.0.3#server-variable-object
        """
        super().__init__()
        self.key = key
        self['default'] = default
        if enum:
            self['enum'] = enum
        if description:
            self['description'] = description


class Server(dict):

    def __init__(self, url, description=None, variables=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#server-object

        Args:
            url (str): see https://spec.openapis.org/oas/v3.0.3#server-object
            description (str or None): see https://spec.openapis.org/oas/v3.0.3#server-object
            variables (list of ServerVariable or None): see https://spec.openapis.org/oas/v3.0.3#server-object
        """
        super().__init__()
        self['url'] = url
        if description:
            self['description'] = description
        if variables:
            self['variables'] = {}
            for variable in variables:
                self['variables'][variable.key] = variable


class Schema(dict):
    pass


class Header(dict):
    allowed_in_values = ['query', 'header', 'path', 'cookie']

    def __init__(self, key, name=None, in_location=None, description=None, required=False, deprecated=False,
                 allow_empty_value=False, style=None, explode=False, allow_reserved=False, schema=None,
                 example=None, examples=None, content=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#parameter-object

        Args:
            key (str): The key which is used then as key for parent elements.
            name (str or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            in_location (str or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            description (str or None): see
                https://spec.openapis.org/oas/v3.0.3#external-documentation-object
            required (bool): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            deprecated (bool): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            allow_empty_value (bool): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            style (str or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            explode (bool): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            allow_reserved (bool): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            schema (Schema or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            example (str or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            examples (list of Example or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            content (list of MediaType or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
        """
        # TODO: implement correct behaviour like it is described in
        #  https://spec.openapis.org/oas/v3.0.3#parameter-object
        super().__init__()
        self.key = key
        self['name'] = name
        if in_location.lower() not in self.allowed_in_values:
            raise AttributeError('The passed "in" value {} is not allowed. It has to be one of {}'.format(
                in_location,
                str(self.allowed_in_values)
            ))
        self['in'] = in_location
        self['required'] = required
        self['deprecated'] = deprecated
        self['allowEmptyValue'] = allow_empty_value
        self['explode'] = explode
        self['allowReserved'] = allow_reserved

        if description:
            self['description'] = description
        if style:
            self['style'] = style
        if schema:
            self['schema'] = schema
        if example:
            self['example'] = example
        if examples:
            self['examples'] = {}
            for e in examples:
                self['examples'][e.key] = e
        if content:
            self['content'] = {}
            for c in content:
                self['content'][c.key] = c


class Example(dict):

    def __init__(self, key, summary=None, description=None, value=None, external_value=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#example-object

        Args:
            key (str): The key which is used then as key for parent elements.
            summary (str or None): see https://spec.openapis.org/oas/v3.0.3#example-object
            description (str or None): see https://spec.openapis.org/oas/v3.0.3#example-object
            value (str or None): see https://spec.openapis.org/oas/v3.0.3#example-object
            external_value (str or None): see https://spec.openapis.org/oas/v3.0.3#example-object
        """
        super().__init__()
        self.key = key
        if summary:
            self['summary'] = summary
        if description:
            self['description'] = description
        if value:
            self['value'] = value
        if external_value:
            self['externalValue'] = external_value


class Encoding(dict):
    def __init__(self, key, content_type=None, headers=None, style=None, explode=False,
                 allow_reserved=False):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#encodingObject

        Args:
            key (str): The key which is used then as key for parent elements.
            content_type (str or None): see https://spec.openapis.org/oas/v3.0.3#encodingObject
            headers (list of Header or None): see https://spec.openapis.org/oas/v3.0.3#encodingObject
            style (str or None): see https://spec.openapis.org/oas/v3.0.3#encodingObject
            explode (bool): see https://spec.openapis.org/oas/v3.0.3#encodingObject
        """
        super().__init__()
        self.key = key
        self['explode'] = explode
        self['allowReserved'] = allow_reserved
        if content_type:
            self['contentType'] = content_type
        if headers:
            self['headers'] = {}
            for header in headers:
                self['headers'][header.key] = header
        if style:
            self['style'] = style


class MediaType(dict):
    def __init__(self, key, schema=None, example=None, examples=None, encoding=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#media-type-object

        Args:
            key (str): The key which is used then as key for parent elements.
            schema (Schema or None): see https://spec.openapis.org/oas/v3.0.3#media-type-object
            example (str or None): see https://spec.openapis.org/oas/v3.0.3#media-type-object
            examples (list of Example or None): see https://spec.openapis.org/oas/v3.0.3#media-type-object
            encoding (list of Encoding or None): see https://spec.openapis.org/oas/v3.0.3#media-type-object
        """
        super().__init__()
        self.key = key
        if schema:
            self['schema'] = schema
        if example:
            self['example'] = example
        if examples:
            self['examples'] = {}
            for e in examples:
                self['examples'][e.key] = e
        if encoding:
            self['encoding'] = {}
            for enc in encoding:
                self['encoding'][enc.key] = enc


class Link(dict):
    pass


class Response(dict):
    def __init__(self, code, description, headers=None, content=None, links=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#response-object

        Args:
            code (str): see https://spec.openapis.org/oas/v3.0.3#http-status-codes and
                https://spec.openapis.org/oas/v3.0.3#responses-object
            description (str): see https://spec.openapis.org/oas/v3.0.3#response-object
            headers (list of Header or None): see https://spec.openapis.org/oas/v3.0.3#response-object
            content (list of MediaType or None): see https://spec.openapis.org/oas/v3.0.3#response-object
            links (list of Link or None): see https://spec.openapis.org/oas/v3.0.3#response-object
        """
        super().__init__()
        self.code = code
        self['description'] = description
        if headers:
            self['headers'] = {}
            for header in headers:
                self['headers'][header.key] = header
        if content:
            self['content'] = {}
            for media_type in content:
                self['content'][media_type.key] = media_type
        if links:
            self['links'] = {}
            for link in links:
                self['links'][link.key] = link


class Responses(dict):
    def __init__(self, responses, default=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#responses-object

        Args:
            responses (list of Response): see https://spec.openapis.org/oas/v3.0.3#responses-object
            default (Response or None): see https://spec.openapis.org/oas/v3.0.3#responses-object
        """
        super().__init__()
        if len(responses) < 1:
            raise AttributeError('You need to define at least one response!')
        for response in responses:
            self[response.code] = response
        if default:
            self['default'] = default


class ExternalDocumentation(dict):
    def __init__(self, url, description=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#external-documentation-object

        Args:
            url (str): see https://spec.openapis.org/oas/v3.0.3#external-documentation-object
            description (str or None): see
                https://spec.openapis.org/oas/v3.0.3#external-documentation-object
        """
        super().__init__()
        self['url'] = url
        if description:
            self['description'] = description


class Parameter(Header):
    allowed_in_values = ['query', 'header', 'path', 'cookie']

    def __init__(self, name, in_location, description=None, required=False, deprecated=False,
                 allow_empty_value=False, style=None, explode=False, allow_reserved=False, schema=None,
                 example=None, examples=None, content=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#parameter-object

        Args:
            name (str): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            in_location (str): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            description (str or None): see
                https://spec.openapis.org/oas/v3.0.3#external-documentation-object
            required (bool): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            deprecated (bool): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            allow_empty_value (bool): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            style (str or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            explode (bool): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            allow_reserved (bool): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            schema (Schema or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            example (str or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            examples (list of Example or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
            content (list of MediaType or None): see https://spec.openapis.org/oas/v3.0.3#parameter-object
        """
        super().__init__('', name, in_location, description=description, required=required,
                         deprecated=deprecated, allow_empty_value=allow_empty_value, style=style,
                         explode=explode, allow_reserved=allow_reserved, schema=schema, example=example,
                         examples=examples, content=content)


class RequestBody(dict):
    def __init__(self, content, description=None, required=False):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#request-body-object

        Args:
            content (list of MediaType): see https://spec.openapis.org/oas/v3.0.3#request-body-object
            description (str or None): see https://spec.openapis.org/oas/v3.0.3#request-body-object
            required (bool): see https://spec.openapis.org/oas/v3.0.3#request-body-object
        """
        super().__init__()
        self['required'] = required
        self['content'] = {}
        for c in content:
            self['content'][c.key] = c
        if description:
            self['description'] = description


class Callback(dict):
    # TODO: implement like described here: https://spec.openapis.org/oas/v3.0.3#callback-object
    pass


class SecurityRequirement(dict):
    # TODO: implement like described here: http://spec.openapis.org/oas/v3.0.3#security-requirement-object
    pass


class Operation(dict):

    def __init__(self, responses, tags=None, summary=None, description=None, external_docs=None,
                 operation_id=None, parameters=None, request_body=None, callbacks=None, deprecated=False,
                 security=None, servers=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#operation-object

        Args:
            responses (Responses) : see https://spec.openapis.org/oas/v3.0.3#operation-object
            tags (list of str or None): see https://spec.openapis.org/oas/v3.0.3#operation-object
            summary (str or None): see https://spec.openapis.org/oas/v3.0.3#operation-object
            description (str or None): see https://spec.openapis.org/oas/v3.0.3#operation-object
            external_docs (ExternalDocumentation or None: see
                https://spec.openapis.org/oas/v3.0.3#operation-object
            operation_id (str or None): see https://spec.openapis.org/oas/v3.0.3#operation-object
            parameters (list of Parameter or None): see https://spec.openapis.org/oas/v3.0.3#operation-object
            request_body (RequestBody or None): see https://spec.openapis.org/oas/v3.0.3#operation-object
            callbacks(list of Callback or None): see https://spec.openapis.org/oas/v3.0.3#operation-object
            deprecated (bool): see https://spec.openapis.org/oas/v3.0.3#operation-object
            security (list of SecurityRequirement or None): see
                https://spec.openapis.org/oas/v3.0.3#operation-object
            servers (list of Server or None): see https://spec.openapis.org/oas/v3.0.3#operation-object
        """
        super().__init__()
        self['responses'] = responses
        self['deprecated'] = deprecated
        if tags:
            self['tags'] = tags
        if summary:
            self['summary'] = summary
        if description:
            self['description'] = description
        if external_docs:
            self['externalDocs'] = external_docs
        if operation_id:
            self['operationId'] = operation_id
        if parameters:
            self['parameters'] = parameters
        if request_body:
            self['requestBody'] = request_body
        if responses:
            self['responses'] = responses
        if callbacks:
            self['callbacks'] = callbacks
        if security:
            self['security'] = security
        if servers:
            self['servers'] = servers


class PathItems(dict):

    def __init__(self, ref=None, summary=None, description=None, get=None, put=None, post=None, delete=None,
                 options=None, head=None, patch=None, trace=None, servers=None, parameters=None):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#path-item-object

        Args:
            ref (str or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            summary (str or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            description (str or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            get (Operation or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            put (Operation or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            post (Operation or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            delete (Operation or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            options (Operation or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            head (Operation or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            patch (Operation or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            trace (Operation or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            servers (list of Server or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
            parameters (list of Parameter or None): see https://spec.openapis.org/oas/v3.0.3#path-item-object
        """
        super().__init__()
        if ref:
            self['$ref'] = ref
        if summary:
            self['summary'] = summary
        if description:
            self['description'] = description
        if get:
            self['get'] = get
        if put:
            self['put'] = put
        if post:
            self['post'] = post
        if delete:
            self['delete'] = delete
        if options:
            self['options'] = options
        if head:
            self['head'] = head
        if patch:
            self['patch'] = patch
        if trace:
            self['trace'] = trace
        if servers:
            self['servers'] = servers
        if parameters:
            self['parameters'] = parameters


class Paths(dict):

    def __init__(self, service_path, path_item):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#paths-object

        Args:
            service_path (str): The sub path of the service. It is used as key to store all available
                operations below.
            path_item (PathItem): see https://spec.openapis.org/oas/v3.0.3#paths-object
        """
        super().__init__(path_item)
        self.service_path = service_path


class OpenApi(dict):

    def __init__(self, info, servers, paths):
        """
        Implementation of https://spec.openapis.org/oas/v3.0.3#openapi-object

        Args:
            info (Info): see https://spec.openapis.org/oas/v3.0.3#openapi-object
            servers (list of Server): see https://spec.openapis.org/oas/v3.0.3#openapi-object
            paths (list of Paths): see https://spec.openapis.org/oas/v3.0.3#openapi-object
        """
        super().__init__()
        self['openapi'] = VERSION
        self['info'] = info
        self['servers'] = servers
        self['paths'] = {}
        for path in paths:
            self['paths'][path.service_path] = path


