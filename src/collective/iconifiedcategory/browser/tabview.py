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
from zope.i18n import translate
from zope.interface import implements
from zope.interface import alsoProvides

from collective.iconifiedcategory import _
from collective.iconifiedcategory import utils
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
        self._obj = brain
        self._metadata = context.categorized_elements.get(brain.UID)

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


class TitleColumn(column.GetAttrColumn):
    header = _(u'Title')
    weight = 20
    attrName = 'title'

    def renderCell(self, obj):
        content = (u'<a href="{link}" alt="{title}" title="{title}">'
                   u'<img src="{icon}" alt="{category}" title="{category}" />'
                   u' {title}</a>')
        return content.format(
            link=obj.absolute_url,
            title=getattr(obj, self.attrName).decode('utf-8'),
            icon=obj.icon_url,
            category=obj.category_title,
        )


class CategoryColumn(column.GetAttrColumn):
    header = _(u'Category')
    weight = 30
    attrName = 'category_title'


class AuthorColumn(column.GetAttrColumn):
    header = _(u'Author')
    weight = 40

    def renderCell(self, obj):
        return obj.Creator


class CreationDateColumn(column.GetAttrColumn):
    header = _(u'Creation date')
    weight = 50

    def renderCell(self, obj):
        return api.portal.get_localized_time(
            datetime=obj.creation_date,
            long_format=True,
        )


class LastModificationColumn(column.GetAttrColumn):
    header = _(u'Last modification')
    weight = 60

    def renderCell(self, obj):
        if obj.creation_date == obj.modification_date:
            return ''
        return api.portal.get_localized_time(
            datetime=obj.modification_date,
            long_format=True,
        )


class FilesizeColumn(column.GetAttrColumn):
    header = _(u'Filesize')
    weight = 70

    def renderCell(self, obj):
        if getattr(obj, 'filesize', None) is None:
            return ''
        return utils.calculate_filesize(obj.filesize)


class IconClickableColumn(column.GetAttrColumn):
    action_view = ''

    def get_url(self, obj):
        if self.is_deactivated(obj):
            return '#'
        return '{0}/@@{1}'.format(obj.absolute_url, self.get_action_view(obj))

    def get_action_view(self, obj):
        return self.action_view

    def alt(self, obj):
        return self.header

    def is_deactivated(self, obj):
        return getattr(obj, self.attrName, False) is None

    def css_class(self, obj):
        if self.is_deactivated(obj):
            return ' deactivated'
        return getattr(obj, self.attrName, False) and ' active' or ''

    def renderCell(self, obj):
        link = (u'<a href="{0}" class="iconified-action{1}" alt="{2}" '
                u'title="{2}"></a>')
        return link.format(
            self.get_url(obj),
            self.css_class(obj),
            self.alt(obj),
        )


class PrintColumn(IconClickableColumn):
    header = _(u'To be printed')
    cssClasses = {'td': 'iconified-print'}
    weight = 80
    attrName = 'to_print'
    action_view = 'iconified-print'

    def alt(self, obj):
        return translate(
            utils.print_message(obj),
            domain='collective.iconifiedcategory',
            context=self.table.request,
        )


class ConfidentialColumn(IconClickableColumn):
    header = _(u'Confidential')
    cssClasses = {'td': 'iconified-confidential'}
    weight = 90
    attrName = 'confidential'
    action_view = 'iconified-confidential'

    def alt(self, obj):
        return translate(
            utils.confidential_message(obj),
            domain='collective.iconifiedcategory',
            context=self.table.request,
        )
