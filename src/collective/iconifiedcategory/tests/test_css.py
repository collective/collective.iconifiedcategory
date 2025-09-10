# -*- coding: utf-8 -*-

from collective.iconifiedcategory.content.events import _cookCssResources
from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api
from plone.app.theming.interfaces import IThemeSettings
from plone.resource.interfaces import IResourceDirectory
from Products.CMFPlone.resources.browser.resource import REQUEST_CACHE_KEY
from Products.CMFPlone.resources.browser.resource import StylesView
from zope.component import getUtility

import re
import transaction


class TestIconifiedCategoryCSS(BaseTestCase):

    def setUp(self):
        super(TestIconifiedCategoryCSS, self).setUp()
        api.portal.set_registry_record(
            interface=IThemeSettings,
            name="custom_css",
            value=" ",
        )

    def _bundle_infos(self):
        styles = StylesView(self.portal, self.layer["request"], None)
        styles.update()
        html = styles.render()
        m = re.search(r'<link[^>]+data-bundle="plonecustomcss"[^>]+>', html)
        self.assertIsNotNone(m)
        tag = m.group(0)
        href_m = re.search(r'href="([^"]+)"', tag)
        href = href_m.group(1)
        hash_m = re.search(r"\+\+webresource\+\+([^/]+)/", href)
        self.assertIsNotNone(hash_m)
        bundle_hash = hash_m.group(1)
        return href, bundle_hash

    def _read_dynamic_css(self):
        persistent = getUtility(IResourceDirectory, name="persistent")
        pkgdir = persistent["collective.iconifiedcategory"]
        return pkgdir.readFile("collective-iconifiedcategory.css").decode("utf-8")

    def test_css_file_is_generated(self):
        _cookCssResources(self.portal)
        css = self._read_dynamic_css()
        self.assertIn(".plone-config-group-1-category-1-1 ", css)
        self.assertIn("http://nohost/plone/config/group-1/category-1-1/@@download", css)
        self.assertIn(".plone-config-group-2-category-2-2 ", css)
        self.assertIn("http://nohost/plone/config/group-2/category-2-2/@@download", css)
        self.assertIn(".plone-config-group-2-category-2-3 ", css)
        self.assertIn("http://nohost/plone/config/group-2/category-2-3/@@download", css)
        api.content.delete(self.portal["file_txt"])
        api.content.delete(self.portal["image"])
        api.content.delete(self.portal["config"])
        _cookCssResources(self.portal)
        css = self._read_dynamic_css()
        self.assertEqual(css.strip(), "")

    def test_bundle_url_changes_on_cook(self):
        _cookCssResources(self.portal)
        transaction.commit()
        href1, hash1 = self._bundle_infos()
        self.assertIn("++webresource++", href1)
        api.content.create(
            type="ContentCategory",
            title="Brand new category",
            icon=self.icon,
            container=self.portal.config["group-1"],
        )
        _cookCssResources(self.portal)
        transaction.commit()
        setattr(self.request, REQUEST_CACHE_KEY, None)
        href2, hash2 = self._bundle_infos()
        self.assertNotEqual(hash1, hash2)
