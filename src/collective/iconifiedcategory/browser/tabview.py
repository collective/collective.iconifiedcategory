# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Products.Five import BrowserView
from plone import api
from z3c.table.table import Table
from z3c.table import column
from zope.interface import implements
from zope.interface import alsoProvides

from collective.iconifiedcategory import _
from collective.iconifiedcategory.interfaces import ICategorizedTable
from collective.iconifiedcategory.interfaces import ICategorizedPrint
from collective.iconifiedcategory.interfaces import ICategorizedConfidential


class CategorizedTabView(BrowserView):

    def table_render(self):
        table = CategorizedTable(self.context, self.request)
        alsoProvides(table, ICategorizedPrint)
        alsoProvides(table, ICategorizedConfidential)
        table.update()
        return table.render()


class CategorizedContent(object):

    def __init__(self, brain, context):
        self._obj = brain.getObject()
        self._metadata = context.categorized_elements.get(self._obj.UID())

    def __getattr__(self, key):
        if key in self._metadata:
            return self._metadata.get(key)
        try:
            return getattr(self._obj, key)
        except AttributeError:
            return self.__getattribute__(key)


class CategorizedTable(Table):
    implements(ICategorizedTable)

    cssClasses = {'table': 'listing iconified-listing'}

    cssClassEven = u'odd'
    cssClassOdd = u'even'
    sortOn = 'table-number-0'

    @property
    def values(self):
        brains = api.content.find(
            context=self.context,
            depth=1,
        )
        return [CategorizedContent(b, self.context) for b in brains
                if b.content_category]

    def render(self):
        if not len(self.rows):
            return None
        return super(CategorizedTable, self).render()


class IconColumn(column.GetAttrColumn):
    header = u''
    cssClasses = {'td': 'iconified-icon'}
    weight = 10

    def renderCell(self, obj):
        return u'<img src="{0}" alt="{1}" title="{1}" />'.format(
            obj.icon_url,
            obj.category_title,
        )


class TitleColumn(column.GetAttrColumn):
    header = _(u'Title')
    cssClasses = {'td': ''}
    weight = 20
    attrName = 'title'

    def renderCell(self, obj):
        return u'<a href="{0}" alt="{1}" title="{1}">{1}</a>'.format(
            obj.absolute_url,
            getattr(obj, self.attrName),
        )


class IconClickableColumn(column.GetAttrColumn):
    action_view = ''

    def get_url(self, obj):
        return '{0}/@@{1}'.format(obj.absolute_url, self.action_view)

    def renderCell(self, obj):
        cls = getattr(obj, self.attrName, False) and ' active' or ''
        link = (u'<a href="{0}" class="iconified-action{1}" alt="{2}" '
                u'title="{2}"></a>')
        return link.format(
            self.get_url(obj),
            cls,
            self.header,
        )


class PrintColumn(IconClickableColumn):
    header = _(u'To be printed')
    cssClasses = {'td': 'iconified-print'}
    weight = 30
    attrName = 'to_print'
    action_view = 'iconified-print'


class ConfidentialColumn(IconClickableColumn):
    header = _(u'Confidential')
    cssClasses = {'td': 'iconified-confidential'}
    weight = 40
    attrName = 'confidential'
    action_view = 'iconified-confidential'
