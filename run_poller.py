#!/usr/bin/python

from settings.settings import settings
from overlay_nodes import poller

poller.run(settings)