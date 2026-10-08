*** Settings ***
Documentation  Categories configuration: types hierarchy through the UI (F3), category forms hiding the fields
...            of the options off in the group (F18), update of the categorized elements (F19), control panel (F12).
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  iconifiedcategory.robot
Test Setup  Open a manager browser on a folder
Test Teardown  Close all browsers


*** Test Cases ***
Only the configuration can be added outside of a configuration
    Go to  ${PLONE_URL}
    The add menu offers  contentcategoryconfiguration
    The add menu offers  contentcategorygroup  ${False}
    The add menu offers  contentcategory  ${False}
    The add menu offers  contentsubcategory  ${False}

Add a group, a category and a subcategory to the configuration
    Go to  ${CONFIG_URL}
    The add menu offers  contentcategorygroup
    The add menu offers  contentcategory  ${False}
    Click the add menu item  contentcategorygroup
    Input text  css=#form-widgets-IBasic-title  Group 3
    Select radio button  form.widgets.to_be_printed_activated  true
    Save the form
    The status message contains  Item created
    The content title is  Group 3
    The add menu offers  contentcategory
    The add menu offers  contentcategorygroup  ${False}
    Click the add menu item  contentcategory
    Input text  css=#form-widgets-IBasic-title  Category 3-1
    Choose file  css=#form-widgets-icon-input  ${CURDIR}/icon.png
    Input text  css=#form-widgets-predefined_title  Predefined title 3-1
    Save the form
    The status message contains  Item created
    The content title is  Category 3-1
    The add menu offers  contentsubcategory
    Click the add menu item  contentsubcategory
    Input text  css=#form-widgets-IBasic-title  Subcategory 3-1-1
    Save the form
    The status message contains  Item created
    The content title is  Subcategory 3-1-1
    Open the add form  ${FOLDER_URL}  Document
    Select the category  Category 3-1
    The title field is  Predefined title 3-1
    Select the category  Subcategory 3-1-1
    The selected category is  Subcategory 3-1-1

The category forms only show the fields of the options on in the group
    [Documentation]  Group 1: only the "to be printed" option is on.
    ...              Plone 4 bug pinned: "Publishable default" is shown although the option is off
    ...              (contentview.FormMixin.related_widgets has no publishable entry).
    Go to  ${CONFIG_URL}/group-1/category-1-1/edit
    The form only shows the fields of the to be printed option
    Open the add form  ${CONFIG_URL}/group-1  ContentCategory
    The form only shows the fields of the to be printed option
    Go to  ${CONFIG_URL}/group-1/category-1-1/subcategory-1-1-1/edit
    The form only shows the fields of the to be printed option
    Activate the group options  group-1  confidentiality  signed  approved
    Go to  ${CONFIG_URL}/group-1/category-1-1/edit
    The form shows the field  confidential
    The form shows the field  to_sign
    The form shows the field  signed
    The form shows the field  to_approve
    The form shows the field  approved

The category view only shows the fields of the options on in the group
    [Documentation]  Plone 4 bug pinned: "Publishable default" is shown although the option is off
    ...              (contentview.BaseView.related_widgets has no publishable entry).
    Go to  ${CONFIG_URL}/group-1/category-1-1
    The view shows the field  predefined_title
    The view shows the field  to_print
    The view shows the field  confidential  ${False}
    The view shows the field  to_sign  ${False}
    The view shows the field  signed  ${False}
    The view shows the field  to_approve  ${False}
    The view shows the field  approved  ${False}
    The view shows the field  publishable
    Activate the group options  group-1  confidentiality
    Reload page
    The view shows the field  confidential

Update the categorized elements after a change of the categories
    Add a categorized document  First document  1-1
    Rename the category  group-1/category-1-1  Renamed category
    Go to  ${FOLDER_URL}
    The summary shows  Category 1-1  1
    Go to  ${CONFIG_URL}
    Click the content action  update_categorized_elements
    The status message contains  Elements updated!
    Location should be  ${CONFIG_URL}
    Go to  ${FOLDER_URL}
    The summary shows  Renamed category  1
    The summary does not show  Category 1-1

The control panel saves the settings
    Open the configlet  Iconified Category
    Wait until page contains  Iconified Category Settings
    Input text  css=#form-widgets-filesizelimit  900
    Save the form
    The status message contains  Changes saved
    Go to  ${PLONE_URL}/@@iconifiedcategory-controlpanel
    Textfield value should be  css=#form-widgets-filesizelimit  900


*** Keywords ***
The form only shows the fields of the to be printed option
    The form shows the field  predefined_title
    The form shows the field  to_print
    The form shows the field  confidential  ${False}
    The form shows the field  to_sign  ${False}
    The form shows the field  signed  ${False}
    The form shows the field  to_approve  ${False}
    The form shows the field  approved  ${False}
    # Plone 4 bug pinned, see the test documentation
    The form shows the field  publishable
