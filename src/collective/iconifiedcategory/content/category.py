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
from plone.autoform import directives as form
from plone.namedfile.field import NamedBlobImage
from plone.rfc822.interfaces import IPrimaryField
from zope.interface import alsoProvides
from zope.interface import implements

from collective.iconifiedcategory import _
from collective.iconifiedcategory.content.base import ICategorize


class ICategory(IFolder, ICategorize):

    form.order_before(icon='predefined_title')
    icon = NamedBlobImage(
        title=_(u'Icon'),
        required=True,
    )
alsoProvides(ICategory['icon'], IPrimaryField)


class Category(Container):
    implements(ICategory)

    @property
    def category_uid(self):
        return self.UID()

    @property
    def category_id(self):
        return self.getId()

    @property
    def category_title(self):
        return self.Title()

    def get_category_group(self, context=None):
        if context is None:
            context = self
        return context.aq_parent


class CategorySchemaPolicy(DexteritySchemaPolicy):

    def bases(self, schema_name, tree):
        return (ICategory, )
