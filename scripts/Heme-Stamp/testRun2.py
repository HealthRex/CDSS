import requests
from requests.auth import HTTPBasicAuth
import json
import os
from datetime import date
from dateutil.parser import parse
import xmltodict
from tqdm import tqdm

def main(credentials, csn):
    client_id = credentials['client_id']
    api_prefix = 'https://epic-ic-test.stanfordmed.org/Interconnect-Cloud-SUPW/'
    ReqPatientIDs = requests.get(
        (f"{api_prefix}api/epic/2010/Common/Patient/"
            "GETPATIENTIDENTIFIERS/Patient/Identifiers"),
        params={'PatientID': csn, 'PatientIDType': 'CSN'},
        headers={'Content-Type': 'application/json; charset=utf-8',
                     'Epic-Client-ID': client_id},
        auth=HTTPBasicAuth(credentials["username"], credentials["password"])
    )
    patient_json = json.loads(ReqPatientIDs.text)

    patient_dict = {}
    for id_load in patient_json["Identifiers"]:
        patient_dict[id_load["IDType"]] = id_load["ID"]


    # GET INFORMATION REGARDING THE ORDER
    # procedure_request = requests.get(
    #     f"{api_prefix}/api/FHIR/STU3/ProcedureRequest",
    #     params={'patient': patient_dict['FHIR STU3']},
    #     headers={'Content-Type': 'application/json; charset=utf-8',
    #              'Epic-Client-ID': client_id},
    #     auth=HTTPBasicAuth(credentials["username"],
    #                        credentials["password"])
    # )
    # patient_orders = xmltodict.parse(procedure_request.text)
    # return patient_orders

    request_results = requests.get(
        (f'{api_prefix}api/epic/2010/Common/Patient/'
         'GETPATIENTDEMOGRAPHICS/Patient/Demographics'),
        params={'PatientID': csn,
                'PatientIDType': 'CSN'},
        headers={'Content-Type': 'application/json; charset=utf-8',
                 'Epic-Client-ID': client_id},
        auth=HTTPBasicAuth(credentials["username"],
                           credentials["password"])
    )

    def calculate_age(born):
        today = date.today()
        return today.year - born.year - ((today.month, today.day)
                                         < (born.month, born.day))

    demographic_json = json.loads(request_results.text)
    age = calculate_age(parse(demographic_json["DateOfBirth"]))
    sex = demographic_json['Gender']
    name = demographic_json['Name']['FirstName'] + " " + demographic_json['Name']['LastName']
    demo_info = (age, sex, name)

    base_name = "WBC"
    lab_result_packet = {
        "PatientID": csn,
        "PatientIDType": "CSN",
        "UserID": "Z0002000",
        "UserIDType": "External",
        "MaxNumberOfResults": 200,
        "FromInstant": "",
        "ComponentTypes":
            [{"Value": base_name, "Type": "base-name"}]
    }
    lab_component_packet = json.dumps(lab_result_packet)
    lab_component_response = requests.post(
        (f'{api_prefix}api/epic/2014/Results/Utility/'
         'GETPATIENTRESULTCOMPONENTS/ResultComponents'),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'Epic-Client-ID': client_id
        },
        auth=HTTPBasicAuth(credentials["username"],
                           credentials["password"]),
        data=lab_component_packet
    )
    lab_response = json.loads(lab_component_response.text)

    if lab_response["ResultComponents"]:
        for i in range(len(lab_response["ResultComponents"])):
            resp = lab_response["ResultComponents"][i]
            value = resp["Value"][0]
            resultDate = resp['ResultDate']
            print("-----------")
            print("value: ", value)
            print("date: ", resultDate)







if __name__ == '__main__':
    with open(os.path.join(os.sys.path[0], "live_HS.confg"), "r") as json_file:
        creds_test = json.load(json_file)
    output = main(credentials=creds_test, csn=creds_test['ex_csn'])
    print(output)
