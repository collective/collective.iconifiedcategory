# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import _
from plone.app.contenttypes.interfaces import IFolder
from plone.autoform import directives as form
from plone.dexterity.content import Container
from plone.dexterity.schema import DexteritySchemaPolicy
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implements


class ICategoryGroup(IFolder):

    form.widget('confidentiality_activated', RadioFieldWidget)
    confidentiality_activated = schema.Bool(
        title=_(u'Activate the "confidential" option'),
        required=False,
        default=False,
    )

    form.widget('to_be_printed_activated', RadioFieldWidget)
    to_be_printed_activated = schema.Bool(
        title=_(u'Activate the "to be printed" option'),
        required=False,
        default=False,
    )

    form.widget('signed_activated', RadioFieldWidget)
    signed_activated = schema.Bool(
        title=_(u'Activate the "to_sign and signed" options'),
        required=False,
        default=False,
    )

    form.widget('publishable_activated', RadioFieldWidget)
    publishable_activated = schema.Bool(
        title=_(u'Activate the "publishable" option'),
        required=False,
        default=False,
    )


class CategoryGroup(Container):
    implements(ICategoryGroup)


class CategoryGroupSchemaPolicy(DexteritySchemaPolicy):

    def bases(self, schema_name, tree):
        return (ICategoryGroup, )
