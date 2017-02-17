# -*- coding: utf-8 -*-

from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api


class TestIconifiedCategoryCSS(BaseTestCase):

    def test__call__(self):
        view = self.portal.restrictedTraverse('@@collective-iconifiedcategory.css')
        css = view()
        self.assertTrue(".config-group-1-category-1-1 " in css)
        self.assertTrue(u"background: transparent url("
                        u"'http://nohost/plone/config/group-1/category-1-1/@@download')"
                        in css)
        self.assertTrue(".config-group-2-category-2-2 " in css)
        self.assertTrue(u"background: transparent url("
                        u"'http://nohost/plone/config/group-2/category-2-2/@@download')"
                        in css)
        self.assertTrue(".config-group-2-category-2-3 " in css)
        self.assertTrue(u"background: transparent url("
                        u"'http://nohost/plone/config/group-2/category-2-3/@@download')"
                        in css)

        # delete the config
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])
        api.content.delete(self.portal['config'])
        self.assertEqual(view(), '')

    def test_css_recooked(self):
        """portal_css is recooked when a category is added/moved/removed."""
        def _current_css_cachekey():
            cachekey = [k for k, v in self.portal.portal_css.concatenatedResourcesByTheme['Plone Default'].items()
                        if 'collective-iconifiedcategory.css' in v and '-cachekey-' in k][0]
            return cachekey
        # portal_css is cooked, the collective-iconfiedcategory.css is stored in a cachekey cooked css
        cachekey1 = _current_css_cachekey()
        # add a category, css resources are cooked again
        category = api.content.create(
            type='ContentCategory',
            title='Brand new category',
            icon=self.icon,
            container=self.portal.config['group-1'],
        )
        cachekey2 = _current_css_cachekey()
        self.assertNotEqual(cachekey1, cachekey2)

        # rename the category so it is moved, css resources are cooked again
        category_parent = category.aq_inner.aq_parent
        category_parent.manage_renameObject(category.getId(), 'renamed_id')
        cachekey3 = _current_css_cachekey()
        self.assertNotEqual(cachekey2, cachekey3)

        # remove the category, css resources are cooked again
        api.content.delete(category)
        cachekey4 = _current_css_cachekey()
        self.assertNotEqual(cachekey3, cachekey4)
