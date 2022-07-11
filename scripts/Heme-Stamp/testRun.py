import requests
from requests.auth import HTTPBasicAuth
import json
import os
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



    # lab_result_packet = {
    #     "PatientID": csn,
    #     "PatientIDType": "CSN",
    #     "UserID": "Z0002000",
    #     "UserIDType": "External",
    #     "MaxNumberOfResults": 200,
    #     "FromInstant": "",
    #     "ComponentTypes":
    #         [{"Value": "HSTAMPMETHOD", "Type": "base-name"}] #HSTAMPMETHOD
    # }
    # lab_component_packet = json.dumps(lab_result_packet)
    # lab_component_response = requests.post(
    #     (f'{api_prefix}api/epic/2014/Results/Utility/'
    #      'GETPATIENTRESULTCOMPONENTS/ResultComponents'),
    #     headers={
    #         'Content-Type': 'application/json; charset=utf-8',
    #         'Epic-Client-ID': client_id
    #     },
    #     auth=HTTPBasicAuth(credentials["username"],
    #                        credentials["password"]),
    #     data=lab_component_packet
    # )
    #
    # print("lab_component_response was acquired")
    # return lab_component_response


    # observation = requests.get(
    #     (f"{api_prefix}api/FHIR/R4/Observation"),
    #     params={
    #         'patient': patient_dict['FHIR'],
    #         'category': 'laboratory'
    #     },
    #     headers={'Content-Type': 'application/json; charset=utf-8',
    #                  'Epic-Client-ID': client_id},
    #     auth=HTTPBasicAuth(credentials["username"], credentials["password"])
    # )
    # print("observation fetched")
    # return observation

    # serviceRequest = requests.get(
    #     (f"{api_prefix}api/FHIR/R4/ServiceRequest"),
    #     params={"ID": "esGKl7r4CvM422pc91Bu3cLSUMsebQTLSpH4Kdufx3KY3"},
    #     headers={'Content-Type': 'application/json; charset=utf-8', 'Epic-Client-ID': client_id},
    #     auth=HTTPBasicAuth(credentials["username"], credentials["password"])
    # )
    # return serviceRequest

    procedure_request = requests.get(
        f"{api_prefix}/api/FHIR/STU3/ProcedureRequest",
        params={'patient': patient_dict['FHIR STU3']},
        headers={'Content-Type': 'application/json; charset=utf-8',
                 'Epic-Client-ID': client_id},
        auth=HTTPBasicAuth(credentials["username"],
                           credentials["password"])
    )
    patient_orders = xmltodict.parse(procedure_request.text)
    return patient_orders


if __name__ == '__main__':
    # with open(os.path.join(os.sys.path[0], "credentials.confg"), "r") as json_file:
    #     creds = json.load(json_file)
    # output = main(credentials=creds, csn=creds['ex_csn'])
    # print(output.json())

    with open(os.path.join(os.sys.path[0], "live_HS.confg"), "r") as json_file:
        creds_test = json.load(json_file)
    output = main(credentials=creds_test, csn=creds_test['ex_csn'])
    #val = output['Bundle']['entry'][0]['resource']['ProcedureRequest']['requester']['agent']['display']
    #val = output['Bundle']['entry']['display']['@value']
    #if val == 'LABHSTAMPBT'
    #print(output['Bundle']['entry'][0]["code"])

    #print(output['Bundle']['entry'][0]['resource']['ProcedureRequest']['code']['coding'][0]['code']['@value'])
    num_outpt = len(output['Bundle']['entry'])
    vals = []
    for i in range(num_outpt):
        val = output['Bundle']['entry'][i]['resource']['ProcedureRequest']['code']['coding']
        print(len(val))
        if len(val) > 0:
            print(val)
            for j in range(len(val)):
                print(val[j])
                print("----")
                vals.append(val[j]['code']['@value'])
        else:
            val = val['code']['@value']
        vals.append(val)
    print(vals)
