Master–detail (list)
====================

A list of records in the sidebar drives a detail view in the content area — the
email inbox, the contact list, the device manager. The sidebar is filled straight
from a data source; you write one builder that renders the selected record.

.. image:: /_static/examples/navigation-master-detail-list-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: Email inbox master–detail — light theme

.. image:: /_static/examples/navigation-master-detail-list-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: Email inbox master–detail — dark theme

How it works
------------

`list_nav(source)` fills the sidebar from a :doc:`data source
</reference/data-sources>`, rendering each record's `title` / `text` /
`icon` as a row. Decorate a builder with `@shell.detail` to render the body
for the selected record — it receives the record as a dict. The first record is
selected automatically, so the detail view is never empty on open.

.. code-block:: python

   shell.list_nav(inbox)

   @shell.detail
   def read(message):
       with bs.Column(horizontal_items="left", gap=12, padding=(16, 10)):
           bs.Label(message["text"], font="heading-lg")
           bs.Label(message["body"])

The list stays in sync with its source — adding, removing, or editing records
updates the sidebar (and re-renders the open detail) automatically.

Example
-------

.. literalinclude:: ../../examples/navigation/master_detail_list.py
   :language: python
   :linenos:

When to use
-----------

Use the list master–detail when the sidebar is a flat list of records and the
content shows one at a time. When records nest under parents (folders, an org
chart), use :doc:`master-detail-tree`. When the sidebar items are a fixed set of
authored screens rather than data, use a :doc:`single-tier app <single-tier>`.
