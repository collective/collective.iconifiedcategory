# -*- coding: utf-8 -*-

from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings
from plone import api


def get_sort_categorized_tab():
    return api.portal.get_registry_record(
        'sort_categorized_tab', interface=IIconifiedCategorySettings)


def get_categorized_childs_infos_columns_threshold():
    return api.portal.get_registry_record(
        'categorized_childs_infos_columns_threshold', interface=IIconifiedCategorySettings)


def get_filesizelimit():
    return api.portal.get_registry_record(
        'filesizelimit', interface=IIconifiedCategorySettings)


def set_sort_categorized_tab(value):
    return api.portal.set_registry_record(
        'sort_categorized_tab', value, interface=IIconifiedCategorySettings)


def set_categorized_childs_infos_columns_threshold(value):
    return api.portal.set_registry_record(
        'categorized_childs_infos_columns_threshold', value, interface=IIconifiedCategorySettings)


def set_filesizelimit(value):
    return api.portal.set_registry_record(
        'filesizelimit', value, interface=IIconifiedCategorySettings)
