# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from zc.relation.interfaces import ICatalog
from zope.component import getAdapter
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds

from collective.iconifiedcategory import CAT_SEPARATOR
from collective.iconifiedcategory import CSS_SEPARATOR
from collective.iconifiedcategory.content.category import ICategory
from collective.iconifiedcategory.interfaces import IIconifiedCategoryConfig
from collective.iconifiedcategory.interfaces import IIconifiedCategoryGroup
from collective.iconifiedcategory.interfaces import IIconifiedInfos


def format_id(*args):
    return CAT_SEPARATOR.join(args)


def format_id_css(id):
    return id.replace(CAT_SEPARATOR, CSS_SEPARATOR)


def query_config_root(context):
    """Try to get the categories config root for the given context"""
    adapter = queryAdapter(IIconifiedCategoryConfig, context)
    config_root = adapter and adapter.get_config() or None
    if not config_root and context is not None:
        catalog = getToolByName(context, 'portal_catalog')
        query = {
            'portal_type': 'ContentCategoryConfiguration',
        }
        result = catalog.unrestrictedSearchResults(query)
        if not result:
            return
        config_root = result[0]._unrestrictedGetObject()
    return config_root


def has_config_root(context):
    """Verify if there is a config root for the given context"""
    return query_config_root(context) is not None


def get_config_root(context):
    """Return the categories config root for the given context"""
    config_root = query_config_root(context)
    if not config_root:
        raise ValueError('Categories config cannot be found')
    return get_group(config_root, context)


def get_group(config, context):
    """Return the associated groups for the given context"""
    adapter = queryMultiAdapter((config, context), IIconifiedCategoryGroup)
    if adapter:
        return adapter.get_group()
    return config


def get_categories(context):
    """Return the categories brains for a specific context"""
    config_root = get_config_root(context)
    catalog = getToolByName(config_root, 'portal_catalog')
    query = {
        'portal_type': 'ContentCategory',
        'sort_on': 'sortable_title',
        'path': '/'.join(config_root.getPhysicalPath()),
    }
    return catalog.unrestrictedSearchResults(query)


def calculate_category_id(category):
    """Return the caculated category id for a category object"""
    return '{0}_-_{1}_-_{2}'.format(
        category.aq_parent.aq_parent.id,
        category.aq_parent.id,
        category.id,
    )


def get_category_object(context, category_id):
    obj = get_config_root(context)
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
    parent._p_changed = True


def remove_categorized_element(parent, obj):
    if obj.UID() in parent.categorized_elements:
        del parent.categorized_elements[obj.UID()]


def get_categorized_infos(obj, category):
    adapter = getAdapter(obj, IIconifiedInfos)
    return obj.UID(), adapter.get_infos(category)


def get_back_references(obj):
    catalog = queryUtility(ICatalog)
    intids = queryUtility(IIntIds)
    if not catalog or not intids:
        return []
    return catalog.findRelations(
        dict(to_id=intids.getId(aq_inner(obj)),
             from_attribute='related_category'),
    )


def has_relations(obj):
    for relation in get_back_references(obj):
        return True
    if ICategory.providedBy(obj):
        for subcategory in obj.listFolderContents():
            for relation in get_back_references(subcategory):
                return True
    return False


def calculate_filesize(size):
    unit = 'B'
    factor = 1
    sizes = {
        1024. * 1024 * 1024 * 1024: 'TB',
        1024. * 1024 * 1024: 'GB',
        1024. * 1024: 'MB',
        1024.: 'KB',
    }
    for s, u in sizes.items():
        if size >= s:
            unit = u
            factor = s
            break
    size = round(size / factor, 1)
    if unit in ('B', 'KB'):
        size = int(size)
    return '{0} {1}'.format(size, unit)


def print_message(obj):
    """Return the print status message for the given object"""
    messages = {
        True: u'Must be printed',
        False: u'Should not be printed',
    }
    return messages.get(obj.to_print, getattr(obj, 'to_print_message', ''))


def confidential_message(obj):
    """Return the confidential status message for the given object"""
    messages = {
        True: u'Confidential',
        False: u'Not confidential',
    }
    return messages.get(getattr(obj, 'confidential', None), '')
