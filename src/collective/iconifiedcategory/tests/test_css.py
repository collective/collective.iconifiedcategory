# -*- coding: utf-8 -*-

from collective.iconifiedcategory.tests.base import BaseTestCase


class TestIconifiedCategoryCSS(BaseTestCase):

    def test__call__(self):
        obj = self.portal['file']
        view = obj.restrictedTraverse('@@collective-iconifiedcategory.css')
        css = view()
        self.assertTrue(".config-group-1-category-1-1 " in css)
        self.assertTrue("background: transparent url("
                        "'http://nohost/plone/config/group-1/category-1-1/@@download/icon/icon1.png')"
                        in css)
        self.assertTrue(".config-group-2-category-2-2 " in css)
        self.assertTrue("background: transparent url("
                        "'http://nohost/plone/config/group-2/category-2-2/@@download/icon/icon2.png')"
                        in css)
        self.assertTrue(".config-group-2-category-2-3 " in css)
        self.assertTrue("background: transparent url("
                        "'http://nohost/plone/config/group-2/category-2-3/@@download/icon/icon3.png')"
                        in css)
