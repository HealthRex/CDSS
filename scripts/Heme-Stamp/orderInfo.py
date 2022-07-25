import requests
from requests.auth import HTTPBasicAuth
import json
import os
import xmltodict
from datetime import date, datetime
from dateutil.parser import parse

class Order(object):
    def __init__(self, credentials, fhir_id, order_date, env, cid):
        self.credentials = credentials
        self.FHIR_ID = fhir_id
        self.date = order_date
        self.client_id = cid
        self.api_prefix = env

    def __call__(self):
        order_dict = {}
        order_dict['FHIR_ID'] = self.FHIR_ID
        order_dict['Physician'], order_dict['Ordered'], active_order = self.get_ordering_phys()
        if active_order:
            lab_names = ['WBC', 'Hgb']
            for lab in lab_names:
                order_dict[lab] = self.get_lab_result(lab)
            age, sex, name = self.get_demographics()
            age_sex = str(age) + sex[0]
            order_dict['Age'], order_dict['Name'] = age_sex, name
            order_dict['MRN'] = self.get_other_identifiers()
            order_dict['Physician'] = order_dict['Physician'][:-4]
            order_dict['Ordered'] = order_dict['Ordered'].split("T")[0]
        return (order_dict, active_order)

    def get_ordering_phys(self):
        active_order = True
        physician = ""
        ordered_date = ""
        procedure_request = requests.get(
            f"{self.api_prefix}/api/FHIR/STU3/ProcedureRequest",
            params={'patient': self.FHIR_ID, 'status': 'canceled'},  # , 'status': 'completed'
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'Epic-Client-ID': self.client_id},
            auth=HTTPBasicAuth(self.credentials["username"],
                               self.credentials["password"])
        )
        patient_orders = xmltodict.parse(procedure_request.text)
        pt_json = json.loads(json.dumps(patient_orders))
        if 'Bundle' not in pt_json:
            active_order = False
            print('1', pt_json['OperationOutcome']['@xmlns'])
            print('2', pt_json['OperationOutcome']['issue'].keys())
        else:
            pt_json = pt_json['Bundle']['entry']

            HS_names = {"STANFORD HEME-STAMP NGS PANEL BLOOD",
                        "STANFORD HEME-STAMP NGS PANEL, NON-BLOOD"}


            phys_names = {'Rondeep Singh Brar, MD', 'David Joseph Iberri, MD', 'William Elias Shomali, MD'}

            i_list = []
            for x in range(len(pt_json)):
                # print("json keys: ", pt_json[x].keys())
                i_val = pt_json[x]['resource']
                if 'ProcedureRequest' in i_val.keys():
                    i_val = i_val['ProcedureRequest']
                else:
                    print('3', i_val.keys())
                    print(i_val['OperationOutcome'])
                    print(self.FHIR_ID)
                i_list.append(i_val)

            all_HS_orders = []
            HS_orders = []

            for v in range(len(i_list)):
                if 'code' in i_list[v].keys() and 'coding' in i_list[v]['code'].keys():
                    if isinstance(i_list[v]['code']['coding'], list):
                        for a in range(len(i_list[v]['code']['coding'])):
                            lab = i_list[v]['code']['coding'][a]['display']['@value']
                            phys = i_list[v]['requester']['agent']['display']['@value']
                            authored_date = i_list[v]
                            if 'authoredOn' in authored_date.keys():
                                authored_date = authored_date['authoredOn']['@value']
                            else:
                                # authored_date = authored_date['requester']['agent']['display']['@value']
                                authored_date = authored_date['occurrenceTiming']['repeat']['boundsPeriod']['start']['@value']

                            if lab in HS_names:
                                HS_orders.append((lab, phys, authored_date))
                                # if phys in phys_names:
                                #     HS_orders.append((lab, phys, authored_date))

                    else:
                        lab = i_list[v]['code']['coding']['display']['@value']
                        phys = i_list[v]['requester']['agent']['display']['@value']
                        authored_date = i_list[v]
                        if 'authoredOn' in authored_date.keys():
                            authored_date = authored_date['authoredOn']['@value']
                        else:
                            # authored_date = authored_date['requester']['agent']['display']['@value']
                            authored_date = authored_date['occurrenceTiming']['repeat']['boundsPeriod']['start'][
                                '@value']

                        if lab in HS_names:
                            HS_orders.append((lab, phys, authored_date))
                            # if phys in phys_names:
                            #     HS_orders.append((lab, phys, authored_date))
                else:
                    # print('4', i_list[v].keys())
                    if 'code' in i_list[v].keys():
                        print('5', i_list[v]['code'].keys())
                        print(i_list[v]['code']['text'])
                        print(self.FHIR_ID)
                    else:
                        print('4', i_list[v].keys())

            #print("all HS orders: ", all_HS_orders)
            print("HS orders: ", HS_orders)

            if len(HS_orders) > 0:
                physician = HS_orders[-1][1]
                ordered_date = HS_orders[-1][2]
        return (physician, ordered_date, active_order)

    def get_lab_result(self, base_name):
        lab_results_dict = {}
        lab_result_packet = {
            "PatientID": self.FHIR_ID,
            "PatientIDType": "FHIR STU3",
            "UserID": "Z0002000",
            "UserIDType": "External",
            "MaxNumberOfResults": 200,
            "FromInstant": "",
            "ComponentTypes":
                [{"Value": base_name, "Type": "base-name"}]
        }
        lab_component_packet = json.dumps(lab_result_packet)
        lab_component_response = requests.post(
            (f'{self.api_prefix}api/epic/2014/Results/Utility/'
             'GETPATIENTRESULTCOMPONENTS/ResultComponents'),
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'Epic-Client-ID': self.client_id
            },
            auth=HTTPBasicAuth(self.credentials["username"],
                               self.credentials["password"]),
            data=lab_component_packet
        )
        lab_response = json.loads(lab_component_response.text)


        date_found = False
        lab_result = 0

        if lab_response["ResultComponents"]:
            for i in range(len(lab_response["ResultComponents"])):
                resp = lab_response["ResultComponents"][i]
                #print("resp: ", resp)
                value = resp["Value"]
                if value is not None:
                    value = value[0]
                result_date = resp['ResultDate']
                lab_results_dict[result_date] = value
                if datetime.strptime(result_date, '%m/%d/%Y').date() <= self.date and not date_found and value is not None:
                    recent_date = result_date
                    # print("recent date: ", recent_date)
                    date_found = True
                    lab_result = value
                # print("-----------")
                # print("value: ", value)
                # print("date: ", result_date)

        return lab_result

    def get_demographics(self):
        request_results = requests.get(
            (f'{self.api_prefix}api/epic/2010/Common/Patient/'
             'GETPATIENTDEMOGRAPHICS/Patient/Demographics'),
            params={'PatientID': self.FHIR_ID,
                    'PatientIDType': 'FHIR STU3'},
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'Epic-Client-ID': self.client_id},
            auth=HTTPBasicAuth(self.credentials["username"],
                               self.credentials["password"])
        )

        demographic_json = json.loads(request_results.text)
        #print(demographic_json)
        age = self.calculate_age(parse(demographic_json["DateOfBirth"]))
        sex = demographic_json['Gender']
        name = demographic_json['Name']['FirstName'] + " " + demographic_json['Name']['LastName']
        demo_info = (age, sex, name)
        return demo_info

    def calculate_age(self, date_born):
        today = date.today()
        return today.year - date_born.year - ((today.month, today.day) < (date_born.month, date_born.day))

    def get_other_identifiers(self):
        ReqPatientIDs = requests.get(
            (f"{self.api_prefix}api/epic/2010/Common/Patient/"
             "GETPATIENTIDENTIFIERS/Patient/Identifiers"),
            params={'PatientID': self.FHIR_ID, 'PatientIDType': 'FHIR STU3'},
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'Epic-Client-ID': self.client_id},
            auth=HTTPBasicAuth(self.credentials["username"], self.credentials["password"])
        )
        patient_json = json.loads(ReqPatientIDs.text)
        patient_dict = {}
        for id_load in patient_json["Identifiers"]:
            patient_dict[id_load["IDType"]] = id_load["ID"]

        return patient_dict['SHCMRN']
