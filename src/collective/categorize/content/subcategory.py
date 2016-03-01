# -*- coding: utf-8 -*-
"""
collective.categorize
---------------------

Created by mpeeters
:copyright: (c) 2015 by Affinitic SPRL
:license: GPL, see LICENCE.txt for more details.
"""

from plone.app.contenttypes.interfaces import IFolder
from plone.dexterity.content import Container
from plone.dexterity.schema import DexteritySchemaPolicy
from zope.interface import implements

from collective.categorize.content.base import ICategorize


class ISubcategory(IFolder, ICategorize):
    pass


class Subcategory(Container):
    implements(ISubcategory)


class SubcategorySchemaPolicy(DexteritySchemaPolicy):

    def bases(self, schema_name, tree):
        return (ISubcategory, )
