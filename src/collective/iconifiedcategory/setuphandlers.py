# -*- coding: utf-8 -*-

from plone import api
from plone import namedfile

import os


def post_install(context):
    """Post install script"""
    if context.readDataFile('collectivecategorize_default.txt') is None:
        return


def post_test_install(context):
    if context.readDataFile('collectivecategorize_testing.txt') is None:
        return
    create_config(context)


def create_config(context):
    portal = api.portal.get()
    current_path = os.path.dirname(__file__)
    config = api.content.create(
        type='ContentCategoryConfiguration',
        title='Config',
        container=portal,
    )
    groups = []
    for idx in range(1, 3):
        obj = api.content.create(
            type='ContentCategoryGroup',
            title='Group {0}'.format(idx),
            container=config,
            to_be_printed_activated=True
        )
        groups.append(obj)
    for group_idx, group in enumerate(groups):
        for cat_idx in reversed(range(1, 4)):
            filename = u'icône{0}.png'.format(cat_idx)
            f = open(os.path.join(current_path, 'tests', filename), 'r')
            icon = namedfile.NamedBlobFile(f.read(), filename=filename)
            title = 'Category {0}-{1}'.format(group_idx + 1, cat_idx)
            category = api.content.create(
                type='ContentCategory',
                title=title,
                container=group,
                icon=icon,
                predefined_title=title,
            )
            for idx in reversed(range(1, 3)):
                api.content.create(
                    type='ContentSubcategory',
                    title='Subcategory {0}-{1}-{2}'.format(
                        group_idx + 1,
                        cat_idx,
                        idx,
                    ),
                    container=category,
                )
