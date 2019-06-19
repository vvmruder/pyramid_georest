.. _special_classes:

Special classes
===============

This part of documentation is about special classes which can be used to deeply change the behaviour of the
pyramid_georest API via subclassing.

The filter system
-----------------


.. _modules-pyramid_georest-lib-rest-filter:

*Filter*
^^^^^^^^

.. autoclass:: pyramid_georest.lib.rest.Filter
    :members:
    :inherited-members:

    .. automethod:: pyramid_georest.lib.rest.Filter.__init__


.. _modules-pyramid_georest-lib-rest-filter-block:

*FilterBlock*
^^^^^^^^^^^^^

.. autoclass:: pyramid_georest.lib.rest.FilterBlock
    :members:
    :inherited-members:

    .. automethod:: pyramid_georest.lib.rest.FilterBlock.__init__


.. _modules-pyramid_georest-lib-rest-clause:

*Clause*
^^^^^^^^

.. autoclass:: pyramid_georest.lib.rest.Clause
    :members:
    :inherited-members:

    .. automethod:: pyramid_georest.lib.rest.Clause.__init__

The render system
-----------------


.. _modules-pyramid_georest-lib-renderer-json:

*RestfulJson*
^^^^^^^^^^^^^

.. autoclass:: pyramid_georest.lib.renderer.RestfulJson
    :members:
    :inherited-members:
    :exclude-members: add_adapter

    .. automethod:: pyramid_georest.lib.renderer.RestfulJson.__init__


.. _modules-pyramid_georest-lib-renderer-geojson:

*RestfulGeoJson*
^^^^^^^^^^^^^^^^

.. autoclass:: pyramid_georest.lib.renderer.RestfulGeoJson
    :members:
    :inherited-members:
    :exclude-members: add_adapter

    .. automethod:: pyramid_georest.lib.renderer.RestfulGeoJson.__init__

The proxy system
----------------


.. _modules-pyramid_georest-lib-renderer-render_proxy:

*RenderProxy*
^^^^^^^^^^^^^

.. autoclass:: pyramid_georest.lib.renderer.RenderProxy
    :members:
    :inherited-members:

    .. automethod:: pyramid_georest.lib.renderer.RenderProxy.__init__


.. _modules-pyramid_georest-lib-renderer-adapter_proxy:

*AdapterProxy*
^^^^^^^^^^^^^^

.. autoclass:: pyramid_georest.lib.renderer.AdapterProxy
    :members:
    :inherited-members:

    .. automethod:: pyramid_georest.lib.renderer.AdapterProxy.__init__

The description system
----------------------


.. _modules-pyramid_georest-lib-description-model_description:

*ModelDescription*
^^^^^^^^^^^^^^^^^^

.. autoclass:: pyramid_georest.lib.description.ModelDescription
    :members:
    :inherited-members:

    .. automethod:: pyramid_georest.lib.description.ModelDescription.__init__


.. _modules-pyramid_georest-lib-description-column_description:

*ColumnDescription*
^^^^^^^^^^^^^^^^^^^

.. autoclass:: pyramid_georest.lib.description.ColumnDescription
    :members:
    :inherited-members:

    .. automethod:: pyramid_georest.lib.description.ColumnDescription.__init__


.. _modules-pyramid_georest-lib-description-relation_description:

*RelationDescription*
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: pyramid_georest.lib.description.RelationDescription
    :members:
    :inherited-members:

    .. automethod:: pyramid_georest.lib.description.RelationDescription.__init__


.. _modules-pyramid_georest-lib-description-translation:

*translate*
^^^^^^^^^^^

.. autofunction:: pyramid_georest.lib.description.translate
