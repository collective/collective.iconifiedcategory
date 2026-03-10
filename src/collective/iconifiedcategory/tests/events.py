# -*- coding: utf-8 -*-

def on_categorized_element_updated(obj, event):
    '''Called a categorized element is updated (when element created/edited).'''
    # add values to the request so we can test it
    obj.REQUEST.set("old_values", event.old_values)
    obj.REQUEST.set("new_values", event.new_values)
    obj.REQUEST.set("parent", event.parent)
    obj.REQUEST.set("limited", event.limited)
