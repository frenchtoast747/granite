Renderable Templates
====================

When you need to be able to create specific types of files for your tool (e.g. ini/config files,
scripts, etc) in a parameterized way, use renderable templates.

.. Note:: The :any:`Renderable`, :any:`RenderedFile`, and :any:`SimpleFile` classes all use the `Jinja2`_
          templating system. See its documentation for any specific questions pertaining to the
          templates themselves.

.. autoclass:: granite.environment.RenderedFile
    :noindex:
    :members:

.. _Jinja2: http://jinja.pocoo.org/docs/