class NoStatusBar(Exception):
    """Used to flag an attempted operation to a status bar, which has not been defined for the root window, or Toplevel
    widget."""
    pass
