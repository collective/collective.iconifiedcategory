*** Settings ***
Documentation  Status icons of the categorized elements tab (F17): a click changes the status of the element
...            (AJAX call to @@iconified-<status>) when the option is on in its category group, the status persists.
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  iconifiedcategory.robot
Test Setup  Open a manager browser on a folder
Test Teardown  Close all browsers


*** Test Cases ***
Change the print status of a categorized content
    Add a categorized document  First document  1-1
    Open the categorized tab of the folder
    The status icon is  First document  print  inactive
    Click the status icon  First document  print
    The status icon is  First document  print  active
    Reload page
    The status icon is  First document  print  active
    Click the status icon  First document  print
    The status icon is  First document  print  inactive
    Reload page
    The status icon is  First document  print  inactive

Change the confidential status of a categorized content
    Activate the group options  group-1  confidentiality
    Add a categorized document  First document  1-1
    Open the categorized tab of the folder
    The status icon is  First document  confidential  inactive
    Click the status icon  First document  confidential
    The status icon is  First document  confidential  active
    Reload page
    The status icon is  First document  confidential  active

Change the publishable status of a categorized content
    Activate the group options  group-1  publishable
    Add a categorized document  First document  1-1
    Open the categorized tab of the folder
    The status icon is  First document  publishable  inactive
    Click the status icon  First document  publishable
    The status icon is  First document  publishable  active
    Reload page
    The status icon is  First document  publishable  active

The signed status goes from not to sign to to sign, signed and back
    Activate the group options  group-1  signed
    Add a categorized document  First document  1-1
    Open the categorized tab of the folder
    The status icon is  First document  signed  deactivated
    Click the status icon  First document  signed
    The status icon is  First document  signed  inactive
    Click the status icon  First document  signed
    The status icon is  First document  signed  active
    Reload page
    The status icon is  First document  signed  active
    Click the status icon  First document  signed
    The status icon is  First document  signed  deactivated
    Reload page
    The status icon is  First document  signed  deactivated

The approved status goes from not to approve to to approve, approved and back
    Activate the group options  group-1  approved
    Add a categorized document  First document  1-1
    Open the categorized tab of the folder
    The status icon is  First document  approved  deactivated
    Click the status icon  First document  approved
    The status icon is  First document  approved  inactive
    Click the status icon  First document  approved
    The status icon is  First document  approved  active
    Reload page
    The status icon is  First document  approved  active
    Click the status icon  First document  approved
    The status icon is  First document  approved  deactivated
    Reload page
    The status icon is  First document  approved  deactivated

A status of an option off in the category group can not be changed
    Add a categorized document  First document  1-1
    Open the categorized tab of the folder
    The status icon is editable  First document  print
    The status icon is editable  First document  confidential  ${False}
    Click the status icon  First document  confidential
    Reload page
    The status icon is  First document  confidential  inactive
