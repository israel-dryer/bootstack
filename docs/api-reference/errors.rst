Errors
======

.. currentmodule:: bootstack.errors

The exception types the framework raises. All inherit from a single base, so you
can catch every framework error with one ``except`` clause or narrow to a
specific failure.

For when each one is raised and how to handle it, see the :doc:`/reference/errors`
guide.

.. autoexception:: BootstackError
   :show-inheritance:

.. autoexception:: DuplicateIdError
   :show-inheritance:

.. autoexception:: NavigationError
   :show-inheritance:

.. autoexception:: ParentResolutionError
   :show-inheritance:

.. autoexception:: SerializationError
   :show-inheritance:

.. autoexception:: StyleBuilderError
   :show-inheritance:

.. autoexception:: ThemeError
   :show-inheritance:

.. autoexception:: UnknownEventError
   :show-inheritance:
