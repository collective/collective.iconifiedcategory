# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope.component import adapter
from zope.component import getGlobalSiteManager

from collective.iconifiedcategory.interfaces import \
    IIconifiedCategoryChangedEvent
from collective.iconifiedcategory.tests.base import BaseTestCase


SUBSCRIBED_ELEMENTS = []


@adapter(IIconifiedCategoryChangedEvent)
def object_modified_subscriber(event):
    SUBSCRIBED_ELEMENTS.append(event.object.id)


class TestUpdateCategorizedElementsConfig(BaseTestCase):

    def setUp(self):
        super(TestUpdateCategorizedElementsConfig, self).setUp()
        SUBSCRIBED_ELEMENTS[:] = []
        self.gsm = getGlobalSiteManager()
        self.gsm.registerHandler(object_modified_subscriber)

    def tearDown(self):
        self.gsm.unregisterHandler(object_modified_subscriber)
        category = self.portal['config']['group-1']['category-1-1']
        category.title = 'Category 1-1'
        super(TestUpdateCategorizedElementsConfig, self).tearDown()

    def test_subscriber(self):
        """
        Test the ObjectModified event notifier for update-categorized-elements
        view on config context
        """
        config = self.portal['config']
        view = config.restrictedTraverse('@@update-categorized-elements')
        view()
        self.assertListEqual(['file', 'image'], SUBSCRIBED_ELEMENTS)

    def test_result(self):
        """
        Test the update-categorized-elements view on config context
        """
        config = self.portal['config']
        category = config['group-1']['category-1-1']
        plone_file = self.portal['file']
        plone_file.title = 'foo.txt'
        element = self.portal.categorized_elements[plone_file.UID()]
        self.assertEqual('Category 1-1', element['category_title'])
        category.title = 'Category 1-1 Modified'

        view = config.restrictedTraverse('@@update-categorized-elements')
        view()
        element = self.portal.categorized_elements[plone_file.UID()]
        self.assertEqual('Category 1-1 Modified', element['category_title'])
        # Title must remain the same
        self.assertEqual('file.txt', element['title'])


class TestUpdateCategorizedElementsCategory(BaseTestCase):

    def setUp(self):
        super(TestUpdateCategorizedElementsCategory, self).setUp()
        SUBSCRIBED_ELEMENTS[:] = []
        self.gsm = getGlobalSiteManager()
        self.gsm.registerHandler(object_modified_subscriber)

    def tearDown(self):
        self.gsm.unregisterHandler(object_modified_subscriber)
        category = self.portal['config']['group-1']['category-1-1']
        category.title = 'Category 1-1'
        super(TestUpdateCategorizedElementsCategory, self).tearDown()

    def test_subscriber(self):
        """
        Test the ObjectModified event notifier for update-categorized-elements
        view on category context
        """
        config = self.portal['config']
        category = config['group-1']['category-1-1']['subcategory-1-1-1']
        view = category.restrictedTraverse('@@update-categorized-elements')
        view()
        self.assertListEqual(['image'], SUBSCRIBED_ELEMENTS)

    def test_result(self):
        """
        Test the update-categorized-elements view on category context
        """
        config = self.portal['config']
        category = config['group-1']['category-1-1']
        plone_file = self.portal['file']
        element = self.portal.categorized_elements[plone_file.UID()]
        self.assertEqual('Category 1-1', element['category_title'])
        category.title = 'Category 1-1 Modified'

        view = category.restrictedTraverse('@@update-categorized-elements')
        view()
        element = self.portal.categorized_elements[plone_file.UID()]
        self.assertEqual('Category 1-1 Modified', element['category_title'])
