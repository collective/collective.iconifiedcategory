# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone import api
from plone import namedfile
from plone.app.testing import login
from plone.app.testing import logout
from zExceptions import Redirect

import os
import unittest

from collective.iconifiedcategory import testing
from collective.iconifiedcategory import utils


class TestUtils(unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.config = self.portal['config']
        api.user.create(
            email='test@test.com',
            username='adminuser',
            password='secret',
        )
        api.user.grant_roles(
            username='adminuser',
            roles=['Manager'],
        )
        login(self.portal, 'adminuser')

    def tearDown(self):
        if 'category-x' in self.config['group-1']:
            api.content.delete(self.config['group-1']['category-x'])
        api.user.delete(username='adminuser')
        logout()

    @property
    def icon(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, 'icon1.png'), 'r')
        return namedfile.NamedBlobFile(f.read(), filename=u'icon1.png')

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
