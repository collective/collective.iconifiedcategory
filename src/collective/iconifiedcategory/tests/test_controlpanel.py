# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective.iconifiedcategory.config import (
    get_categorized_childs_infos_columns_threshold,
)
from collective.iconifiedcategory.config import get_filesizelimit
from collective.iconifiedcategory.config import get_sort_categorized_tab
from collective.iconifiedcategory.tests.base import BaseTestCase
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from Products.statusmessages.interfaces import IStatusMessage


class TestIconifiedCategorySettingsView(BaseTestCase):

    def test__call__(self):
        rendered = self.portal.restrictedTraverse("@@iconifiedcategory-controlpanel")()
        self.assertIn("Iconified Category Settings", rendered)
        for name in (
            "sort_categorized_tab",
            "categorized_childs_infos_columns_threshold",
            "filesizelimit",
        ):
            self.assertIn("form.widgets.{0}".format(name), rendered)
        # Manage portal is required
        login(self.portal, TEST_USER_NAME)
        self.assertRaises(
            Unauthorized,
            self.portal.restrictedTraverse,
            "@@iconifiedcategory-controlpanel",
        )


class TestIconifiedCategorySettingsEditForm(BaseTestCase):

    def test_handleSave(self):
        request = self.portal.REQUEST
        request.form.update(
            {
                "form.widgets.sort_categorized_tab-empty-marker": "1",
                "form.widgets.categorized_childs_infos_columns_threshold": "40",
                "form.widgets.filesizelimit": "25000",
                "form.buttons.save": "Save",
            }
        )
        self.portal.restrictedTraverse("@@iconifiedcategory-controlpanel")()
        self.assertFalse(get_sort_categorized_tab())
        self.assertEqual(get_categorized_childs_infos_columns_threshold(), 40)
        self.assertEqual(get_filesizelimit(), 25000)
        self.assertEqual(
            [m.message for m in IStatusMessage(request).show()], ["Changes saved."]
        )
