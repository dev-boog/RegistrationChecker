from gui_utils import clear_results, display_info
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

browser_congfig = BrowserConfig()
run_config = CrawlerRunConfig()

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
        "Is Exported": find_next_line("Exported", lines),
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
