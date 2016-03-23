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
        )
        groups.append(obj)
    categories = []
    for group in groups:
        for idx in range(1, 4):
            filename = u'icon{0}.png'.format(idx)
            f = open(os.path.join(current_path, 'tests', filename), 'r')
            icon = namedfile.NamedBlobFile(f.read(), filename=filename)
            obj = api.content.create(
                type='ContentCategory',
                title='Category {0}'.format(idx),
                container=group,
                icon=icon,
            )
            categories.append(obj)
