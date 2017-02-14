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
from plone.autoform import directives as form
from z3c.form.browser.radio import RadioFieldWidget


class ICategorize(Interface):

    predefined_title = schema.TextLine(
        title=_(u'Predefined title'),
        required=False,
    )

    form.widget('confidential', RadioFieldWidget)
    confidential = schema.Bool(
        title=_(u'Confidential default'),
        required=False,
        default=False,
    )

    form.widget('to_print', RadioFieldWidget)
    to_print = schema.Bool(
        title=_(u'To be printed default'),
        required=False,
        default=False,
    )

    form.widget('enabled', RadioFieldWidget)
    enabled = schema.Bool(
        title=_(u'Enabled?'),
        default=True,
        required=False,
    )
