# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

import copy
from Acquisition import aq_inner
from zope.globalrequest import getRequest
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.memoize import ram
from time import time
from zc.relation.interfaces import ICatalog
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.component import queryUtility
from zope.i18n import translate
from zope.intid.interfaces import IIntIds

from collective.iconifiedcategory import CAT_SEPARATOR
from collective.iconifiedcategory import CSS_SEPARATOR
from collective.iconifiedcategory.content.category import ICategory
from collective.iconifiedcategory.content.categorygroup import ICategoryGroup
from collective.iconifiedcategory.interfaces import IIconifiedCategoryConfig
from collective.iconifiedcategory.interfaces import IIconifiedCategoryGroup
from collective.iconifiedcategory.interfaces import IIconifiedContent
from collective.iconifiedcategory.interfaces import IIconifiedInfos


def format_id(*args):
    return CAT_SEPARATOR.join(args)


def format_id_css(id):
    return id.replace(CAT_SEPARATOR, CSS_SEPARATOR)


def query_config_root(context):
    """Try to get the categories config root for the given context"""
    adapter = queryAdapter(context, IIconifiedCategoryConfig)
    config_root = adapter and adapter.get_config() or None
    if not config_root and context is not None:
        catalog = api.portal.get_tool('portal_catalog')
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
    adapter = getMultiAdapter((config, context), IIconifiedCategoryGroup)
    return adapter.get_group()


def get_categories(context):
    """Return the categories brains for a specific context"""
    config_root = get_config_root(context)
    catalog = api.portal.get_tool('portal_catalog')
    query = {
        'portal_type': 'ContentCategory',
        'sort_on': 'sortable_title',
        'path': '/'.join(config_root.getPhysicalPath()),
        'enabled': True
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
    depth = 1
    if ICategoryGroup.providedBy(obj):
        depth = 2
    for path in category_id.split(CAT_SEPARATOR)[depth:]:
        obj = obj[path]
    return obj


def get_category_icon_url(category):
    portal_url = api.portal.get_tool('portal_url')
    if ICategory.providedBy(category):
        icon = category.icon
        obj = category
    else:
        icon = category.aq_parent.icon
        obj = category.aq_parent

    return '{0}/@@download/icon/{1}'.format(
        portal_url.getRelativeContentURL(obj),
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


def _categorized_elements(context):
    return copy.deepcopy(getattr(context, 'categorized_elements', {}))


def get_categorized_elements(context,
                             result_type='dict',
                             portal_type=None,
                             sort_on=None):
    """Return categorized elements.
       p_result_type may be :
       - 'dict': default, essential metadata are returned as a dict;
       - 'objects': categorized objects are returned;
       - 'brains': categorized brains are returned."""
    elements = []
    for uid, element in _categorized_elements(context).items():
        if portal_type and not element['portal_type'] == portal_type:
            continue
        brains = api.content.find(context=context, UID=uid)
        if not brains:
            continue
        brain = brains[0]
        adapter = getMultiAdapter((context, context.REQUEST, brain),
                                  IIconifiedContent)
        if adapter.can_view() is True:
            if result_type == 'objects':
                elements.append(brain.getObject())
            elif result_type == 'brains':
                elements.append(brain)
            else:
                elements.append(element)
    if sort_on:
        if result_type == 'dict':
            elements = sorted(elements, key=lambda x, sort_on=sort_on: x[sort_on])
        else:
            elements = sorted(elements, key=lambda x, sort_on=sort_on: getattr(x, sort_on))
    return elements


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


def warn_filesize(size):
    filesizelimit = api.portal.get_registry_record(
        'collective.iconifiedcategory.filesizelimit') or 5000000
    if size > filesizelimit:
        return True
    return False


def render_filesize(size):
    pretty_filesize = calculate_filesize(size)
    if warn_filesize(size):
        pretty_filesize = \
            u"<span class='warn_filesize' title='{0}'>{1}</span>".format(
                translate('help_warn_filesize',
                          domain='collective.iconifiedcategory',
                          context=getRequest(),
                          default='Annex size is huge, it could '
                          'be difficult to be downloaded!'),
                pretty_filesize)
    return pretty_filesize


def print_message(obj):
    """Return the print status message for the given object"""
    messages = {
        True: u'Must be printed',
        False: u'Should not be printed',
        None: u'Not convertible to a printable format',
    }
    return messages.get(obj.to_print, getattr(obj, 'to_print_message', ''))


def confidential_message(obj):
    """Return the confidential status message for the given object"""
    messages = {
        True: u'Confidential',
        False: u'Not confidential',
    }
    return messages.get(getattr(obj, 'confidential', None), '')


@ram.cache(lambda f, p: (p, time() // (60 * 60)))
def is_file_type(portal_type):
    """Verify if the given portal type provides IFile or IImage"""
    portal_type = api.portal.get_tool('portal_types')[portal_type]
    module_path, classname = (
        u'.'.join(portal_type.klass.split('.')[:-1]),
        portal_type.klass.split('.')[-1],
    )
    module = __import__(module_path, {}, {}, [classname])
    cls = getattr(module, classname, None)
    if cls is None:
        return False
    for interface in (IFile, IImage):
        if cls.__implemented__(interface):
            return True
    return False
