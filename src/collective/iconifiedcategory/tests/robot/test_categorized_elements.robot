*** Settings ***
Documentation  Categorized elements of a folder: summary below the content (F13, F7), tooltip of a
...            category (F14), manage link (F15) and categorized elements tab (F16).
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  iconifiedcategory.robot
Test Setup  Open a manager browser on a folder
Test Teardown  Close all browsers


*** Test Cases ***
A content without categorized elements shows nothing below its content
    Go to  ${FOLDER_URL}
    The summary shows nothing

The summary below the content counts the elements of each category
    Add a categorized document  First document  1-1
    Add a categorized document  Second document  1-1
    Add a categorized document  Third document  1-2-1
    Go to  ${FOLDER_URL}
    The summary shows  Category 1-1  2
    The summary shows  Category 1-2  1
    The summary does not show  Category 2-1
    The summary icon is loaded  Category 1-1

Hovering a category of the summary shows its elements
    Add a categorized document  First document  1-1
    Add a categorized document  Second document  1-1
    Add a categorized document  Third document  1-2
    Go to  ${FOLDER_URL}
    Hover the category of the summary  Category 1-1
    The tooltip shows the category  Category 1-1
    The tooltip lists  First document  ${FOLDER_URL}/first-document
    The tooltip lists  Second document  ${FOLDER_URL}/second-document
    Element should not contain  ${TOOLTIP}  Third document
    The tooltip shows the status  First document  print  inactive

The more infos link of the tooltip opens the categorized elements tab
    Add a categorized document  First document  1-1
    Go to  ${FOLDER_URL}
    Hover the category of the summary  Category 1-1
    The tooltip shows the category  Category 1-1
    Click the more infos link of the tooltip
    Location should be  ${FOLDER_URL}/@@iconifiedcategory
    The categorized tab is shown

The manage link leads to the categorized elements tab
    [Documentation]  @@categorized-childs-manage is a fragment for the pages of other packages (icon only)
    Add a categorized document  First document  1-1
    Go to  ${FOLDER_URL}/@@categorized-childs-manage
    Element attribute value should be  css=a.manage-categorized-elements  href  ${FOLDER_URL}/@@iconifiedcategory
    Element attribute value should be  css=a.manage-categorized-elements  title  Manage categorized elements
    Go to  ${FOLDER_URL}/@@iconifiedcategory
    The categorized tab is shown

The categorized elements tab lists the elements of the folder
    Go to  ${FOLDER_URL}
    The content view is available  iconifiedcategory  ${False}
    Add a categorized document  First document  1-1
    Add a categorized document  Second document  1-2-1
    Go to  ${FOLDER_URL}
    Click the content view  iconifiedcategory
    The categorized tab is shown
    The categorized tab lists  First document  ${FOLDER_URL}/first-document  Category 1-1
    The categorized tab lists  Second document  ${FOLDER_URL}/second-document  Category 1-2 / Subcategory 1-2-1
