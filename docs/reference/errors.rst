Errors
======

Exceptions raised by the bootstack API. All inherit from :class:`BootstackError
<bootstack.errors.BootstackError>`, so a single ``except bootstack.BootstackError``
catches anything the framework raises.

.. code-block:: python

   import bootstack as bs

   try:
       widget.on("not-a-real-event", handler)
   except bs.UnknownEventError as err:
       print("bad event name:", err)

API reference
-------------

.. autoclass:: bootstack.errors.BootstackError
   :members:
   :undoc-members:

.. autoclass:: bootstack.errors.UnknownEventError
   :members:
   :undoc-members:

.. autoclass:: bootstack.errors.ParentResolutionError
   :members:
   :undoc-members:

.. autoclass:: bootstack.errors.DuplicateIdError
   :members:
   :undoc-members:

.. autoclass:: bootstack.errors.SerializationError
   :members:
   :undoc-members:
