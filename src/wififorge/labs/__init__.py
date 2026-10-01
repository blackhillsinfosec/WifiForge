"""Bundled WifiForge labs.

Each module in this package is a self-contained lab exposing a ``LAB`` metadata
object and a ``run()`` entry point. They are discovered at runtime by
:mod:`wififorge.labs.loader`, so dropping a new module in here (or in a directory
pointed to by ``--labs-dir`` / ``$WIFIFORGE_LABS``) is all it takes to add a lab.
"""
