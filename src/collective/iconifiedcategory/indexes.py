# -*- coding: utf-8 -*-

from collective.iconifiedcategory import utils
from collective.iconifiedcategory.content.base import ICategorize
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from Products.PluginIndexes.common.UnIndex import _marker


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
    try:
        category_object = utils.get_category_object(obj, obj.content_category)
    except KeyError:
        return _marker
    return category_object.UID()
