# -*- coding: utf-8 -*-

from collective.iconifiedcategory.tests.base import BaseTestCase


class TestCategorizedTabView(BaseTestCase):

    def test_table_render(self):
        view = self.portal.restrictedTraverse('@@iconifiedcategory')
        result = view()
        self.assertTrue('<a href="http://nohost/plone/image" ' in result)
        self.assertTrue('<a href="http://nohost/plone/file" ' in result)
        self.assertTrue('<td>Category 1-1</td>' in result)
