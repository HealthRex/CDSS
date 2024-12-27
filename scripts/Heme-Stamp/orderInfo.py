import requests
from requests.auth import HTTPBasicAuth
import json
import xmltodict
from datetime import date, datetime
from dateutil.parser import parse
import re

class Order(object):
    def __init__(self, credentials, fhir_id, order_date, env, cid, order_status="active"):
        self.credentials = credentials
        self.FHIR_ID = fhir_id
        self.date = order_date
        self.client_id = cid
        self.api_prefix = env
        self.order_status = order_status

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
        return (order_dict, active_order)

    def get_ordering_phys(self):
        active_order = True
        physician = ""
        ordered_date = ""
        procedure_request = requests.get(
            f"{self.api_prefix}/api/FHIR/STU3/ProcedureRequest",
            params={'patient': self.FHIR_ID, 'status': self.order_status},
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'Epic-Client-ID': self.client_id},
            auth=HTTPBasicAuth(self.credentials["username"],
                               self.credentials["password"])
        )
        patient_orders = xmltodict.parse(procedure_request.text)
        pt_json = json.loads(json.dumps(patient_orders))

        if 'Bundle' not in pt_json:
            active_order = False
        else:
            pt_json = pt_json['Bundle']['entry']

            i_list = []
            if isinstance(pt_json, dict):
                if 'resource' in pt_json.keys():
                    i_val = pt_json['resource']
                    if 'ProcedureRequest' in i_val.keys():
                        i_val = i_val['ProcedureRequest']
                    i_list.append(i_val)

            elif isinstance(pt_json, list):
                for x in range(len(pt_json)):
                    if isinstance(pt_json[x], dict) and 'resource' in pt_json[x].keys():
                        i_val = pt_json[x]['resource']
                        if isinstance(i_val, dict) and 'ProcedureRequest' in i_val.keys():
                            i_val = i_val['ProcedureRequest']
                        i_list.append(i_val)

            HS_orders = []

            for v in range(len(i_list)):

                if isinstance(i_list[v], dict) and 'code' in i_list[v].keys() and \
                        isinstance(i_list[v]['code'], dict) and 'coding' in i_list[v]['code'].keys():

                    has_heme = re.search(".*heme.*", str(i_list[v]['code']['coding']).lower())
                    has_ngs = re.search(".*ngs.*", str(i_list[v]['code']['coding']).lower())
                    has_stamp = re.search(".*stamp.*", str(i_list[v]['code']['coding']).lower())
                    if has_heme is not None and has_ngs is not None and has_stamp is not None:
                        print('OUTPUT')
                        print(i_list[v]['code']['coding'])
                        phys = i_list[v]['requester']['agent']['display']['@value']

                        if isinstance(i_list[v], dict) and 'authoredOn' in i_list[v].keys():
                            authored_date = i_list[v]['authoredOn']['@value']
                        else:
                            print("NO AUTHOR")
                            print("FHIR ID: ", self.FHIR_ID)
                            authored_date = i_list[v]['occurrenceTiming']['repeat']['boundsPeriod']['start']['@value']
                        authored_date_conv = datetime.strptime(authored_date, "%Y-%m-%dT%H:%M:%SZ").date()
                        if authored_date_conv <= self.date:
                            HS_orders.append((phys, authored_date))


            if len(HS_orders) > 0:
                HS_orders.sort(key=lambda tup: datetime.strptime(tup[1], "%Y-%m-%dT%H:%M:%SZ"))

                physician, ordered_date = HS_orders[-1]

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
                value = resp["Value"]
                if value is not None:
                    value = value[0]
                result_date = resp['ResultDate']
                lab_results_dict[result_date] = value
                if datetime.strptime(result_date,
                                     '%m/%d/%Y').date() <= self.date and not date_found and value is not None:
                    date_found = True
                    lab_result = value

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
