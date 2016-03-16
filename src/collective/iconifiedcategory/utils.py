# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone import api
from zope.component import queryAdapter

from collective.iconifiedcategory import CAT_SEPARATOR
from collective.iconifiedcategory import CSS_SEPARATOR
from collective.iconifiedcategory.interfaces import IIconifiedCategoryConfig


def format_id(*args):
    return CAT_SEPARATOR.join(args)


def format_id_css(id):
    return id.replace(CAT_SEPARATOR, CSS_SEPARATOR)


def get_categories(context):
    """Return the categories brains for a specific context"""
    config_root = queryAdapter(IIconifiedCategoryConfig, context)
    if not config_root and context is not None:
        config_root = api.portal.get_navigation_root(context)
    return api.content.find(
        context=config_root,
        portal_type='ContentCategory',
        sort_on='sortable_title',
    )


def calculate_category_id(category):
    """Return the caculated category id for a category object"""
    return '{0}_-_{1}_-_{2}'.format(
        category.aq_parent.aq_parent.id,
        category.aq_parent.id,
        category.id,
    )
