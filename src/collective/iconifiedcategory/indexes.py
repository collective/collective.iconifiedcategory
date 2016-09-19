# -*- coding: utf-8 -*-

from plone.indexer import indexer
from collective.iconifiedcategory.content.base import ICategorize


@indexer(ICategorize)
def enabled(obj):
    """
      Indexes the 'sortable_title 'enabled' attribute.
    """
    return obj.enabled
