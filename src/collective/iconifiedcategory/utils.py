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
from collective.iconifiedcategory.content.category import ICategory
from collective.iconifiedcategory.interfaces import IIconifiedCategoryConfig


def format_id(*args):
    return CAT_SEPARATOR.join(args)


def format_id_css(id):
    return id.replace(CAT_SEPARATOR, CSS_SEPARATOR)


def get_categories_config(context):
    """Return the categories config root for the given context"""
    config_root = queryAdapter(IIconifiedCategoryConfig, context)
    if not config_root and context is not None:
        result = api.content.find(
            context=api.portal.get_navigation_root(context),
            portal_type='ContentCategoryConfiguration',
        )
        if not result:
            raise ValueError('Categories config is missing')
        config_root = result[0].getObject()
    return config_root


def get_categories(context):
    """Return the categories brains for a specific context"""
    config_root = get_categories_config(context)
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


def get_category_object(context, category_id):
    obj = get_categories_config(context)
    for path in category_id.split(CAT_SEPARATOR)[1:]:
        obj = obj[path]
    return obj


def get_category_icon_url(category):
    if ICategory.providedBy(category):
        icon = category.icon
        obj = category
    else:
        icon = category.aq_parent.icon
        obj = category.aq_parent
    return '{0}/@@download/icon/{1}'.format(
        obj.absolute_url(),
        icon.filename,
    )


def update_categorized_elements(parent, obj, category):
    if 'categorized_elements' not in parent.__dict__:
        parent.categorized_elements = {}
    uid, infos = get_categorized_infos(obj, category)
    parent.categorized_elements[uid] = infos


def remove_categorized_element(parent, obj):
    if obj.UID() in parent.categorized_elements:
        del parent.categorized_elements[obj.UID()]


def get_categorized_infos(obj, category):
    infos = {
        'title': obj.Title(),
        'id': obj.getId(),
        'category': obj.content_category,
        'category_uid': category.UID(),
        'category_id': category.getId(),
        'category_title': category.Title(),
        'absolute_url': obj.absolute_url(),
        'icon_url': get_category_icon_url(category),
    }
    return obj.UID(), infos
