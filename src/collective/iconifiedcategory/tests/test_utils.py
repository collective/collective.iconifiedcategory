# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone import api
from plone.dexterity.utils import createContentInContainer
from zExceptions import Redirect

import unittest

from collective.iconifiedcategory import testing
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.tests.base import BaseTestCase


class TestUtils(BaseTestCase, unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def test_category_before_remove(self):
        """
        Ensure that an error is raised if we try to remove an used category
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        document = api.content.create(
            type='Document',
            title='doc-category-remove',
            container=self.portal,
            content_category='config_-_group-1_-_category-x',
            to_print=False,
            confidential=False,
        )
        self.assertRaises(Redirect, api.content.delete, category)
        api.content.delete(document)
        api.content.delete(category)

    def test_category_with_subcategory_before_remove(self):
        """
        Ensure that an error is raised if we try to remove a category that
        contains an used subcategory
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        api.content.create(
            type='ContentSubcategory',
            title='Subcategory X',
            icon=self.icon,
            container=category,
        )
        document = api.content.create(
            type='Document',
            title='doc-category-remove-2',
            container=self.portal,
            content_category='config_-_group-1_-_category-x_-_subcategory-x',
            to_print=False,
            confidential=False,
        )
        self.assertRaises(Redirect, api.content.delete, category)
        api.content.delete(document)
        api.content.delete(category)

    def test_subcategory_before_removed(self):
        """
        Ensure that an error is raised if we try to remove an used subcategory
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        subcategory = api.content.create(
            type='ContentSubcategory',
            title='Subcategory X',
            icon=self.icon,
            container=category,
        )
        document = api.content.create(
            type='Document',
            title='doc-subcategory-remove',
            container=self.portal,
            content_category='config_-_group-1_-_category-x_-_subcategory-x',
            to_print=False,
            confidential=False,
        )
        self.assertRaises(Redirect, api.content.delete, subcategory)
        api.content.delete(document)
        api.content.delete(subcategory)
        api.content.delete(category)

    def test_category_moved(self):
        """
        Ensure that an error is raised if we try to move an used category
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        document = api.content.create(
            type='Document',
            title='doc-category-move-1',
            container=self.portal,
            content_category='config_-_group-1_-_category-x',
            to_print=False,
            confidential=False,
        )
        self.assertRaises(Redirect, api.content.move, category,
                          self.config['group-2'])
        api.content.delete(document)
        category = api.content.move(category, self.config['group-2'])
        api.content.delete(category)

    def test_category_subcategory_moved(self):
        """
        Ensure that an error is raised if we try to move a category that
        contains an used subcategory
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        api.content.create(
            type='ContentSubcategory',
            title='Subcategory X',
            icon=self.icon,
            container=category,
        )
        document = api.content.create(
            type='Document',
            title='doc-category-move-2',
            container=self.portal,
            content_category='config_-_group-1_-_category-x_-_subcategory-x',
            to_print=False,
            confidential=False,
        )
        new_folder = self.config['group-1']
        self.assertRaises(Redirect, api.content.move, category, new_folder)
        api.content.delete(document)
        category = api.content.move(category, new_folder)
        api.content.delete(category)

    def test_subcategory_moved(self):
        """
        Ensure that an error is raised if we try to move an used subcategory
        """
        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        subcategory = api.content.create(
            type='ContentSubcategory',
            title='Subcategory X',
            icon=self.icon,
            container=category,
        )
        document = api.content.create(
            type='Document',
            title='doc-subcategory-move',
            container=self.portal,
            content_category='config_-_group-1_-_category-x_-_subcategory-x',
            to_print=False,
            confidential=False,
        )
        new_folder = self.config['group-1']['category-1-1']
        self.assertRaises(Redirect, api.content.move, subcategory, new_folder)
        api.content.delete(document)
        subcategory = api.content.move(subcategory, new_folder)
        api.content.delete(subcategory)
        api.content.delete(category)

    def test_calculate_filesize(self):
        self.assertEqual('100 B', utils.calculate_filesize(100))
        self.assertEqual('1 KB', utils.calculate_filesize(1024))
        self.assertEqual('1.1 MB', utils.calculate_filesize(1150976))
        self.assertEqual('15.5 MB', utils.calculate_filesize(16252928))

    def test_print_message(self):
        obj = type('obj', (object, ), {
            'to_print': False,
        })()
        self.assertEqual(u'Should not be printed', utils.print_message(obj))

        obj.to_print = True
        self.assertEqual(u'Must be printed', utils.print_message(obj))

        obj.to_print = None
        self.assertEqual(u'Not convertible to a printable format',
                         utils.print_message(obj))

    def test_confidential_message(self):
        obj = type('obj', (object, ), {})()
        self.assertEqual(u'', utils.confidential_message(obj))

        obj.confidential = True
        self.assertEqual(u'Confidential', utils.confidential_message(obj))

        obj.confidential = False
        self.assertEqual(u'Not confidential', utils.confidential_message(obj))

    def test_warn_filesize(self):
        # default warning is for files > 5Mb
        self.assertEqual(
            api.portal.get_registry_record(
                'collective.iconifiedcategory.filesizelimit'),
            5000000)
        file1 = api.content.create(
            id='file1',
            type='File',
            file=self.file,
            container=self.portal,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        self.assertEqual(file1.file.size, 3017)
        self.assertFalse(utils.warn_filesize(file1.file.size))

        # now enable warning (a specific portal_message is added when file created)
        api.portal.set_registry_record(
            'collective.iconifiedcategory.filesizelimit',
            3000)
        file2 = api.content.create(
            id='file2',
            type='File',
            file=self.file,
            container=self.portal,
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        self.assertEqual(file2.file.size, 3017)
        self.assertTrue(utils.warn_filesize(file2.file.size))

    def test_render_filesize(self):
        self.assertEqual(utils.render_filesize(1000),
                         '1000 B')
        self.assertEqual(utils.render_filesize(1024),
                         '1 KB')
        self.assertEqual(utils.render_filesize(5000),
                         '4 KB')
        self.assertEqual(utils.render_filesize(5000000),
                         '4.8 MB')
        self.assertEqual(utils.render_filesize(5000000),
                         '4.8 MB')
        # warning if filesize > 5000000
        self.assertEqual(utils.render_filesize(5000001),
                         u"<span class='warn_filesize' title='Annex size is huge, "
                         "it could be difficult to be downloaded!'>4.8 MB</span>")

    def test_get_categorized_elements(self):
        # first remove existing elements so it does not influence our test
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])

        category = api.content.create(
            type='ContentCategory',
            title='Category X',
            icon=self.icon,
            container=self.config['group-1'],
        )
        document = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='doc-subcategory-move',
            description='Document description',
            content_category='config_-_group-1_-_category-x',
            to_print=False,
            confidential=False,
        )
        result = utils.get_categorized_elements(self.portal)
        self.assertEqual(
            result,
            [{'UID': document.UID(),
              'category_id': 'category-x',
              'category_title': 'Category X',
              'category_uid': category.UID(),
              'subcategory_id': None,
              'subcategory_title': None,
              'subcategory_uid': None,
              'confidential': False,
              'title': 'doc-subcategory-move',
              'description': 'Document description',
              'icon_url': 'config/group-1/category-x/@@download/icon/icon1.png',
              'portal_type': 'Document',
              'preview_status': 'not_convertable',
              'download_url': None,
              'to_print': False,
              'filesize': None,
              'relative_url': 'doc-subcategory-move',
              'warn_filesize': False,
              'id': 'doc-subcategory-move'}])
        # filter on portal_type
        self.assertEqual(
            utils.get_categorized_elements(self.portal,
                                           portal_type='Document'),
            result)
        self.failIf(utils.get_categorized_elements(self.portal,
                                                   portal_type='Document2'))
        # ask the objects
        self.assertEqual(
            utils.get_categorized_elements(self.portal,
                                           result_type='objects'),
            [document])
        # ask brains
        self.assertEqual(
            [brain.UID for brain in
             utils.get_categorized_elements(self.portal,
                                            result_type='brains')],
            [document.UID()])

        # sort_on
        document2 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='2doc-subcategory-move',
            content_category='config_-_group-1_-_category-x',
            to_print=False,
            confidential=False,
        )
        # result_type='dict'
        result = utils.get_categorized_elements(self.portal, sort_on='title')
        expected = [res['title'] for res in result]
        self.assertEqual(expected, ['2doc-subcategory-move', 'doc-subcategory-move'])

        # result_type='objects'
        self.assertEqual(
            set(utils.get_categorized_elements(self.portal,
                                               result_type='objects')),
            set([document, document2]))
        self.assertEqual(
            utils.get_categorized_elements(self.portal,
                                           result_type='objects',
                                           sort_on='title'),
            [document2, document])
        # result_type='brains'
        self.assertEqual(
            [brain.UID for brain in
             utils.get_categorized_elements(self.portal,
                                            result_type='brains',
                                            sort_on='sortable_title')],
            [document2.UID(), document.UID()])

        # teardown
        self.assertRaises(Redirect, api.content.delete, category)
        api.content.delete(document)
        api.content.delete(document2)
        api.content.delete(category)

    def test_update_all_categorized_elements(self):
        # first remove existing elements so it does not influence our test
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])

        document1 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='doc1',
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        document1UID = document1.UID()
        document2 = createContentInContainer(
            container=self.portal,
            portal_type='Document',
            title='doc2',
            content_category='config_-_group-1_-_category-1-1',
            to_print=False,
            confidential=False,
        )
        document2UID = document2.UID()
        self.assertEqual(len(self.portal.categorized_elements), 2)
        self.assertTrue(document1UID in self.portal.categorized_elements)
        self.assertTrue(document2UID in self.portal.categorized_elements)
        self.portal.categorized_elements = {}
        self.assertEqual(len(self.portal.categorized_elements), 0)
        utils.update_all_categorized_elements(self.portal)
        self.assertEqual(len(self.portal.categorized_elements), 2)
        self.assertTrue(document1UID in self.portal.categorized_elements)
        self.assertTrue(document2UID in self.portal.categorized_elements)

        # if a content_category is wrong, element is no more stored in categorized_elements
        document1.content_category = 'some_wrong_category_id'
        utils.update_all_categorized_elements(self.portal)
        self.assertEqual(len(self.portal.categorized_elements), 1)
        self.assertTrue(document2UID in self.portal.categorized_elements)
