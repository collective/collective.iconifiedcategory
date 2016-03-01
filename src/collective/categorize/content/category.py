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
from plone.autoform import directives as form
from plone.namedfile.field import NamedBlobImage
from zope.interface import implements

from collective.categorize import _
from collective.categorize.content.base import ICategorize


class ICategory(IFolder, ICategorize):

    form.order_after(icon='title')
    icon = NamedBlobImage(
        title=_(u'Icon'),
        required=True,
    )


class Category(Container):
    implements(ICategory)


class CategorySchemaPolicy(DexteritySchemaPolicy):

    def bases(self, schema_name, tree):
        return (ICategory, )
