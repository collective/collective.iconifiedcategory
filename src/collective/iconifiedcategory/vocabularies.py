# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone import api
from zope.schema.vocabulary import SimpleVocabulary

from collective.iconifiedcategory import utils


class CategoryVocabulary(object):

    def __call__(self, context):
        terms = []
        categories = utils.get_categories(context, the_objects=True)
        for category in categories:
            category_id = utils.calculate_category_id(category)
            terms.append(SimpleVocabulary.createTerm(
                category_id,
                category_id,
                category.Title(),
            ))
            subcategories = api.content.find(
                context=category,
                object_provides='collective.iconifiedcategory.content.subcategory.ISubcategory',
                enabled=True,
            )
            for subcategory in subcategories:
                subcategory_id = utils.calculate_category_id(subcategory.getObject())
                terms.append(SimpleVocabulary.createTerm(
                    subcategory_id,
                    subcategory_id,
                    subcategory.Title,
                ))
        return SimpleVocabulary(terms)


class CategoryTitleVocabulary(object):

    def __call__(self, context):
        terms = []
        terms = []
        categories = utils.get_categories(context, the_objects=True)
        for category in categories:
            category_id = utils.calculate_category_id(category)
            if category.predefined_title:
                terms.append(SimpleVocabulary.createTerm(
                    category_id,
                    category_id,
                    category.predefined_title,
                ))
            subcategories = api.content.find(
                context=category,
                object_provides='collective.iconifiedcategory.content.subcategory.ISubcategory',
                enabled=True,
            )
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
