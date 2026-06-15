Installation
============

Requirements
------------

bootstack requires **Python 3.12** or later. No other system dependencies
are needed — everything ships with the package.

Install
-------

Install directly from the repository:

.. code-block:: bash

   pip install git+https://github.com/israel-dryer/bootstack.git

Optional features
-----------------

A few data-format integrations are optional extras — install them only if you
need them, by adding the extra in brackets:

.. code-block:: bash

   pip install "bootstack[excel]"      # .xlsx export from DataTable
   pip install "bootstack[parquet]"    # read and write Parquet and Feather
   pip install "bootstack[hdf5]"       # read and write HDF5

Combine extras in one install — for example `bootstack[excel,parquet]`. During
the pre-release, append the repository URL just like the base install above
(e.g. `pip install "bootstack[excel] @ git+https://github.com/israel-dryer/bootstack.git"`).

These extras power the file reader/writer registry behind data sources and
`DataTable` export. The core CSV/TSV/JSON formats need no extra; see
:doc:`/reference/data-sources`.

Verify
------

Run the built-in diagnostics to confirm the installation is healthy:

.. code-block:: bash

   bootstack doctor

Or verify from Python:

.. code-block:: python

   import bootstack as bs
   print(bs.__version__)

See it
------

Launch the widget gallery for a live tour of every widget, theme, and
layout container — no code required:

.. code-block:: bash

   bootstack gallery

Browse the full icon catalog:

.. code-block:: bash

   bootstack icons
