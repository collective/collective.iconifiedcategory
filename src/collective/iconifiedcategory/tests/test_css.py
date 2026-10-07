# -*- coding: utf-8 -*-

from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api
from Products.CMFPlone.resources.browser.resource import REQUEST_CACHE_KEY
from Products.CMFPlone.resources.browser.resource import StylesView

import re


class TestIconifiedCategoryCSS(BaseTestCase):

    def test__call__(self):
        view = self.portal.restrictedTraverse("@@collective-iconifiedcategory.css")
        css = view()
        self.assertTrue(".plone-config-group-1-category-1-1 " in css)
        self.assertTrue(
            "background: transparent url("
            "'http://nohost/plone/config/group-1/category-1-1/@@download')" in css
        )
        self.assertTrue(".plone-config-group-2-category-2-2 " in css)
        self.assertTrue(
            "background: transparent url("
            "'http://nohost/plone/config/group-2/category-2-2/@@download')" in css
        )
        self.assertTrue(".plone-config-group-2-category-2-3 " in css)
        self.assertTrue(
            "background: transparent url("
            "'http://nohost/plone/config/group-2/category-2-3/@@download')" in css
        )
        self.assertIn(
            "text/css", self.portal.REQUEST.response.getHeader("Content-Type")
        )

        # delete the config
        api.content.delete(self.portal["file_txt"])
        api.content.delete(self.portal["image"])
        api.content.delete(self.portal["config"])
        self.assertEqual(view(), "")

    def test_css_recooked(self):
        """The url of the bundle changes when a category is added/moved/removed
        (Plone 4 recooked the CSS registry)."""

        def _bundle_url():
            setattr(self.portal.REQUEST, REQUEST_CACHE_KEY, None)
            styles = StylesView(self.portal, self.portal.REQUEST, None)
            styles.update()
            return re.search(
                r'data-bundle="iconifiedcategory-dynamic" href="([^"]+)"',
                styles.render(),
            ).group(1)

        url1 = _bundle_url()
        self.assertTrue(url1.startswith("http://nohost/plone/++webresource++"))
        self.assertTrue(url1.endswith("/@@collective-iconifiedcategory.css"))
        # add a category
        category = api.content.create(
            type="ContentCategory",
            title="Brand new category",
            icon=self.icon,
            container=self.portal.config["group-1"],
        )
        url2 = _bundle_url()
        self.assertNotEqual(url1, url2)

        # rename the category so it is moved
        api.content.rename(obj=category, new_id="renamed_id")
        url3 = _bundle_url()
        self.assertNotEqual(url2, url3)

        # remove the category
        api.content.delete(category)
        url4 = _bundle_url()
        self.assertNotEqual(url3, url4)
        self.assertEqual(url1, url4)
