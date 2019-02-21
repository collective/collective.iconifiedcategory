# -*- coding: utf-8 -*-
from collective.iconifiedcategory import logger
from collective.iconifiedcategory.utils import update_all_categorized_elements
from plone import api
from plone.dexterity.fti import DexterityFTI
from Products.CMFPlone.utils import base_hasattr

import transaction


behavior_id = 'collective.iconifiedcategory.behaviors.iconifiedcategorization.IIconifiedCategorization'


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
    types_tool = api.portal.get_tool('portal_types')
    portal_types = []
    for type_info in types_tool.listTypeInfo():
        if isinstance(type_info, DexterityFTI) and behavior_id in type_info.behaviors:
            portal_types.append(type_info.id)

    # query objects
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(portal_type=portal_types)

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
