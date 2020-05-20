import sys
import time
import re

from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from medinfo.cpoe.cpoeSim.analysis.CPOETrackerAnalysis import SimulationAnalyzer


class SimulationReplayer:
    def __init__(self, selected_browser):
        self.wait_timeout = 10

        if selected_browser == "chrome":
            self.browser = webdriver.Chrome()
        elif selected_browser == "edge":
            self.browser = webdriver.Edge()
        elif selected_browser == "ie":
            self.browser = webdriver.Ie()
        elif selected_browser == "opera":
            self.browser = webdriver.Opera()
        elif selected_browser == "safari":
            self.browser = webdriver.Safari()
        else:  # default is Firefox
            # To prevent download dialog
            profile = webdriver.FirefoxProfile()
            profile.set_preference('browser.download.folderList', 2)  # custom location
            profile.set_preference('browser.download.manager.showWhenStarting', False)
            profile.set_preference('browser.download.dir', 'C:\\=== WORK ===\\=== Stanford ===\\replay\\')
            profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/json')

            self.browser = webdriver.Firefox(profile)

        self.browser.get("http://localhost/cgibin/cpoe/SimSetup.py")
        assert "Patient Management Simulation Setup" in self.browser.title

    def replay(self, user, patient, enable_recommender, data_file, timeline_mode):
        # will fail on NoSuchElementExceptions with exception message and stacktrace

        user_selection_box = Select(self.browser.find_element_by_name("sim_user_id"))
        user_selection_box.select_by_value(str(user))

        patient_selection_box = Select(self.browser.find_element_by_name("sim_patient_id"))
        patient_selection_box.select_by_value(str(patient))

        enable_recommender_checkbox = self.browser.find_element_by_name("enableRecommender")
        enable_recommender_checked = enable_recommender_checkbox.is_selected()
        if ((enable_recommender and not enable_recommender_checked)
                or (not enable_recommender and enable_recommender_checked)):
            enable_recommender_checkbox.click()

        proceed_button = self.browser.find_element_by_xpath("//input[@type='submit' and @value='Proceed to Simulation']")
        proceed_button.click()

        siman = SimulationAnalyzer(data_file)
        timeline = siman.construct_timeline()

        delays = []
        prev_timestamp = timeline[0][0]  # timestamp
        for event in timeline:
            delays.append(event[0] - prev_timestamp)
            prev_timestamp = event[0]
            print(event)

        print("Replaying...")
        for i, event in enumerate(timeline):
            print(event)
            if timeline_mode == "realtime":  # respect the time intervals in the original json
                print("Sleeping before execution...")
                time.sleep(delays[i] / 1000)
                print("Woke up. Executing...")

            # All modes from all json files
            # +1 >
            # +15 >>
            # < -1
            # ActiveOrdersRemoval   - appears only in 13_44_data.json - how are discontinuations recorded?
            # Diagnoses
            # FindOrders
            # NewOrderInteraction
            # NoteContent
            # Notes
            # OrderHistory
            # OrderSets
            # Recommended
            # Related
            # ResultInteraction
            # ResultsReview
            # SignOrders
            mode = event[1]
            if mode == "<< -15":
                self.click_button("button", "<< -15")
                self.handle_sign_orders_alert_if_displayed_and_click_button("button", "<< -15")
                self.wait_for_recommendations_if_enabled(enable_recommender)
            elif mode == "< -1":
                self.click_button("button", "< -1")
                self.handle_sign_orders_alert_if_displayed_and_click_button("button", "< -1")
                self.wait_for_recommendations_if_enabled(enable_recommender)
            elif mode == "+1 >":
                self.click_button("button", "+1 >")
                self.handle_sign_orders_alert_if_displayed_and_click_button("button", "+1 >")
                self.wait_for_recommendations_if_enabled(enable_recommender)
            elif mode == "+15 >>":
                self.click_button("button", "+15 >>")
                self.handle_sign_orders_alert_if_displayed_and_click_button("button", "+15 >>")
                self.wait_for_recommendations_if_enabled(enable_recommender)

            elif mode == "Notes":
                self.click_button("button", "Notes")
            elif mode == "ResultsReview":
                self.click_button("button", "Results Review")
            elif mode == "OrderHistory":
                self.click_button("button", "Order History")

            elif mode == "FindOrders":
                search_query = event[2]["searchQuery"]
                self.fill_search_query(search_query)
                self.click_button("submit", "Find Orders")

                if search_query == "":
                    self.wait_for_results_of("Common Orders")
                    self.wait_for_results_of("Related Orders")
                else:
                    self.wait_for_results_of("Order Search Results")
            elif mode == "OrderSets":
                self.fill_search_query(event[2]["searchQuery"])
                self.click_button("button", "Order Sets")

                self.wait_for_results_of("Order Set Search Results")
            elif mode == "Diagnoses":
                self.fill_search_query(event[2]["searchQuery"])
                self.click_button("button", "Diagnoses")

                self.wait_for_results_of("Order Search Results")

            # Refresh button - not clear how it is refresh represented in json - seems to not be presented at all -
            # it is equivalent to clicking FindOrders button with empty searchQuery
            elif mode == "NoteContent":
                # TODO not clear which note content to click - json doesn't contain id - click the last one
                link_text = event[2]["linkText"]
                links = self.browser.find_elements_by_link_text(link_text)
                links[-1].click()  # click the last one
            elif mode == "NewOrderInteraction":
                self.fill_search_query(event[2]["searchQuery"])

                action = event[2]["action"]
                item = event[2]["itemInfo"]     # NewOrderInteraction has only clinical_item_id in itemInfo

                item_xpath = "//input[@class='newOrderCheckbox' and @type='checkbox' and @value='" + item + "']"
                item_checkbox = self.browser.find_element_by_xpath(item_xpath)
                item_checkbox_checked = item_checkbox.get_attribute("checked")
                if ((action == "selected" and not item_checkbox_checked)
                        or (action == "unselected" and item_checkbox_checked)):
                    item_checkbox.click()
            elif mode == "SignOrders":
                self.fill_search_query(event[2]["searchQuery"])

                sign_orders_button = self.browser.find_element_by_name("signOrders")
                sign_orders_button.click()

                self.wait_for_recommendations_if_enabled(enable_recommender)
            elif mode == "ResultInteraction":
                self.fill_search_query(event[2]["searchQuery"])

                action = event[2]["action"]
                item = event[2]["itemInfo"]
                clinical_item_id_and_name = '|'.join(item.split('|')[:2]) + '|'     # returns 'clinical_item_id|name|'

                # Avoid checking/unchecking order in new orders section.
                # Can't use @class='orderCheckbox' here as we'll miss orderset ids that way.
                # item_xpath = "//input[(not(@class) or @class!='newOrderCheckbox') and @type='checkbox' and @value='" + item + "']"
                # Some v1 jsons were recorded before some suffixes were added, e.g., '(TTE)' suffix for 'ECHO - TRANSTHORACIC ECHO +DOPPLER item'
                # More problematic ones are where the prefix was added, e.g.,
                # item_xpath = "//input[not(@class='newOrderCheckbox') and @type='checkbox' and starts-with(@value, '" + item + "')]"
                # item_xpath = "//input[not(@class='newOrderCheckbox') and @type='checkbox' and @value='" + item + "']"

                # So, to match correctly for all versions, we'll use the prefix 'clinical_item_id|name|' of the order.
                item_xpath = "//input[not(@class='newOrderCheckbox') and @type='checkbox' " \
                             "and concat(substring-before(@value, '|'), " \
                                        "'|', " \
                                        "substring-before(substring-after(@value, '|'), '|')," \
                                        " '|')='" + clinical_item_id_and_name + "']"

                WebDriverWait(self.browser, self.wait_timeout).until(
                    expected_conditions.presence_of_element_located((By.XPATH, item_xpath)))
                item_checkbox = self.browser.find_element_by_xpath(item_xpath)
                item_checkbox_checked = item_checkbox.get_attribute("checked")
                if ((action == "selected" and not item_checkbox_checked)
                        or (action == "unselected" and item_checkbox_checked)):
                    item_checkbox.click()
            elif mode == "Recommended" or "Related":    # Recommended seems to be the older name for Related mode
                search_query = event[2]["searchQuery"]      # just the clinical_item_id

                related_orders_href_xpath = "//a[@href='javascript:loadRelatedOrders(" + search_query + ")']"
                related_orders_href = self.browser.find_element_by_xpath(related_orders_href_xpath)
                related_orders_href.click()

                # wait for the results to appears
                self.wait_for_results_of("Common Orders")
                self.wait_for_results_of("Related Orders")

        self.save_replay()
        self.browser.close()

    def handle_sign_orders_alert_if_displayed_and_click_button(self, type, value):
        # At least early v1 jsons didn't display 'Sign orders before click' alert.
        # handle if alert is displayed - accept alert and uncheck all checkboxes
        try:
            WebDriverWait(self.browser, 2).until(expected_conditions.alert_is_present())
            sign_orders_alert = self.browser.switch_to.alert
            sign_orders_alert.accept()

            # uncheck all checked checkboxes
            checkboxes = self.browser.find_elements_by_xpath("//input[@type='checkbox']")
            for checkbox in checkboxes:
                if checkbox.is_selected():
                    checkbox.click()

            self.click_button(type, value)
        except TimeoutException:
            pass  # we don't care if the alert wasn't displayed - in fact, that's what we want

    def wait_for_recommendations_if_enabled(self, enable_recommender):
        if enable_recommender:
            self.wait_for_results_of("Common Orders")
            self.wait_for_results_of("Related Orders")

    def wait_for_results_of(self, results_title):
        title_cell_xpath = "//td[@class='subheading' and contains(., '" + results_title + "')]"
        WebDriverWait(self.browser, self.wait_timeout).until(
            expected_conditions.presence_of_element_located((By.XPATH, title_cell_xpath)))

    def click_button(self, type, value):
        self.browser.find_element_by_xpath("//input[@type='" + type + "' and @value='" + value + "']").click()

    def fill_search_query(self, search_query):
        WebDriverWait(self.browser, self.wait_timeout).until(
            expected_conditions.presence_of_element_located((By.NAME, "orderSearch")))

        search_query_input = self.browser.find_element_by_name("orderSearch")
        search_query_input.clear()
        search_query_input.send_keys(search_query)

    def save_replay(self):
        patient_management_link = self.browser.find_element_by_link_text("Patient Management")
        patient_management_link.click()
        alert = self.browser.switch_to.alert
        alert.accept()

    def copy_patient_template(self, new_patient_name, patient_template_id):
        new_patient_name_input = self.browser.find_element_by_name("sim_patient_name")
        new_patient_name_input.clear()
        new_patient_name_input.send_keys(new_patient_name)

        # first select box is for simulation itself - that's why using last element in the list
        patient_template_selection_box = Select(self.browser.find_elements_by_name("sim_patient_id")[-1])
        patient_template_selection_box.select_by_value(str(patient_template_id))

        copy_patient_button = self.browser.find_element_by_name("copyPatientTemplate")
        copy_patient_button.click()

        self.browser.close()

    def create_new_user(self, new_user_name):
        new_user_name_input = self.browser.find_element_by_name("sim_user_name")
        new_user_name_input.clear()
        new_user_name_input.send_keys(new_user_name)

        create_user_button = self.browser.find_element_by_name("createUser")
        create_user_button.click()

        self.browser.close()


def main(argv):
    # IE doesn't seem to work very well.
    # Can't make Edge save the json file.
    # Didn't test Chrome, Opera and Safari.
    browser_choices = ["chrome", "edge", "firefox", "ie", "opera", "safari"]

    parser = ArgumentParser()
    parser.add_argument("command", nargs='?', default="replay",
                        choices=["replay", "create_user", "copy_patient_template"],
                        help="A command to perform: replay - replay the scenario in given JSON file, "
                             "create_user - create a new user given its name, "
                             "copy_patient_template - create new patient by copying another. "
                             "Default is 'replay'.")
    parser.add_argument("-f", "--file",  dest="data_file", help="JSON file containing collected data.")
    parser.add_argument("-b", "--browser", dest="browser", default="firefox", choices=browser_choices,
                        help="Select a browser to use for replay. Default is 'firefox'.")
    parser.add_argument("-u", "--user", dest="user", help="If used with 'replay' command: "
                                                          "user ID under which to replay the json data. "
                                                          "If used with 'create_user' command: "
                                                          "name of the new user to be created.")
    parser.add_argument("-p", "--patient", dest="patient", help="If used with 'replay' command: "
                                                                "Patient ID under which to replay the json data. "
                                                                "If used with 'copy_patient_template' command: "
                                                                "name of the new patient to be created.")
    parser.add_argument("-r1", "--recommender-on", dest="enable_recommender", action="store_true",
                        help="Enable recommender for this replay case. By default, it is enabled.")
    parser.add_argument("-r0", "--recommender-off", dest="enable_recommender", action="store_false",
                        help="Disable recommender for this replay case.")
    parser.set_defaults(enable_recommender=True)

    parser.add_argument("-pt", "--patient-template", dest="patient_template",
                        help="Patient ID which serves as a template for a new patient.")
    parser.add_argument("-m", "--mode", dest="mode", default="fast", choices=["realtime", "fast"],
                        help="Whether to take into account the timestamp intervals in the original json.")
    args = parser.parse_args(argv[1:])
    
    replayer = SimulationReplayer(args.browser)

    if args.command == "replay":
        replayer.replay(args.user, args.patient, args.enable_recommender, args.data_file, args.mode)
    elif args.command == "create_user":
        replayer.create_new_user(args.user)
    elif args.command == "copy_patient_template":
        replayer.copy_patient_template(args.patient, args.patient_template)


if __name__ == "__main__":
    main(sys.argv)