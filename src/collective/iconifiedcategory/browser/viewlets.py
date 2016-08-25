# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone.app.layout.viewlets import common as base

from collective.iconifiedcategory.utils import get_categorized_elements


class CategorizedChildViewlet(base.ViewletBase):

    def update(self):
        super(CategorizedChildViewlet, self).update()
        self.categorized_elements = get_categorized_elements(self.context,
                                                             sort_on='category_title')

    def can_view(self):
        return ('categorized_elements' in self.context.__dict__ and
                len(self.categorized_elements) > 0)

    def categories_infos(self):
        infos = {e['category_uid']: {'id': e['category_id'],
                                     'title': e['category_title'],
                                     'counts': 0,
                                     'icon': e['icon_url']}
                 for e in self.categorized_elements}
        for key, element in infos.items():
            element['counts'] = len([e for e in self.categorized_elements
                                     if e['category_uid'] == key])
        return infos.values()

    @property
    def categories_ids(self):
        return set([e['category_id'] for e in self.categorized_elements])

    def infos(self):
        infos = {e: [] for e in self.categories_ids}
        for element in self.categorized_elements:
            infos[element['category_id']].append(element)
        return infos
