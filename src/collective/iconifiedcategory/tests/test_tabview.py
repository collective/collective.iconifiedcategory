# -*- coding: utf-8 -*-

from plone import api
from collective.iconifiedcategory.tests.base import BaseTestCase


class TestCategorizedTabView(BaseTestCase):

    def test_table_render(self):
        view = self.portal.restrictedTraverse('@@iconifiedcategory')
        result = view()
        self.assertTrue('<a href="http://nohost/plone/image" ' in result)
        self.assertTrue('<a href="http://nohost/plone/file" ' in result)
        self.assertTrue('<td>Category 1-1</td>' in result)

        # when nothing to display
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])
        self.assertEqual(self.portal.categorized_elements, {})
        self.assertTrue('No element to display.' in view())
