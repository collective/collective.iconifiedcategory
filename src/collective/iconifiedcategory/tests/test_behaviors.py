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
from collective.iconifiedcategory.utils import calculate_category_id
from collective.iconifiedcategory.utils import get_category_object


class TestIconifiedCategorization(BaseTestCase, unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def test_content_category_not_set_if_not_activated(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        content_category_id = calculate_category_id(category)
        category_group.to_be_printed_activated = False
        category_group.confidentiality_activated = False
        category.to_print = True
        category.confidential = True
        obj = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertFalse(obj.to_print)
        self.assertFalse(obj.confidential)

    def test_content_category_confidential_on_creation(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        content_category_id = calculate_category_id(category)
        category_group.confidentiality_activated = True

        # set to False
        category.confidential = False
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertFalse(file2.confidential)

        # set to True
        category.confidential = True
        file3 = api.content.create(
            id='file3',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertTrue(file3.confidential)

    def test_content_category_to_print_on_creation(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        content_category_id = calculate_category_id(category)
        category_group.to_be_printed_activated = True
        # enable conversion
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()

        # set to False
        category.to_print = False
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertFalse(file2.to_print)

        # set to True
        category.to_print = True
        file3 = api.content.create(
            id='file3',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertTrue(file3.to_print)

    def test_content_category_to_sign_signed_on_creation(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        content_category_id = calculate_category_id(category)
        category_group.signed_activated = True

        # set to False both attributes
        category.to_sign = False
        category.signed = False
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertFalse(file2.to_sign)
        self.assertFalse(file2.signed)

        # set True for to_sign, False for signed
        category.to_sign = True
        category.signed = False
        file3 = api.content.create(
            id='file3',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertTrue(file3.to_sign)
        self.assertFalse(file3.signed)

        # set True for both attributes
        category.to_sign = True
        category.signed = True
        file4 = api.content.create(
            id='file4',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        self.assertTrue(file4.to_sign)
        self.assertTrue(file4.signed)

    def test_content_category_to_print_only_set_if_convertible_when_conversion_enabled(self):
        """ """
        category_group = self.portal.config['group-1']
        category = self.portal.config['group-1']['category-1-1']
        content_category_id = calculate_category_id(category)
        category_group.to_be_printed_activated = True

        # set to True
        category.to_print = True
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category=content_category_id)
        # enable conversion
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
        file2.file.contentType = 'text/unknown'

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
