# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope.schema.vocabulary import SimpleVocabulary
from plone import api

from collective.iconifiedcategory import utils


class CategoryVocabulary(object):

    def __call__(self, context):
        terms = []
        categories = utils.get_categories(context)
        for category in categories:
            obj = category._unrestrictedGetObject()
            category_id = utils.calculate_category_id(obj)
            terms.append(SimpleVocabulary.createTerm(
                category_id,
                category_id,
                category.Title,
            ))
            subcategories = api.content.find(
                context=obj,
                portal_type='ContentSubcategory',
                enabled=True
            )
            for subcategory in subcategories:
                terms.append(SimpleVocabulary.createTerm(
                    utils.format_id(category_id, subcategory.id),
                    utils.format_id(category_id, subcategory.id),
                    subcategory.Title,
                ))
        return SimpleVocabulary(terms)


class CategoryTitleVocabulary(object):

    def __call__(self, context):
        terms = []
        terms = []
        categories = utils.get_categories(context)
        for category in categories:
            obj = category._unrestrictedGetObject()
            category_id = utils.calculate_category_id(obj)
            if obj.predefined_title:
                terms.append(SimpleVocabulary.createTerm(
                    category_id,
                    category_id,
                    obj.predefined_title,
                ))
            subcategories = api.content.find(
                context=obj,
                portal_type='ContentSubcategory',
            )
            for subcategory in subcategories:
                obj = subcategory.getObject()
                if obj.predefined_title:
                    terms.append(SimpleVocabulary.createTerm(
                        utils.format_id(category_id, subcategory.id),
                        utils.format_id(category_id, subcategory.id),
                        obj.predefined_title,
                    ))
        return SimpleVocabulary(terms)
