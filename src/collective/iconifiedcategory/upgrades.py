# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.fti import DexterityFTI
from Products.CMFPlone.utils import base_hasattr
from collective.iconifiedcategory.utils import get_category_object
from collective.iconifiedcategory.utils import update_categorized_elements

behavior_id = 'collective.iconifiedcategory.behaviors.iconifiedcategorization.IIconifiedCategorization'


def upgrade_to_2000(context):
    '''
    '''
    # get portal_types using IIconifiedCategorization behavior
    types_tool = api.portal.get_tool('portal_types')
    portal_types = []
    for type_info in types_tool.listTypeInfo():
        if isinstance(type_info, DexterityFTI) and behavior_id in type_info.behaviors:
            portal_types.append(type_info.id)

    # query objects
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(portal_type=portal_types)
    for brain in brains:
        obj = brain.getObject()
        if not(base_hasattr(obj, 'signed')):
            setattr(obj, 'signed', None)
            category = get_category_object(obj, obj.content_category)
            update_categorized_elements(parent=obj.aq_parent,
                                        obj=obj,
                                        category=category,
                                        sort=False,
                                        logging=True)
        else:
            # already migrated
            return
