# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope.interface import Interface
from zope import schema
from z3c.form.form import Form
from z3c.form import button
from z3c.form import field
from plone.z3cform.layout import FormWrapper
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.iconifiedcategory import _


class IConfidential(Interface):

    confidential_group = schema.Choice(
        title=_(u'Confidential group'),
        vocabulary='plone.app.vocabularies.Groups',
        required=True,
    )


class ConfidentialForm(Form):
    fields = field.Fields(IConfidential)
    ignoreContext = True

    @property
    def action(self):
        return u'{0}/@@iconified-confidential'.format(self.context)

    @button.buttonAndHandler(_(u'Confirm'))
    def handleApply(self, action):
        """This code will never be called"""
        pass


class ConfidentialFormView(FormWrapper):
    form = ConfidentialForm
    index = ViewPageTemplateFile('templates/confidential_form.pt')
