# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import testing
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.event import IconifiedAttrChangedEvent
from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api
from Products.CMFPlone.utils import base_hasattr

import unittest


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

    def test_iconifiedattrchangedevent(self):
        from zope.event import subscribers
        dummy = []
        subscribers.append(dummy.append)
        event = IconifiedAttrChangedEvent(object(), '', 'old', 'new')
        self._notify(event)
        self.assertEqual(dummy, [event])


class TestTriggeredEvents(BaseTestCase, unittest.TestCase):

    def test_categorized_elements_correct_after_copy_paste_categorized_content(self):
        file_obj = self.portal['file_txt']
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

    def test_defer_categorized_content_created_event(self):
        """Test that when defering management of the entire
           categorized_content_created event."""
        # not defered
        container = api.content.create(
            id='folder',
            type='Folder',
            container=self.portal
        )
        self.portal.REQUEST.set('defer_categorized_content_created_event', False)
        file_obj1 = api.content.create(
            id='file1',
            type='File',
            file=self.file,
            container=container,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        file_obj2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=container,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        self.assertTrue(file_obj1.UID() in container.categorized_elements)
        self.assertTrue(file_obj2.UID() in container.categorized_elements)

        # defered defer_categorized_content_created_event
        container2 = api.content.create(
            id='folder2',
            type='Folder',
            container=self.portal
        )
        self.portal.REQUEST.set('defer_categorized_content_created_event', True)
        file_obj3 = api.content.create(
            id='file3',
            type='File',
            file=self.file,
            container=container2,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        file_obj4 = api.content.create(
            id='file4',
            type='File',
            file=self.file,
            container=container2,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        self.assertFalse(base_hasattr(container2, 'categorized_elements'))
        # calling utils.update_all_categorized_elements will update necessary things
        utils.update_all_categorized_elements(container2)
        self.assertTrue(file_obj3.UID() in container2.categorized_elements)
        self.assertTrue(file_obj4.UID() in container2.categorized_elements)
        # tear down
        self.portal.REQUEST.set('defer_categorized_content_created_event', False)
        self.portal.REQUEST.set('defer_update_categorized_elements', False)

    def test_defer_update_categorized_elements(self):
        """Using 'defer_update_categorized_elements' will avoid the call to
           utils.update_all_categorized_elements on categorized element create/update."""
        # defered defer_update_categorized_elements
        container = api.content.create(
            id='folder',
            type='Folder',
            container=self.portal
        )
        self.portal.REQUEST.set('defer_update_categorized_elements', True)
        file_obj1 = api.content.create(
            id='file1',
            type='File',
            file=self.file,
            container=container,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        file_obj2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=container,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        self.assertFalse(base_hasattr(container, 'categorized_elements'))
        # calling utils.update_all_categorized_elements will update necessary things
        utils.update_all_categorized_elements(container)
        self.assertTrue(file_obj1.UID() in container.categorized_elements)
        self.assertTrue(file_obj2.UID() in container.categorized_elements)
        # tear down
        self.portal.REQUEST.set('defer_categorized_content_created_event', False)
        self.portal.REQUEST.set('defer_update_categorized_elements', False)

    def test_defer_update_categorized_elements_when_cloned(self):
        """Call to 'update_all_categorized_elements' may be defered
           when cloning a categorized elements container."""
        container = api.content.create(
            id='folder',
            type='Folder',
            container=self.portal
        )
        api.content.create(
            id='file1',
            type='File',
            file=self.file,
            container=container,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=container,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        # clone container
        self.portal.REQUEST.set('defer_update_categorized_elements', True)
        copy_info = self.portal.manage_copyObjects(ids=[container.getId()])
        paste_infos = self.portal.manage_pasteObjects(copy_info)
        new_container = self.portal.get(paste_infos[0]['new_id'])
        new_file_obj1 = new_container.file1
        new_file_obj2 = new_container.file2
        self.assertFalse(new_file_obj1.UID() in new_container.categorized_elements)
        self.assertFalse(new_file_obj2.UID() in new_container.categorized_elements)
        # calling utils.update_all_categorized_elements will update necessary things
        utils.update_all_categorized_elements(new_container)
        self.assertTrue(new_file_obj1.UID() in new_container.categorized_elements)
        self.assertTrue(new_file_obj2.UID() in new_container.categorized_elements)
        self.assertEqual(len(new_container.categorized_elements), 2)
        # tear down
        self.portal.REQUEST.set('defer_update_categorized_elements', False)

    def test_delete_categorized_element(self):
        """When an element having a content_category is deleted, the parent's
           categorized_elements are update accordingly."""
        file_UID = self.portal.file_txt.UID()
        image_UID = self.portal.image.UID()
        self.assertTrue(file_UID in self.portal.categorized_elements)
        self.assertTrue(image_UID in self.portal.categorized_elements)

        # remove self.portal.file, will be removed from parent's categorized_elements
        api.content.delete(self.portal.file_txt)
        self.assertFalse(file_UID in self.portal.categorized_elements)

        # remove self.portal.image
        # does not break if was not in parent's categorized_elements
        self.portal.categorized_elements.clear()
        self.assertFalse(image_UID in self.portal.categorized_elements)
        api.content.delete(self.portal.image)
        self.assertFalse(image_UID in self.portal.categorized_elements)

        # does not break if parent does not have a categorized_elements attribute
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        delattr(self.portal, 'categorized_elements')
        api.content.delete(file2)
