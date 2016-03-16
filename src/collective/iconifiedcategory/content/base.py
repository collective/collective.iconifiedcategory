# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope import schema
from zope.interface import Interface

from collective.iconifiedcategory import _


class ICategorize(Interface):

    title = schema.TextLine(
        title=_(u'Title'),
        required=True,
    )

    predefined_title = schema.TextLine(
        title=_(u'Predefined title'),
        required=False,
    )

    confidential = schema.Bool(
        title=_(u'Confidential'),
        required=False,
        default=False,
    )

    to_print = schema.Bool(
        title=_(u'To be printed'),
        required=False,
        default=False,
    )
