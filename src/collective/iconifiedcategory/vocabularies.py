# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import utils
from imio.helpers.content import find
from zope.schema.vocabulary import SimpleVocabulary


class CategoryVocabulary(object):

    def _get_categories(self, context, only_enabled=True):
        """Return categories to display in the vocabulary.
           This needs to return a list of category objects."""
        categories = utils.get_categories(context, the_objects=True, only_enabled=only_enabled)
        return categories

    def _get_subcategories(self, context, category, only_enabled=True):
        """Return subcategories for given category.
           This needs to return a list of subcategory brains."""
        query = {'object_provides': 'collective.iconifiedcategory.content.subcategory.ISubcategory'}
        if only_enabled:
            query['enabled'] = True
        subcategories = find(
            context=category,
            unrestricted=True,
            **query
        )
        return subcategories

    def __call__(self, context, use_category_uid_as_token=False, only_enabled=True):
        terms = []
        categories = self._get_categories(context, only_enabled=only_enabled)
        for category in categories:
            if use_category_uid_as_token:
                category_id = category.UID()
            else:
                category_id = utils.calculate_category_id(category)
            category_title = category.Title()
            if category.only_pdf:
                category_title = category_title + ' [PDF!]'
            terms.append(SimpleVocabulary.createTerm(
                category_id,
                category_id,
                category_title,
            ))
            subcategories = self._get_subcategories(context, category, only_enabled=only_enabled)
            for subcategory in subcategories:
                subcategory = subcategory.getObject()
                if use_category_uid_as_token:
                    subcategory_id = subcategory.UID()
                else:
                    subcategory_id = utils.calculate_category_id(subcategory)
                subcategory_title = subcategory.Title()
                if subcategory.only_pdf:
                    subcategory_title = subcategory_title + ' [PDF!]'
                terms.append(SimpleVocabulary.createTerm(
                    subcategory_id,
                    subcategory_id,
                    subcategory_title,
                ))
        return SimpleVocabulary(terms)


class EveryCategoryVocabulary(CategoryVocabulary):

    def __call__(self, context, use_category_uid_as_token=False, only_enabled=False):
        return super(EveryCategoryVocabulary, self).__call__(
            context,
            use_category_uid_as_token=use_category_uid_as_token,
            only_enabled=only_enabled)


class CategoryTitleVocabulary(CategoryVocabulary):

    def __call__(self, context, only_enabled=True):
        terms = []
        categories = self._get_categories(context, only_enabled=only_enabled)
        for category in categories:
            category_id = utils.calculate_category_id(category)
            if category.predefined_title:
                terms.append(SimpleVocabulary.createTerm(
                    category_id,
                    category_id,
                    category.predefined_title,
                ))
            subcategories = self._get_subcategories(context, category, only_enabled=only_enabled)
            for subcategory in subcategories:
                subcategory = subcategory.getObject()
                subcategory_id = utils.calculate_category_id(subcategory)
                if subcategory.predefined_title:
                    terms.append(SimpleVocabulary.createTerm(
                        subcategory_id,
                        subcategory_id,
                        subcategory.predefined_title,
                    ))
        return SimpleVocabulary(terms)


class EveryCategoryTitleVocabulary(CategoryTitleVocabulary):

    def __call__(self, context, only_enabled=False):
        return super(EveryCategoryTitleVocabulary, self).__call__(
            context,
            only_enabled=only_enabled)
