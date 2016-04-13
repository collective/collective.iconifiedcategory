# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest

from collective.iconifiedcategory import testing


class TestVocabularies(unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_category_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.categories',
        )
        vocabulary = vocabulary(self.portal)
        terms = [t.title for t in vocabulary]
        self.assertEqual(2 * 3 * 3, len(terms))
        categories = [
            'Category 1-1', 'Category 1-2', 'Category 1-3',
            'Category 2-1', 'Category 2-2', 'Category 2-3',
        ]
        self.assertListEqual(
            sorted([t for t in terms if t.startswith('Category')]),
            sorted(categories),
        )
        subcategories = [
            'Subcategory 1-1-1', 'Subcategory 1-1-2',
            'Subcategory 1-2-1', 'Subcategory 1-2-2',
            'Subcategory 1-3-1', 'Subcategory 1-3-2',
            'Subcategory 2-1-1', 'Subcategory 2-1-2',
            'Subcategory 2-2-1', 'Subcategory 2-2-2',
            'Subcategory 2-3-1', 'Subcategory 2-3-2',
        ]
        self.assertListEqual(
            sorted([t for t in terms if t.startswith('Subcategory')]),
            sorted(subcategories),
        )

    def test_category_title_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.category_titles',
        )
        vocabulary = vocabulary(self.portal)
        terms = [t.title for t in vocabulary]
        self.assertEqual(6, len(terms))
        categories = [
            'Category 1-1', 'Category 1-2', 'Category 1-3',
            'Category 2-1', 'Category 2-2', 'Category 2-3',
        ]
        self.assertListEqual(sorted(categories), sorted(terms))
