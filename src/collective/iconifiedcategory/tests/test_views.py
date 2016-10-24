# -*- coding: utf-8 -*-

import lxml
from plone import api
from collective.iconifiedcategory.tests.base import BaseTestCase


class TestCategorizedChildView(BaseTestCase):

    def test__call__(self):
        view = self.portal.restrictedTraverse('@@categorized-childs')

        # the category and elements of category is displayed
        result = view()
        self.assertTrue('<img src="http://nohost/plone/config/group-1/category-1-1/@@download/icon/icon1.png"'
                        in result)
        self.assertTrue('<a href="http://nohost/plone/file/@@download/file/file.txt">' in result)
        self.assertTrue('<a href="http://nohost/plone/image/@@download/file/icon1.png">' in result)

        # remove the categorized elements
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])
        result = lxml.html.fromstring(view())
        self.assertEqual(result.text, 'Nothing.')
