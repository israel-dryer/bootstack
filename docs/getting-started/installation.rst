Installation
============

Requirements
------------

bootstack needs **Python 3.12** or later and **Tk/Tcl**, the GUI runtime it
draws with. Tk ships with most Python distributions, so usually there is nothing
extra to install — see :ref:`checking-tk` below if a window fails to appear.

Install
-------

Install bootstack with pip:

.. code-block:: bash

   python -m pip install bootstack

Upgrade to the latest release the same way:

.. code-block:: bash

   python -m pip install --upgrade bootstack

To pin an exact version — for a reproducible environment — name it directly.
Pick a version from the
`release history <https://pypi.org/project/bootstack/#history>`__:

.. code-block:: bash

   python -m pip install bootstack==0.1.0

.. _checking-tk:

Checking your Tk installation
-----------------------------

Because bootstack renders through Tk, a working Tk is the one system requirement.
Confirm it with the standard library's self-test, which opens a small window:

.. code-block:: bash

   python -m tkinter

If a window appears, you are set. If you instead see
``ModuleNotFoundError: No module named '_tkinter'`` or a ``TclError``, install Tk
for your platform:

**Linux** — Tk is packaged separately from Python:

.. code-block:: bash

   sudo apt-get install python3-tk      # Debian / Ubuntu
   sudo dnf install python3-tkinter     # Fedora
   sudo pacman -S tk                    # Arch

**Windows** — re-run the official `python.org <https://www.python.org/downloads/>`_
installer and keep **"tcl/tk and IDLE"** checked (it is on by default); the
Microsoft Store build also includes it.

**macOS** — use the `python.org <https://www.python.org/downloads/>`_ installer,
which bundles a current Tk. The system Python and some Homebrew builds ship an
older Tk; if you hit rendering glitches, switch to the python.org build.

.. note::

   Inside a virtual environment, Tk support comes from the **base** interpreter
   the environment was created from. If ``python -m tkinter`` works system-wide
   but not in your venv, recreate the venv from a Python that has Tk.

Optional features
-----------------

A few integrations are optional extras — install them only if you need them, by
adding the extra in brackets:

.. code-block:: bash

   python -m pip install "bootstack[excel]"        # .xlsx export from DataTable
   python -m pip install "bootstack[parquet]"      # read and write Parquet and Feather
   python -m pip install "bootstack[hdf5]"         # read and write HDF5
   python -m pip install "bootstack[viz]"          # Chart — embed matplotlib figures
   python -m pip install "bootstack[viz-seaborn]"  # Chart, with seaborn added

Combine extras in one install — for example ``bootstack[excel,parquet]``. The
data-format extras power the file reader/writer registry behind data sources and
``DataTable`` export (the core CSV/TSV/JSON formats need no extra); ``viz`` /
``viz-seaborn`` enable the :doc:`Chart </widgets/chart>` widget. See
:doc:`/reference/data-sources`.

Verify
------

Run the built-in diagnostics to confirm everything is healthy:

.. code-block:: bash

   bootstack doctor

Or check from Python that the package imports and a window opens:

.. code-block:: python

   import bootstack as bs

   with bs.App(title="Hello") as app:
       bs.Label("bootstack is working!", font="heading-md")
   app.run()

See it
------

Launch the widget gallery for a live tour of every widget, theme, and layout
container — no code required:

.. code-block:: bash

   bootstack gallery

Browse the full icon catalog:

.. code-block:: bash

   bootstack icons

Next steps
----------

- :doc:`quickstart` — build your first app in a few lines.
- :doc:`app-structures` — the common shapes a bootstack app takes.
