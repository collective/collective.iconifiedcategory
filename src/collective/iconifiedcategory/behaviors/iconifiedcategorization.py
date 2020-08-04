# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Acquisition import aq_base
from collective.iconifiedcategory import _
from collective.iconifiedcategory.utils import get_category_object
from collective.iconifiedcategory.utils import validateFileIsPDF
from collective.iconifiedcategory.widget.widget import CategoryTitleFieldWidget
from collective.z3cform.select2.widget.widget import SingleSelect2FieldWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import invariant
from zope.interface import provider


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

    @invariant
    def validateFileIsPDFInvariant(data):
        validateFileIsPDF(data)


class IIconifiedCategorizationMarker(Interface):
    """ """


@implementer(IIconifiedCategorization)
@adapter(IIconifiedCategorizationMarker)
class IconifiedCategorization(object):

    def __init__(self, context):
        self.context = context

    @property
    def default_titles(self):
        return None

    @property
    def content_category(self):
        return getattr(self.context, 'content_category', None)

    def _content_category_changed_default_values(self, new_value):
        """When changing content_category, change default values
           if original default was not yet changed."""
        try:
            current_category = get_category_object(
                self.context, self.context.content_category)
            new_category = get_category_object(
                self.context, new_value)
        except KeyError:
            # in case we can not get the category, we return
            # this can be the case when changing category of an element
            # and old category does not exist in the content_category_grouyp context
            return
        category_group = current_category.get_category_group(current_category)
        # to_print
        if category_group.to_be_printed_activated and \
           self.context.to_print == current_category.to_print:
            self.context.to_print = new_category.to_print
        # confidential
        if category_group.confidentiality_activated and \
           self.context.confidential == current_category.confidential:
            self.context.confidential = new_category.confidential
        # to_sign/signed
        if category_group.signed_activated and \
           self.context.to_sign == current_category.to_sign and \
           self.context.signed == current_category.signed:
            self.context.to_sign = new_category.to_sign
            self.context.signed = new_category.signed
        # publishable
        if category_group.publishable_activated and \
           self.context.publishable == current_category.publishable:
            self.context.publishable = new_category.publishable

    @content_category.setter
    def content_category(self, value):
        # if content_category changed, we check also if default values
        # need to be updated.  We will update values that were not modified
        # since last default values
        if getattr(self.context, 'content_category', None) and self.context.content_category != value:
            self._content_category_changed_default_values(value)
        self.context.content_category = value
        self.context.reindexObject(idxs=['content_category_uid'])

    @property
    def to_print(self):
        return getattr(aq_base(self.context), 'to_print', False)

    @property
    def confidential(self):
        return getattr(aq_base(self.context), 'confidential', False)

    @property
    def to_sign(self):
        return getattr(aq_base(self.context), 'to_sign', False)

    @property
    def signed(self):
        return getattr(aq_base(self.context), 'signed', False)

    @property
    def publishable(self):
        return getattr(aq_base(self.context), 'publishable', False)
