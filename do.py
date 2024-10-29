"""
FUA

continue adding events from line 280

reference new.py as required

work on helper functions specified with FUA at the 
top of the function

continue working on the below logic from 
the base of the function

allow users to specify configs via json

specify all possible values for each select option tag 
at the top of the function underneath its corresponding
array

include details for a possible config.json and specify the format for that api as well
"""

import os
import re
import json
import time
from playwright.sync_api import sync_playwright

def read_credentials(credentials_filepath):
    try:
        with open(credentials_filepath, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("File not found. Please check the file path.")
    except json.JSONDecodeError:
        print("Error decoding JSON. Please check the file format.")

def convert_room_capacity(room_capacity_raw):
    """
    convert integer room capacity
    to the fbs string required value
    """
    if room_capacity_raw < 5:
        return "LessThan5Pax"
    elif 5 <= room_capacity_raw <= 10:
        return "From6To10Pax"
    elif 11 <= room_capacity_raw <= 15:
        return "From11To15Pax"
    elif 16 <= room_capacity_raw <= 20:
        return "From16To20Pax"
    elif 21 <= room_capacity_raw <= 50:
        return "From21To50Pax"
    elif 51 <= room_capacity_raw <= 100:
        return "From51To100Pax"
    else:
        return "MoreThan100Pax"

def scrape_smu_fbs(base_url, credentials_filepath):

    """
    handle automated login to SMU FBS based on
    personal credentials.json and scrapes the desired pages
    """

    # FUA these values below are to be recieved as parameters to the function with optional parameters as well
    """
    FUA
    
    add documentation for each of the following options 
    for all possible options for each selection when booking 
    a room initially in FBS
    """
    DATE = "01-Nov-2024" # FUA to add a function that converts this date input so users can specify date input to the function in any number of formats
    DURATION_HRS = "2"
    START_TIME = "11:00"
    END_TIME = "13:00" # FUA to add a function that calculates this based on the duration_hrs fed in
    ROOM_CAPACITY_RAW = 0 
    ROOM_CAPACITY_FORMATTED = convert_room_capacity(ROOM_CAPACITY_RAW)
    # options tags can then be selected by value, values range from LessThan5Pax, From6To10Pax, From11To15Pax, From16To20Pax, From21To50Pax, From51To100Pax, MoreThan100Pax
    BUILDING_ARRAY = ["School of Accountancy", "School of Computing & Information Systems 1"]
    FLOOR_ARRAY = ["Basement 1", "Level 1", "Level 2", "Level 4"]
    FACILITY_TYPE_ARRAY = ["Meeting Pod", "Group Study Room", "Classroom"]
    EQUIPMENT_ARRAY = ["Projector", "TV Panel"]
    SCREENSHOT_FILEPATH = "./screenshot_log/"

    errors = []
    local_credentials = read_credentials(credentials_filepath)
    # print(local_credentials["username"])
    # print(local_credentials["password"])

    try:

        p = sync_playwright().start() 
        browser = p.chromium.launch(headless=False, slow_mo=1000) # for easier debugging
        # browser = p.chromium.launch(headless=True) 
        page = browser.new_page()

        try:

            # ---------- LOGIN CREDENTIALS ----------

            page.goto(base_url)

            page.wait_for_selector('input#userNameInput')
            page.wait_for_selector('input#passwordInput')
            page.wait_for_selector('span#submitButton')

            print(f"navigating to {base_url}")

            username_input = page.query_selector("input#userNameInput") # for debugging
            password_input = page.query_selector("input#passwordInput") # for debugging
            signin_button = page.query_selector("span#submitButton")

            page.fill("input#userNameInput", local_credentials["username"])
            page.fill("input#passwordInput", local_credentials["password"])
            signin_button.click()

            page.wait_for_timeout(6000)
            page.wait_for_load_state('networkidle')

            # ---------- NAVIGATE TO GIVEN DATE ----------

            # page.screenshot(path=f"{SCREENSHOT_FILEPATH}0.png")

            frame = page.frame(name="frameBottom") 
            if not frame:
                errors.append("Framebottom could not be found.")
            else:
                frame = page.frame(name="frameContent")
                current_date_input = frame.query_selector("input#DateBookingFrom_c1_textDate") # might need to get the value attribute from here
                while current_date_input != DATE:
                    current_date_input = frame.query_selector("input#DateBookingFrom_c1_textDate").get_attribute("value") 
                    print(f"current day is {current_date_input}, going to next day...")
                    next_day_button_input = frame.query_selector("a#BtnDpcNext.btn") # click the button until desired date, which by default is the next day
                    next_day_button_input.click()
                    frame.wait_for_timeout(1000)

            # ---------- EXTRACT PAGE DATA ----------

                # ----- SELECT START TIME -----

                select_start_time_input = frame.query_selector("select#TimeFrom_c1_ctl04") # options tags can then be selected by value, values range from 00:00 to 23:30
                if select_start_time_input:
                    frame.evaluate(f'document.querySelector("select#TimeFrom_c1_ctl04").value = "{START_TIME}"')
                    print(f"Selected start time to be {START_TIME}")
                else:
                    print("Select element for start time not found")

                # ----- SELECT END TIME -----

                select_end_time_input = frame.query_selector_all("select#TimeTo_c1_ctl04") # options tags can then be selected by value, values range from 00:00 to 23:30
                if select_end_time_input:
                    frame.evaluate(f'document.querySelector("select#TimeTo_c1_ctl04").value = "{END_TIME}"')
                    print(f"Selected end time to be {END_TIME}")
                else:
                    print("Select element for end time not found")

                # page.screenshot(path=f"{SCREENSHOT_FILEPATH}1.png")
                frame.wait_for_timeout(3000)

                # ----- SELECT BUILDINGS -----

                if BUILDING_ARRAY:

                    # select_building_option_array = page.query_selector_all("div#DropMultiBuildingList_c1\:\:ddl\:\: label") # then read the inner_text fo the span and if the text 
                    # for building in select_building_option_array:
                    #     if building.inner_text in BUILDING_ARRAY: 
                    #         building.query_selector("input").click() # click the checkbox
                    # page.click('div#DropMultiBuildingList_c1_panelTreeView input[type="button"][value="OK"]') # click the OK button
                    # print(f"{len(BUILDING_ARRAY)} buildings selected")

                    if frame.is_visible('#DropMultiBuildingList_c1_textItem'):
                        frame.click('#DropMultiBuildingList_c1_textItem') # opens the dropdown list
                        for building_name in BUILDING_ARRAY:
                            frame.click(f'text="{building_name}"')
                            print(f"selecting {building_name}...")
                        frame.evaluate("popup.hide()") # closes the dropdown list
                        page.wait_for_load_state('networkidle')
                        # page.screenshot(path=f"{SCREENSHOT_FILEPATH}2.png")
                        frame.wait_for_timeout(3000)

                # ----- SELECT FLOORS -----

                if FLOOR_ARRAY:

                    # select_floor_option_array = page.query_selector_all("div#DropMultiFloorList_c1::ddl:: label")
                    # for floor in select_floor_option_array:
                    #     if floor.inner_text() in FLOOR_ARRAY:
                    #         floor.query_selector("input").click()  # click the checkbox
                    # page.click('div#DropMultiFloorList_c1_panelTreeView input[type="button"][value="OK"]')  # click the OK button
                    # print(f"{len(FLOOR_ARRAY)} floors selected")

                    if frame.is_visible('#DropMultiFloorList_c1_textItem'):
                        frame.click('#DropMultiFloorList_c1_textItem') # opens the dropdown list
                        for floor_name in FLOOR_ARRAY:
                            frame.click(f'text="{floor_name}"')
                            print(f"selecting {floor_name}...")
                        frame.evaluate("popup.hide()") # closes the dropdown list
                        page.wait_for_load_state('networkidle')
                        # page.screenshot(path=f"{SCREENSHOT_FILEPATH}3.png")
                        frame.wait_for_timeout(3000)

                # ----- SELECT FACILITY TYPE -----

                if FACILITY_TYPE_ARRAY:

                    # select_facility_option_array = page.query_selector_all("div#DropMultiFacilityTypeList_c1::ddl:: label")
                    # for facility in select_facility_option_array:
                    #     if facility.inner_text() in FACILITY_TYPE_ARRAY:
                    #         facility.query_selector("input").click()  # click the checkbox
                    # page.click('div#DropMultiFacilityTypeList_c1_panelTreeView input[type="button"][value="OK"]')  # click the OK button
                    # print(f"{len(FACILITY_TYPE_ARRAY)} facilities selected")

                    if frame.is_visible('#DropMultiFacilityTypeList_c1_textItem'):
                        frame.click('#DropMultiFacilityTypeList_c1_textItem') # opens the dropdown list
                        for facility_type_name in FACILITY_TYPE_ARRAY:
                            frame.click(f'text="{facility_type_name}"')
                            print(f"selecting {facility_type_name}...")
                        frame.evaluate("popup.hide()") # closes the dropdown list
                        page.wait_for_load_state('networkidle')
                        # page.screenshot(path=f"{SCREENSHOT_FILEPATH}4.png")
                        frame.wait_for_timeout(3000)

                # ----- SELECT ROOM CAPACITY -----

                select_capacity_input = frame.query_selector("select#DropCapacity_c1") # options tags can then be selected by value, values range from LessThan5Pax, From6To10Pax, From11To15Pax, From16To20Pax, From21To50Pax, From51To100Pax, MoreThan100Pax
                if select_capacity_input:
                    frame.evaluate(f'document.querySelector("select#DropCapacity_c1").value = "{ROOM_CAPACITY_FORMATTED}"')
                    print(f"Selected room capacity to be {ROOM_CAPACITY_FORMATTED}")
                else:
                    print("Select element for room capacity not found")
                # page.screenshot(path=f"{SCREENSHOT_FILEPATH}5.png")
                frame.wait_for_timeout(3000)

                if EQUIPMENT_ARRAY:

                    # select_equipment_option_array = page.query_selector_all("div#DropMultiEquipmentList_c1::ddl:: label")
                    # for equipment in select_equipment_option_array:
                    #     if equipment.inner_text() in EQUIPMENT_ARRAY:
                    #         equipment.query_selector("input").click()  # click the checkbox
                    # page.click('div#DropMultiEquipmentList_c1_panelTreeView input[type="button"][value="OK"]')  # click the OK button
                    # print(f"{len(EQUIPMENT_ARRAY)} equipment selected")

                    if frame.is_visible('#DropMultiEquipmentList_c1_textItem'):
                        frame.click('#DropMultiEquipmentList_c1_textItem') # opens the dropdown list
                        for equipment_name in EQUIPMENT_ARRAY:
                            frame.click(f'text="{equipment_name}"')
                            print(f"selecting {equipment_name}...")
                        frame.evaluate("popup.hide()") # closes the dropdown list
                        page.wait_for_load_state('networkidle')
                        # page.screenshot(path=f"{SCREENSHOT_FILEPATH}6.png")
                        frame.wait_for_timeout(3000)

                page.screenshot(path=f"{SCREENSHOT_FILEPATH}0.png")

                # ----- ROOM EXTRACTION -----

                frame.wait_for_selector("table#GridResults_gv")
                matching_rooms = []
                rows = frame.query_selector_all("table#GridResults_gv tbody tr")
                for row in rows:
                    tds = row.query_selector_all("td")
                    if len(tds) > 1: 
                        matching_rooms.append(tds[1].inner_text().strip())  
                if not matching_rooms:
                    print("No rooms fitting description found.")
                else:
                    print(f"{len(matching_rooms)} rooms fitting description found.")
                    for room in matching_rooms:
                        print(f"-{room}")

                    # ----- SEARCH AVAILABILITY -----

                    frame.query_selector("a#CheckAvailability").click()
                    print("Submitting search availability request...")
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(6000)

                    # ---------- CHOOSE TIMESLOT ----------

                    page.screenshot(path=f"{SCREENSHOT_FILEPATH}1.png")
                    print(f"saving screenshot of rooms to filepath {SCREENSHOT_FILEPATH}")

                    """
                    FUA 
                    
                    continue adding scraping code here once the available timeslots 
                    have been loaded in or make a screenshot or curl the HTML and use 
                    a OCR library to extract that data instead, that works as well
                    
                    or integrate bharath's code from there later
                    """

        except Exception as e:
            errors.append(f"Error processing {base_url}: {e}")

        finally:
            print("closing browser...")
            browser.close() 

    except Exception as e:
        errors.append(f"Failed to initialize Playwright: {e}")

    return errors

if __name__ == "__main__":
    TARGET_URL = "https://fbs.intranet.smu.edu.sg/home"
    CREDENTIALS_FILEPATH = "credentials.json"
    scrape_smu_fbs(TARGET_URL, CREDENTIALS_FILEPATH)
