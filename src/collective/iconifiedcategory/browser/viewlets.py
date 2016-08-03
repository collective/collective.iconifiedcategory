# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone import api
from plone.app.layout.viewlets import common as base
from zope.component import getMultiAdapter

from collective.iconifiedcategory.interfaces import IIconifiedContent
from collective.iconifiedcategory.interfaces import IIconifiedPreview


class CategorizedChildViewlet(base.ViewletBase):

    def update(self):
        super(CategorizedChildViewlet, self).update()
        self.categorized_elements = self.get_categorized_elements()

    def can_view(self):
        return ('categorized_elements' in self.context.__dict__ and
                len(self.categorized_elements) > 0)

    def has_preview(self, element):
        """Verify if the element has a preview for collective.documentviewer"""
        return IIconifiedPreview(element).has_preview

    @property
    def _categorized_elements(self):
        return getattr(self.context, 'categorized_elements', {})

    def get_categorized_elements(self):
        elements = []
        for uid, element in self._categorized_elements.items():
            brain = api.content.find(context=self.context, UID=uid)
            if not brain:
                continue
            adapter = getMultiAdapter((brain[0], self.request),
                                      IIconifiedContent)
            if adapter.can_view() is True:
                elements.append(element)
        return sorted(elements, key=lambda x: x['category_title'])

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
