# -*- coding: utf-8 -*-

from collective.iconifiedcategory import DEFAULT_FILESIZE_LIMIT
from collective.iconifiedcategory.config import get_categorized_childs_infos_columns_threshold
from collective.iconifiedcategory.config import get_filesizelimit
from collective.iconifiedcategory.config import get_sort_categorized_tab
from collective.iconifiedcategory.config import set_categorized_childs_infos_columns_threshold
from collective.iconifiedcategory.config import set_filesizelimit
from collective.iconifiedcategory.config import set_sort_categorized_tab
from collective.iconifiedcategory.tests.base import BaseTestCase


class TestConfig(BaseTestCase):

    def test_registry_get_and_set(self):
        # sort_categorized_tab
        self.assertTrue(get_sort_categorized_tab())
        set_sort_categorized_tab(False)
        self.assertFalse(get_sort_categorized_tab())
        # categorized_childs_infos_columns_threshold
        self.assertEqual(get_categorized_childs_infos_columns_threshold(), 25)
        set_categorized_childs_infos_columns_threshold(50)
        self.assertEqual(get_categorized_childs_infos_columns_threshold(), 50)
        # sort_categorized_tab
        self.assertEqual(get_filesizelimit(), DEFAULT_FILESIZE_LIMIT)
        set_filesizelimit(25000)
        self.assertEqual(get_filesizelimit(), 25000)
