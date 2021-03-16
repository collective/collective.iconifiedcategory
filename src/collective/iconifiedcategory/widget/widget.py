# -*- coding: utf-8 -*-

from z3c.form import interfaces
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IChoice


class ICategoryTitleWidget(Interface):
    """Marker interface for hidden select widget"""


class CategoryTitleWidget(SelectWidget):
    implements(ICategoryTitleWidget, interfaces.ISelectWidget)

    @property
    def placeholder(self):
        return self.field.placeholder

    @property
    def select2_id(self):
        return self.id.replace('-', '_')


@adapter(IChoice, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def CategoryTitleFieldWidget(field, request):
    """IFieldWidget factory for CategoryTitleWidget"""
    return FieldWidget(field, CategoryTitleWidget(request))
