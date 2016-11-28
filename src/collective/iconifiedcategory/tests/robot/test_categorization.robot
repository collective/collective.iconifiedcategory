# ============================================================================
# EXAMPLE ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s collective.iconifiedcategory -t test_categorization.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src collective.iconifiedcategory.testing.COLLECTIVE_ICONIFIED_CATEGORY_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/collective.iconifiedcategory/tests/robot/test_categorization.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a member I want to be able to log into the website
  [Documentation]  Example of a BDD-style (Behavior-driven development) test.
  Given a login form
   When I enter valid credentials
   Then I am logged in

Scenario: As an editor I want to be able to categorize content
  Given I am logged in as a Manager
   When I create a folder
    And I create a categorized document
    And I move to the parent
   Then I should have categorized elements
    And I delete the folder

Scenario: As an editor I want to be able to use categorized predefined titles
  Given I am logged in as a Manager
   When I create a folder
    And I go to the document creation
    And I select a category using predefined title
   Then I should have a predefined title
    And I delete the folder

Scenario: As an editor the predefined title does not erase an existing title
  Given I am logged in as a Manager
   When I create a folder
    And I go to the document creation
    And I select a category using predefined title
    And I set a title
   Then I edit the document again, the title should remain

Scenario: As an editor I can change the print status of a categorized content
  Given I am logged in as a Manager
   When I create a folder
    And I create a categorized document
    And I move to the parent
    And I move to the categorized elements tab
   Then I should change the print status
    And I delete the folder


*** Keywords *****************************************************************

I am logged in as a ${role}
  Enable autologin as  ${role}
  Go to  ${PLONE_URL}

Select a category
  [Arguments]  ${category}

  Focus  css=a.select2-choice
  Click Link  css=a.select2-choice
  Click Element  css=span.config-group-1-${category}

# --- Given ------------------------------------------------------------------

a login form
  Go To  ${PLONE_URL}/login_form
  Wait Until Page Contains  Login Name
  Wait Until Page Contains  Password


# --- WHEN -------------------------------------------------------------------

I enter valid credentials
  Input Text  __ac_name  admin
  Input Text  __ac_password  secret
  Click Button  Log in

I create a folder
  Go To  ${PLONE_URL}/++add++Folder
  Wait Until Page Contains  Title
  Input Text  form.widgets.IDublinCore.title  Folder
  Click Button  Save

I edit a folder
  Go To  ${PLONE_URL}/folder/edit
  Wait Until Page Contains  Title

I delete the folder
  Go To  ${PLONE_URL}/folder
  Wait Until Page Contains  Folder
  Click Delete Action

I go to the document creation
  Open Add New Menu
  Click Link  link=Page
  Wait Until Page Contains  Page

I create a categorized document
  I go to the document creation
  Select a category  category-1-2
  Wait Until Page Contains  Category 1-2
  Input Text  form.widgets.IDublinCore.title  DocumentTitle
  Click Button  Save
  Wait Until Page Contains  DocumentTitle
  Page Should Contain  Item created

I select a category using predefined title
  Select a category  category-1-3
  Wait Until Page Contains  Category 1-3

I set a title
  Input Text  form.widgets.IDublinCore.title  DocumentTitle
  Click Button  Save

I move to the parent
  Click Link  link=Folder
  Wait Until Page Contains  Folder
  Page Should Contain  Folder

I move to the categorized elements tab
  Click Link  link=Categorized elements
  Wait Until Page Contains  Categorized elements
  Page Should Contain  Title


# --- THEN -------------------------------------------------------------------

I am logged in
  Wait Until Page Contains  You are now logged in
  Page Should Contain  You are now logged in

I am on the folder view
  Wait Until Page Contains  Folder
  Page Should Contain  Element created

I should have categorized elements
  Page Should Contain  Categorized elements

I should have a predefined title
  Textfield Value Should Be  name=form.widgets.IDublinCore.title  Category 1-3
  Click Button  Save
  Wait Until Page Contains  Category 1-3
  Page Should Contain  Item created

I edit the document again, the title should remain
  Go To  ${PLONE_URL}/folder/documenttitle/edit
  Textfield Value Should Be  name=form.widgets.IDublinCore.title  DocumentTitle
  Click Button  Save
  Page Should Contain  DocumentTitle

I should change the print status
  Page Should Not Contain Element  css=td.iconified-print a.active
  Click Link  css=td.iconified-print a.iconified-action
  Wait Until Page Contains Element  css=td.iconified-print a.active
  Page Should Contain Element  css=td.iconified-print a.active
