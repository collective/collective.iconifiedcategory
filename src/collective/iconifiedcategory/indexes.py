# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer

from collective.iconifiedcategory import utils
from collective.iconifiedcategory.content.base import ICategorize


@indexer(ICategorize)
def enabled(obj):
    """
    Indexes the 'sortable_title 'enabled' attribute.
    """
    return obj.enabled


@indexer(IDexterityContent)
def content_category_uid(obj):
    """Index the category_uid"""
    if not hasattr(obj, 'content_category'):
        return
    category_object = utils.get_category_object(obj, obj.content_category)
    return category_object.UID()
