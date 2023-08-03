# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import _
from plone.autoform import directives as form
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant


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

    form.widget('to_sign', RadioFieldWidget)
    to_sign = schema.Bool(
        title=_(u'To sign default'),
        required=False,
        default=False,
    )

    form.widget('signed', RadioFieldWidget)
    signed = schema.Bool(
        title=_(u'Signed default'),
        required=False,
        default=False,
    )

    form.widget('publishable', RadioFieldWidget)
    publishable = schema.Bool(
        title=_(u'Publishable default'),
        required=False,
        default=False,
    )

    form.widget('enabled', RadioFieldWidget)
    enabled = schema.Bool(
        title=_(u'Enabled?'),
        default=True,
        required=False,
    )

    form.widget('only_pdf', RadioFieldWidget)
    only_pdf = schema.Bool(
        title=_(u'Only PDF?'),
        default=False,
        required=False,
    )

    show_preview = schema.Choice(
        title=_(u'Show preview?'),
        description=_(u'Show preview description.'),
        vocabulary='collective.iconifiedcategory.show_preview_vocabulary',
        default=0,
        required=True,
    )

    @invariant
    def signedInvariant(data):
        """'signed' may only be True if 'to_sign' is True."""
        if data.to_sign is False and data.signed is True:
            raise Invalid(_(u"'Signed' can not be True when 'To sign?' is False!"))
