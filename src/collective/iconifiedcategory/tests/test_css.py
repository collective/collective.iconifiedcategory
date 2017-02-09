# -*- coding: utf-8 -*-

from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api


class TestIconifiedCategoryCSS(BaseTestCase):

    def test__call__(self):
        view = self.portal.restrictedTraverse('@@collective-iconifiedcategory.css')
        css = view()
        self.assertTrue(".config-group-1-category-1-1 " in css)
        self.assertTrue(u"background: transparent url("
                        u"'http://nohost/plone/config/group-1/category-1-1/@@download/icon/ic\xf4ne1.png')"
                        in css)
        self.assertTrue(".config-group-2-category-2-2 " in css)
        self.assertTrue(u"background: transparent url("
                        u"'http://nohost/plone/config/group-2/category-2-2/@@download/icon/ic\xf4ne2.png')"
                        in css)
        self.assertTrue(".config-group-2-category-2-3 " in css)
        self.assertTrue(u"background: transparent url("
                        u"'http://nohost/plone/config/group-2/category-2-3/@@download/icon/ic\xf4ne3.png')"
                        in css)

        # delete the config
        api.content.delete(self.portal['file'])
        api.content.delete(self.portal['image'])
        api.content.delete(self.portal['config'])
        self.assertEqual(view(), '')

    def test_css_recooked(self):
        """portal_css is recooked when a category is added/moved/removed."""
        # portal_css is cooked, the collective-iconfiedcategory.css is stored with ploneCustom, get the key
        cachekey1 = [k for k, v in self.portal.portal_css.concatenatedResourcesByTheme['Plone Default'].items()
                     if 'collective-iconifiedcategory.css' in v and k.startswith('ploneCustom')][0]

        # add a category, css resources is cooked
        category = api.content.create(
            type='ContentCategory',
            title='Brand new category',
            icon=self.icon,
            container=self.portal.config['group-1'],
        )
        cachekey2 = [k for k, v in self.portal.portal_css.concatenatedResourcesByTheme['Plone Default'].items()
                     if 'collective-iconifiedcategory.css' in v and k.startswith('ploneCustom')][0]
        self.assertNotEqual(cachekey1, cachekey2)

        # rename the category so it is moved
        category_parent = category.aq_inner.aq_parent
        category_parent.manage_renameObject(category.getId(), 'renamed_id')
        cachekey3 = [k for k, v in self.portal.portal_css.concatenatedResourcesByTheme['Plone Default'].items()
                     if 'collective-iconifiedcategory.css' in v and k.startswith('ploneCustom')][0]
        self.assertNotEqual(cachekey2, cachekey3)

        # remove the category
        api.content.delete(category)
        cachekey4 = [k for k, v in self.portal.portal_css.concatenatedResourcesByTheme['Plone Default'].items()
                     if 'collective-iconifiedcategory.css' in v and k.startswith('ploneCustom')][0]
        self.assertNotEqual(cachekey3, cachekey4)
