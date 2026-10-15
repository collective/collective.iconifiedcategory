# -*- coding: utf-8 -*-

from collective.iconifiedcategory.tests.base import BaseTestCase
from plone import api
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestIndexes(BaseTestCase):

    def test_enabled(self):
        catalog = api.portal.get_tool("portal_catalog")
        category = self.config["group-1"]["category-1-1"]
        subcategory = category["subcategory-1-1-1"]
        self.assertEqual(
            len(
                catalog(
                    portal_type=["ContentCategory", "ContentSubcategory"], enabled=True
                )
            ),
            18,
        )
        self.assertEqual(len(catalog(enabled=False)), 0)
        category.enabled = False
        category.reindexObject()
        subcategory.enabled = False
        subcategory.reindexObject()
        self.assertEqual(
            sorted([b.UID for b in catalog(enabled=False)]),
            sorted([category.UID(), subcategory.UID()]),
        )

    def test_content_category_uid(self):
        catalog = api.portal.get_tool("portal_catalog")
        category = self.config["group-1"]["category-1-1"]
        subcategory = category["subcategory-1-1-1"]
        # file_txt uses category-1-1, image uses subcategory-1-1-1
        self.assertEqual(
            [b.getId for b in catalog(content_category_uid=category.UID())],
            ["file_txt"],
        )
        self.assertEqual(
            [b.getId for b in catalog(content_category_uid=subcategory.UID())],
            ["image"],
        )
        # also a metadata column
        brain = catalog(UID=self.portal["file_txt"].UID())[0]
        self.assertEqual(brain.content_category_uid, category.UID())
        # changing the category reindexes
        self.portal["file_txt"].content_category = "config_-_group-1_-_category-1-2"
        notify(ObjectModifiedEvent(self.portal["file_txt"]))
        self.assertEqual(
            [b.getId for b in catalog(content_category_uid=category.UID())], []
        )
        self.assertEqual(
            [
                b.getId
                for b in catalog(
                    content_category_uid=self.config["group-1"]["category-1-2"].UID()
                )
            ],
            ["file_txt"],
        )
