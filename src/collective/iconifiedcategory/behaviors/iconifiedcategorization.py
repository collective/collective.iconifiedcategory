# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Acquisition import aq_base
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
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.widget.widget import CategoryTitleFieldWidget


@provider(IFormFieldProvider)
class IIconifiedCategorization(Interface):

    form.order_before(content_category='title')
    form.order_before(content_category='IBasic.title')
    form.order_before(content_category='IDublinCore.title')
    form.widget(content_category=SingleSelect2FieldWidget)
    content_category = schema.Choice(
        title=_(u'Category'),
        source='collective.iconifiedcategory.categories',
        required=True,
    )

    form.order_before(default_titles='title')
    form.order_before(default_titles='IBasic.title')
    form.order_before(default_titles='IDublinCore.title')
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

    @property
    def content_category(self):
        return getattr(self.context, 'content_category', None)

    @content_category.setter
    def content_category(self, value):
        if self.content_category is None:
            category = utils.get_category_object(self.context, value)
            # left False if print/confidential
            # not enabled on ContentCategoryGroup
            category_group = category.get_category_group(category)
            if category_group.to_be_printed_activated:
                self.context.to_print = category.to_print
            else:
                self.context.to_print = False
            if category_group.confidentiality_activated:
                self.context.confidential = category.confidential
            else:
                self.context.confidential = False
        self.context.content_category = value
        self.context.reindexObject(idxs=['content_category_uid'])

    @property
    def to_print(self):
        return getattr(aq_base(self.context), 'to_print', False)

    @property
    def confidential(self):
        return getattr(aq_base(self.context), 'confidential', False)
