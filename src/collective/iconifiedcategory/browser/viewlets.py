# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone.app.layout.viewlets import common as base


class CategorizedChildViewlet(base.ViewletBase):

    def can_view(self):
        return 'categorized_elements' in self.context.__dict__

    @property
    def categorized_elements(self):
        return sorted(
            self.context.categorized_elements.values(),
            key=lambda x: x['category_title'],
        )

    def infos(self):
        infos = {e['category_uid']: {'id': e['category_id'],
                                     'title': e['category_title'],
                                     'counts': 0,
                                     'icon': e['icon_url']}
                 for e in self.categorized_elements}
        for key, element in infos.items():
            element['counts'] = len([e for e in self.categorized_elements
                                     if e['category_uid'] == key])
        return infos.values()
