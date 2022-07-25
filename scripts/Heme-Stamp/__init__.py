import os
import json
import orderInfo
from datetime import date
import cosmos
import order_action

def main():
    with open(os.path.join(os.sys.path[0], "live_HS.confg"), "r") as creds_json_file:
        credentials = json.load(creds_json_file)

    order_date = date.today()

    ENV = 'https://epic-ic-background.stanfordmed.org/Interconnect-Cloud/'
    # CID taken out for privacy

    a = cosmos.getcosmosbetweendate("2022-06-18", "2022-07-10")
    # a = cosmos.getcosmosbydate("2022-06-19")

    # a = cosmos.getcosmos()
    FHIR_ID_set = set()
    if len(a) > 0:
        for i in range(len(a)):
            if 'Error' not in a[i]['patient'].keys():
                # print(a[i]['patient'])
                # print("--------")
                FHIR_ID_set.add(a[i]['patient']['FHIR ID'])

    # phys_list = ['Rondeep Singh Brar, MD', 'David Joseph Iberri, MD', 'William Elias Shomali, MD']
    phys_list = ['Rondeep Singh Brar', 'David Joseph Iberri', 'William Elias Shomali']
    order_list = []
    for FHIR_ID in FHIR_ID_set:
        order = orderInfo.Order(credentials, FHIR_ID, order_date, ENV, CID)
        order_dict, active_order = order()
        # print("active_order: ", active_order)
        # print(order_dict)
        # print("-----------\n")
        if order_dict["Physician"] in phys_list and active_order:
            order_list.append(order_dict)
    print(order_list)
    for order_dict in order_list:
        order_dict["Msg_sent"] = False
        order_action.upload_order(order_dict)
    #
    # # we don't want to generate emails until all recent orders have been uploaded to bigquery
    order_action.send_email()

if __name__ == '__main__':
    main()