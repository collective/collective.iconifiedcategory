# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import testing
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestVocabularies(unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def _check_category_vocabulary(self, vocabulary):
        """ """
        terms = [t.title for t in vocabulary]
        self.assertEqual(2 * 3 * 3, len(terms))
        categories = [
            'Category 1-3',
            'Category 2-3',
            'Category 1-2',
            'Category 2-2',
            'Category 1-1',
            'Category 2-1',
        ]
        self.assertListEqual(
            [t for t in terms if t.startswith('Category')],
            categories,
        )
        subcategories = [
            'Subcategory 1-3-2', 'Subcategory 1-3-1',
            'Subcategory 2-3-2', 'Subcategory 2-3-1',
            'Subcategory 1-2-2', 'Subcategory 1-2-1',
            'Subcategory 2-2-2', 'Subcategory 2-2-1',
            'Subcategory 1-1-2', 'Subcategory 1-1-1',
            'Subcategory 2-1-2', 'Subcategory 2-1-1',
        ]
        self.assertListEqual(
            [t for t in terms if t.startswith('Subcategory')],
            subcategories,
        )

    def test_category_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.categories',
        )
        vocabulary = vocabulary(self.portal)
        self._check_category_vocabulary(vocabulary)

    def test_category_vocabulary_use_category_uid_as_token(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.categories',
        )
        vocabulary = vocabulary(self.portal, use_category_uid_as_token=True)
        self._check_category_vocabulary(vocabulary)

    def test_category_title_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.category_titles',
        )
        terms = [t.title for t in vocabulary(self.portal)]
        self.assertEqual(6, len(terms))
        expected = [
            'Category 1-1', 'Category 1-2', 'Category 1-3',
            'Category 2-1', 'Category 2-2', 'Category 2-3',
        ]
        self.assertListEqual(sorted(expected), sorted(terms))

        # add some predefined_title to some subcategories
        subcat = self.portal.config['group-1']['category-1-1']['subcategory-1-1-1']
        self.assertIsNone(subcat.predefined_title)
        subcat.predefined_title = u'Some predefined title'
        notify(ObjectModifiedEvent(subcat))
        terms = [t.title for t in vocabulary(self.portal)]
        self.assertEqual(7, len(terms))
        expected = [
            'Category 1-1', u'Some predefined title',
            'Category 1-2', 'Category 1-3',
            'Category 2-1', 'Category 2-2', 'Category 2-3',
        ]
        self.assertListEqual(sorted(expected), sorted(terms))

    def test_category_title_only_pdf_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.categories',
        )
        # change only_pdf to True for a category and a subcategory
        cat = self.portal.config['group-1']['category-1-1']
        cat.only_pdf = True
        subcat = self.portal.config['group-1']['category-1-1']['subcategory-1-1-1']
        subcat.only_pdf = True

        terms = [t.title for t in vocabulary(self.portal)]
        self.assertEqual(
            terms,
            ['Category 1-3', 'Subcategory 1-3-2', 'Subcategory 1-3-1',
             'Category 2-3', 'Subcategory 2-3-2', 'Subcategory 2-3-1',
             'Category 1-2', 'Subcategory 1-2-2', 'Subcategory 1-2-1',
             'Category 2-2', 'Subcategory 2-2-2', 'Subcategory 2-2-1',
             'Category 1-1 [PDF!]', 'Subcategory 1-1-2', 'Subcategory 1-1-1 [PDF!]',
             'Category 2-1', 'Subcategory 2-1-2', 'Subcategory 2-1-1'])
