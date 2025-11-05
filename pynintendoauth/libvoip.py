"""LibVoip.so."""

import logging
import ctypes
import os

_LOGGER = logging.getLogger(__name__)

try:
    os.environ["LD_LIBRARY_PATH"] = os.path.join(os.path.dirname(__file__), "libs")
    _LOGGER.debug("Loading libraries from %s", os.environ["LD_LIBRARY_PATH"])
    libvoip = ctypes.cdll.LoadLibrary(os.path.join(os.environ["LD_LIBRARY_PATH"], "libvoip.so"))
except OSError:
    _LOGGER.exception("Error loading shared objects.")
