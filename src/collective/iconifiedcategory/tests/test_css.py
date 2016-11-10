# -*- coding: utf-8 -*-

from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api
from zope.annotation import IAnnotations


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

        # delete the config
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])
        api.content.delete(self.portal['config'])
        # view is memoized, we need to clean the cache
        annotations = IAnnotations(self.portal.REQUEST)
        del annotations['plone.memoize']
        self.assertEqual(view(), '')
