*** Settings ***
Documentation  Plone 4.3 keywords. Same keyword names and arguments as ui_plone6.robot.
...            Robot Framework 3.0 syntax (Python 2 environment).
...            Checked on Plone 4.3 (collective.iconifiedcategory master): every keyword used by the
...            iconifiedcategory scenarios. The others are NOT CHECKED YET (see imio.actionspanel).
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Library  Remote  ${PLONE_URL}/RobotRemote


*** Variables ***
${MODAL}  css=div.overlay-ajax
${ERROR_PAGE_TEXT}  there seems to be an error
${NOT_FOUND_TEXT}  This page does not seem to exist
# category field of the IIconifiedCategorization behavior (collective.z3cform.select2 3.x, select2 3.x)
${CATEGORY_FIELD}  css=#formfield-form-widgets-IIconifiedCategorization-content_category


*** Keywords ***
Log in with the login form
    [Documentation]  Real login (creates the user folder), unlike autologin
    [Arguments]  ${username}  ${password}
    Disable autologin
    Go to  ${PLONE_URL}/login_form
    Input text  css=#__ac_name  ${username}
    Input password  css=#__ac_password  ${password}
    Click button  css=input[name="submit"]
    Wait until page contains element  css=#portal-personaltools

Click the content action
    [Documentation]  Item of the Actions menu (object_buttons), by action id
    [Arguments]  ${action_id}
    Click element  css=#plone-contentmenu-actions dt.actionMenuHeader a
    Wait until element is visible  css=#plone-contentmenu-actions-${action_id}
    Click element  css=#plone-contentmenu-actions-${action_id}

The content action is available
    [Arguments]  ${action_id}  ${expected}=${True}
    Click element  css=#plone-contentmenu-actions dt.actionMenuHeader a
    Wait until element is visible  css=#plone-contentmenu-actions dd.actionMenuContent
    Run keyword if  ${expected}
    ...  Page should contain element  css=#plone-contentmenu-actions-${action_id}
    ...  ELSE  Page should not contain element  css=#plone-contentmenu-actions-${action_id}

Open the add menu
    Click element  css=#plone-contentmenu-factories dt.actionMenuHeader a
    Wait until element is visible  css=#plone-contentmenu-factories dd.actionMenuContent

The personal action links to
    [Documentation]  Item of the user menu (user actions), by action id
    [Arguments]  ${action_id}  ${url}
    Element attribute value should be  css=#personaltools-${action_id} a  href  ${url}

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
    Click button  ${MODAL} #form-buttons-save

Cancel the modal
    Click button  ${MODAL} #form-buttons-cancel

The modal is closed
    Wait until element is not visible  ${MODAL}

The status message contains
    [Documentation]  Skips the hidden, empty #kssPortalMessage placeholder
    [Arguments]  ${text}
    Wait until element contains  css=.portalMessage:not(#kssPortalMessage)  ${text}

The page is not an error
    Page should not contain  ${ERROR_PAGE_TEXT}

The page is not found
    Page should contain  ${NOT_FOUND_TEXT}

The edit link is not available
    Page should not contain element  css=#contentview-edit

The content title is
    [Arguments]  ${title}
    Element should contain  css=h1.documentFirstHeading  ${title}

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
    [Documentation]  Tab of the content views (object actions), by action id
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
    Click element  xpath=//*[@id="content"]//a[normalize-space()="${title}"]

# Category field (IIconifiedCategorization behavior)

Select the category
    [Documentation]  Option of the category field, by title
    [Arguments]  ${title}
    Click element  ${CATEGORY_FIELD} a.select2-choice
    Wait until element is visible  css=.select2-drop-active
    Click element
    ...  xpath=//div[contains(@class, "select2-drop-active")]//div[contains(@class, "select2-result-label")][normalize-space()="${title}"]
    Wait until element is not visible  css=.select2-drop-active

The selected category is
    [Arguments]  ${title}
    Element text should be  ${CATEGORY_FIELD} a.select2-choice > span  ${title}

The selected category shows its icon
    [Documentation]  Background image of the category, from the categories CSS (<category>/@@download)
    [Arguments]  ${category_path}
    ${image}=  Execute javascript
    ...  return window.getComputedStyle(document.querySelector('#formfield-form-widgets-IIconifiedCategorization-content_category a.select2-choice > span > span')).backgroundImage;
    Should contain  ${image}  ${category_path}/@@download
