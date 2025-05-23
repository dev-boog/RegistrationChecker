import asyncio
import threading
import dearpygui.dearpygui as dpg

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

from fetch_data import fetch_details, fetch_remap_details
from gui_utils import clear_results, display_info


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

        with dpg.window(label=self.title, tag="MainWindow", no_move=False):
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
            event_loop.call_soon_threadsafe(asyncio.create_task, fetch_details(reg_num, dpg.get_value("save_markdown")))
            dpg.add_text(f"Crawling phantomtuning.co.uk...", parent="results_performance_child")
            event_loop.call_soon_threadsafe(asyncio.create_task, fetch_remap_details(reg_num, dpg.get_value("save_markdown")))

    # Function to init the GUI
    def run(self):  
        dpg.create_context()
        self.setup()
        dpg.create_viewport(title=self.title, width=self.width, height=self.height)

        # dpg.configure_viewport(0, decorated=False)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("MainWindow", True)
        dpg.start_dearpygui()
        dpg.destroy_context()

         
if __name__ == "__main__":
    gui = LookupGUI()
    gui.run()
