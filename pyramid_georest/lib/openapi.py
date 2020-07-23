# -*- coding: utf-8 -*-

VERSION = '3.0.3'


class Contact(dict):

    def __init__(self, name=None, url=None, email=None):
        """
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#contactObject

        Args:
            name (str or None): see doc link above
            url (str or None): see doc link above
            email (str ro None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#licenseObject

        Args:
            name (str or None): see doc link above
            url (str or None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#infoObject

        Args:
            title (str): see doc link above
            version (str): see doc link above
            description (str or None): see doc link above
            terms_of_service (str or None): see doc link above
            contact (Contact or None): see doc link above
            api_license (License or None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md
            #serverVariableObject

        Args:
            key (str): The key which is used then as key for parent elements.
            default (str): see doc link above
            enum (list of str or None): see doc link above
            description (str or None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#serverObject

        Args:
            url (str): see doc link above
            description (str or None): see doc link above
            variables (list of ServerVariable or None): see doc link above
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

    def __init__(self, definition):
        """
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md#schemaObject
        We simply offer full dictionary freedom here since the schemaObject almost does. So please rely on the
        documentation strongly!

        This definition is added only to have a library internal point of wrapping.

        Args:
            definition (dict): The schema definition as a python dict. Please rely to the docs linked above.
        """
        super().__init__(definition)


class Header(dict):
    allowed_in_values = ['query', 'header', 'path', 'cookie']

    def __init__(self, key, name=None, in_location=None, description=None, required=False, deprecated=False,
                 allow_empty_value=False, style=None, explode=False, allow_reserved=False, schema=None,
                 example=None, examples=None, content=None):
        """
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#parameterObject

        Args:
            key (str): The key which is used then as key for parent elements.
            name (str or None): see doc link above
            in_location (str or None): see doc link above
            description (str or None): see doc link above
            required (bool): see doc link above
            deprecated (bool): see doc link above
            allow_empty_value (bool): see doc link above
            style (str or None): see doc link above
            explode (bool): see doc link above
            allow_reserved (bool): see doc link above
            schema (Schema or None): see doc link above
            example (str or None): see doc link above
            examples (list of Example or None): see doc link above
            content (list of MediaType or None): see doc link above
        """
        # TODO: implement correct behaviour like it is described in
        #  https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#parameterObject
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#exampleObject

        Args:
            key (str): The key which is used then as key for parent elements.
            summary (str or None): see doc link above
            description (str or None): see doc link above
            value (str or None): see doc link above
            external_value (str or None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#encodingObject

        Args:
            key (str): The key which is used then as key for parent elements.
            content_type (str or None): see doc link above
            headers (list of Header or None): see doc link above
            style (str or None): see doc link above
            explode (bool): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#mediaTypeObject

        Args:
            key (str): The key which is used then as key for parent elements.
            schema (Schema or None): see doc link above
            example (str or None): see doc link above
            examples (list of Example or None): see doc link above
            encoding (list of Encoding or None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#responseObject

        Args:
            code (str): see doc link above and
                https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#httpCodes
            description (str): see doc link above
            headers (list of Header or None): see doc link above
            content (list of MediaType or None): see doc link above
            links (list of Link or None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#responsesObject

        Args:
            responses (list of Response): see doc link above
            default (Response or None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md
            #externalDocumentationObject

        Args:
            url (str): see doc link above
            description (str or None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#parameterObject

        Args:
            name (str): see doc link above
            in_location (str): see doc link above
            description (str or None): see doc link above
            required (bool): see doc link above
            deprecated (bool): see doc link above
            allow_empty_value (bool): see doc link above
            style (str or None): see doc link above
            explode (bool): see doc link above
            allow_reserved (bool): see doc link above
            schema (Schema or None): see doc link above
            example (str or None): see doc link above
            examples (list of Example or None): see doc link above
            content (list of MediaType or None): see doc link above
        """
        super().__init__('', name, in_location, description=description, required=required,
                         deprecated=deprecated, allow_empty_value=allow_empty_value, style=style,
                         explode=explode, allow_reserved=allow_reserved, schema=schema, example=example,
                         examples=examples, content=content)


class RequestBody(dict):
    def __init__(self, content, description=None, required=False):
        """
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#requestBodyObject

        Args:
            content (list of MediaType): see doc link above
            description (str or None): see doc link above
            required (bool): see doc link above
        """
        super().__init__()
        self['required'] = required
        self['content'] = {}
        for c in content:
            self['content'][c.key] = c
        if description:
            self['description'] = description


class Callback(dict):
    # TODO: implement like described here:
    #  https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#callbackObject
    pass


class SecurityRequirement(dict):
    # TODO: implement like described here:
    #  http://spec.openapis.org/oas/v3.0.3#securityRequirementObject
    pass


class Operation(dict):

    def __init__(self, responses, tags=None, summary=None, description=None, external_docs=None,
                 operation_id=None, parameters=None, request_body=None, callbacks=None, deprecated=False,
                 security=None, servers=None):
        """
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#operationObject

        Args:
            responses (Responses) : see doc link above
            tags (list of str or None): see doc link above
            summary (str or None): see doc link above
            description (str or None): see doc link above
            external_docs (ExternalDocumentation or None: see doc link above
            operation_id (str or None): see doc link above
            parameters (list of Parameter or None): see doc link above
            request_body (RequestBody or None): see doc link above
            callbacks(list of Callback or None): see doc link above
            deprecated (bool): see doc link above
            security (list of SecurityRequirement or None): see doc link above
            servers (list of Server or None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#pathItemObject

        Args:
            ref (str or None): see doc link above
            summary (str or None): see doc link above
            description (str or None): see doc link above
            get (Operation or None): see doc link above
            put (Operation or None): see doc link above
            post (Operation or None): see doc link above
            delete (Operation or None): see doc link above
            options (Operation or None): see doc link above
            head (Operation or None): see doc link above
            patch (Operation or None): see doc link above
            trace (Operation or None): see doc link above
            servers (list of Server or None): see doc link above
            parameters (list of Parameter or None): see doc link above
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
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#pathsObject

        Args:
            service_path (str): The sub path of the service. It is used as key to store all available
                operations below.
            path_item (PathItem): see doc link above
        """
        super().__init__(path_item)
        self.service_path = service_path


class Components(dict):
    pass


class Tag(dict):

    def __init__(self, name, description=None, external_docs=None):
        """
        Implemenation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#tagObject

        Args:
            name (str): see doc link above
            description (str): see doc link above
            external_docs (ExternalDocumentation): see doc link above
        """
        super().__init__()
        self['name'] = name
        if description:
            self['description'] = description
        if external_docs:
            self['externalDocs'] = external_docs


class OpenApi(dict):

    def __init__(self, info, servers, paths, components=None, external_docs=None, security=None, tags=None):
        """
        Implementation of
            https://github.com/OAI/OpenAPI-Specification/blob/v3.0.3-dev/versions/3.0.3.md#oasObject

        Args:
            info (Info): see doc link above
            servers (list of Server): see doc link above
            paths (list of Paths): see doc link above
            components (Components): see doc link above
            external_docs (ExternalDocumentation): see doc link above
            security (list of SecurityRequirement): see doc link above
            tags (list of Tag): see doc link above

        """
        super().__init__()
        self['openapi'] = VERSION
        self['info'] = info
        self['servers'] = servers
        self['paths'] = {}
        for path in paths:
            self['paths'][path.service_path] = path
        if components:
            self['components'] = components
        if external_docs:
            self['externalDocs'] = external_docs
        if security:
            self['security'] = security
        if tags:
            self['tags'] = tags
