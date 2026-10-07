# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory

# enable :json type converter
import imio.helpers.converters  # noqa
import logging


logger = logging.getLogger("collective.iconifiedcategory")

CAT_SEPARATOR = "_-_"
CSS_SEPARATOR = "-"
DEFAULT_FILESIZE_LIMIT = 5000000

# optional on Plone 6: without it, nothing is convertible (no preview, File not printable)
try:
    import collective.documentviewer  # noqa: F401

    HAS_DOCUMENTVIEWER = True
except ImportError:
    HAS_DOCUMENTVIEWER = False

_ = MessageFactory("collective.iconifiedcategory")
