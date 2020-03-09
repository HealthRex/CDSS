#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
import logging
import pytz
import random
import tempfile;

from datetime import datetime

import unittest

from parameterized import parameterized
from medinfo.dataconversion.test.Const import RUNNER_VERBOSITY
from medinfo.dataconversion.Util import log

from medinfo.db.test.Util import DBTestCase

from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel

from medinfo.dataconversion.starr_conv import STARRTreatmentTeamConversion
from medinfo.dataconversion.starr_conv import STARRUtil

TEST_SOURCE_TABLE = 'test_dataset.starr_treatment_team'
TEST_DEST_DATASET = 'test_dataset'

NAME_TO_ACRONYM = {
    'Intern': 'I',
    'Cross Cover Intern': 'CCI',
    'Wound/Ostomy/Continence RN': 'WR',
    'Primary Intern': 'PI',
    'Primary Resident': 'PR',
    'Cross Cover Attending': 'CCA',
    'Student Nurse': 'SN',
    'Clinical Pharmacist': 'CP',
    'Medical Assistant': 'MA',
    'Licensed Vocational Nurse': 'LVN',
    'Clinical Nurse Specialist': 'CNS',
    'Cross Cover Fellow': 'CCF',
    'ED Unit Secretary': 'EUS',
    'Primary Fellow': 'PF',
    'Cross Cover Resident': 'CCR',
    'Consulting Attending': 'CA',
    'Consulting Fellow': 'CF',
    'Spiritual Care': 'SC',
    'Consulting Med Student': 'CMS',
    'Primary Advanced Practice Provider': 'PAPP',
    'Physician Assistant': 'PA',
    'Consulting Resident': 'CR',
    'Nurse Coordinator': 'NC',
    'Fellow': 'F',
    'Consulting Intern': 'CI',
    'Co-Attending': 'C',
    'Surgeon': 'S',
    'Primary Med Student': 'PMS',
    'ED Tech': 'ET',
    'Resident': 'R',
    'Chief Resident': 'CR',
    'Medical Student': 'MS',
    'Primary Medical Student': 'PMS',
    'Pulmonologist': 'P',
    'Pediatrician': 'P',
    'Hematologist': 'H',
    'Primary Care Physician': 'PCP',
    'Primary Physician Assistant': 'PPA',
    'Cardiologist': 'C',
    'Triage Nurse': 'TN',
    'Transplant Social Worker': 'TSW',
    'Additional Communicating Provider': 'ACP',
    'ED Registrar': 'ER',
    'Gastroenterologist': 'G',
    'Medical Oncologist': 'MO',
    'Primary Sub-Intern': 'PS',
    'Lactation Consultant': 'LC',
    'Trauma Attending': 'TA',
    'Post-Transplant Nurse': 'PN',
    'Cross Cover Advanced Practice Provider ': 'CCAPP',
    'Internist': 'I',
    'Nephrologist': 'N',
    'Research Coordinator': 'RC',
    'Infectious Disease': 'ID',
    'Trauma Resident ': 'TR',
    'Primary Sub-intern': 'PS',
    'Neurologist': 'N',
    'Transplant Surgeon': 'TS',
    'Consulting Medical Oncologist': 'CMO',
    'Family Practitioner': 'FP',
    'Dermatologist': 'D',
    'Aging Adult Services Coordinator': 'AASC',
    'Transplant Nephrologist': 'TN',
    'Post-Transplant Nephrologist': 'PN',
    'Consulting Surgical Oncologist': 'CSO',
    'Surgical Oncologist': 'SO',
    'Nursery Nurse': 'NN',
    'Transplant Pharmacist': 'TP',
    'Psychologist': 'P',
    'Restorative Aide': 'RA',
    'Child Life Specialist': 'CLS',
    'Consulting Hematologist': 'CH',
    'Endocrinologist': 'E',
    'Electrophysiologist': 'E',
    'Anesthesiologist': 'A',
    'Transplant Dietitian': 'TD',
    'Urologist': 'U',
    'stop0': 's',
    'Radiation Oncologist': 'RO',
    'Referring Provider': 'RP',
    'Activity Therapist': 'AT',
    'Transplant Pulmonologist': 'TP',
    'Obstetrician': 'O',
    'Heart Failure Cardiologist': 'HFC',
    'Post RN Coordinator': 'PRC',
    'Delivery Assist': 'DA',
    'Referring Nephrologist': 'RN',
    'Hepatologist': 'H',
    'Case Manager': 'CM',
    'Primary Team': 'PT',
    'Social Worker': 'SW',
    'Care Coordinator': 'CC',
    'Registered Nurse': 'RN',
    'Speech Therapist': 'ST',
    'Nursing Assistant': 'NA',
    'Clinical Dietitian': 'CD',
    'Consulting Service': 'CS',
    'Emergency Resident': 'ER',
    'Nurse Practitioner': 'NP',
    'Physical Therapist': 'PT',
    'Occupational Therapist': 'OT',
    'Physical Therapist Assistant': 'PTA',
    'Respiratory Care Practitioner': 'RCP',
    'Independent Living Donor Advocate': 'ILDA',
    'Pre RN Coordinator': 'PRC',
    'Dietician Intern': 'DI',
    'Survivorship Provider': 'SP',
    'Consulting Reconstructive Surgeon': 'CRS',
    'Referring Pulmonologist': 'RP'
}

PROV_TO_CLEAN_ACRONYM = {
    'SMITH, JOHN': ('', ''),
    'SMITH, JANE': ('', ''),
    'DOE, JOHN': ('', ''),
    'DOE, JANE': ('', ''),
    'CON CARDIOLOGY': ('CON CARDIOLOGY', 'CC'),
    'CON MEDICINE': ('CON MEDICINE', 'CM'),
    'CON PULMONARY': ('CON PULMONARY', 'CP'),
    'CON NEURO ICU': ('CON NEURO ICU', 'CNI'),
    'CON CARDIOL ARRHYTHMIA': ('CON CARDIOL ARRHYTHMIA', 'CCA'),
    'CON NEURO EPILEPSY CONSULT': ('CON NEURO EPILEPSY CONSULT', 'CNEC'),
    'CON NEPHROLOGY JAMISON': ('CON NEPHROLOGY JAMISON', 'CNJ'),
    'CON CARDIAC SURGERY': ('CON CARDIAC SURGERY', 'CCS'),
    'TT CVICU TEAM 2 - SPECTRAS 1-2345, 2-3456': ('TT CVICU TEAM 2', 'TCT2'),
    'CON PAIN': ('CON PAIN', 'CP'),
    'CON ONCOLOGY': ('CON ONCOLOGY', 'CO'),
    'CON NEUROLOGY GENERAL': ('CON NEUROLOGY GENERAL', 'CNG'),
    'CON NEURO STROKE': ('CON NEURO STROKE', 'CNS'),
    'TT NEUROSURGERY C SPINE FLOOR, PGR 12345': ('TT NEUROSURGERY C SPINE FLOOR', 'TNCSF'),
    'CON NEPHROLOGY TRANSPLANT': ('CON NEPHROLOGY TRANSPLANT', 'CNT'),
    'TT ACUTE CARE SURGERY TRAUMA, PGR 12345': ('TT ACUTE CARE SURGERY TRAUMA', 'TACST'),
    'CON INTERNAL MEDICINE CONSULT': ('CON INTERNAL MEDICINE CONSULT', 'CIMC'),
    'CON ICU': ('CON ICU', 'CI'),
    'CON ALLERGY IMMUNOLOGY CONSULT': ('CON ALLERGY IMMUNOLOGY CONSULT', 'CAIC'),
    'TT CVICU TEAM 1 - SPECTRAS 1-2345, 2-3456': ('TT CVICU TEAM 1', 'TCT1'),
    'TT NEUROSURGERY A VASCULAR FLOOR, PGR 12345': ('TT NEUROSURGERY A VASCULAR FLOOR', 'TNAVF'),
    'CON HEMATOLOGY': ('CON HEMATOLOGY', 'CH'),
    'CON ORTHOPEDICS HOSPITALIST': ('CON ORTHOPEDICS HOSPITALIST', 'COH'),
    'TT COLORECTAL SURGERY, PGR 12345': ('TT COLORECTAL SURGERY', 'TCS'),
    'CON THORACIC SURGERY': ('CON THORACIC SURGERY', 'CTS'),
    'TT NEUROSURGERY B TUMOR FLOOR, PGR 12345': ('TT NEUROSURGERY B TUMOR FLOOR', 'TNBTF'),
    'CON PULM TRANSPLANT': ('CON PULM TRANSPLANT', 'CPT'),
    'TT NEUROSURGERY B TUMOR ICU, PGR 12345': ('TT NEUROSURGERY B TUMOR ICU', 'TNBTI'),
    'CON HEPATOLOGY': ('CON HEPATOLOGY', 'CH'),
    'TT NEUROSURGERY C SPINE ICU, PGR 12345': ('TT NEUROSURGERY C SPINE ICU', 'TNCSI'),
    'TT PAIN, .': ('TT PAIN', 'TP'),
    'TT MICU GREEN RESIDENT A -- PGR 12345': ('TT MICU GREEN RESIDENT A', 'TMGRA'),
    'CON NEPHROLOGY MAFFLY': ('CON NEPHROLOGY MAFFLY', 'CNM'),
    'CON VASCULAR SURGERY': ('CON VASCULAR SURGERY', 'CVS'),
    'TT MED TX HEP RES B, PGR 12345': ('TT MED TX HEP RES B', 'TMTHRB'),
    'TT GEN SURG WHITE - PAGER 12345': ('TT GEN SURG WHITE', 'TGSW'),
    'CON PULMONARY REHAB CONSULT': ('CON PULMONARY REHAB CONSULT', 'CPRC'),
    'CON PAMF MEDICINE': ('CON PAMF MEDICINE', 'CPM'),
    'TT MED TX HEP RES A, PGR 12345': ('TT MED TX HEP RES A', 'TMTHRA'),
    'CON PALLIATIVE CARE - PGR 12345': ('CON PALLIATIVE CARE', 'CPC'),
    'TT INTERVENTIONAL RADIOLOGY, .': ('TT INTERVENTIONAL RADIOLOGY', 'TIR'),
    'CON INTERVENT RAD': ('CON INTERVENT RAD', 'CIR'),
    'CON PULM HYPERTENSION': ('CON PULM HYPERTENSION', 'CPH'),
    'CON MICU CONSULT': ('CON MICU CONSULT', 'CMC'),
    'CON PRIMARY CARE': ('CON PRIMARY CARE', 'CPC'),
    'TT CARDIOLOGY 5A, .': ('TT CARDIOLOGY 5A', 'TC5'),
    'TT NEURO EPILEPSY MONITOR UNIT, .': ('TT NEURO EPILEPSY MONITOR UNIT', 'TNEMU'),
    'CON TRANSPLANT SURGERY': ('CON TRANSPLANT SURGERY', 'CTS'),
    'TT MICU BLUE RESIDENT A -- PGR 12345': ('TT MICU BLUE RESIDENT A', 'TMBRA'),
    'TT MED TX-HEP, .': ('TT MED TX-HEP', 'TMT'),
    'CON PSYCHIATRY': ('CON PSYCHIATRY', 'CP'),
    'TT BMT, .': ('TT BMT', 'TB'),
    'TT CARDIOLOGY 6B, .': ('TT CARDIOLOGY 6B', 'TC6'),
    'TT ORTHO TRAUMA, .': ('TT ORTHO TRAUMA', 'TOT'),
    'TT MED PAMF NON RESI': ('TT MED PAMF NON RESI', 'TMPNR'),
    'TT GEN SURG RED - PAGER 12345': ('TT GEN SURG RED', 'TGSR'),
    'TT CARDIOLOGY 6B INTERN -- PGR 12345': ('TT CARDIOLOGY 6B INTERN', 'TC6I'),
    'TT NEUROLOGY, .': ('TT NEUROLOGY', 'TN'),
    'TT CARDIOLOGY 5B, .': ('TT CARDIOLOGY 5B', 'TC5'),
    'TT ONCOLOGY, .': ('TT ONCOLOGY', 'TO'),
    'TT MED DAY B, PGR 12345': ('TT MED DAY B', 'TMDB'),
    'CON GASTROENTEROLOGY': ('CON GASTROENTEROLOGY', 'CG'),
    'TT CARDIOLOGY 6A, .': ('TT CARDIOLOGY 6A', 'TC6'),
    'CON COLORECTAL SURGERY': ('CON COLORECTAL SURGERY', 'CCS'),
    'TT CARDIOLOGY INTERVENTIONAL -- PGR 12345': ('TT CARDIOLOGY INTERVENTIONAL', 'TCI'),
    'TT NEUROSURGERY A VASCULAR ICU, PGR 12345': ('TT NEUROSURGERY A VASCULAR ICU', 'TNAVI'),
    'TT GYN, .': ('TT GYN', 'TG'),
    'CON NEURO ONCOLOGY': ('CON NEURO ONCOLOGY', 'CNO'),
    'TT GYN ONC, .': ('TT GYN ONC', 'TGO'),
    'TT GEN SURG GOLD - PAGER 12345': ('TT GEN SURG GOLD', 'TGSG'),
    'CON GERIATRICS': ('CON GERIATRICS', 'CG'),
    'TT HEMATOLOGY, .': ('TT HEMATOLOGY', 'TH'),
    'CON GYNECOLOGY': ('CON GYNECOLOGY', 'CG'),
    'CON ENDOCRINOLOGY': ('CON ENDOCRINOLOGY', 'CE'),
    'CON CRITICAL CARE CONSULT': ('CON CRITICAL CARE CONSULT', 'CCCC'),
    'TT NEUROSURGERY, .': ('TT NEUROSURGERY', 'TN'),
    'TT MED DAY A, PGR 12345': ('TT MED DAY A', 'TMDA'),
    'CON GENERAL SURGERY': ('CON GENERAL SURGERY', 'CGS'),
    'TT ONCOLOGY NP, PGR 12345': ('TT ONCOLOGY NP', 'TON'),
    'TT HEMATOLOGY NP A, PGR 12345': ('TT HEMATOLOGY NP A', 'THNA'),
    'TT PULMONARY TRANSPLANT, .': ('TT PULMONARY TRANSPLANT', 'TPT'),
    'CON KIDNEY TRANSPLANT': ('CON KIDNEY TRANSPLANT', 'CKT'),
    'CON CARD INTERVEN/AMI CONSULT': ('CON CARD INTERVEN/AMI CONSULT', 'CCIC'),
    'CON CARDIOL TRANSPLANT': ('CON CARDIOL TRANSPLANT', 'CCT'),
    'TT ORTHO SURGERY, .': ('TT ORTHO SURGERY', 'TOS'),
    'CON CARDIOLOGY ADMISSION REQUEST': ('CON CARDIOLOGY ADMISSION REQUEST', 'CCAR'),
    'TT PLASTIC SURGERY, .': ('TT PLASTIC SURGERY', 'TPS'),
    'TT HEART LUNG TRANSPLANT, .': ('TT HEART LUNG TRANSPLANT', 'THLT'),
    'TT UROLOGY, .': ('TT UROLOGY', 'TU'),
    'CON CYSTIC FIBROSIS ADULT': ('CON CYSTIC FIBROSIS ADULT', 'CCFA'),
    'TT CARDIOLOGY INTERVENTIONAL, .': ('TT CARDIOLOGY INTERVENTIONAL', 'TCI'),
    'TT CYSTIC FIBROSIS ADULT, .': ('TT CYSTIC FIBROSIS ADULT', 'TCFA'),
    'TT ENT HEAD NECK, .': ('TT ENT HEAD NECK', 'TEHN'),
    'TT ORTHO SPINE, .': ('TT ORTHO SPINE', 'TOS'),
    'TT NEUROSURGERY C, .': ('TT NEUROSURGERY C', 'TNC'),
    'TT NEUROSURGERY B, .': ('TT NEUROSURGERY B', 'TNB'),
    'TT ENT SPECIALTY, .': ('TT ENT SPECIALTY', 'TES'),
    'TT HEART TRANSPLANT/VAD -- PGR 12345': ('TT HEART TRANSPLANT/VAD', 'THT'),
    'TT CARDIOLOGY ARRHYTHMIA, .': ('TT CARDIOLOGY ARRHYTHMIA', 'TCA'),
    'TT ORTHO JOINT, .': ('TT ORTHO JOINT', 'TOJ'),
    'TT ORTHO FOOT & ANKLE, .': ('TT ORTHO FOOT ANKLE', 'TOFA'),
    'TT PAIN RESIDENT 2 -- PGR 12345': ('TT PAIN RESIDENT 2', 'TPR2'),
    'CON NEUROSURGERY': ('CON NEUROSURGERY', 'CN'),
    'CON CARDIOTHROACIC SURGERY': ('CON CARDIOTHROACIC SURGERY', 'CCS'),
    'TT HAND SURGERY, .': ('TT HAND SURGERY', 'THS'),
    'TT ORTHO TUMOR, .': ('TT ORTHO TUMOR', 'TOT'),
    'CON LIVER TRANSPLANT': ('CON LIVER TRANSPLANT', 'CLT'),
    'TT NEUROSURGERY A, .': ('TT NEUROSURGERY A', 'TNA'),
    'CON ENT': ('CON ENT', 'CE'),
    'CON HOSPICE CONSULT': ('CON HOSPICE CONSULT', 'CHC'),
    'CON PLASTIC SURGERY': ('CON PLASTIC SURGERY', 'CPS'),
    'CON NEURO IR': ('CON NEURO IR', 'CNI'),
    'CON INF DIS': ('CON INF DIS', 'CID'),
    'CON INF DIS IMMUNOCOMP': ('CON INF DIS IMMUNOCOMP', 'CIDI'),
    'CON DERMATOLOGY': ('CON DERMATOLOGY', 'CD'),
    'CON OPHTHALMOLOGY': ('CON OPHTHALMOLOGY', 'CO'),
    'CON RHEUMATOLOGY': ('CON RHEUMATOLOGY', 'CR'),
    'CON UROLOGY': ('CON UROLOGY', 'CU'),
    'CON HAND SURGERY': ('CON HAND SURGERY', 'CHS'),
    'CON WOUND/OSTOMY/CONTINENCE RN': ('CON WOUND/OSTOMY/CONTINENCE RN', 'CWR'),
    'CON NEPHROLOGY ATTENDING': ('CON NEPHROLOGY ATTENDING', 'CNA'),
    'CON MEDICINE ADMISSION REQUEST': ('CON MEDICINE ADMISSION REQUEST', 'CMAR'),
    'CON ORTHOPEDICS': ('CON ORTHOPEDICS', 'CO'),
    'CON OBSTETRICS': ('CON OBSTETRICS', 'CO'),
    'CON NEURO ENDOCRINE CONSULT': ('CON NEURO ENDOCRINE CONSULT', 'CNEC'),
    'CON SPINE TRAUMA': ('CON SPINE TRAUMA', 'CST'),
    'CON MICU ADMISSION REQUEST': ('CON MICU ADMISSION REQUEST', 'CMAR'),
    'CON MEDICAL GENETICS': ('CON MEDICAL GENETICS', 'CMG'),
    'CON SURGERY CONSULT': ('CON SURGERY CONSULT', 'CSC'),
    'TT PAMF NON RESIDENT SURGERY': ('TT PAMF NON RESIDENT SURGERY', 'TPNRS'),
    'CON CARDIOL INTERVENT-AMI': ('CON CARDIOL INTERVENT-AMI', 'CCI'),
    'CON INF DIS POSTITIVE CARE': ('CON INF DIS POSTITIVE CARE', 'CIDPC'),
    'CON SLEEP': ('CON SLEEP', 'CS'),
    'CON ANESTHESIA CONSULT ADULT': ('CON ANESTHESIA CONSULT ADULT', 'CACA')
}


AGGR_NAME_TO_ACRONYM = {
    'Intern': ('', ''),
    'Cross Cover Intern': ('Cross Cover', 'CC'),
    'Wound/Ostomy/Continence RN': ('Wound/Ostomy/Continence RN', 'WR'),
    'Primary Intern': ('Primary', 'P'),
    'Primary Resident': ('Primary', 'P'),
    'Cross Cover Attending': ('Cross Cover', 'CC'),
    'Student Nurse': ('Student Nurse', 'SN'),
    'Clinical Pharmacist': ('Clinical Pharmacist', 'CP'),
    'Medical Assistant': ('Medical Assistant', 'MA'),
    'Licensed Vocational Nurse': ('Licensed Vocational Nurse', 'LVN'),
    'Clinical Nurse Specialist': ('Clinical Nurse Specialist', 'CNS'),
    'Cross Cover Fellow': ('Cross Cover Fellow', 'CCF'),
    'ED Unit Secretary': ('ED Unit Secretary', 'EUS'),
    'Primary Fellow': ('Primary', 'P'),
    'Cross Cover Resident': ('Cross Cover', 'CC'),
    'Consulting Attending': ('Consulting', 'C'),
    'Consulting Fellow': ('Consulting', 'C'),
    'Spiritual Care': ('Spiritual Care', 'SC'),
    'Consulting Med Student': ('Consulting', 'C'),
    'Primary Advanced Practice Provider': ('Primary', 'P'),
    'Physician Assistant': ('Primary', 'P'),
    'Consulting Resident': ('Consulting', 'C'),
    'Nurse Coordinator': ('Nurse Coordinator', 'NC'),
    'Fellow': ('Fellow', 'F'),
    'Consulting Intern': ('Consulting', 'C'),
    'Co-Attending': ('Co-Attending', 'C'),
    'Surgeon': ('Surgeon', 'S'),
    'Primary Med Student': ('Primary', 'P'),
    'ED Tech': ('ED Tech', 'ET'),
    'Resident': ('', ''),
    'Chief Resident': ('Chief', 'C'),
    'Medical Student': ('Medical Student', 'MS'),
    'Primary Medical Student': ('Primary', 'P'),
    'Pulmonologist': ('Pulmonologist', 'P'),
    'Pediatrician': ('Pediatrician', 'P'),
    'Hematologist': ('Hematologist', 'H'),
    'Primary Care Physician': ('Primary', 'P'),
    'Primary Physician Assistant': ('Primary', 'P'),
    'Cardiologist': ('Cardiologist', 'C'),
    'Triage Nurse': ('Triage Nurse', 'TN'),
    'Transplant Social Worker': ('Transplant Social Worker', 'TSW'),
    'Additional Communicating Provider': ('Additional Communicating Provider', 'ACP'),
    'ED Registrar': ('ED Registrar', 'ER'),
    'Gastroenterologist': ('Gastroenterologist', 'G'),
    'Medical Oncologist': ('Medical Oncologist', 'MO'),
    'Primary Sub-Intern': ('Primary', 'P'),
    'Lactation Consultant': ('Lactation Consultant', 'LC'),
    'Trauma Attending': ('Trauma', 'T'),
    'Post-Transplant Nurse': ('Post-Transplant Nurse', 'PN'),
    'Cross Cover Advanced Practice Provider ': ('Cross Cover Advanced Practice Provider', 'CCAPP'),
    'Internist': ('Internist', 'I'),
    'Nephrologist': ('Nephrologist', 'N'),
    'Research Coordinator': ('Research Coordinator', 'RC'),
    'Infectious Disease': ('Infectious Disease', 'ID'),
    'Trauma Resident ': ('Trauma', 'T'),
    'Primary Sub-intern': ('Primary', 'P'),
    'Neurologist': ('Neurologist', 'N'),
    'Transplant Surgeon': ('Transplant Surgeon', 'TS'),
    'Consulting Medical Oncologist': ('Consulting', 'C'),
    'Family Practitioner': ('Family Practitioner', 'FP'),
    'Dermatologist': ('Dermatologist', 'D'),
    'Aging Adult Services Coordinator': ('Aging Adult Services Coordinator', 'AASC'),
    'Transplant Nephrologist': ('Transplant Nephrologist', 'TN'),
    'Post-Transplant Nephrologist': ('Post-Transplant Nephrologist', 'PN'),
    'Consulting Surgical Oncologist': ('Consulting', 'C'),
    'Surgical Oncologist': ('Surgical Oncologist', 'SO'),
    'Nursery Nurse': ('Nursery Nurse', 'NN'),
    'Transplant Pharmacist': ('Transplant Pharmacist', 'TP'),
    'Psychologist': ('Psychologist', 'P'),
    'Restorative Aide': ('Restorative Aide', 'RA'),
    'Child Life Specialist': ('Child Life Specialist', 'CLS'),
    'Consulting Hematologist': ('Consulting', 'C'),
    'Endocrinologist': ('Endocrinologist', 'E'),
    'Electrophysiologist': ('Electrophysiologist', 'E'),
    'Anesthesiologist': ('Anesthesiologist', 'A'),
    'Transplant Dietitian': ('Transplant Dietitian', 'TD'),
    'Urologist': ('Urologist', 'U'),
    'stop0': ('stop0', 's'),
    'Radiation Oncologist': ('Radiation Oncologist', 'RO'),
    'Referring Provider': ('Referring Provider', 'RP'),
    'Activity Therapist': ('Activity Therapist', 'AT'),
    'Transplant Pulmonologist': ('Transplant Pulmonologist', 'TP'),
    'Obstetrician': ('Obstetrician', 'O'),
    'Heart Failure Cardiologist': ('Heart Failure Cardiologist', 'HFC'),
    'Post RN Coordinator': ('Post RN Coordinator', 'PRC'),
    'Delivery Assist': ('Delivery Assist', 'DA'),
    'Referring Nephrologist': ('Referring Nephrologist', 'RN'),
    'Hepatologist': ('Hepatologist', 'H'),
    'Case Manager': ('Case Manager', 'CM'),
    'Primary Team': ('Primary', 'P'),
    'Social Worker': ('Social Worker', 'SW'),
    'Care Coordinator': ('Care Coordinator', 'CC'),
    'Registered Nurse': ('Registered Nurse', 'RN'),
    'Speech Therapist': ('Speech Therapist', 'ST'),
    'Nursing Assistant': ('Nursing Assistant', 'NA'),
    'Clinical Dietitian': ('Clinical Dietitian', 'CD'),
    'Consulting Service': ('Consulting', 'C'),
    'Emergency Resident': ('Emergency', 'E'),
    'Nurse Practitioner': ('Primary', 'P'),
    'Physical Therapist': ('Physical Therapist', 'PT'),
    'Occupational Therapist': ('Occupational Therapist', 'OT'),
    'Physical Therapist Assistant': ('Physical Therapist Assistant', 'PTA'),
    'Respiratory Care Practitioner': ('Respiratory Care Practitioner', 'RCP'),
    'Independent Living Donor Advocate': ('Independent Living Donor Advocate', 'ILDA'),
    'Pre RN Coordinator': ('Pre RN Coordinator', 'PRC'),
    'Dietician Intern': ('Dietician', 'D'),
    'Survivorship Provider': ('Survivorship Provider', 'SP'),
    'Consulting Reconstructive Surgeon': ('Consulting', 'C'),
    'Referring Pulmonologist': ('Referring Pulmonologist', 'RP')
}

AGGR_PROV_TO_CLEAN_ACRONYM = {
    'SMITH, JOHN': ('', ''),
    'SMITH, JANE': ('', ''),
    'DOE, JOHN': ('', ''),
    'DOE, JANE': ('', ''),
    'CON CARDIOLOGY': ('CON CARDIOLOGY', 'CC'),
    'CON MEDICINE': ('CON MEDICINE', 'CM'),
    'CON PULMONARY': ('CON PULMONARY', 'CP'),
    'CON NEURO ICU': ('CON NEURO ICU', 'CNI'),
    'CON CARDIOL ARRHYTHMIA': ('CON CARDIOL ARRHYTHMIA', 'CCA'),
    'CON NEURO EPILEPSY CONSULT': ('CON NEURO EPILEPSY CONSULT', 'CNEC'),
    'CON NEPHROLOGY JAMISON': ('CON NEPHROLOGY JAMISON', 'CNJ'),
    'CON CARDIAC SURGERY': ('CON CARDIAC SURGERY', 'CCS'),
    'TT CVICU TEAM 2 - SPECTRAS 1-2345, 2-3456': ('TT CVICU TEAM', 'TCT'),
    'CON PAIN': ('CON PAIN', 'CP'),
    'CON ONCOLOGY': ('CON ONCOLOGY', 'CO'),
    'CON NEUROLOGY GENERAL': ('CON NEUROLOGY GENERAL', 'CNG'),
    'CON NEURO STROKE': ('CON NEURO STROKE', 'CNS'),
    'TT NEUROSURGERY C SPINE FLOOR, PGR 12345': ('TT NEUROSURGERY SPINE FLOOR', 'TNSF'),
    'CON NEPHROLOGY TRANSPLANT': ('CON NEPHROLOGY TRANSPLANT', 'CNT'),
    'TT ACUTE CARE SURGERY TRAUMA, PGR 12345': ('TT ACUTE CARE SURGERY TRAUMA', 'TACST'),
    'CON INTERNAL MEDICINE CONSULT': ('CON INTERNAL MEDICINE CONSULT', 'CIMC'),
    'CON ICU': ('CON ICU', 'CI'),
    'CON ALLERGY IMMUNOLOGY CONSULT': ('CON ALLERGY IMMUNOLOGY CONSULT', 'CAIC'),
    'TT CVICU TEAM 1 - SPECTRAS 1-2345, 2-3456': ('TT CVICU TEAM', 'TCT'),
    'TT NEUROSURGERY A VASCULAR FLOOR, PGR 12345': ('TT NEUROSURGERY VASCULAR FLOOR', 'TNVF'),
    'CON HEMATOLOGY': ('CON HEMATOLOGY', 'CH'),
    'CON ORTHOPEDICS HOSPITALIST': ('CON ORTHOPEDICS HOSPITALIST', 'COH'),
    'TT COLORECTAL SURGERY, PGR 12345': ('TT COLORECTAL SURGERY', 'TCS'),
    'CON THORACIC SURGERY': ('CON THORACIC SURGERY', 'CTS'),
    'TT NEUROSURGERY B TUMOR FLOOR, PGR 12345': ('TT NEUROSURGERY TUMOR FLOOR', 'TNTF'),
    'CON PULM TRANSPLANT': ('CON PULM TRANSPLANT', 'CPT'),
    'TT NEUROSURGERY B TUMOR ICU, PGR 12345': ('TT NEUROSURGERY TUMOR ICU', 'TNTI'),
    'CON HEPATOLOGY': ('CON HEPATOLOGY', 'CH'),
    'TT NEUROSURGERY C SPINE ICU, PGR 12345': ('TT NEUROSURGERY SPINE ICU', 'TNSI'),
    'TT PAIN, .': ('TT PAIN', 'TP'),
    'TT MICU GREEN RESIDENT A -- PGR 12345': ('TT MICU', 'TM'),
    'CON NEPHROLOGY MAFFLY': ('CON NEPHROLOGY MAFFLY', 'CNM'),
    'CON VASCULAR SURGERY': ('CON VASCULAR SURGERY', 'CVS'),
    'TT MED TX HEP RES B, PGR 12345': ('TT MED TX HEP', 'TMTH'),
    'TT GEN SURG WHITE - PAGER 12345': ('TT GEN SURG', 'TGS'),
    'CON PULMONARY REHAB CONSULT': ('CON PULMONARY REHAB CONSULT', 'CPRC'),
    'CON PAMF MEDICINE': ('CON PAMF MEDICINE', 'CPM'),
    'TT MED TX HEP RES A, PGR 12345': ('TT MED TX HEP', 'TMTH'),
    'CON PALLIATIVE CARE - PGR 12345': ('CON PALLIATIVE CARE', 'CPC'),
    'TT INTERVENTIONAL RADIOLOGY, .': ('TT INTERVENTIONAL RADIOLOGY', 'TIR'),
    'CON INTERVENT RAD': ('CON INTERVENT RAD', 'CIR'),
    'CON PULM HYPERTENSION': ('CON PULM HYPERTENSION', 'CPH'),
    'CON MICU CONSULT': ('CON MICU CONSULT', 'CMC'),
    'CON PRIMARY CARE': ('CON PRIMARY CARE', 'CPC'),
    'TT CARDIOLOGY 5A, .': ('TT CARDIOLOGY', 'TC'),
    'TT NEURO EPILEPSY MONITOR UNIT, .': ('TT NEURO EPILEPSY MONITOR UNIT', 'TNEMU'),
    'CON TRANSPLANT SURGERY': ('CON TRANSPLANT SURGERY', 'CTS'),
    'TT MICU BLUE RESIDENT A -- PGR 12345': ('TT MICU', 'TM'),
    'TT MED TX-HEP, .': ('TT MED TX-HEP', 'TMT'),
    'CON PSYCHIATRY': ('CON PSYCHIATRY', 'CP'),
    'TT BMT, .': ('TT BMT', 'TB'),
    'TT CARDIOLOGY 6B, .': ('TT CARDIOLOGY', 'TC'),
    'TT ORTHO TRAUMA, .': ('TT ORTHO TRAUMA', 'TOT'),
    'TT MED PAMF NON RESI': ('TT MED PAMF', 'TMP'),
    'TT GEN SURG RED - PAGER 12345': ('TT GEN SURG', 'TGS'),
    'TT CARDIOLOGY 6B INTERN -- PGR 12345': ('TT CARDIOLOGY', 'TC'),
    'TT NEUROLOGY, .': ('TT NEUROLOGY', 'TN'),
    'TT CARDIOLOGY 5B, .': ('TT CARDIOLOGY', 'TC'),
    'TT ONCOLOGY, .': ('TT ONCOLOGY', 'TO'),
    'TT MED DAY B, PGR 12345': ('TT MED DAY', 'TMD'),
    'CON GASTROENTEROLOGY': ('CON GASTROENTEROLOGY', 'CG'),
    'TT CARDIOLOGY 6A, .': ('TT CARDIOLOGY', 'TC'),
    'CON COLORECTAL SURGERY': ('CON COLORECTAL SURGERY', 'CCS'),
    'TT CARDIOLOGY INTERVENTIONAL -- PGR 12345': ('TT CARDIOLOGY INTERVENTIONAL', 'TCI'),
    'TT NEUROSURGERY A VASCULAR ICU, PGR 12345': ('TT NEUROSURGERY VASCULAR ICU', 'TNVI'),
    'TT GYN, .': ('TT GYN', 'TG'),
    'CON NEURO ONCOLOGY': ('CON NEURO ONCOLOGY', 'CNO'),
    'TT GYN ONC, .': ('TT GYN ONC', 'TGO'),
    'TT GEN SURG GOLD - PAGER 12345': ('TT GEN SURG', 'TGS'),
    'CON GERIATRICS': ('CON GERIATRICS', 'CG'),
    'TT HEMATOLOGY, .': ('TT HEMATOLOGY', 'TH'),
    'CON GYNECOLOGY': ('CON GYNECOLOGY', 'CG'),
    'CON ENDOCRINOLOGY': ('CON ENDOCRINOLOGY', 'CE'),
    'CON CRITICAL CARE CONSULT': ('CON CRITICAL CARE CONSULT', 'CCCC'),
    'TT NEUROSURGERY, .': ('TT NEUROSURGERY', 'TN'),
    'TT MED DAY A, PGR 12345': ('TT MED DAY', 'TMD'),
    'CON GENERAL SURGERY': ('CON GENERAL SURGERY', 'CGS'),
    'TT ONCOLOGY NP, PGR 12345': ('TT ONCOLOGY', 'TO'),
    'TT HEMATOLOGY NP A, PGR 12345': ('TT HEMATOLOGY', 'TH'),
    'TT PULMONARY TRANSPLANT, .': ('TT PULMONARY TRANSPLANT', 'TPT'),
    'CON KIDNEY TRANSPLANT': ('CON KIDNEY TRANSPLANT', 'CKT'),
    'CON CARD INTERVEN/AMI CONSULT': ('CON CARD INTERVEN/AMI CONSULT', 'CCIC'),
    'CON CARDIOL TRANSPLANT': ('CON CARDIOL TRANSPLANT', 'CCT'),
    'TT ORTHO SURGERY, .': ('TT ORTHO SURGERY', 'TOS'),
    'CON CARDIOLOGY ADMISSION REQUEST': ('CON CARDIOLOGY ADMISSION REQUEST', 'CCAR'),
    'TT PLASTIC SURGERY, .': ('TT PLASTIC SURGERY', 'TPS'),
    'TT HEART LUNG TRANSPLANT, .': ('TT HEART LUNG TRANSPLANT', 'THLT'),
    'TT UROLOGY, .': ('TT UROLOGY', 'TU'),
    'CON CYSTIC FIBROSIS ADULT': ('CON CYSTIC FIBROSIS ADULT', 'CCFA'),
    'TT CARDIOLOGY INTERVENTIONAL, .': ('TT CARDIOLOGY INTERVENTIONAL', 'TCI'),
    'TT CYSTIC FIBROSIS ADULT, .': ('TT CYSTIC FIBROSIS ADULT', 'TCFA'),
    'TT ENT HEAD NECK, .': ('TT ENT HEAD NECK', 'TEHN'),
    'TT ORTHO SPINE, .': ('TT ORTHO SPINE', 'TOS'),
    'TT NEUROSURGERY C, .': ('TT NEUROSURGERY', 'TN'),
    'TT NEUROSURGERY B, .': ('TT NEUROSURGERY', 'TN'),
    'TT ENT SPECIALTY, .': ('TT ENT SPECIALTY', 'TES'),
    'TT HEART TRANSPLANT/VAD -- PGR 12345': ('TT HEART TRANSPLANT/VAD', 'THT'),
    'TT CARDIOLOGY ARRHYTHMIA, .': ('TT CARDIOLOGY ARRHYTHMIA', 'TCA'),
    'TT ORTHO JOINT, .': ('TT ORTHO JOINT', 'TOJ'),
    'TT ORTHO FOOT & ANKLE, .': ('TT ORTHO FOOT ANKLE', 'TOFA'),
    'TT PAIN RESIDENT 2 -- PGR 12345': ('TT PAIN', 'TP'),
    'CON NEUROSURGERY': ('CON NEUROSURGERY', 'CN'),
    'CON CARDIOTHROACIC SURGERY': ('CON CARDIOTHROACIC SURGERY', 'CCS'),
    'TT HAND SURGERY, .': ('TT HAND SURGERY', 'THS'),
    'TT ORTHO TUMOR, .': ('TT ORTHO TUMOR', 'TOT'),
    'CON LIVER TRANSPLANT': ('CON LIVER TRANSPLANT', 'CLT'),
    'TT NEUROSURGERY A, .': ('TT NEUROSURGERY', 'TN'),
    'CON ENT': ('CON ENT', 'CE'),
    'CON HOSPICE CONSULT': ('CON HOSPICE CONSULT', 'CHC'),
    'CON PLASTIC SURGERY': ('CON PLASTIC SURGERY', 'CPS'),
    'CON NEURO IR': ('CON NEURO IR', 'CNI'),
    'CON INF DIS': ('CON INF DIS', 'CID'),
    'CON INF DIS IMMUNOCOMP': ('CON INF DIS IMMUNOCOMP', 'CIDI'),
    'CON DERMATOLOGY': ('CON DERMATOLOGY', 'CD'),
    'CON OPHTHALMOLOGY': ('CON OPHTHALMOLOGY', 'CO'),
    'CON RHEUMATOLOGY': ('CON RHEUMATOLOGY', 'CR'),
    'CON UROLOGY': ('CON UROLOGY', 'CU'),
    'CON HAND SURGERY': ('CON HAND SURGERY', 'CHS'),
    'CON WOUND/OSTOMY/CONTINENCE RN': ('CON WOUND/OSTOMY/CONTINENCE RN', 'CWR'),
    'CON NEPHROLOGY ATTENDING': ('CON NEPHROLOGY', 'CN'),
    'CON MEDICINE ADMISSION REQUEST': ('CON MEDICINE ADMISSION REQUEST', 'CMAR'),
    'CON ORTHOPEDICS': ('CON ORTHOPEDICS', 'CO'),
    'CON OBSTETRICS': ('CON OBSTETRICS', 'CO'),
    'CON NEURO ENDOCRINE CONSULT': ('CON NEURO ENDOCRINE CONSULT', 'CNEC'),
    'CON SPINE TRAUMA': ('CON SPINE TRAUMA', 'CST'),
    'CON MICU ADMISSION REQUEST': ('CON MICU ADMISSION REQUEST', 'CMAR'),
    'CON MEDICAL GENETICS': ('CON MEDICAL GENETICS', 'CMG'),
    'CON SURGERY CONSULT': ('CON SURGERY CONSULT', 'CSC'),
    'TT PAMF NON RESIDENT SURGERY': ('TT PAMF SURGERY', 'TPS'),
    'CON CARDIOL INTERVENT-AMI': ('CON CARDIOL INTERVENT-AMI', 'CCI'),
    'CON INF DIS POSTITIVE CARE': ('CON INF DIS POSTITIVE CARE', 'CIDPC'),
    'CON SLEEP': ('CON SLEEP', 'CS'),
    'CON ANESTHESIA CONSULT ADULT': ('CON ANESTHESIA CONSULT ADULT', 'CACA')
}


class TestSTARRTreatmentTeamConversion(DBTestCase):
    TEST_DATA_SIZE = 50

    test_data = []
    expected_data = []

    test_data_csv = tempfile.gettempdir() + '/test_starr_treatment_team_dummy_data.csv'

    def setUp(self):
        log.setLevel(logging.INFO)  # without this no logs are printed

        """Prepare state for test cases"""
        DBTestCase.setUp(self)

        log.info("Sourcing from BigQuery DB")
        ClinicalItemDataLoader.build_clinical_item_psql_schemata()

        self.converter = STARRTreatmentTeamConversion.STARRTreatmentTeamConversion()  # Instance to test on
        self.bqConn = self.converter.bqConn
        self.starrUtil = STARRUtil.StarrCommonUtils(self.converter.bqClient)

        # point the converter to dummy source table
        STARRTreatmentTeamConversion.SOURCE_TABLE = TEST_SOURCE_TABLE

        log.warn("Removing test table, if exists: {}".format(TEST_SOURCE_TABLE))
        bq_cursor = self.bqConn.cursor()
        bq_cursor.execute('DROP TABLE IF EXISTS {};'.format(TEST_SOURCE_TABLE))

    def generate_test_and_expected_data(self, test_data_size, aggregate):
        for curr_row in range(test_data_size):
            patient_id = 'JC' + format(curr_row, '06')
            test_data_row = self.generate_test_data_row(curr_row, self.starrUtil.random_period(), patient_id)
            self.test_data.append(test_data_row)
            self.generate_expected_data_rows(test_data_row, self.expected_data, aggregate)

        # pi.external_id desc (ci.external_id is always None, so not included here)
        self.expected_data.sort(key=lambda tup: (-tup[0]))

        log.debug('test_data: {}'.format(self.test_data))
        log.debug('expected_data: {}'.format(self.expected_data))

    @staticmethod
    def generate_test_data_row(curr_row, treatment_period, patient_id):
        return (
            'SS' + format(curr_row, '07'),
            patient_id,
            curr_row,
            datetime.fromtimestamp(treatment_period[0]),
            datetime.fromtimestamp(treatment_period[1]),
            NAME_TO_ACRONYM.keys()[random.randint(0, len(NAME_TO_ACRONYM) - 1)],
            PROV_TO_CLEAN_ACRONYM.keys()[random.randint(0, len(PROV_TO_CLEAN_ACRONYM) - 1)],
            datetime.fromtimestamp(treatment_period[0], tz=pytz.UTC),
        )

    def generate_expected_data_rows(self, row, expected_data, aggregate):
        if not aggregate:
            expected_row = (
                self.starrUtil.convertPatIdToSTRIDE(row[0]),
                self.starrUtil.convertPatIdToSTRIDE(row[1]),
                row[2],
                STARRTreatmentTeamConversion.CATEGORY_TEMPLATE,
                None,
                NAME_TO_ACRONYM[row[5]] if PROV_TO_CLEAN_ACRONYM[row[6]][1] == ''
                                        else PROV_TO_CLEAN_ACRONYM[row[6]][1] + ' (' + NAME_TO_ACRONYM[row[5]] + ')',
                row[5].strip() if PROV_TO_CLEAN_ACRONYM[row[6]][1] == ''
                               else PROV_TO_CLEAN_ACRONYM[row[6]][0].title() + ' (' + row[5].strip() + ')',
                row[3].replace(tzinfo=pytz.UTC),
                row[7].replace(tzinfo=pytz.UTC),
            )
        else:
            expected_row = (
                self.starrUtil.convertPatIdToSTRIDE(row[0]),
                self.starrUtil.convertPatIdToSTRIDE(row[1]),
                row[2],
                STARRTreatmentTeamConversion.CATEGORY_TEMPLATE,
                None,
                AGGR_NAME_TO_ACRONYM[row[5]][1]
                    if AGGR_PROV_TO_CLEAN_ACRONYM[row[6]][1] == ''
                    else AGGR_PROV_TO_CLEAN_ACRONYM[row[6]][1] + ' (' + AGGR_NAME_TO_ACRONYM[row[5]][1] + ')',
                AGGR_NAME_TO_ACRONYM[row[5]][0]
                    if AGGR_PROV_TO_CLEAN_ACRONYM[row[6]][1] == ''
                    else AGGR_PROV_TO_CLEAN_ACRONYM[row[6]][0].title() + ' (' + AGGR_NAME_TO_ACRONYM[row[5]][0] + ')',
                row[3].replace(tzinfo=pytz.UTC),
                row[7].replace(tzinfo=pytz.UTC)
            )

        expected_data.append(expected_row)

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        self.test_data[:] = []
        self.expected_data[:] = []
        os.remove(self.test_data_csv)

        log.info("Purge test records from the database")

        DBUtil.execute(
            """delete from patient_item
            where clinical_item_id in
            (   select clinical_item_id
                from clinical_item as ci, clinical_item_category as cic
                where ci.clinical_item_category_id = cic.clinical_item_category_id
                and cic.source_table = '%s'
            )
            """ % TEST_SOURCE_TABLE
        )
        DBUtil.execute(
            """delete from clinical_item
            where clinical_item_category_id in
            (   select clinical_item_category_id
                from clinical_item_category
                where source_table = '%s'
            )
            """ % TEST_SOURCE_TABLE
        )
        DBUtil.execute("delete from clinical_item_category where source_table = '%s';" % TEST_SOURCE_TABLE)

        bq_cursor = self.bqConn.cursor()
        bq_cursor.execute('DELETE FROM %s.patient_item WHERE true;' % TEST_DEST_DATASET)
        bq_cursor.execute('DELETE FROM %s.clinical_item WHERE true;' % TEST_DEST_DATASET)
        bq_cursor.execute('DELETE FROM %s.clinical_item_category WHERE true;' % TEST_DEST_DATASET)

        bq_cursor.execute('DROP TABLE %s;' % TEST_SOURCE_TABLE)

        DBTestCase.tearDown(self)

    @parameterized.expand([
        ["without_aggregation", False],
        ["with_aggregation", True]
    ])
    def test_dataConversion(self, name, aggregation):
        log.info("Generating test source data")
        self.generate_test_and_expected_data(self.TEST_DATA_SIZE, aggregate=aggregation)
        self.starrUtil.dump_test_data_to_csv(self.converter.HEADERS, self.test_data, self.test_data_csv)
        self.starrUtil.upload_csv_to_bigquery('starr_datalake2018', 'treatment_team', TEST_DEST_DATASET,
                                              'starr_treatment_team', self.test_data_csv, self.converter.HEADERS)

        log.debug("Run the conversion process...")
        conv_options = STARRTreatmentTeamConversion.ConversionOptions()
        conv_options.aggregate = aggregation
        temp_dir = tempfile.gettempdir();
        self.converter.convertAndUpload(conv_options, tempDir=temp_dir, datasetId=TEST_DEST_DATASET)

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
                pi.item_date,
                pi.item_date_utc
            from
                %s.patient_item as pi,
                %s.clinical_item as ci,
                %s.clinical_item_category as cic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = '%s'
            order by
                pi.external_id desc, ci.external_id desc
            """ % (TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_SOURCE_TABLE)

        bq_cursor = self.bqConn.cursor()
        bq_cursor.execute(test_query)
        actual_data = [row.values() for row in bq_cursor.fetchall()]
        log.debug('actual data: {}'.format(actual_data))
        log.debug('expected data: {}'.format(self.expected_data))
        self.assertEqualTable(self.expected_data, actual_data)


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSTARRTreatmentTeamConversion))

    return test_suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
