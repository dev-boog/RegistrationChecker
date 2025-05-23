import dearpygui.dearpygui as dpg

# Function to clear the results in the specified child window
def clear_results(child):
    children = dpg.get_item_children(child, 1)
    if children:
        for child in children:
            dpg.delete_item(child)
     

# Function to format the results in the specified child window
def display_info(info_dict, child):
    for label, value in info_dict.items():
        with dpg.group(horizontal=True, parent=child):
            dpg.add_text(f"{label}: ", color=[255, 106, 106, 255])
            dpg.add_text(str(value), color=[255, 255, 255])
    dpg.add_spacer(height=5, parent=child)  