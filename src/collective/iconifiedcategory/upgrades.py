# -*- coding: utf-8 -*-
from collective.iconifiedcategory import logger
from collective.iconifiedcategory.interfaces import IIconifiedInfos
from collective.iconifiedcategory.utils import update_all_categorized_elements
from plone import api
from plone.dexterity.fti import DexterityFTI
from Products.CMFPlone.utils import base_hasattr
from Products.ZCatalog.ProgressHandler import ZLogHandler
from zope.component import getAdapter

import transaction


behavior_id = 'collective.iconifiedcategory.behaviors.iconifiedcategorization.IIconifiedCategorization'


def _portal_types_using_behavior():
    ''' '''
    types_tool = api.portal.get_tool('portal_types')
    portal_types = []
    for type_info in types_tool.listTypeInfo():
        if isinstance(type_info, DexterityFTI) and behavior_id in type_info.behaviors:
            portal_types.append(type_info.id)
    return portal_types


def upgrade_to_2100(context):
    '''
    '''
    # get every categories and generate scales for it or it is generated at first access
    brains = api.content.find(object_provides='collective.iconifiedcategory.content.category.ICategory')
    for brain in brains:
        category = brain.getObject()
        category.restrictedTraverse('@@images').scale(scale='listing')
    # commit so scales are really available when updating categorized elements here under
    transaction.commit()

    # get portal_types using IIconifiedCategorization behavior
    portal_types = _portal_types_using_behavior()
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(portal_type=portal_types)

    logger.info('Querying elements to update among "{0}" objects of portal_type "{1}"'.format(
        len(brains), ', '.join(portal_types)))
    parents_to_update = []
    for brain in brains:
        obj = brain.getObject()
        # this can be useless if using behavior 'Scan metadata' collective.dms.scanbehavior
        if not(base_hasattr(obj, 'to_sign')):
            setattr(obj, 'to_sign', False)
        if not(base_hasattr(obj, 'signed')):
            setattr(obj, 'signed', False)

        parent = obj.aq_parent
        if parent not in parents_to_update:
            parents_to_update.append(parent)

    # finally update parents that contains categorized elements
    nb_of_parents_to_update = len(parents_to_update)
    i = 1
    for parent_to_update in parents_to_update:
        logger.info('Running update_all_categorized_elements for element {0}/{1} ({2})'.format(
            i, nb_of_parents_to_update, '/'.join(parent_to_update.getPhysicalPath())))
        i = i + 1
        # recompute everything including sorting
        update_all_categorized_elements(parent_to_update)


def upgrade_to_2101(context):
    ''' '''
    # get portal_types using IIconifiedCategorization behavior
    portal_types = _portal_types_using_behavior()
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(portal_type=portal_types)

    logger.info('Querying elements to update among "{0}" objects of portal_type "{1}"'.format(
        len(brains), ', '.join(portal_types)))
    parents_to_update = []
    for brain in brains:
        obj = brain.getObject()
        if not(base_hasattr(obj, 'publishable')):
            setattr(obj, 'publishable', False)

        parent = obj.aq_parent
        if parent not in parents_to_update:
            parents_to_update.append(parent)

    # finally update parents that contains categorized elements
    nb_of_parents_to_update = len(parents_to_update)
    i = 1
    for parent_to_update in parents_to_update:
        logger.info('Running update_all_categorized_elements for element {0}/{1} ({2})'.format(
            i, nb_of_parents_to_update, '/'.join(parent_to_update.getPhysicalPath())))
        i = i + 1
        update_all_categorized_elements(parent_to_update)


def upgrade_to_2102(context):
    '''Now that elements using the behavior are marked with IIconifiedCategorizationMarker,
       reindex object_provides to get elements to update.
       Then compute "allowedRolesAndUsers" for categorized elements.
     '''
    catalog = api.portal.get_tool('portal_catalog')
    # update object_provides index
    pghandler = ZLogHandler(steps=1000)
    catalog.reindexIndex('object_provides', context.REQUEST, pghandler=pghandler)

    # compute allowedRolesAndUsers for categorized elements
    brains = catalog(
        object_provides='collective.iconifiedcategory.'
        'behaviors.iconifiedcategorization.IIconifiedCategorizationMarker')
    i = 0
    pghandler = ZLogHandler(steps=1000)
    pghandler.info('Computing "allowedRolesAndUsers" for categorized elements...')
    pghandler.init('ComputeAllowedRolesAndUsers', len(brains))

    for brain in brains:
        i += 1
        pghandler.report(i)
        obj = brain.getObject()
        adapter = getAdapter(obj, IIconifiedInfos)
        allowedRolesAndUsers = adapter._allowedRolesAndUsers
        parent = obj.aq_inner.aq_parent
        parent.categorized_elements[obj.UID()]['allowedRolesAndUsers'] = allowedRolesAndUsers
        parent._p_changed = True
    pghandler.finish()


def upgrade_to_2103(context):
    '''The element "last_updated" is now in categorized_elements.'''
    catalog = api.portal.get_tool('portal_catalog')

    # compute "modified" for categorized elements
    brains = catalog(
        object_provides='collective.iconifiedcategory.'
        'behaviors.iconifiedcategorization.IIconifiedCategorizationMarker')
    i = 0
    pghandler = ZLogHandler(steps=1000)
    pghandler.info('Computing "last_updated" for categorized elements...')
    pghandler.init('ComputeLastUpdatedForCategorizedElements', len(brains))

    for brain in brains:
        i += 1
        pghandler.report(i)
        obj = brain.getObject()
        parent = obj.aq_inner.aq_parent
        modified = obj.modified()
        modified._timezone_naive = True
        if 'last_updated' in parent.categorized_elements[obj.UID()]:
            # already upgraded
            pghandler.info('STOPPING, already migrated...')
            break
        parent.categorized_elements[obj.UID()]['last_updated'] = modified.asdatetime()
        parent._p_changed = True
    pghandler.finish()
