# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from zope import schema
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import provider
from collective.z3cform.select2.widget.widget import SingleSelect2FieldWidget

from collective.iconifiedcategory import _
from collective.iconifiedcategory.widget.widget import CategoryTitleFieldWidget


@provider(IFormFieldProvider)
class IIconifiedCategorization(Interface):

    form.order_after(content_category='IDublinCore.title')
    form.widget(content_category=SingleSelect2FieldWidget)
    content_category = schema.Choice(
        title=_(u'Category'),
        source='collective.iconifiedcategory.categories',
        required=True,
    )

    form.order_after(default_titles='IDublinCore.title')
    form.mode(default_titles='hidden')
    form.widget(default_titles=CategoryTitleFieldWidget)
    default_titles = schema.Choice(
        title=_(u'Default title'),
        vocabulary='collective.iconifiedcategory.category_titles',
        required=False,
    )


@implementer(IIconifiedCategorization)
@adapter(IDexterityContent)
class IconifiedCategorization(object):

    def __init__(self, context):
        self.context = context
