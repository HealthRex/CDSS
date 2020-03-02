#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
import logging
import pytz
import random
import tempfile
import time

from datetime import datetime

import unittest

from parameterized import parameterized
from medinfo.dataconversion.test.Const import RUNNER_VERBOSITY
from medinfo.dataconversion.Const import TEMPLATE_MEDICATION_PREFIX
from medinfo.dataconversion.Util import log

from medinfo.db.test.Util import DBTestCase

from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel

from medinfo.dataconversion.starr_conv import STARROrderProcConversion
from medinfo.dataconversion.starr_conv import STARRUtil

TEST_SOURCE_TABLE = 'test_dataset.starr_order_proc'
TEST_ORDERSET_TABLE = 'test_dataset.starr_proc_orderset'

TEST_DEST_DATASET = 'test_dataset'


ORDERING_MODES = [
    'Inpatient',
    'Outpatient'
]

ORDER_TYPES = [
    None,
    "Pharmacy Consult",
    "Sleep Center",
    "HB Chargeables",
    "Code Status",
    "Pathology",
    "GI",
    "Evercore",
    "Nursing Referral",
    "Respiratory Care",
    "Cardiac Angio",
    "Pharmacy Supplies",
    "Bedside Procedure",
    "Therapeutic Recreation Orderables",
    "PR Charge",
    "Procedures",
    "PT",
    "OT",
    "Cast Room",
    "Bronchoscopy",
    "Manual Entry Imaging",
    "Manual Entry Cardiac Angio",
    "Lab",
    "Blood Bank",
    "PFT",
    "Vascular Ultrasound",
    "IVF Labs",
    "SLP",
    "Diet Communication",
    "Manual Entry Procedures",
    "Imaging Non-Reportable",
    "Nursing",
    "Diet",
    "Precaution",
    "Immunization/Injection",
    "Zeiss",
    "General Supply",
    "Legal",
    "Manual Entry Bronchoscopy",
    "Lab Panel",
    "Charge",
    "Imaging",
    "Cath Angio",
    "Device Check",
    "Notify Physician",
    "ENT",
    "Manual Entry Lab",
    "Manual Entry ECHO",
    "Radiation Oncology",
    "Point of Care Testing",
    "ECHO",
    "Lab Only",
    "Microbiology",
    "Generic Surgical History",
    "Admission",
    "Reference Labs",
    "NSG PICC Refer",
    "Transfer",
    "NOURISHMENTS",
    "OB Ultrasound",
    "Restraints",
    "Ophthalmology",
    "Nursing Transfusion",
    "HIV Lab Non-Restricted",
    "Isolation",
    "Other Order Scanned Report",
    "Manual Entry HIV Lab Restricted",
    "Microbiology Culture",
    "ECG",
    "Consult",
    "Outpatient Referral",
    "Neurology",
    "MyHealth Questionnaire Assignment",
    "Transport",
    "Transfusion Communication",
    "Electrophysiology",
    "Vaultstream",
    "filter exclude all",
    "Consult to Cardiology ",
    "REHAB",
    "BB Call Slip",
    "HIV Lab Restricted",
    "Discharge",
    "Surgical Procedures",
    "Language Services"
]

PROC_CODES = [
    "NUR1025",
    "LABPOCGLU",
    "LABCBCD",
    "POC14",
    "LABMETC",
    "NUR1018",
    "LABMETB",
    "99146543",
    "NUR1019",
    "LABMGN",
    "NUR1044",
    "LABCBCO",
    "LABPT",
    "LAB234",
    "99146537",
    "NUR1106",
    "EKG5",
    "RT109",
    "LABSPR",
    "LABPTT",
    "NUR1940",
    "99146539",
    "LABTSH",
    "LABPHOS",
    "NUR194000",
    "NUR762",
    "NUR1068",
    "NUR1613",
    "LABPCG3",
    "LABUA",
    "ADT12",
    "NUR1043",
    "146543",
    "LABA1C",
    "NUR1022",
    "NUR764",
    "IMGDXCH1",
    "LABTYPSNI",
    "NUR1013",
    "DIET990",
    "NUR301",
    "LABBBPRBC",
    "NUR1094",
    "LABCAI",
    "LABURNC",
    "NUR810",
    "LABABG",
    "LABSURG",
    "NUR350",
    "LABLPD",
    "LABHFP",
    "LABUAPRN",
    "DIET102",
    "LABK",
    "NUR30024",
    "99146535",
    "IMGDXCH2",
    "NUR30022",
    "COD2",
    "LABLPDC",
    "LABFT4",
    "LABFK506L",
    "LABLDH",
    "LABTNI",
    "99146541",
    "RT108",
    "NUR1664",
    "NUR4030",
    "146535",
    "LABVD25H",
    "LABARI",
    "LABESRP",
    "LABBLC",
    "NUR1231",
    "LAB230",
    "LABCRP",
    "LABDATACONV",
    "LABCR",
    "ECH15",
    "NURSE 1500",
    "2500147414",
    "PT4",
    "NUR1016",
    "TRN2",
    "LABASI",
    "PHX0003",
    "LABTBP",
    "LABVBG",
    "NUR4067",
    "99214",
    "LABURIC",
    "146541",
    "LABOSR",
    "LABHCTX",
    "LABBLC2",
    "NUR1588",
    "NUR1024",
    "99245",
    "LABALT",
    "LABMB",
    "ADT100",
    "NUR1012",
    "LABNA",
    "LABFER",
    "99215",
    "OT1",
    "DC3",
    "NUR324",
    "LABLIPS",
    "LABCBCS",
    "DC8",
    "LABTSLIP",
    "NUR1373",
    "99205",
    "LABLACWB",
    "DC1",
    "LABAST",
    "NUR372",
    "LABPSA",
    "DC5",
    "NUR775",
    "ADT1",
    "LABB12",
    "LABCK",
    "ADT7",
    "IMGDXCH1P",
    "PT6",
    "LABLAC",
    "IMGXR0023",
    "LABVANPRL",
    "LABROMRS",
    "LABNTBNP",
    "416543",
    "PATH10",
    "RT101",
    "146537",
    "880100004",
    "LABPCTNI",
    "LABTBP1",
    "IMGXR0031",
    "OT2",
    "LABHBSAG",
    "416542",
    "LABHEPAR",
    "RT104",
    "LABTRFS",
    "LABTRIG",
    "NUR1448",
    "LABHCVA",
    "NUR30020",
    "LABPLTS",
    "DIET101",
    "LABPCCR",
    "NUR2241",
    "LABGYN",
    "NUR1060",
    "LABCA",
    "NUR3511",
    "NUR700",
    "REF94",
    "LABBBPPLT",
    "IMGCTH",
    "NUR323",
    "NUR4005",
    "NUR1066",
    "POC24",
    "LABBBPFFP",
    "LABTSHFT4",
    "NUR4044",
    "LABTBIL",
    "NUR811",
    "LABPCCG4V",
    "NUR1991",
    "LABBUN",
    "LABGGT",
    "LABALB",
    "LAB219",
    "IMGDXAB1",
    "LABUALB",
    "LABGLF",
    "NUR4077",
    "NUR1293",
    "LABBMT1",
    "445875",
    "GICOLO",
    "RT72",
    "DC2",
    "LABCHOL",
    "LABPCEG7",
    "NUR716",
    "RES5",
    "LABCDTPCR",
    "RT100",
    "IMGBI0008",
    "RT82",
    "LABCMVQT",
    "DIET122",
    "DIET131",
    "LABLCLPD",
    "POC17"
]

DESCRIPTIONS = [
    "VITAL SIGNS",
    "GLUCOSE BY METER",
    "POC GLUCOSE BY METER",
    "METABOLIC PANEL, COMPREHENSIVE",
    "CBC WITH DIFFERENTIAL",
    "MONITOR INTAKE AND OUTPUT",
    "METABOLIC PANEL, BASIC",
    "CBC WITH DIFF",
    "HX OTH ORD SCAN REPORT",
    "INCENTIVE SPIROMETER (WHILE AWAKE)",
    "MAGNESIUM, SERUM/PLASMA",
    "NURSING PULSE OXIMETRY (SPOT CHECK)",
    "PROTHROMBIN TIME",
    "HX LAB PROC SCAN REPORT",
    "ASSESSMENT FREQUENCY (PSYCH UNIT)",
    "NURSING COMMUNICATION",
    "ECG 12-LEAD",
    "RESP - NEBULIZER",
    "SPECIMEN REMARK",
    "PTT PARTIAL THROMBOPLASTIN TIME",
    "CBC",
    "HX IMAGING PROC SCAN REPORT",
    "TSH",
    "PHOSPHORUS, SERUM/PLASMA",
    "NEUROLOGICAL CHECKS",
    "WEIGHT",
    "ISTAT G3+, ARTERIAL",
    "CBC W/O DIFF",
    "URINALYSIS WITH MICROSCOPIC",
    "DISCHARGE PATIENT",
    "NURSING PULSE OXIMETRY",
    "PERIPHERAL IV INSERTION CARE",
    "NURSING COMMUNICATION(FOR ORDERSET ONLY)",
    "OTHER ORDER SCANNED REPORT",
    "HEMOGLOBIN A1C",
    "RESPIRATORY RATE",
    "XR CHEST 1V",
    "TYPE AND SCREEN",
    "OOB/UP IN CHAIR WITH ASSIST",
    "DIET REGULAR",
    "NEUROVASCULAR ASSESSMENT",
    "SEQUENTIAL COMPRESSION DEVICE (SCD)",
    "RED BLOOD CELLS",
    "AMBULATE WITH ASSISTANCE",
    "URINE CULTURE",
    "SURGICAL PROCEDURE",
    "NOTIFY MD:",
    "HEPATIC FUNCTION PANEL A",
    "DIET NPO",
    "POTASSIUM, SERUM/PLASMA",
    "DISCHARGE PATIENT WHEN CRITERIA MET",
    "HX ECG PROC SCAN REPORT",
    "XR CHEST 2V",
    "FULL CODE",
    "ADMIT TO PHASE",
    "LIPID PANEL WITH CALCULATED LDL",
    "I&O DRAINS OUPUT",
    "T4, FREE",
    "CALCIUM IONIZED, SERUM/PLASMA",
    "TACROLIMUS (FK506)",
    "LIPID PANEL WITH DIRECT LDL",
    "LDH TOTAL, SERUM / PLASMA",
    "TROPONIN I",
    "HX OTH PROC SCAN REPORT",
    "RESP - MDI",
    "SALINE LOCK AND FLUSH",
    "OXYGEN: NASAL CANNULA(NURSING ONLY)",
    "ECG PROCEDURE SCANNED REPORT",
    "CARDIAC MONITOR",
    "VITAMIN D, 25-HYDROXYVITAMIN",
    "ABO/RH (ARI)",
    "SEDIMENTATION RATE (ESR)",
    "MANUAL DIFFERENTIAL/SLIDE REVIEW",
    "BLOOD GASES, ARTERIAL",
    "C - REACTIVE PROTEIN",
    "HISTORICAL RESULT",
    "CREATININE, SERUM/PLASMA",
    "NOTIFY MD:VITAL SIGNS",
    "UHA LAB - SCANNED",
    "PT EVALUATE AND TREAT",
    "MEASURE URINARY OUTPUT",
    "ADMIT TO INPATIENT",
    "ECHO - TRANSTHORACIC ECHO +DOPPLER",
    "PATIENT TRANSPORT",
    "AB SCREEN (ASI)",
    "URINALYSIS SCREEN, CULTURE IF POSITIVE",
    "TRANSCHART CONVERTED LAB DATA",
    "TRANSFUSION BLOOD PRODUCT 1",
    "BLOOD GASES, VENOUS",
    "OXYGEN ADMINISTRATION",
    "EVAL/MGMT OF EST PATIENT LEVEL 4",
    "URIC ACID, SERUM / PLASMA",
    "OTHER PROCEDURE SCANNED REPORT",
    "OUTSIDE SLIDE REVIEW",
    "HEMATOCRIT",
    "BLOOD CULTURE (2 AEROBIC BOTTLES)",
    "OOB",
    "VITAL SIGNS PER PROTOCOL",
    "OFFICE CONSLTJ 80 MIN",
    "ALT, SERUM/PLASMA",
    "CK, MB (MASS)",
    "OOB/UP IN CHAIR",
    "SODIUM, SERUM / PLASMA",
    "FERRITIN",
    "EVAL/MGMT OF EST PATIENT LEVEL 5",
    "OT EVALUATE AND TREAT",
    "PHYSICAL ACTIVITY",
    "PAIN ASSESSMENT",
    "LIPASE",
    "FOLLOW UP INSTRUCTIONS",
    "EVAL/MGMT OF NEW PATIENT LEVEL 5",
    "LACTATE, WHOLE BLOOD",
    "DISCHARGE DIET",
    "BLOOD CULTURE (AEROBIC & ANAEROBIC BOTTLES)",
    "AST, SERUM/PLASMA",
    "PSA",
    "REASON TO CALL YOUR PHYSICIAN",
    "WOUND CARE",
    "ARTERIAL BLOOD GAS",
    "VITAMIN B12",
    "CREATINE KINASE, TOTAL",
    "TRANSFUSION SERVICE CALL SLIP",
    "XR CHEST 1V PORTABLE",
    "PT ONGOING TREATMENT",
    "LACTIC ACID",
    "XR CHEST 1 VIEW",
    "FOLEY RETENTION CATHETER",
    "CBC WITH DIFF AND SLIDE REVIEW",
    "VANCOMYCIN TROUGH LEVEL",
    "NT - PROBNP",
    "UHA FLU SHOT PROTOCOL AUTHORIZATION",
    "BLOOD TYPE VERIFICATION",
    "RESP - FLUTTER/PEP THERAPY",
    "LAB PROCEDURE SCANNED REPORT",
    "URINALYSIS, SCREEN FOR CULTURE",
    "SIMPLE AIRWAY",
    "ISTAT TROPONIN I",
    "TRANSFUSION BLOOD PRODUCT 2",
    "MRSA SCREEN",
    "LIPID PANEL",
    "XR CHEST 2 VIEWS",
    "OT ONGOING TREATMENT",
    "UHA FLU SHOT PROTOCOL AUTHORIZATION 2017-2018",
    "RESP - VENTILATOR SETTINGS",
    "TRANSFERRIN SATURATION",
    "TRIGLYCERIDES, SERUM / PLASMA",
    "JACKSON PRATT DRAIN",
    "RASS SEDATION ASSESSMENT",
    "PLATELET COUNT",
    "DIET CLEAR LIQUID",
    "CDU VITAL SIGNS",
    "ISTAT CREATININE",
    "UP AD LIB",
    "PAP SMEAR",
    "EARLY AMBULATION",
    "CALCIUM, SERUM/PLASMA",
    "RISK FOR VENOUS THROMBOEMBOLISM - VTE RISK ASSESSMENT",
    "TRANSFUSE RED BLOOD CELLS",
    "TRANSFER PATIENT",
    "REFERRAL TO PHYSICAL THERAPY",
    "PLATELET APHERESIS PRODUCT",
    "CT HEAD",
    "TEMPERATURE THERAPY",
    "DRAIN CARE",
    "TURN, COUGH, DEEP BREATHE",
    "POC ISTAT TROPONIN I",
    "FRESH FROZEN PLASMA PRODUCT",
    "TSH W/ REFLEX FT4",
    "WEAN O2 THERAPY",
    "BILIRUBIN TOTAL, SERUM/PLASMA",
    "HBSAG",
    "IRRIGATE TUBE/DRAIN",
    "ISTAT CG4,VENOUS",
    "UREA NITROGEN, SERUM/PLASMA",
    "GAMMA - GLUTAMYL TRANSFERASE",
    "ALBUMIN, SERUM/PLASMA",
    "XR ABDOMEN 1V",
    "HEPATITIS C AB IGG",
    "ALBUMIN WITH CREATININE, URINE (RANDOM)",
    "GLUCOSE FASTING",
    "TREATMENT PARAMETERS 1",
    "D/C BY ESCORT IF D/C CRITERIA IS MET",
    "ADMIT/PLACE PATIENT",
    "BMT PANEL 1",
    "POPULATION HEALTH PROTOCOL AUTHORIZATION",
    "RESP - CHEST PHYSIOTHERAPY",
    "DISCHARGE WOUND CARE",
    "CHOLESTEROL TOTAL, SERUM/PLASMA",
    "ISTAT EG7, ARTERIAL",
    "POC URINE DIPSTICK",
    "BLOOD CULTURE (AEROBIC & ANAEROBIC BOTTLE)",
    "DC IV",
    "RAINBOW DRAW (FOR ED/RRT/CODE BLUE ONLY)",
    "RESP - INTRAPULMONARY PERCUSSIVE VENTILATION",
    "MAMMO BREAST SCREENING",
    "RESP - UNLISTED RESPIRATORY CARE ORDER",
    "CALCIUM IONIZED, WHOLE BLOOD",
    "CHECK TUBE FEEDING",
    "DIET NUTRITIONAL SUPPLEMENTS",
    "DIET NPO AFTER MIDNIGHT"
]

PROTOCOL_NAMES = [
    "IP GENERAL DISCHARGE ORDER SET",
    "IP MED GENERAL ADMIT",
    "ANE PACU ",
    "PRE-ADMISSION/PRE-OP ORDERS",
    "IP GI ENDOSCOPY PRE/POSTOP PROCEDURE",
    "RETIRED ANE PACU (OUTPATIENT)",
    "IP/ED GENERAL TRANSFUSION",
    "IP ICU/CCU GENERAL ADMIT",
    "RETIRED P CTS ICU CARDIAC SURGERY POSTOP",
    "IP ORT TOTAL JOINT REPLACEMENT",
    "IP GEN HEPARIN INFUSION PROTOCOLS",
    "IP SUR GENERAL ADMIT",
    "IP INTERAGENCY DISCHARGE ORDERS",
    "IP PAI PATIENT CONTROLLED ANALGESIA (PCA)",
    "IP SUBCUTANEOUS INSULIN ORDER SET",
    "IP CAR CARDIOLOGY POST PROCEDURE - INPATIENT",
    "IP RAD INTERVENTIONAL RADIOLOGY POSTOP (SAME DAY DISCHARGE)",
    "IP NSR ICU NEUROSURGERY POSTOPERATIVE",
    "IP GEN INTERAGENCY DISCHARGE ORDERS",
    "IP CAR CARDIOLOGY PRE PROCEDURE",
    "IP ORT TRAUMA",
    "IP NSR NEUROSURGERY ADMISSION/POST-OP",
    "IP RAD INTERVENTIONAL RADIOLOGY PRE-PROCEDURE",
    "RETIRED IP CTS CARDIAC SURGERY TRANSFER",
    "IP INSULIN CONTINUOUS IV INFUSION",
    "INTRA-OPERATIVE BLOOD PRODUCT AND TRANSFUSION ORDERS",
    "IP PAI EPIDURAL ANALGESIA POSTOP",
    "IP PSY PSYCHIATRY ADMIT",
    "IP ICU SUR/TRAUMA  ADMIT",
    "SHC AMB ONC BMT",
    "ED GENERAL COMPLAINT",
    "NURSING TRIAGE SEPSIS NURSING PROTOCOL",
    "AMB ALG IMMUNOTHERAPY MMC",
    "IP VAST RN POST PLACEMENT (VAST RN ONLY)",
    "IP NEU GENERAL WARD ADMIT",
    "IP CAR GENERAL ADMIT",
    "AMB PED IMMUNIZATIONS MMC",
    "ED CHEST PAIN",
    "RETIRED IP PAMF ORTHO THA",
    "IP CTS LUNG RESECTION POSTOP",
    "CDU CHEST PAIN OBSERVATION",
    "IP SUR COLON/RECTAL/SMALL BOWEL RESECTION POSTOP",
    "IP RAD NEURORADIOLOGY PRE-PROCEDURE",
    "ED ABDOMINAL PAIN ",
    "IP ANE ANESTHESIA PREOP",
    "IP CTS CARDIAC SURGERY ADMISSION",
    "IP CAR ICD/PACEMAKER IMPLANT (POST-PROCEDURE)",
    "CDU GENERAL PROTOCOL OBSERVATION",
    "SVC ANE PACU",
    "IP ENT HEAD AND NECK POSTOP",
    "AMB SLEEP OFFICE VISIT",
    "(RETIRED) IP PICC LINE PLACEMENT / EXCHANGE",
    "IP CAR EPS/ABLATION (PRE-PROCEDURE)",
    "CC HEME BONE MARROW BIOPSY AND ASPIRATE",
    "OPH CATARACT PERIOPERATIVE ORDERS RIGHT EYE",
    "OPH CATARACT PERIOPERATIVE ORDERS LEFT EYE",
    "IP SUR GENERAL POSTOP",
    "IP PULM RH CATH POST",
    "AMB HM UHA SUPER SMARTSET",
    "ED TRAUMA 97",
    "NURSING TRIAGE CARDIAC COMPLAINTS PROTOCOL",
    "CC RAD ONC PRE-SIMULATION",
    "CC BMT BONE MARROW BIOPSY AND ASPIRATE",
    "IP REN HEMODIALYSIS",
    "IP PULM RH CATH PREOP",
    "IP CAR ICD/PACEMAKER IMPLANT(PRE-PROCEDURE)",
    "AMB LIV PRE-TRANSPLANT STANFORD DEFAULTED WISH LIST ORDERS",
    "IP RAD NEURORADIOLOGY POST-PROCEDURE",
    "IP PAI PERIPHERAL NERVE CATHETER/REGIONAL ANALGESIA ADMIT",
    "ED FLOOR  HOLDING ORDERS",
    "SVC IP GEN GENERAL ADMIT",
    "IP CAR EPS/ABLATION (POST-PROCEDURE)",
    "AMB HM SHC SUPER SMARTSET",
    "IP GYN  GENERAL ADMISSION",
    "IP MED CYSTIC FIBROSIS ADMIT",
    "IP CTS ICU CARDIAC SURGERY POSTOP",
    "IP SUR BARIATRIC SURGERY POSTOP",
    "IP SUR DAY OF SURGERY ORDERS",
    "ED ADMIT",
    "IP GU RADICAL CYSTECTOMY POSTOP",
    "IP CAPR CARDIOVERSION",
    "UHA IMM ADULT",
    "NURSING TRIAGE ABDOMINAL PAIN PROTOCOL",
    "RETIRED IP ORT SPINAL FUSION POSTOP",
    "IP SUBCUTANEOUS INSULIN ADJUSTMENT ORDER SET",
    "IP GEN BRONCHOSCOPY PRE/INTRA/POST",
    "AMB SLEEP ATTENDINGS SLEEP STUDY",
    "IP GEN COMFORT CARE - NON ICU UNITS",
    "ED TIA PATHWAY",
    "CC APHERESIS HPC-A COLLECTION",
    "PRE-ADMISSION/PRE-OP ORDERS CV SURGERY",
    "PEDIATRIC IMMUNIZATIONS FOR UHA",
    "SVC IP GEN DISCHARGE",
    "NURSING TRIAGE STROKE PROTOCOL",
    "RETIRED IP NSR NEUROSURGERY TRANSFER ORDERS",
    "IP ENT MAXILLOFACIAL SURGERY POSTOP",
    "RETIRED IP NSR NEURO SPINE",
    "SVC IP GI ENDOSCOPY PRE/POST PROCEDURE",
    "IP PSY ASC ECT",
    "IP PLS GENERAL POSTOP",
    "SVC SUR PRE-ADMISSION/PRE-OP",
    "IP RAD INTERVENTIONAL RADIOLOGY POSTOP (WITH ADMISSION)",
    "AMB ORT HAND_WRIST",
    "IP ORT SHOULDER ELBOW ADMISSION POSTOP",
    "IP VAS GENERAL ADMIT",
    "IP TRS LIVER TRANSPLANT POSTOP",
    "INPT/AMB BMT DONOR/AUTOLOGOUS PT VIROLOGY",
    "IP INSULIN TRANSITION OFF IV INFUSION",
    "ED SHORTNESS OF BREATH",
    "SHC AMB ONC LYMPHOMA ONCOLOGY",
    "OPH OCULOPLASTICS PERIOPERATIVE ORDERS",
    "IP PLS BREAST RECONSTRUCT UNILAT/BILATERAL  FREE TRAM FLAP",
    "IP GU RADICAL PROSTATECTOMY POSTOP",
    "IP LAB SPECIMEN TESTING, CSF",
    "IP TRS KIDNEY/PANCREASE TRANSPLANT RECIPIENT PREOP",
    "AMB HEART TRANSPLANT ANNUAL STANFORD RN ORDERS",
    "AMB POSITIVE CARE HIV/AIDS DIAGNOSIS",
    "AMB NEU MULTIPLE SCLEROSIS",
    "IP NEU STROKE ADMISSION",
    "IP VAD ICU POST OP",
    "IP LAB SPECIMEN TESTING, BLOOD CULTURE - INFECTIOUS AGENT DETECTION",
    "IP TRS KIDNEY AND/-OR  PANCREAS RECIPIENT POSTOP",
    "IP VAS GENERAL POSTOP",
    "RETIRED IP ENT GENERAL POSTOP",
    "IP LABS CULTURES",
    "IP REH PHASE I EPILEPSY ADMIT",
    "IP NEU ICU STROKE ISCHEMIC/INTRACEREBRAL HEMORRHAGE ADMIT",
    "IP GEN TUBE FEEDING",
    "IP BMT ALLOGENEIC READMISSION",
    "AMB REI P - FEMALE ORDER SET",
    "ED PSYCH/DRUG PROBLEM",
    "ED TRAUMA RADIOLOGY",
    "IP TRS HEART TRANSPLANT POSTOP",
    "IP TRANSESOPHAGEAL ECHO (TEE) ORDER SET",
    "RETIRED IP GEN PACU ORDERS",
    "CC APHERESIS THERAPEUTIC PLASMA EXCHANGE",
    "AMB AWCC WOUND CARE",
    " AMB URO URODYNAMICS",
    "CDU TIA",
    "IP GYN MINIMALLY INVASIVE SURGERY POSTOP",
    "IP CTS TAVR CV POSTOP",
    "IP GU GENERAL ADMIT",
    "SVC IP ANE ANESTHESIA PREOP",
    "NURSING TRIAGE PAIN MANAGEMENT PROTOCOL",
    "AMB LUNG/HEART-LUNG PRE-EVALUATION STUDIES",
    "IP ENT GENERAL ADMISSION",
    "IP CTS CARDIAC SURGERY TRANSFER",
    "AMB HEART TRANSPLANT ROUTINE STANFORD RN ORDERS",
    "CC APHERESIS EXTRACORPOREAL PHOTOPHERESIS (ECP)",
    "RETIRED IP PAI SINGLE SHOT INTRATHECAL NARCOTICS POSTOP",
    "IP CAR CONGESTIVE HEART FAILURE",
    "RETIRED IP PAMF ORTHO SPINE",
    "CDU ABDOMINAL PAIN OBSERVATION",
    "IP TRS LUNG, HEART-LUNG TRANSPLANT POSTOP",
    "IP GYN EXLAP/TAH/BSO GENERAL",
    "IP LAB SPECIMEN TESTING, RESPIRATORY SECRETIONS",
    "AMB REI P - PHYSICIAN ORDER FOR RETRIEVAL / TRANSFER PROCEDURE",
    "OP TRANSFUSION ORDERS RECURRING",
    "OPH RETINA PERIOPERATIVE ORDERS LEFT EYE",
    "RETIRED OP TRANSFUSION ORDERS ONE TIME",
    "IP GU TURP/TURBT POSTOP",
    "SVC IP NB NEWBORN NURSERY ADMISSION",
    "OPH RETINA PERIOPERATIVE ORDERS RIGHT EYE",
    "RETIRED IP LAB TRANSFUSION SERVICE,  SPECIAL NEEDS",
    "IP NSR CERVICAL AND LUMBAR FUSIONS",
    "ED TRAUMA 99",
    "IP SUR BREAST PROCEDURES POSTOP",
    "AMB IGM ACUPUNCTURE WITHOUT E & M CODES",
    "AMB REI P - IVF LAB ORDERS",
    "AMB ORT SPINE PMR",
    "AMB IMM ADULT",
    "IP GEN TPN/PPN  ADULT PROTOCOL",
    "IP ICU END OF LIFE CARE",
    "PED ADOLESCENT WELL FEMALE UHA",
    "IP REN CONTINUOUS RENAL REPLACEMENT THERAPY(CRRT)",
    "AMB FLU CLINIC",
    "CDU SYNCOPE OBSERVATION",
    "IP POST PROCEDURE ORDERS PARACENTESIS",
    "RETIRED IP OPH RETINA POSTOP ",
    "SVC IP OB INTRAPARTUM ADMISSION",
    "SHC AMB INFLUENZA VACCINE MASTER",
    "IP GEN INSULIN INFUSION ICU",
    "SVC IP ANE OB LABOR EPIDURAL",
    "RETIRED IP NSR NEURO SPINE TRANSFER",
    "IP/ED INSULIN - DIABETIC KETOACIDOSIS (DKA)/ HYPEROSMOLAR HYPERGLYCEMIC STATE (HHS)",
    "AMB PED ADOLESCENT WELL MALE UHA",
    "ED FEVER/NEUTROPENIA",
    "RETIRED IP GYN LAPAROSCOPY POSTOP",
    "IP INSULIN PUMP (CONTINUOUS SUBCUTANEOUS INSULIN INFUSION (CSII))",
    "ANE ECT PACU ORDERS",
    "IP BMT AUTOLOGOUS READMISSION ORDERS",
    "RETIRED IP ENT - HEAD AND NECK ADMISSION-PREOP",
    "IP RXWARFARIN PROTOCOL (PHARMACY USE ONLY)",
    "IP TRS HEART TRANSPLANT PREOP",
    "IP ORT TUMOR POSTOP",
    "IP CAR CARDIOLOGY POST PROCEDURE - OUTPATIENT",
    "NURSING TRIAGE SUICIDAL/HOMICIDAL COMPLAINTS PROTOCOL",
    "SHC TXP KIDNEY EVALUATION",
    "RETIRED IP POST-PROCEDURE ORDERS THORACENTESIS",
    "RETIRED IP PAMF ORTHO TKA"
]

SS_SECTION_NAMES = [
    None,
    " "
    "Nursing",
    "NURSING",
    "General",
    "Laboratory",
    "Discharge Orders",
    "LABORATORY",
    "DISCHARGE ORDERS",
    "Vital Signs",
    "VITAL SIGNS",
    "Pre-op (Day of Surgery) Orders",
    "Notify Physician",
    "NOTIFY PHYSICIAN",
    "Admission/Transfer",
    "Orders",
    "Pre-Admission Orders",
    "VTE Prophylaxis",
    "Transfusion Orders",
    "Activity",
    "ACTIVITY",
    "ADMISSION/TRANSFER",
    "LABORATORY/ECG",
    "NUTRITION",
    "Immunizations",
    "Nutrition",
    "VTE PROPHYLAXIS",
    "RESPIRATORY",
    "Admission Orders",
    "Consults",
    "Respiratory",
    "Code Status",
    "CODE STATUS",
    "Glucose Checks",
    "CONSULTS",
    "IMMUNIZATIONS",
    "Follow Up Instructions",
    "ORDERS",
    "VITALS",
    "Intra-Operative Blood Product and Transfusion Orders (By Product)",
    "Facility Orders",
    "PRE-OP (DAY OF SURGERY) ORDERS",
    "IMAGING",
    "Nursing Orders",
    "Laboratory/ECG",
    "Ad-hoc Orders",
    "DISCHARGE INSTRUCTIONS",
    "Discharge Instructions",
    "PROCEDURES",
    "Imaging",
    "MEDICATIONS",
    "Trauma 97 Initial ED Orders",
    "After Visit Orders",
    "PRE-ADMISSION ORDERS",
    "Interagency Referrals",
    "THERAPY REFERRALS",
    "Intra-Operative Labs",
    "Labs",
    "Procedures",
    "Orders - Labs, X-rays, Procedures",
    "Other Tests",
    "Protocol",
    "Nursing ",
    "Medications",
    "Hypoglycemia Control",
    "Insulin Adjustments ",
    "OTHER TESTS",
    "Monitoring",
    "Dressing",
    "MICROBIOLOGY TESTS",
    "PICC Insertion/Exchange",
    "Notify MD",
    "Pain Medication Regimens",
    "Inpatient Pre-op Orders",
    "Stroke Symptoms",
    "Vitals",
    "GLUCOSE CHECKS",
    "ADMISSION",
    "OTHER LAB TESTS",
    "Therapy Referrals ",
    "Cultures",
    "Home Orders",
    "Orders (Labs,Procedures,Images,Referrals)",
    "MONITORING",
    "HYPOGLYCEMIA CONTROL",
    "Transfusion",
    "DRESSING",
    "Trauma Radiology",
    "TRANSFUSION",
    "Isolation/Precautions",
    "PICC INSERTION/EXCHANGE",
    "Orders - (labs, imaging, referrals)",
    "Orders - (Labs, Procedures, Injections, Images, Referrals)",
    "LABS",
    "Vitals/Nursing",
    "Hypoglycemic Protocol For IV Insulin Infusion",
    "Treatment Procedures",
    "Post-Operative Admit Panel",
    "Colon Cancer Screening",
    "NURSING ORDERS",
    "INTERAGENCY REFERRALS",
    "Referrals",
    "Pre Procedure ",
    "Patient Preparation",
    "SPECIAL NEEDS CROSSMATCH",
    "Visit for Flu Vaccine",
    "INSULIN ADJUSTMENTS ",
    "INFLUENZA VACCINE ORDER PANELS",
    "Assessment and Privileges",
    "Standard Labs",
    "Pre- Procedure",
    "Rehabilitation/ Home Care",
    "Trauma 99 Initial ED Orders",
    "Routine Orders",
    "DISCONTINUE PREVIOUS INSULIN/ORAL ANTIDIABETIC ORDERS",
    "IV Fluids",
    "Post Procedure",
    "Tube Feeding ",
    "Injections",
    "Hepatitis C Screening",
    "Vital/Nursing",
    "PICC Line",
    "STANDARD LABS",
    "Precaution",
    "Vascular Access Team Services",
    "SPECIAL NEEDS BLOOD PRODUCTS",
    "Diabetes Management",
    "IV FLUIDS",
    "INSULIN BASAL, PRANDIAL AND CORRECTIVE SUBCUTANEOUS SCALES",
    "PRE PROCEDURE ",
    "Post Procedure ",
    "Precautions",
    "Outpatient Orders",
    "Pathology",
    "PATIENT PREPARATION",
    "HYPOGLYCEMIC PROTOCOL FOR IV INSULIN INFUSION",
    "Breast Cancer Screening",
    "Procedure Orders",
    "BASIC BLOOD PRODUCTS",
    "GENERAL LABS",
    "Orders - Labs, Procedures, Referrals, etc",
    "Wounds",
    "Nursing PRE-PROCEDURE",
    "Physician Charging",
    "Medication Management",
    "Cervical Cancer Screening",
    "General Labs",
    "Cytogenetics",
    "Pre-Dialysis Laboratory",
    "POST PROCEDURE ",
    "Virology",
    "ORTHO NURSING",
    "MICROBIOLOGY",
    "PROCEDURES/ORDERS",
    "Trauma 95 Initial ED Orders",
    "SPUTUM INDUCED",
    "Flow Cytometry",
    "Trauma",
    "MEDICATION",
    "FULL INTENSITY HEPARIN PROTOCOL",
    "Nurse Communication",
    "Nursing POST-PROCEDURE",
    "Day of Surgery Orders",
    "SPUTUM,EXPECTORATED",
    "PICC LINE",
    "LOW INTENSITY HEPARIN INFUSION PROTOCOL",
    "Influenza Vaccine =>3 Years Old",
    "Insulin Bolus And Infusion",
    "PATHOLOGY",
    "Injectible Meds",
    "Admission",
    "Retrieval Orders",
    "CYTOGENETICS",
    "Blood Products",
    "Cardiac Event Monitor",
    "ADMIT ORDERS",
    "Sleep Apnea Orders",
    "CONSULT",
    "PRE-DIALYSIS LABORATORY",
    "HLA Recipient Kit Request",
    "INSULIN INFUSION HYPOGLYCEMIC PROTOCOL",
    "PRECAUTIONS",
    "HLA Kit Request",
    "DME",
    "Massive Transfusion Adult (>50 KG)",
    "TRAUMA",
    "Wound Care for SNF or Home Care",
    "Fluoro Procedures",
    "Recipient Testing PRE-TRANSPLANT",
    "1. Delirium General  Management",
    "ANCILLARY STUDIES",
    "Admisison Orders",
    "IP Insulin Continuous IV Infusion (For Cardiac Transplant)",
    "Case Request",
    "PRE PROCEDURE",
    "Laboratory Phase I ",
    "Hypoglycemia Control For Insulin Transition Off IV Infusion Protocol",
    "PRIVILEGES",
    "Recipient Testing",
    "TUBE FEEDING CHOICES"
]

SS_SG_NAMES = [
    None,
    "Nursing",
    "Vital Signs",
    "Orders",
    "Notify Physician",
    "Admission",
    "Activity",
    "Chemistry",
    "Hematology",
    "Nutrition",
    "Pre-procedure",
    "Notify MD",
    "Labs",
    "Code Status",
    "VTE Prophylaxis",
    "Respiratory",
    "Discharge",
    "Consults",
    "Intra/Post Procedure",
    "Laboratory",
    "Pre-Admission Lab Studies",
    "Discharge Patient",
    "Post Procedure",
    "Monitor",
    "Instructions",
    "Protocol Labs",
    "Order Blood Products  (NOT AN ORDER TO TRANFUSE)",
    "Monitoring",
    "Discharge Instructions",
    "Admission Orders",
    "Transfuse Blood Products  (DOES NOT ORDER PRODUCT)",
    "Glucose Checks",
    "Interventions",
    "Assessment",
    "ADMINISTRATION MMC",
    "IMM/INJ PED ORDERS MMC",
    "Intervention",
    "Procedures",
    "ECG",
    "Therapy Referrals",
    "Type and Screen",
    "Day of Surgery IV insertion w PRN lidocaine and TKO fluid rate",
    "POC",
    "Day of Surgery Low Risk DVT/PE Prophylaxis: (<5% risk of DVT: Patient <40 years old and minor surgery and no additional risk factors)",
    "Xray",
    "Interagency Referrals",
    "Hypoglycemic Treatment",
    "Prepare and Send Blood Products",
    "Moderate Risk DVT/PE Prophylaxis (10-20% risk of DVT: age 40-60 years old with no additional risk factors or minor surgery in patients with additional risk factors)",
    "Low Risk DVT/PE Prophylaxis(<5% risk of DVT)Patient <40 yrs old and minor surgery and no additional risk factors.",
    "Dressing",
    "One Time Labs - Prior to Heparin",
    "Pre-Admission Ancillary Studies",
    "Insulin Adjustments",
    "TRAUMA 97",
    "IV Fluids",
    "Intra-Operative Labs",
    "Day of Surgery Nursing",
    "Point of Care (POC) Labs",
    "Medication Side Effects Management",
    "Order Blood Products",
    "Microbiology",
    "Immunizations",
    "Day of Surgery Nursing Orders",
    "Consult",
    "Precautions",
    "Notify Pain Service",
    "Order Blood Products (NOT AN ORDER TO TRANSFUSE)",
    "Day of Surgery Lab Studies",
    "Lab",
    "Transfuse Blood Products",
    "Pre-Admission Type and Screen",
    "Transfuse Blood Products (DOES NOT ORDER PRODUCT)",
    "ADULT IMMUNIZATIONS FOR UHA DEPARTMENTS",
    "Facility Nursing",
    "Referrals",
    "Glucose PRN",
    "Nursing Orders",
    "Basic Microbiology",
    "Urine Studies",
    "VTE Prophylaxis Regimen",
    "ICU Hemodynamic Monitoring",
    "PICC Nursing Communication",
    "Vital Sign",
    "Day of Surgery Skin Preparation",
    "AMB PRO SLEEP FOR ATTENDINGS ONLY",
    "Nursing Communications",
    "Pre-transplant Labs for Recipient",
    "BMT Donor Tests",
    "IN-LAB SLEEP STUDY (AGE 19 OR OLDER)",
    "Discharge Orders",
    "Moderate Risk DVT/PE Prophylaxis (10-20% risk of DVT: Patient 40-60 years old with no additional risk factors or minor surgery in patients with additional risk factors)",
    "Hemodialysis",
    "LABS - Single Orders (Stanford Draw)",
    "ADMIT",
    "Labs POC",
    "Vital signs",
    "Laboratory/ECG",
    "Vitals/Nursing",
    "Low Risk DVT/PE Prophylaxis: (<5% risk of DVT: Patient <40 years old and minor surgery and no additional risk factors)",
    "Pharmacologic VTE Prophyalxis Contraindicated",
    "Pre-Admission Urine Studies",
    "Pre-Admission Chlorhexidine Orders",
    "High Risk DVT/PE Prophylaxis (20-40% risk of DVT: surgery in patients > 60 years old or age >40 years with additional risk factors)",
    "Basic Chemistry/Hematology",
    "Deep Vein Thrombosis Prevention",
    "Home Nursing",
    "UHA AMB PRO PED WCC 3-11 YEARS",
    "Precaution",
    "Isolation/Precautions",
    "Daily Labs",
    "High Risk DVT/PE Prophylaxis: (20-40% risk of DVT: Surgery in patients >60 years old or age >40 years with additional risk factors)",
    "Saline Lock",
    "Hypoglycemic Protocol: BG less than 70 mg/dL",
    "PRO PED ADOL WCC MMC",
    "Day of Surgery DVT Prophylaxis",
    "Neurological Checks",
    "Pre Procedure",
    "PICC Insertion/Exchange",
    "Wean Ventilator",
    "Hypoglycemia Control",
    "Drains and Tubes",
    "General Nursing",
    "Cardiac markers",
    "Neurovascular",
    "Urine Output Protocol",
    "Post-Operative Panel (Trauma)",
    "Tube Feeding Formula",
    "PICC Line",
    "Day of Surgery Deep Vein Thrombosis Prevention",
    "Pre-Operative Skin Preparation ",
    "Debridement",
    " Procedures",
    "LAB - Standard Orders",
    "PRO URODYNAMICS",
    "During Visit Orders",
    "Imaging",
    "Bone Marrow Biopsy, Aspirate Testing",
    "Flow Cytometry",
    "INFLUENZA VACCINE",
    "ADULT IMMUNIZATIONS",
    "Upper Abdominal Pain",
    "Virology",
    "Day of Surgery Antibiotics",
    "Lab Work",
    "Order Basic Blood Products",
    "Pre-Operative Skin Preparation",
    "Rehabilitation/Home Care",
    "General Labs",
    "TRAUMA RADIOLOGY",
    "Oral Care",
    "Patient Preparation",
    "Nursing Interventions",
    "Nursing ",
    "WARFARIN BY PHARMACY PROTOCOL PT/INR/LFT CHECK MARKING",
    "Cardiac Monitor",
    "Notify Pain Service Physician",
    "PRO ACUPUNCTURE",
    "Consents",
    "X-ray",
    "Cardiology",
    "Vital Signs ",
    "Order, Send, and Transfuse Blood Products",
    "Transfusion Order",
    "Screening Colonoscopy",
    "LABS ROUTINE/HIV - STANFORD LABS",
    "Wound",
    "AMB IMM/INJ PED ORDERS ",
    "Labs:Fluid",
    "AMB PRO SLEEP ORD",
    "Hepatitis C Screening",
    "Standard Transplant Evaluation Tests",
    "Vitals",
    "Rehabilitation /SNF ",
    "XRay",
    "After Visit Orders",
    "Nursing Assessment",
    "Nursing Routine",
    "Discharge Instrcutions",
    "EVALUATION LAB WORK PHASE I",
    "Orthopat",
    "Sedation Assessment",
    "PROCEDURES",
    "Basic Microbiology - Always order BOTH tests",
    "Trauma Radiology",
    "Tetanus, Diptheria and Pertusis Vaccines",
    "Nursing Triage Order Set Initiated",
    "OUT-OF-CENTER TESTING (PORTABLE MONITORING)",
    "Extended Microbiology",
    "Transfer",
    "Outpatient Orders",
    "Pre-Procedure (NSG)",
    "Hypoglycemic Protocol: (BG<70)",
    "ED Trauma 99",
    "Nursing Protocols",
    "IMAGING",
    "Day of Surgery Pharmacologic VTE Prophyalxis Contraindicated",
    "Respiratory/Ventilator",
    "Collection",
    "Labs: Fluid"
]

STAND_INTERVALS = [
    None,
    "LAB ONE TIME",
    "ONCE",
    "CONTINUOUS",
    "PRN",
    "PROCEDURE ONCE",
    "TODAY",
    "QAM LAB",
    "TID",
    "AS SPECIFIED",
    "EVERY 4 HOURS",
    "INAM LAB",
    "DAILY",
    "EVERY HOUR",
    "EVERY 6 HOURS",
    "TOMORROW  ",
    "EVERY 2 HOURS",
    "LAB ADD ON",
    "EVERY 15 MIN",
    "EVERY 8 HOURS",
    "EVERY 12 HOURS",
    "Transfuse 1 unit",
    "4 TIMES DAILY BEFORE MEALS & AT BEDTIME",
    "EVERY 2 HOURS WHILE AWAKE (ORDERS)",
    "Transfuse 2 units",
    "VS PER ED POLICY",
    "THREE TIMES A WEEK INFO",
    "QPM LAB",
    "Per Treatment Parameters - Manual Release",
    "QAM RAD",
    "INPM LAB",
    "FOUR TIMES A WEEK INFO",
    "FIVE TIMES A WEEK INFO",
    "Once a Week",
    "PER PROTOCOL",
    "Once Every 4 Weeks",
    "Q4HR-PRN",
    "Per Treatment Parameters",
    "EVERY 7 DAYS",
    "EVERY MONDAY",
    "Lab One Time",
    "Once a Day",
    "Every 1 Week",
    "Q4H",
    "EVERY MO,TH",
    "Every 1 Week - Manual Release",
    "Every 4 Weeks",
    "Every 4 Weeks - Manual Release",
    "EVERY 4 HOURS WHILE AWAKE",
    "EVERY MWF",
    "TWO TIMES A WEEK INFO",
    "Q6H",
    "TWICE A DAY",
    "2 TIMES DAILY",
    "EVERY 30 MIN",
    "2 TIMES A DAY",
    "Q12H",
    "Once Every 12 Weeks",
    "EVERY OTHER DAY AT 0600",
    "Q8H",
    "Once Every 3 Weeks",
    "Every 12 Weeks",
    "Three Times a Week",
    "Q6 PRN",
    "Once Every 2 Weeks",
    "Every 12 Weeks - Manual Release",
    "LAB ONE TIME (IN 15 MIN)",
    "Five Times a Week",
    "EVERY 4 DAYS",
    "Every 2 Weeks - Manual Release",
    "SEVEN TIMES A WEEK INFO",
    "2 Times a Week",
    "4 TIMES DAILY",
    "DAILY INFO",
    "TID CHECKS",
    "EVERY MORNING",
    "Once",
    "Every 3 Weeks - Manual Release",
    "EVERY MON, WED & FRI",
    "EVERY OTHER DAY",
    "Every 6 Months",
    "EVERY TUE THUR SUN",
    "Daily",
    "EVERY MON WED FRI SAT",
    "Transfuse 4 units",
    "3 Times a Week",
    "Four Times a Week",
    "Every 8 Weeks",
    "Every 2 Weeks",
    "SIX TIMES A WEEK INFO",
    "Today, 2 Months, 6 Months",
    "EVERY 5 MINUTES",
    "Every 6 MONTHS - Manual Release",
    "Tomorrow",
    "WEEKLY",
    "EVERY SHIFT",
    "Once Every 8 Weeks",
    "Every 6 MONTHS",
    "AT BEDTIME",
    "EVERY THIRD DAY",
    "Q4 HR W/A (0900,1300,1700,2100)",
    "Q4 HR W/A (0800,1200,1600,2000)",
    "QNOC",
    "MONTHLY",
    "EVERY 3 HOURS",
    "Twice a Week",
    "EVERY 1 WEEK",
    "3 TIMES PER DAY",
    "Q2HR-PRN",
    "INAM RAD",
    "Two Times a Week",
    "Twice a Week - Manual Release",
    "Once a Day - Manual Release",
    "WEEKLY INFO",
    "Continuous",
    "BID 0800,1800",
    "Every 8 Weeks - Manual Release",
    "3 TIMES DAILY",
    "BID + PRN",
    "IN AM",
    "EVERY SUNDAY",
    "SIX TIMES DAILY",
    "Q6 HR W/A 0900,1500,2100",
    "EVERY OTHER WEDNESDAY",
    "5 TIMES DAILY BEFORE MEALS & AT BEDTIME AND 0200",
    "EVERY 6 HOURS WHILE AWAKE",
    "Q0200",
    "2 TIMES DAILY (0900,1900)",
    "Three Times a Week - Manual Release",
    "Q2H",
    "DAILY AND AS NEEDED",
    "EVERY WEDNESDAY",
    "RESP PRN",
    "Once Every 6 Weeks",
    "EVERY THURSDAY",
    "WITH VITAL SIGNS",
    "Q4 HR W/A PRN",
    "2 TIMES DAILY (0800,1800)",
    "QID-PRN",
    "Six Times a Week",
    "Seven Times a Week",
    "Every Weekday",
    "EVERY TUESDAY",
    "FREE WATER FOR TUBE FEEDING TID",
    "Blood - Once",
    "Every 3 Weeks",
    "Today",
    "Transfuse 6 units",
    "BID-PRN",
    "Every 6 Weeks - Manual Release",
    "Q1H",
    "TWICE A DAY INFO",
    "QID",
    "Every 2 Hours While Awake",
    "EVERY MON & FRI",
    "Transfusion",
    "EVERY THIRD DAY AT 0600",
    "Transfuse 3 units",
    "Every other day at 0600",
    "QAM LAB (0600)",
    "EVERY 2 WEEKS",
    "Q30 Min",
    "EVERY 72 HOURS",
    "BID 0900,1900",
    "Every 6 Weeks",
    "4 Times a Week",
    "Q4 HR W/A (0600,1000,1400,1800)",
    "ONE TIME",
    "EVERY 10 MIN ",
    "3 TIMES DAILY BEFORE MEALS",
    "EVERY FRIDAY",
    "Transfuse 8 units",
    "TID (0000, 0800, 1600)",
    "EVERY MON AND THUR",
    "BID",
    "EVERY TUE THUR SAT",
    "Once Every 9 Weeks",
    "2 TIMES DAILY AFTER MEALS",
    "Weekly",
    "THREE TIMES A WEEK",
    "4 TIMES DAILY AND AS NEEDED",
    "EVERY MON & THU",
    "Every 72 hrs",
    "Twice A Day",
    "Twice a Day",
    "Q6 HR W/A 0800,1400,2000",
    "FIVE TIMES A WEEK",
    "TID-PRN",
    "FOUR TIMES A WEEK",
    "DAILY (0800)",
    "Today, 2 Months, 6 Months Manual Release",
    "Q15 Min",
    "EVERY 8 HOURS (0600, 1400, 2200)",
    "Q3H",
    "Q Week",
    "EVERY HOUR (0100, 0200, ETC)",
    "Every 9 Weeks",
    "EVERY TUE, THU & SAT",
    "EVERY 4 HOURS AND AS NEEDED",
    "EVERY SUNDAY (2000) "
]


class TestSTARROrderProcConversion(DBTestCase):
    TEST_DATA_SIZE = 2 * len(ORDER_TYPES)    # at least 2 rows per med route combined with inpatient vs outpatient

    ORDER_PROC_HEADER = ['order_proc_id_coded', 'jc_uid', 'pat_enc_csn_id_coded', 'order_type', 'proc_id',
                         'proc_code', 'description', 'order_time_jittered', 'ordering_mode', 'stand_interval', 'instantiated_time_jittered']
    PROC_ORDERSET_HEADER = ['order_proc_id_coded', 'protocol_id', 'protocol_name', 'ss_section_id', 'ss_section_name',
                            'ss_sg_key', 'ss_sg_name']

    test_data = []
    orderset_data = []
    clinical_items = {}
    expected_data = []
    expected_orderset_data = []

    test_data_csv = tempfile.gettempdir() + '/test_starr_order_proc_dummy_data.csv'
    orderset_data_csv = tempfile.gettempdir() + '/test_starr_order_proc_orderset_data.csv'

    def setUp(self):
        log.setLevel(logging.INFO)  # without this no logs are printed

        """Prepare state for test cases"""
        DBTestCase.setUp(self)

        log.info("Sourcing from BigQuery DB")
        ClinicalItemDataLoader.build_clinical_item_psql_schemata()

        self.converter = STARROrderProcConversion.STARROrderProcConversion()  # Instance to test on
        self.bqConn = self.converter.bqConn
        self.starrUtil = STARRUtil.StarrCommonUtils(self.converter.bqClient)

        # point the converter to dummy source table
        STARROrderProcConversion.SOURCE_TABLE = TEST_SOURCE_TABLE
        STARROrderProcConversion.ORDERSET_TABLE = TEST_ORDERSET_TABLE

    def generate_test_and_expected_data(self, test_data_size):
        self.generate_orderproc_and_orderset_data(test_data_size)

        # need to sort data to use the same clinical_item.descriptions as the duplicate clinical_items are not stored
        self.test_data.sort(key=lambda tup: (tup[0], tup[1], tup[2], tup[3]))
        self.orderset_data.sort(key=lambda row: row[0])

        # join test order_proc and proc_orderset data to create a test row
        joined_test_data = self.left_join_orderproc_and_orderset_data()

        for joined_test_data_row in joined_test_data:
            self.generate_expected_data_rows(joined_test_data_row[0], joined_test_data_row[1])

        # pi.external_id desc, pi.patient_id, pi.encounter_id, ci.external_id desc
        self.expected_data.sort(key=lambda tup: (-tup[0], tup[1], tup[2], -tup[4]))

        # pi.external_id, ci.external_id, cic.description, ci.name, ci.description
        self.expected_orderset_data.sort(key=lambda tup: (tup[0], tup[1], tup[2], tup[3], tup[4]))

    def left_join_orderproc_and_orderset_data(self):
        joined_test_data = []
        for test_data_row in self.test_data:
            if self.ignore_row(test_data_row[9]):
                continue

            found_join_row = False
            for test_orderset_row in self.orderset_data:
                if test_data_row[0] == test_orderset_row[0]:
                    found_join_row = True
                    joined_test_data.append((test_data_row, test_orderset_row))
            if not found_join_row:
                joined_test_data.append((test_data_row, None))
        return joined_test_data

    def generate_orderproc_and_orderset_data(self, test_data_size):
        seen_test_data_rows = set()
        while len(self.test_data) < test_data_size:
            curr_row = len(self.test_data)
            patient_id = 'JC' + format(curr_row, '06')

            test_data_row = self.generate_test_data_row(curr_row, patient_id)
            self.test_data.append(test_data_row)

            # should generate at most 1 row of proc_orderset per order_proc row (tested code does LEFT OUTER JOIN)
            should_generate_orderset_row = random.randint(0, 10)    # 10 times more likely to generate than not
            if should_generate_orderset_row:
                orderset_row = self.generate_orderset_row(test_data_row[0])
                self.orderset_data.append(orderset_row)

    @staticmethod
    def ignore_row(stand_interval):
        # TODO should we include order_time_jittered not null and instantiated_time_jittered is null?
        # process only rows where op.stand_interval not like '%PRN'
        return (stand_interval is not None and stand_interval.endswith('PRN'))

    @staticmethod
    def generate_test_data_row(curr_row, patient_id):
        proc_id = random.randint(0, len(PROC_CODES) - 1)
        return (
            curr_row,  # order_proc_id_coded
            patient_id,
            random.randint(0, curr_row / 2),  # pat_enc_csn_id_coded - want some of them to be repeated
            ORDER_TYPES[random.randint(0, len(ORDER_TYPES) - 1)],
            proc_id,
            PROC_CODES[proc_id],
            DESCRIPTIONS[random.randint(0, len(DESCRIPTIONS) - 1)],
            datetime.fromtimestamp(random.randint(1, int(time.time()))),  # random order_time_jittered
            ORDERING_MODES[random.randint(0, len(ORDERING_MODES) - 1)],  # ordering_modes
            STAND_INTERVALS[random.randint(0, len(STAND_INTERVALS) - 1)],
            None    # instantiated_time_jittered
        )

    @staticmethod
    def generate_orderset_row(order_proc_id_coded):
        protocol_id = random.randint(1, len(PROTOCOL_NAMES))
        ss_section_id = random.randint(0, len(SS_SECTION_NAMES) - 1)
        ss_sg_key = random.randint(0, len(SS_SG_NAMES) - 1)

        return (
            order_proc_id_coded,  # to match the given order_proc_row
            -protocol_id,
            PROTOCOL_NAMES[protocol_id - 1],
            ss_section_id,
            SS_SECTION_NAMES[ss_section_id],
            str(ss_sg_key),
            SS_SG_NAMES[ss_sg_key]
        )

    def generate_expected_data_rows(self, row, orderset_row):
        cic_description = row[3]
        ci_description = row[6]
        proc_code = row[5]

        ci_key = (TEST_SOURCE_TABLE, cic_description, proc_code)

        if ci_key not in self.clinical_items:
            # TODO for now put just the description - we might need also external_id = proc_id, name = proc_code
            self.clinical_items[ci_key] = ci_description

            # replace previous ci_descriptions in expected_data
            for i in range(len(self.expected_data)):
                if self.expected_data[i][3] == cic_description and self.expected_data[i][5] == proc_code:
                    self.expected_data[i] = self.expected_data[i][:6] + (self.clinical_items[ci_key], self.expected_data[i][7])

            # replace previous ci_descriptions in expected_orderset_data
            for i in range(len(self.expected_orderset_data)):
                if self.expected_orderset_data[i][2] == cic_description and self.expected_orderset_data[i][3] == proc_code:
                    self.expected_orderset_data[i] = self.expected_orderset_data[i][:4] + (self.clinical_items[ci_key],) + self.expected_orderset_data[i][5:]

        ci_description = self.clinical_items[ci_key]

        expected_row = (
            row[0],                                                                             # external_id
            self.starrUtil.convertPatIdToSTRIDE(row[1]),                                        # patient_id
            row[2],                                                                             # encounter_id
            cic_description,                                                                    # cic_description
            row[4],                                                                             # ci_external_id
            proc_code,                                                                          # ci_name
            ci_description,                                                                     # ci_description
            row[7]                                                                              # pi_item_date
        )

        if expected_row not in self.expected_data:
            self.expected_data.append(expected_row)

        if orderset_row is not None:
            # generate expected data for orderset - in %item_collection% tables
            expected_orderset_row = (
                row[0],             # pi_external_id
                row[4],
                cic_description,
                proc_code,          # ci_name
                ci_description,
                orderset_row[1],    # protocol_id
                orderset_row[2],    # protocol_name
                orderset_row[4],    # ss_section_name
                orderset_row[6]     # ss_sg_name
            )
            self.expected_orderset_data.append(expected_orderset_row)

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        self.test_data[:] = []
        self.orderset_data[:] = []
        self.expected_data[:] = []
        self.expected_orderset_data[:] = []
        self.clinical_items.clear()

        self.starrUtil.remove_file(self.test_data_csv)
        self.starrUtil.remove_file(self.orderset_data_csv)

        bq_cursor = self.bqConn.cursor()
        bq_cursor.execute('DELETE FROM {}.patient_item_collection_link WHERE true;'.format(TEST_DEST_DATASET))
        bq_cursor.execute('DELETE FROM {}.item_collection_item WHERE true;'.format(TEST_DEST_DATASET))
        bq_cursor.execute('DELETE FROM {}.item_collection WHERE true;'.format(TEST_DEST_DATASET))

        bq_cursor.execute('DELETE FROM {}.patient_item WHERE true;'.format(TEST_DEST_DATASET))
        bq_cursor.execute('DELETE FROM {}.clinical_item WHERE true;'.format(TEST_DEST_DATASET))
        bq_cursor.execute('DELETE FROM {}.clinical_item_category WHERE true;'.format(TEST_DEST_DATASET))

        bq_cursor.execute('DROP TABLE IF EXISTS {};'.format(TEST_SOURCE_TABLE))
        bq_cursor.execute('DROP TABLE IF EXISTS {};'.format(TEST_ORDERSET_TABLE))

        DBTestCase.tearDown(self)

    def test_data_conversion(self):
        log.info("Generating test source data")

        self.generate_test_and_expected_data(self.TEST_DATA_SIZE)

        # upload proc_orderset
        self.starrUtil.dump_test_data_to_csv(self.PROC_ORDERSET_HEADER, self.orderset_data, self.orderset_data_csv)
        self.starrUtil.upload_csv_to_bigquery('starr_datalake2018', 'proc_orderset', TEST_DEST_DATASET,
                                              'starr_proc_orderset', self.orderset_data_csv, self.PROC_ORDERSET_HEADER)

        # upload order_proc
        self.starrUtil.dump_test_data_to_csv(self.ORDER_PROC_HEADER, self.test_data, self.test_data_csv)
        self.starrUtil.upload_csv_to_bigquery('starr_datalake2018', 'order_proc', TEST_DEST_DATASET,
                                              'starr_order_proc', self.test_data_csv, self.ORDER_PROC_HEADER)

        log.debug("Run the conversion process...")
        temp_dir = tempfile.gettempdir()
        self.converter.convertAndUpload(tempDir=temp_dir, target_dataset_id=TEST_DEST_DATASET, removeCsvs=True)

        # Just query back for the same data, de-normalizing the data back to a general table
        test_query = \
            """
            select
                pi.external_id as pi_external_id,
                pi.patient_id,
                pi.encounter_id,
                cic.description as cic_description,
                ci.external_id as ci_external_id,
                ci.name,
                ci.description as ci_description,
                pi.item_date
            from
                {}.patient_item as pi,
                {}.clinical_item as ci,
                {}.clinical_item_category as cic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = '{}'
            order by
                pi.external_id desc, pi.patient_id, pi.encounter_id, ci.external_id desc
            """.format(TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_SOURCE_TABLE)

        bq_cursor = self.bqConn.cursor()
        bq_cursor.execute(test_query)
        # remove timezone info in pi.item_date from coming from bigquery - we're storing datetime without timezone
        actual_data = [row.values()[:7] + (row.values()[7].replace(tzinfo=None), ) for row in bq_cursor.fetchall()]

        log.debug('actual data: {}'.format(actual_data))
        log.debug('expected data: {}'.format(self.expected_data))
        self.assertEqualTable(self.expected_data, actual_data)

        # Query for orderset links
        test_orderset_query = \
            """
            select
                pi.external_id as pi_external_id,
                ci.external_id as ci_external_id,
                cic.description as cic_description,
                ci.name as ci_name,
                ci.description,
                ic.external_id,
                ic.name,
                ic.section,
                ic.subgroup
            from
                {}.patient_item as pi,
                {}.clinical_item as ci,
                {}.clinical_item_category as cic,
                {}.patient_item_collection_link as picl,
                {}.item_collection_item as ici,
                {}.item_collection as ic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = '{}' and
                pi.patient_item_id = picl.patient_item_id and
                picl.item_collection_item_id = ici.item_collection_item_id and
                ici.item_collection_id = ic.item_collection_id
            order by
                pi.external_id, ci.external_id, cic.description, ci.name, ci.description
            """.format(TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_DEST_DATASET,
                       TEST_DEST_DATASET, TEST_SOURCE_TABLE)

        bq_cursor.execute(test_orderset_query)
        actual_orderset_data = [row.values() for row in bq_cursor.fetchall()]

        log.debug('actual orderset data: {}'.format(actual_orderset_data))
        log.debug('expected orderset data: {}'.format(self.expected_orderset_data))
        self.assertEqualTable(self.expected_orderset_data, actual_orderset_data)


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSTARROrderProcConversion))

    return test_suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
