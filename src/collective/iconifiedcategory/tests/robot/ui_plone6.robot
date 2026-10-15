*** Settings ***
Documentation  Plone 6 Classic UI keywords. Same keyword names and arguments as ui_plone4.robot.
...            Robot Framework 3.0 syntax: shared with the Plone 4.3 (Python 2) environment.
...            Selectors checked on Plone 6.1 (collective.contact.contactlist, collective.iconifiedcategory).
...            Category field: plone.app.z3cform Select2Widget (pat-select2, select2 3.5, same markup as Plone 4).
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Library  Remote  ${PLONE_URL}/RobotRemote


*** Variables ***
${MODAL}  css=.modal-dialog
${ERROR_PAGE_TEXT}  there seems to be an error
${NOT_FOUND_TEXT}  This page does not seem to exist
# category field of the IIconifiedCategorization behavior (plone.app.z3cform Select2Widget)
${CATEGORY_FIELD}  css=#formfield-form-widgets-IIconifiedCategorization-content_category


*** Keywords ***
Log in with the login form
    [Documentation]  Real login (creates the user folder), unlike autologin
    [Arguments]  ${username}  ${password}
    Disable autologin
    Go to  ${PLONE_URL}/login
    Input text  css=#__ac_name  ${username}
    Input password  css=#__ac_password  ${password}
    Click button  css=#buttons-login
    Wait until page contains element  css=#personaltools-menulink

Click the content action
    [Documentation]  Item of the Actions menu (object_buttons), by action id
    [Arguments]  ${action_id}
    Click element  css=#plone-contentmenu-actions > a
    Wait until element is visible  css=#plone-contentmenu-actions-${action_id}
    Click element  css=#plone-contentmenu-actions-${action_id}

The content action is available
    [Arguments]  ${action_id}  ${expected}=${True}
    Click element  css=#plone-contentmenu-actions > a
    Wait until element is visible  css=#plone-contentmenu-actions ul
    Run keyword if  ${expected}
    ...  Page should contain element  css=#plone-contentmenu-actions-${action_id}
    ...  ELSE  Page should not contain element  css=#plone-contentmenu-actions-${action_id}

Open the add menu
    Click element  css=#plone-contentmenu-factories > a
    Wait until element is visible  css=#plone-contentmenu-factories ul

The personal action links to
    [Documentation]  Item of the user menu (user actions), by action id
    [Arguments]  ${action_id}  ${url}
    Element attribute value should be  css=#personaltools-${action_id}  href  ${url}

The personal action is not available
    [Arguments]  ${action_id}
    Page should not contain element  css=#personaltools-${action_id}

The modal is open
    [Documentation]  Overlay (Plone 4) or modal (Plone 6) showing a form
    Wait until element is visible  ${MODAL} form

Modal element
    [Documentation]  Locator of the element with this id inside the modal
    ...              (an argument starting with # would be a robot comment)
    [Arguments]  ${id}
    [Return]  ${MODAL} [id="${id}"]

Save the modal
    Click button  css=.modal-footer #form-buttons-save

Cancel the modal
    Click button  css=.modal-footer #form-buttons-cancel

The modal is closed
    Wait until page does not contain element  ${MODAL}

The status message contains
    [Arguments]  ${text}
    Wait until element contains  css=.portalMessage  ${text}

The page is not an error
    Page should not contain  ${ERROR_PAGE_TEXT}

The page is not found
    Page should contain  ${NOT_FOUND_TEXT}

The edit link is not available
    Page should not contain element  css=#contentview-edit

The content title is
    [Documentation]  Plone 6.1 content views: h1 without the documentFirstHeading class
    [Arguments]  ${title}
    Element should contain  css=#content h1  ${title}

# Add menu and content views (tabs)

Click the add menu item
    [Documentation]  Item of the add menu, by normalized type id (e.g. contentcategorygroup)
    [Arguments]  ${type_id}
    Open the add menu
    Click element  css=#plone-contentmenu-factories a#${type_id}

The add menu offers
    [Documentation]  Item of the add menu (opened or not), by normalized type id
    [Arguments]  ${type_id}  ${expected}=${True}
    Run keyword if  ${expected}
    ...  Page should contain element  css=#plone-contentmenu-factories a#${type_id}
    ...  ELSE  Page should not contain element  css=#plone-contentmenu-factories a#${type_id}

Click the content view
    [Documentation]  Item of the content views (object actions) of the toolbar, by action id
    [Arguments]  ${action_id}
    Click element  css=#contentview-${action_id} a

The content view is available
    [Arguments]  ${action_id}  ${expected}=${True}
    Run keyword if  ${expected}
    ...  Page should contain element  css=#contentview-${action_id} a
    ...  ELSE  Page should not contain element  css=#contentview-${action_id}

Open the configlet
    [Documentation]  Link of the Site Setup page, by title
    [Arguments]  ${title}
    Go to  ${PLONE_URL}/@@overview-controlpanel
    Click element  xpath=//*[@id="content"]//a[.//div[normalize-space()="${title}"]]

# Category field (IIconifiedCategorization behavior)

Select the category
    [Documentation]  Option of the category field, by title (pat-select2 is initialized asynchronously)
    [Arguments]  ${title}
    Wait until page contains element  ${CATEGORY_FIELD} a.select2-choice
    Click element  ${CATEGORY_FIELD} a.select2-choice
    Wait until element is visible  css=.select2-drop-active
    Click element
    ...  xpath=//div[contains(@class, "select2-drop-active")]//div[contains(@class, "select2-result-label")][normalize-space()="${title}"]
    Wait until element is not visible  css=.select2-drop-active

The selected category is
    [Arguments]  ${title}
    Wait until page contains element  ${CATEGORY_FIELD} a.select2-choice
    Element text should be  ${CATEGORY_FIELD} a.select2-choice > span.select2-chosen  ${title}

The selected category shows its icon
    [Documentation]  Background image of the category, from the categories CSS (<category>/@@download)
    [Arguments]  ${category_path}
    ${image}=  Execute javascript
    ...  return window.getComputedStyle(document.querySelector('#formfield-form-widgets-IIconifiedCategorization-content_category a.select2-choice > span.select2-chosen > span')).backgroundImage;
    Should contain  ${image}  ${category_path}/@@download
