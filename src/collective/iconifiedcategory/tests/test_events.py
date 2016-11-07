# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

import unittest

from plone import api

from collective.iconifiedcategory import testing
from collective.iconifiedcategory.event import IconifiedChangedEvent
from collective.iconifiedcategory.tests.base import BaseTestCase


class TestIconifiedChangedEvent(unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def setUp(self):
        from zope.event import subscribers
        self._old_subscribers = subscribers[:]
        subscribers[:] = []

    def tearDown(self):
        from zope.event import subscribers
        subscribers[:] = self._old_subscribers

    def _notify(self, event):
        from zope.event import notify
        notify(event)

    def test_iconifiedchangedevent(self):
        from zope.event import subscribers
        dummy = []
        subscribers.append(dummy.append)
        event = IconifiedChangedEvent(object(), 'old', 'new')
        self._notify(event)
        self.assertEqual(dummy, [event])


class testTriggeredEvents(BaseTestCase, unittest.TestCase):

    def test_categorized_elements_correct_after_copy_paste_categorized_content(self):
        file_obj = self.portal['file']
        file_obj_UID = file_obj.UID()
        img_obj = self.portal['image']
        img_obj_UID = img_obj.UID()
        self.assertEquals(len(self.portal.categorized_elements), 2)
        self.assertTrue(file_obj_UID in self.portal.categorized_elements)
        self.assertTrue(img_obj_UID in self.portal.categorized_elements)

        # copy paste a contained categorized content
        copied_data = self.portal.manage_copyObjects(ids=[file_obj.getId()])
        infos = self.portal.manage_pasteObjects(copied_data)
        new_file = self.portal[infos[0]['new_id']]
        new_file_UID = new_file.UID()
        self.assertEquals(len(self.portal.categorized_elements), 3)
        self.assertTrue(file_obj_UID in self.portal.categorized_elements)
        self.assertTrue(img_obj_UID in self.portal.categorized_elements)
        self.assertTrue(new_file_UID in self.portal.categorized_elements)

    def test_categorized_elements_correct_after_copy_paste_categorized_content_container(self):
        container = api.content.create(
            id='folder',
            type='Folder',
            container=self.portal
        )
        file_obj1 = api.content.create(
            id='file1',
            type='File',
            file=self.file,
            container=container,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        file_obj1_UID = file_obj1.UID()
        file_obj2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=container,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        file_obj2_UID = file_obj2.UID()
        self.assertEquals(len(container.categorized_elements), 2)
        self.assertTrue(file_obj1_UID in container.categorized_elements)
        self.assertTrue(file_obj2_UID in container.categorized_elements)

        # copy/paste the container
        copied_data = self.portal.manage_copyObjects(ids=[container.getId()])
        infos = self.portal.manage_pasteObjects(copied_data)
        new_container = self.portal[infos[0]['new_id']]
        self.assertEquals(len(new_container.categorized_elements), 2)
        # old no more referenced
        self.assertTrue(file_obj1_UID not in new_container.categorized_elements)
        self.assertTrue(file_obj2_UID not in new_container.categorized_elements)
        # copied contents are correctly referenced
        copied_file1 = new_container['file1']
        copied_file2 = new_container['file2']
        self.assertTrue(copied_file1.UID() in new_container.categorized_elements)
        self.assertTrue(copied_file2.UID() in new_container.categorized_elements)
