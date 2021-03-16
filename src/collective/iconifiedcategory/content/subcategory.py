# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory.content.base import ICategorize
from plone.app.contenttypes.interfaces import IFolder
from plone.dexterity.content import Item
from plone.dexterity.schema import DexteritySchemaPolicy
from zope.interface import implements


class ISubcategory(IFolder, ICategorize):
    pass


class Subcategory(Item):
    implements(ISubcategory)

    @property
    def category_uid(self):
        return self.aq_parent.UID()

    @property
    def category_id(self):
        return self.aq_parent.getId()

    @property
    def category_title(self):
        return self.aq_parent.Title()

    def get_category(self):
        return self.aq_parent

    def get_category_group(self, context=None):
        if context is None:
            context = self
        return context.aq_parent.aq_parent


class SubcategorySchemaPolicy(DexteritySchemaPolicy):

    def bases(self, schema_name, tree):
        return (ISubcategory, )
