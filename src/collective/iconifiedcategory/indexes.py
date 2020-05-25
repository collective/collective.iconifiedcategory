# -*- coding: utf-8 -*-

from collective.iconifiedcategory import utils
from collective.iconifiedcategory.behaviors.iconifiedcategorization import IIconifiedCategorizationMarker
from collective.iconifiedcategory.content.base import ICategorize
from imio.helpers.content import _contained_objects
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
    res = []
    if IIconifiedCategorizationMarker.providedBy(obj):
        try:
            category_object = utils.get_category_object(obj, obj.content_category)
        except KeyError:
            return _marker
        res.append(category_object.UID())
    else:
        # maybe current element holds unindexed elements using a content_category...
        for contained_obj in _contained_objects(obj, only_unindexed=True):
            try:
                if IIconifiedCategorizationMarker.providedBy(contained_obj):
                    category_object = utils.get_category_object(
                        contained_obj, contained_obj.content_category)
                    res.append(category_object.UID())
            except KeyError:
                continue
    return res or _marker
