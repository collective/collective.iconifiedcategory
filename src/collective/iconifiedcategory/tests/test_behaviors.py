# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from plone import api

import unittest

from collective.documentviewer.config import CONVERTABLE_TYPES
from collective.documentviewer.settings import GlobalSettings
from collective.iconifiedcategory import testing
from collective.iconifiedcategory.behaviors.iconifiedcategorization import IconifiedCategorization
from collective.iconifiedcategory.tests.base import BaseTestCase
from collective.iconifiedcategory.utils import get_category_object


class TestIconifiedCategorization(BaseTestCase, unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def test_content_category_setter_not_set_if_not_activated(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        category_group.to_be_printed_activated = False
        category_group.confidentiality_activated = False
        category.to_print = True
        category.confidential = True
        obj = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
        )
        # call setter
        adapted_context = IconifiedCategorization(obj)
        setattr(adapted_context, 'content_category', 'config_-_group-1_-_category-1-1')
        self.assertFalse(obj.to_print)
        self.assertFalse(obj.confidential)

    def test_content_category_setter_confidential(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        category_group.confidentiality_activated = True

        # set to False
        category.confidential = False
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
        )
        adapted_file2 = IconifiedCategorization(file2)
        setattr(adapted_file2, 'content_category', 'config_-_group-1_-_category-1-1')
        self.assertFalse(file2.confidential)

        # set to True
        category.confidential = True
        file3 = api.content.create(
            id='file3',
            type='File',
            file=self.file,
            container=self.portal,
        )
        adapted_file3 = IconifiedCategorization(file3)
        setattr(adapted_file3, 'content_category', 'config_-_group-1_-_category-1-1')
        self.assertTrue(file3.confidential)

    def test_content_category_setter_to_print(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        category_group.to_be_printed_activated = True

        # set to False
        category.to_print = False
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
        )
        adapted_file2 = IconifiedCategorization(file2)
        setattr(adapted_file2, 'content_category', 'config_-_group-1_-_category-1-1')
        self.assertFalse(file2.to_print)

        # set to True
        category.to_print = True
        file3 = api.content.create(
            id='file3',
            type='File',
            file=self.file,
            container=self.portal,
        )
        adapted_file3 = IconifiedCategorization(file3)
        setattr(adapted_file3, 'content_category', 'config_-_group-1_-_category-1-1')
        self.assertTrue(file3.to_print)

    def test_content_category_setter_to_print_only_set_if_convertible_when_conversion_enabled(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        category_group.to_be_printed_activated = True

        # set to True
        category.to_print = True
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
        )
        # enable conversion
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
        file2.file.contentType = 'text/unknown'

        adapted_file2 = IconifiedCategorization(file2)
        setattr(adapted_file2, 'content_category', 'config_-_group-1_-_category-1-1')
        notify(ObjectModifiedEvent(file2))
        self.assertIsNone(file2.to_print)

    def test_content_category_setter_reindex_content_category_uid(self):
        """ """
        catalog = api.portal.get_tool('portal_catalog')
        obj = self.portal['file']
        category = get_category_object(obj, obj.content_category)
        # correctly indexed on creation
        category_brain = catalog(content_category_uid=category.UID())[0]
        self.assertEqual(category_brain.UID, obj.UID())
        obj_brain = catalog(UID=obj.UID())[0]
        self.assertEqual(obj_brain.content_category_uid, category.UID())
        # correctly reindexed when content_category changed thru setter
        category2 = self.portal.config['group-1']['category-1-2']
        self.assertNotEqual(category, category2)
        adapted_obj = IconifiedCategorization(obj)
        setattr(adapted_obj, 'content_category', 'config_-_group-1_-_category-1-2')
        category2_brain = catalog(content_category_uid=category2.UID())[0]
        self.assertEqual(category2_brain.UID, obj.UID())
        obj_brain = catalog(UID=obj.UID())[0]
        self.assertEqual(obj_brain.content_category_uid, category2.UID())
