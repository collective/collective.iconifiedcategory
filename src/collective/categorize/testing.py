# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.categorize


class CollectiveCategorizeLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=collective.categorize)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.categorize:default')


COLLECTIVE_CATEGORIZE_FIXTURE = CollectiveCategorizeLayer()


COLLECTIVE_CATEGORIZE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_CATEGORIZE_FIXTURE,),
    name='CollectiveCategorizeLayer:IntegrationTesting'
)


COLLECTIVE_CATEGORIZE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_CATEGORIZE_FIXTURE,),
    name='CollectiveCategorizeLayer:FunctionalTesting'
)


COLLECTIVE_CATEGORIZE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_CATEGORIZE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveCategorizeLayer:AcceptanceTesting'
)
