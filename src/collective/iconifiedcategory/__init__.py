# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory
from ZPublisher.Converters import type_converters

import json
import logging


logger = logging.getLogger('collective.iconifiedcategory')

CAT_SEPARATOR = '_-_'
CSS_SEPARATOR = '-'

_ = MessageFactory('collective.iconifiedcategory')


# create type converter for json
if 'field2json' not in type_converters:
    def field2json(v):
        v = json.loads(v)
        return v
    type_converters['json'] = field2json
