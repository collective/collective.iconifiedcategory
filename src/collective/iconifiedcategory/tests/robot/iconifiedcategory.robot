*** Settings ***
Documentation  collective.iconifiedcategory keywords, built on the ui_plone${PLONE_MAJOR}.robot keywords.
...            Robot Framework 3.1 syntax (FOR ... END; shared with the Plone 4.3 environment, RF 3.2.2).
...            Test fixture (testing profile): ${PLONE_URL}/config with "Group 1" and "Group 2"
...            (to be printed option on), categories "Category <group>-<1..3>" (predefined title = title),
...            subcategories "Subcategory <group>-<category>-<1..2>". Document and File are categorized.
Resource  ui_plone${PLONE_MAJOR}.robot
# Create categorized content, set attributes (testing.py)
Library  Remote  ${PLONE_URL}/IconifiedCategoryRobotRemote  WITH NAME  IconifiedCategoryRemote


*** Variables ***
${CONFIG_URL}  ${PLONE_URL}/config
${FOLDER_URL}  ${PLONE_URL}/folder
${TITLE_FIELD}  css=#form-widgets-IDublinCore-title
${SUMMARY}  css=#content .categorized-elements
${TOOLTIP}  css=.tooltipster-base
${TABLE}  css=table.iconified-listing


*** Keywords ***
Open a manager browser
    Open test browser
    Enable autologin as  Manager

Open a manager browser on a folder
    Open a manager browser
    Create content  type=Folder  id=folder  title=Folder
    Go to  ${FOLDER_URL}

Category id
    [Documentation]  Stored id of a category: Category id  1-2  or  1-2-1 for a subcategory
    [Arguments]  ${number}
    ${parts}=  Evaluate  '${number}'.split('-')
    ${id}=  Set variable  ${PLONE_SITE_ID}-config_-_group-${parts[0]}_-_category-${parts[0]}-${parts[1]}
    ${length}=  Get length  ${parts}
    ${id}=  Set variable if  ${length} == 3  ${id}_-_subcategory-${number}  ${id}
    [Return]  ${id}

Add a categorized document
    [Documentation]  Document of the folder, category by number (1-2: Category 1-2)
    [Arguments]  ${title}  ${category}
    ${category_id}=  Category id  ${category}
    ${uid}=  Create categorized content  folder  Document  ${title}  ${category_id}
    [Return]  ${uid}

Activate the group options
    [Documentation]  Activate options (confidentiality, signed, approved, publishable...) of a category group
    [Arguments]  ${group}  @{options}
    FOR  ${option}  IN  @{options}
        Set content attribute  config/${group}  ${option}_activated  ${True}
    END

Rename the category
    [Documentation]  Without the edit form: the icons of the testing profile categories are files, not images,
    ...              the edit form refuses them ("Object is of wrong type.")
    [Arguments]  ${path}  ${title}
    Set content attribute  config/${path}  title  ${title}

Open the add form
    [Arguments]  ${container_url}  ${portal_type}
    Go to  ${container_url}/++add++${portal_type}
    Wait until page contains element  css=#form-buttons-save

Save the form
    Click button  css=#form-buttons-save

The title field is
    [Arguments]  ${title}
    Textfield value should be  ${TITLE_FIELD}  ${title}

# Summary below the content (categorized-childs viewlet)

Summary link
    [Documentation]  Locator of the link of a category in the summary (tooltipster moves the link title away:
    ...              the category is found by its icon)
    [Arguments]  ${category_title}
    [Return]  xpath=//*[@id="content"]//div[contains(@class, "categorized-elements")]/a[contains(@class, "tooltipster-childs-infos")][img[@title="${category_title}"]]

The summary shows
    [Documentation]  Category of the summary with its number of elements
    [Arguments]  ${category_title}  ${count}
    ${locator}=  Summary link  ${category_title}
    Element text should be  ${locator}  ${count}

The summary does not show
    [Arguments]  ${category_title}
    ${locator}=  Summary link  ${category_title}
    Page should not contain element  ${locator}

The summary shows nothing
    Wait until element contains  css=#content  Categorized elements
    Page should not contain element  ${SUMMARY} a.tooltipster-childs-infos
    Element should contain  css=#content  Nothing.

The summary icon is loaded
    [Documentation]  The image of the category is displayed (loaded, not a broken image)
    [Arguments]  ${category_title}
    Wait until keyword succeeds  10s  0.5s  The image is loaded
    ...  \#content .categorized-elements a.tooltipster-childs-infos img[title="${category_title}"]

The image is loaded
    [Arguments]  ${selector}
    ${loaded}=  Execute javascript
    ...  var img = document.querySelector('${selector}'); return img.complete && img.naturalWidth > 0;
    Should be true  ${loaded}

Hover the category of the summary
    [Arguments]  ${category_title}
    ${locator}=  Summary link  ${category_title}
    Mouse over  ${locator}

The tooltip shows the category
    [Arguments]  ${category_title}
    Wait until element is visible  ${TOOLTIP} .tooltipster-categorized-elements
    Element should contain  ${TOOLTIP} label.content-category  ${category_title}

The tooltip lists
    [Documentation]  Element of the tooltip, its title links to the element
    [Arguments]  ${title}  ${url}
    Element attribute value should be
    ...  xpath=//div[contains(@class, "tooltipster-base")]//a[contains(@class, "categorized-element-title")][normalize-space()="${title}"]
    ...  href  ${url}

The tooltip shows the status
    [Documentation]  State icon of an element of the tooltip (print, confidential, signed, approved, publishable),
    ...              ${state}: active, inactive or deactivated
    [Arguments]  ${title}  ${status}  ${state}
    ${locator}=  Set variable
    ...  xpath=//div[contains(@class, "tooltipster-base")]//li[.//a[normalize-space()="${title}"]]//span[contains(@class, "iconified-${status}")]
    Element should have the state  ${locator}  ${state}

Click the more infos link of the tooltip
    Click element  xpath=//div[contains(@class, "tooltipster-base")]//a[normalize-space()="More infos"]

# Categorized elements tab (@@iconifiedcategory)

Open the categorized tab of the folder
    Go to  ${FOLDER_URL}/@@iconifiedcategory
    The categorized tab is shown

The categorized tab is shown
    Wait until page contains element  ${TABLE}
    Element should contain  css=h1.documentFirstHeading  Categorized elements

The categorized tab lists
    [Documentation]  Row of the table: title (linked to the element) and category
    [Arguments]  ${title}  ${url}  ${category}
    Element attribute value should be  ${TABLE} a[title="${title}"]  href  ${url}
    Element text should be
    ...  xpath=//table[contains(@class, "iconified-listing")]//tr[.//a[@title="${title}"]]/td[contains(@class, "category-column")]
    ...  ${category}

Status icon
    [Documentation]  Locator of the status icon of an element of the categorized tab
    [Arguments]  ${title}  ${status}
    [Return]  xpath=//table[contains(@class, "iconified-listing")]//tr[.//a[@title="${title}"]]/td[contains(@class, "iconified-${status}")]/a

Click the status icon
    [Documentation]  ${status}: print, confidential, signed, approved or publishable
    [Arguments]  ${title}  ${status}
    ${locator}=  Status icon  ${title}  ${status}
    Click element  ${locator}

The status icon is
    [Documentation]  ${state}: active, inactive or deactivated (waits for the AJAX update)
    [Arguments]  ${title}  ${status}  ${state}
    ${locator}=  Status icon  ${title}  ${status}
    Wait until keyword succeeds  10s  0.5s  Element should have the state  ${locator}  ${state}

The status icon is editable
    [Arguments]  ${title}  ${status}  ${expected}=${True}
    ${locator}=  Status icon  ${title}  ${status}
    ${class}=  Get element attribute  ${locator}  class
    Run keyword if  ${expected}  Should contain  ${class}  editable
    ...  ELSE  Should not contain  ${class}  editable

Element should have the state
    [Documentation]  active: class active; deactivated: class deactivated; inactive: none of them
    [Arguments]  ${locator}  ${state}
    ${class}=  Get element attribute  ${locator}  class
    ${found}=  Evaluate  ' '.join([c for c in "${class}".split() if c in ('active', 'deactivated')]) or 'inactive'
    Should be equal  ${found}  ${state}

# Category forms

The form shows the field
    [Documentation]  Field of an add or edit form (its label), by field name
    [Arguments]  ${field}  ${expected}=${True}
    Run keyword if  ${expected}
    ...  Element should be visible  css=#formfield-form-widgets-${field} label
    ...  ELSE  Page should not contain element  css=#formfield-form-widgets-${field} label

The view shows the field
    [Documentation]  Field of a view (its display widget), by field name
    [Arguments]  ${field}  ${expected}=${True}
    Run keyword if  ${expected}
    ...  Element should be visible  css=#form-widgets-${field}
    ...  ELSE  Page should not contain element  css=#form-widgets-${field}
