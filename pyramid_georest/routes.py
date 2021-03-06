# -*- coding: iso-8859-1 -*-


def check_route_prefix(route_prefix):
    if route_prefix is not None and len(route_prefix) > 0:
        return route_prefix + '/'
    else:
        return ''


def create_api_routing(config, api):
    """
    Central method to create the routing per api. This way a independent routing is created which takes even
    the route prefix into account.

    Args:
        config (pyramid.config.Configurator): The pyramid apps config object
        api (pyramid_georest.lib.rest.Api): The Api which the routing is bound to.
    """

    # delivers multiple records/filtered
    config.add_route(
        '{api_name}/read'.format(api_name=api.name),
        '/' + api.pure_name + '/{schema_name}/{table_name}/read/{format}'
    )
    config.add_view(
        api,
        route_name='{api_name}/read'.format(api_name=api.name),
        attr='read',
        request_method=(api.read_method, api.read_filter_method)
    )

    # counts records/filtered in database
    config.add_route(
        '{api_name}/count'.format(api_name=api.name),
        '/' + api.pure_name + '/{schema_name}/{table_name}/count'
    )
    config.add_view(
        api,
        route_name='{api_name}/count'.format(api_name=api.name),
        attr='count',
        request_method=(api.read_method, api.read_filter_method),
        renderer='string'
    )

    # delivers specific record
    config.add_route(
        '{api_name}/show'.format(api_name=api.name),
        '/' + api.pure_name + '/{schema_name}/{table_name}/read/{format}/*primary_keys'
    )
    config.add_view(
        api,
        route_name='{api_name}/show'.format(api_name=api.name),
        attr='show',
        request_method=api.read_method
    )

    # create specific record
    config.add_route(
        '{api_name}/create'.format(api_name=api.name),
        '/' + api.pure_name + '/{schema_name}/{table_name}/create/{format}'
    )
    config.add_view(
        api,
        route_name='{api_name}/create'.format(api_name=api.name),
        attr='create',
        request_method=api.create_method
    )

    # update specific record
    config.add_route(
        '{api_name}/update'.format(api_name=api.name),
        '/' + api.pure_name + '/{schema_name}/{table_name}/update/{format}/*primary_keys'
    )
    config.add_view(
        api,
        route_name='{api_name}/update'.format(api_name=api.name),
        attr='update',
        request_method=api.update_method
    )

    # delete specific record
    config.add_route(
        '{api_name}/delete'.format(api_name=api.name),
        '/' + api.pure_name + '/{schema_name}/{table_name}/delete/{format}/*primary_keys'
    )
    config.add_view(
        api,
        route_name='{api_name}/delete'.format(api_name=api.name),
        attr='delete',
        request_method=api.delete_method
    )

    # delivers the description of the desired dataset
    config.add_route(
        '{api_name}/model'.format(api_name=api.name),
        '/' + api.pure_name + '/{schema_name}/{table_name}/model/{format}'
    )
    config.add_view(
        api,
        route_name='{api_name}/model'.format(api_name=api.name),
        attr='model',
        request_method=api.read_method
    )

    # delivers an adapter for restful interaction via angular
    config.add_route(
        '{api_name}/adapter'.format(api_name=api.name),
        '/' + api.pure_name + '/{schema_name}/{table_name}/adapter/{format}'
    )
    config.add_view(
        api,
        route_name='{api_name}/adapter'.format(api_name=api.name),
        attr='adapter',
        request_method=api.read_method
    )

    # commit the configuration
    config.commit()
