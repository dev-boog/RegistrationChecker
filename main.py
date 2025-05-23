import asyncio
import threading
import os
import dearpygui.dearpygui as dpg

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

# Configure the web crawler
browser_congfig = BrowserConfig()
run_config = CrawlerRunConfig()

# Create and start a background asyncio event loop
event_loop = asyncio.new_event_loop()

def run_loop():
    asyncio.set_event_loop(event_loop)
    event_loop.run_forever()

loop_thread = threading.Thread(target=run_loop, daemon=True)
loop_thread.start()



# GUI class for the registration lookup application
class LookupGUI:
    def __init__(self, title="Registration Lookup", width=400, height=640):
        self.title = title
        self.width = width
        self.height = height

    
    def setup_theme(self):
        # Load font
        with dpg.font_registry():
            font_path = r"C:\Windows\Fonts\segoeui.ttf" 
            menu_font = dpg.add_font(font_path, 16)
        dpg.bind_font(menu_font)
    
        # Load color theme
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (44, 44, 44), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (55, 55, 55), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (66, 66, 66), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (55, 55, 55), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (66, 66, 66), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (77, 77, 77), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (44, 44, 44), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (67, 68, 69), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 63), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 106, 106, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.0, category=dpg.mvThemeCat_Core)
            
        dpg.bind_theme(global_theme)

    # Draw the GUI components
    def setup(self):
        self.setup_theme()

        with dpg.window(label=self.title, tag="MainWindow"):
            
            dpg.add_text("Registration Number")
            dpg.add_input_text(label="##Enter Registration Number", tag="input_reg", default_value="", width=-1)

            dpg.add_button(label="Fetch Information", callback=self.search_reg, width=-1)

            dpg.add_checkbox(label="Save Markdown Files", tag="save_markdown", default_value=False) 

            dpg.add_text("General Information (CheckCarDetails)", bullet=True)
            with dpg.child_window(tag="results_child", width=-1, height=360, no_scrollbar=False):
                dpg.add_text("", tag="results_text")

            dpg.add_text("Remap Information (PhantomTuning)", bullet=True)
            with dpg.child_window(tag="results_performance_child", width=-1, height=-1, no_scrollbar=True):
                dpg.add_text("", tag="results_performance_text")

    # Handle the button click event to fetch information
    def search_reg(self, sender, app_data, user_data):
        reg_num = dpg.get_value("input_reg").strip()
        if reg_num:
            clear_results("results_child")
            clear_results("results_performance_child")

            dpg.add_text(f"Crawling checkcardetails.co.uk...", parent="results_child")
            event_loop.call_soon_threadsafe(asyncio.create_task, fetch_details(reg_num))
            dpg.add_text(f"Crawling phantomtuning.co.uk...", parent="results_performance_child")
            event_loop.call_soon_threadsafe(asyncio.create_task, fetch_remap_details(reg_num))

    # Function to init the GUI
    def run(self): 
        dpg.create_context()
        self.setup()
        dpg.create_viewport(title=self.title, width=self.width, height=self.height)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("MainWindow", True)
        dpg.start_dearpygui()
        dpg.destroy_context()


# Function to extract specific information from the lines of text based on a prefix
def extract_line(prefix, lines):
    for line in lines:
        if prefix in line:
            return line.replace(prefix, "").strip()
    return "N/A"

def find_next_line(prefix, lines):
    for idx, line in enumerate(lines):
        if prefix in line:
            if idx + 1 < len(lines):
                return lines[idx + 1].strip()
            else:
                return "N/A"
    return "N/A"

def find_previous_line(prefix, lines):
    for idx, line in enumerate(lines):
        if prefix in line:
            if idx > 0: 
                return lines[idx - 1].strip()
            else:
                return "N/A"  
    return "N/A"


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


# Scrape details on the car from CheckCarDetails.co.uk 
# - Sometimes 0-60 doesnt get scraped, litro no clue why...
async def fetch_details(registration_number):
    try:
        async with AsyncWebCrawler(config=browser_congfig) as crawler:
            result = await crawler.arun(url=f"https://www.checkcardetails.co.uk/cardetails/{registration_number}", config=run_config)          
            lines = result.markdown.splitlines()
            # Sometimes the lines contain similar content to needed data, so we need to remove them if they're irrelevant
            unwanted_data = [ 
                "###### MOT History"
            ]
            lines = [line for line in lines if line not in unwanted_data]
            if (dpg.get_value("save_markdown")):
                with open(f"MarkdownFiles/{registration_number}_CarCheckDetails.md", "w") as f:
                    f.write(result.markdown)
                    f.close()
    except Exception as e:
        print(f"Error fetching details: {e}")
        return

    general_info = {
        "Vechicle": find_previous_line("Not The Right Vehicle? ", lines).replace("##### ", ""),
        "Model": extract_line("Description| ", lines),
        "Year Manufactured": extract_line("Year Manufacture| ", lines),
        "Primary Colour": extract_line("Primary Colour| ", lines),
        "Engine": extract_line("Engine| ", lines),
        "Transmission": extract_line("Transmission| ", lines),
        "Body Style": extract_line("Body Style| ", lines),
        "Fuel Type": extract_line("Fuel Type| ", lines),
        "Vehicle Age": extract_line("Vehicle Age| ", lines),
        "Last V5C Issue": extract_line("Last V5C Issue Date| ", lines),
        "Last MOT Mileage": extract_line("Last MOT Mileage| ", lines),
        "Average Yearly Mileage": extract_line("Average| ", lines),
        "Max Speed": extract_line("Max Speed| ", lines),
        "BHP": extract_line("Power| ", lines),
        "Torque": extract_line("Torque| ", lines),
        "0-60 (mph)": extract_line("0 To 60 MPH| ", lines),
        "Road Tax Estimate (12 Month)": extract_line("Tax 12 Months Cost| ", lines),
        "Road Tax Estimate (6 Month)": extract_line("Tax 6 Months Cost| ", lines),	
        "Passed MOT": find_next_line("Passed", lines),
        "Failed MOT": find_next_line("Failed", lines),
        "MOT Expiry": find_next_line("## MOT", lines).replace("Expires: ", ""),
        "Tax Expirery": find_next_line("## TAX", lines).replace("Expires: ", ""),
        "Wheel Plan": extract_line("Wheel Plan| ", lines),
        "Registration Place": extract_line("Registration Place| ", lines),
        "Registration Date": extract_line("Registration Date| ", lines),
        "Total Keepers": find_next_line("Total Keepers", lines),
        "V5C Certificate Count": find_next_line("V5C Certificate Count", lines),
        "Is Explorted": find_next_line("Exported", lines),
        "Towns & Cities MPG": extract_line("Urban Driving around towns and cities| ", lines),
        "Towns & Faster A-Roads": extract_line("Extra Urban Driving in towns and on faster A-roads| ", lines),
        "Combined MPG": extract_line("Combined A mix of urban and extra urban driving| ", lines),
    }

    clear_results("results_child")
    display_info(general_info, "results_child")	

# Scrape details on remaping the car from PhantomTuning.co.uk 
async def fetch_remap_details(registration_number):
    try:
        async with AsyncWebCrawler(config=browser_congfig) as crawler:  
            result = await crawler.arun(url=f"https://beds.phantomtuning.co.uk/pt/results-engine/?reg={registration_number}", config=run_config)
            lines = result.markdown.splitlines()
            if (dpg.get_value("save_markdown")):
                with open(f"MarkdownFiles/{registration_number}_PhantomTuning.md", "w") as f:
                    f.write(result.markdown)
                    f.close()
    except Exception as e:
        print(f"Error fetching remap details: {e}")
        return

    general_info = {
        "Stage 1 Remap BHP Gains": extract_line("Power (bhp) | ", lines),
        "Stage 1 Remap Torque Gains": extract_line("Torque (nm) | ", lines),
    }

    clear_results("results_performance_child")
    display_info(general_info, "results_performance_child")


if __name__ == "__main__":
    gui = LookupGUI()
    gui.run()
