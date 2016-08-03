# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveIconifiedCategoryLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IIconifiedCategoryConfig(Interface):
    pass


class IIconifiedCategoryGroup(Interface):
    pass


class IIconifiedContent(Interface):
    pass


class IIconifiedInfos(Interface):
    pass


class IIconifiedPrintable(Interface):
    pass


class IIconifiedPreview(Interface):
    pass


class ICategorizedTable(Interface):
    pass


class ICategorizedPrint(ICategorizedTable):
    pass


class ICategorizedConfidential(ICategorizedTable):
    pass


class IIconifiedCategorySubtyper(Interface):

    have_categorized_elements = schema.Bool(
        u'Is current object contains categorized elements',
        readonly=True,
    )


# Events

class IIconifiedChangedEvent(IObjectEvent):

    old_value = Attribute("The old value")
    new_value = Attribute("The new value")


class IIconifiedPrintChangedEvent(IIconifiedChangedEvent):
    pass


class IIconifiedConfidentialChangedEvent(IIconifiedChangedEvent):
    pass
