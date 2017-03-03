# -*- coding: utf-8 -*-
"""Init and utils."""
import logging
from zope.i18nmessageid import MessageFactory

logger = logging.getLogger('collective.iconifiedcategory')

CAT_SEPARATOR = '_-_'
CSS_SEPARATOR = '-'

_ = MessageFactory('collective.iconifiedcategory')
