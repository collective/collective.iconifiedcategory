*** Settings ***
Documentation  Category field of the categorized content forms (F9, F7): category choice, predefined title.
...            Version-independent: Plone selectors and the category widget are in ui_plone*.robot.
Resource  iconifiedcategory.robot
Test Setup  Open a manager browser on a folder
Test Teardown  Close all browsers


*** Test Cases ***
Categorize a content with the category field
    Open the add form  ${FOLDER_URL}  Document
    Select the category  Category 1-2
    The selected category is  Category 1-2
    Input text  ${TITLE_FIELD}  My document
    Save the form
    The status message contains  Item created
    The content title is  My document
    Go to  ${FOLDER_URL}
    The summary shows  Category 1-2  1

The category field shows the icon of the category
    Open the add form  ${FOLDER_URL}  Document
    Select the category  Category 2-1
    The selected category shows its icon  config/group-2/category-2-1

The predefined title of the category fills the title
    Open the add form  ${FOLDER_URL}  Document
    Select the category  Category 1-2
    The title field is  Category 1-2
    Select the category  Category 2-1
    The title field is  Category 2-1
    Save the form
    The status message contains  Item created
    The content title is  Category 2-1

A subcategory without predefined title keeps the title
    Open the add form  ${FOLDER_URL}  Document
    Input text  ${TITLE_FIELD}  My document
    Select the category  Subcategory 1-2-1
    The title field is  My document
    Save the form
    The status message contains  Item created
    The content title is  My document
    Go to  ${FOLDER_URL}
    The summary shows  Category 1-2  1

The predefined title does not erase an existing title
    Open the add form  ${FOLDER_URL}  Document
    Select the category  Category 1-3
    Input text  ${TITLE_FIELD}  My document
    Save the form
    The status message contains  Item created
    Go to  ${FOLDER_URL}/my-document/edit
    The selected category is  Category 1-3
    The title field is  My document
    Save the form
    The status message contains  Changes saved
    The content title is  My document
