# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.iconifiedcategory.interfaces import ICollectiveIconifiedCategoryLayer
from collective.iconifiedcategory.testing import (
    COLLECTIVE_ICONIFIED_CATEGORY_INTEGRATION_TESTING,
)
from plone import api
from plone.base.utils import get_installer
from plone.browserlayer import utils as browserlayer_utils

import unittest


TYPES = (
    "ContentCategoryConfiguration",
    "ContentCategoryGroup",
    "ContentCategory",
    "ContentSubcategory",
)
INDEXES = ("content_category_uid", "enabled")
RECORDS = (
    "sort_categorized_tab",
    "categorized_childs_infos_columns_threshold",
    "filesizelimit",
)
RECORD_PREFIX = "collective.iconifiedcategory.interfaces.IIconifiedCategorySettings."
ACTIONS = (
    "object/iconifiedcategory",
    "object_buttons/update_categorized_elements",
    "object_buttons/update_and_sort_categorized_elements",
)


def _actions():
    portal_actions = api.portal.get_tool("portal_actions")
    return [
        path
        for path in ACTIONS
        if path.split("/")[1] in portal_actions[path.split("/")[0]].objectIds()
    ]


def _configlets():
    return [a.getId() for a in api.portal.get_tool("portal_controlpanel").listActions()]


def _records():
    registry = api.portal.get_tool("portal_registry")
    return [name for name in RECORDS if RECORD_PREFIX + name in registry]


class TestSetup(unittest.TestCase):
    """Test that collective.iconifiedcategory is properly installed."""

    layer = COLLECTIVE_ICONIFIED_CATEGORY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.installer = get_installer(self.portal, self.request)

    def test_product_installed(self):
        """Test if collective.iconifiedcategory is installed."""
        self.assertTrue(
            self.installer.is_product_installed("collective.iconifiedcategory")
        )

    def test_browserlayer(self):
        """Test that ICollectiveIconifiedCategoryLayer is registered."""
        from collective.iconifiedcategory.interfaces import (
            ICollectiveIconifiedCategoryLayer,
        )
        from plone.browserlayer import utils

        self.assertIn(ICollectiveIconifiedCategoryLayer, utils.registered_layers())

    def test_types(self):
        portal_types = api.portal.get_tool("portal_types")
        self.assertEqual(
            [t for t in TYPES if t in portal_types.objectIds()], list(TYPES)
        )

    def test_catalog(self):
        catalog = api.portal.get_tool("portal_catalog")
        self.assertEqual(
            catalog.Indexes["content_category_uid"].meta_type, "KeywordIndex"
        )
        self.assertEqual(catalog.Indexes["enabled"].meta_type, "BooleanIndex")
        self.assertIn("content_category_uid", catalog.schema())

    def test_registry(self):
        self.assertEqual(_records(), list(RECORDS))

    def test_actions(self):
        self.assertEqual(_actions(), list(ACTIONS))

    def test_controlpanel(self):
        self.assertIn("iconifiedcategory", _configlets())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_ICONIFIED_CATEGORY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.installer = get_installer(self.portal, self.request)
        self.installer.uninstall_product("collective.iconifiedcategory")

    def test_product_uninstalled(self):
        """Test if collective.iconifiedcategory is cleanly uninstalled."""
        self.assertFalse(
            self.installer.is_product_installed("collective.iconifiedcategory")
        )

    def test_browserlayer(self):
        self.assertNotIn(
            ICollectiveIconifiedCategoryLayer, browserlayer_utils.registered_layers()
        )

    def test_types(self):
        portal_types = api.portal.get_tool("portal_types")
        self.assertEqual([t for t in TYPES if t in portal_types.objectIds()], [])

    def test_catalog(self):
        # Plone 6 uninstall profile removes the catalog indexes and columns
        catalog = api.portal.get_tool("portal_catalog")
        self.assertEqual([i for i in INDEXES if i in catalog.indexes()], [])
        self.assertEqual([c for c in INDEXES if c in catalog.schema()], [])

    def test_registry(self):
        # Plone 6 uninstall profile removes the registry records
        self.assertEqual(_records(), [])

    def test_actions(self):
        self.assertEqual(_actions(), [])

    def test_controlpanel(self):
        self.assertNotIn("iconifiedcategory", _configlets())
