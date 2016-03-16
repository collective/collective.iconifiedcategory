# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone.app.contenttypes.interfaces import IFolder
from plone.dexterity.content import Container
from plone.dexterity.schema import DexteritySchemaPolicy
from zope.interface import implements
from zope import schema

from collective.iconifiedcategory import _


class ICategoryGroup(IFolder):

    confidentiality_activated = schema.Bool(
        title=_(u'Activate the "confidential" option'),
        required=False,
        default=False,
    )

    to_be_printed_activated = schema.Bool(
        title=_(u'Activate the "to be printed" option'),
        required=False,
        default=False,
    )


class CategoryGroup(Container):
    implements(ICategoryGroup)


class CategoryGroupSchemaPolicy(DexteritySchemaPolicy):

    def bases(self, schema_name, tree):
        return (ICategoryGroup, )
