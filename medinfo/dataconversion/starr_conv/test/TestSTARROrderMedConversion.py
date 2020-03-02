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

from medinfo.dataconversion.starr_conv import STARROrderMedConversion
from medinfo.dataconversion.starr_conv import STARRUtil

TEST_SOURCE_TABLE = 'test_dataset.starr_order_med'
TEST_ORDERSET_TABLE = 'test_dataset.starr_med_orderset'

TEST_DEST_DATASET = 'test_dataset'


ORDERING_MODES = [
    'Inpatient',
    'Outpatient'
]

MED_ROUTES = [
    None,
    "Intramuscular",
    "Inhalation",
    "Topical",
    "Left Eye",
    "Right Eye",
    "Vaginal",
    "Injection",
    "Ophthalmic",
    "G Tube",
    "Transdermal",
    "Swish & Swallow",
    "RT Inhalation",
    "Intra-articular",
    "J Tube",
    "Buccal",
    "Rectal",
    "NG Tube",
    "Intrathecal",
    "Intravitreal",
    "Intradermal",
    "Otic",
    "Surgical Site Intra-Op Only",
    "Right Ear",
    "In Vitro",
    "Other",
    "Tendon Sheath Injection",
    "Intrauterine",
    "Intra-Catheter",
    "Mucous Membrane",
    "Not Applicable",
    "DELETE5",
    "Percutaneous",
    "Intrapleural",
    "Intranasal",
    "Intracavernosal",
    "Intralesional",
    "Implant",
    "Drain",
    "Apheresis",
    "Left Nostril",
    "Infiltration",
    "Intra-amniotic",
    "OG Tube",
    "Intraventricular",
    "Endotracheal",
    "Right Nostril",
    "Intra-arterial",
    "Intracardiac",
    "Nerve Block",
    "intravesical irrigation",
    "Hemodialysis",
    "Intraventricular CNS",
    "Thru Sheath",
    "Intrabursal",
    "Subtenons",
    "Juxtascleral",
    "Cervical",
    "Intratracheal",
    "intraocular injection",
    "Thru Peripheral IV",
    "Intrasynovial",
    "Periodontal",
    "interscalene",
    "Subconjunctival",
    "Continuous Epidural",
    "Continuous Nebulization",
    "Stoma",
    "Contin. Intrathecal Infusion",
    "Transtracheal",
    "Subcutaneous via CO2 Activated Syringe",
    "Intra-urethral",
    "Oral",
    "Misc.(Non-Drug; Combo Route)",
    "Intravenous",
    "Subcutaneous",
    "Both Eyes",
    "Intraperitoneal",
    "Sublingual",
    "Feeding Tube",
    "Nasal",
    "Swish & Spit",
    "CRRT",
    "Nebulization",
    "Translingual",
    "Intravesical",
    "Both Nostrils",
    "Left Ear",
    "Irrigation",
    "Both Ears",
    "PEG-J Tube",
    "Bladder Instillation",
    "Urethral",
    "Continuous IV Infusion",
    "Intravenous/Intramuscular",
    "Dental",
    "Topical ocular use",
    "Intraocular",
    "Subdermal",
    "Submucosal Injection",
    "Epidural",
    "Base of the eyelashes",
    "scalp",
    "Feeding Tube (FTub)",
    "Mouth/Throat",
    "Intracavity",
    "local intranasal application",
    "O2 Aerosolization",
    "DELETE19",
    "Contin. Subcutaneous Infusion",
    "Gums",
    "Extracorporeal",
    "Intraconjunctival",
    "adductor canal block",
    "Wound irrigation",
    "Neonatal Feeding",
    "Intra-lesional",
    "intravenous push",
    "Local Infiltration",
    "Perfusion",
    "DELETE20",
    "Intraosseous",
    "Intraspinal",
    "urinary catheter irrigation",
    "intratympanic",
    "Hand Bulb Nebulizer",
    "IPPB",
    "Ostomy",
    "Combination",
    "abdominal subcutaneous",
    "Subgingival-Local",
    "Intrathoracic",
    "intraocular irrigation",
    "INTRAVARICEAL",
    "Intracoronary",
    "subcutaneous (via wearable injector)",
    "central line irrigation",
    "Intrapericardial",
    "Submucosal Inj",
    "Laryngotracheal",
    "Retrobulbar",
    "Tendon Sheath Inj",
    "Osteochondrial",
    "Intradetrusor",
    "Intraductal",
    "Cont Nebulization",
    "hemodialysis port injection"
]

MED_DESCRIPTIONS = [
    "ONDANSETRON HCL (PF) 4 MG/2 ML INJ SOLN",
    "FENTANYL (PF) 50 MCG/ML INJECTION",
    "SODIUM CHLORIDE 0.9 % 0.9 % IV SOLP",
    "MIDAZOLAM 1 MG/ML INJ SOLN",
    "ACETAMINOPHEN 325 MG PO TABS",
    "NS IV BOLUS",
    "TPN ADULT STANDARD",
    "HEPARIN, PORCINE (PF) 100 UNIT/ML IV SYRG",
    "DIPHENHYDRAMINE HCL 50 MG/ML INJ SOLN",
    "OXYCODONE 5 MG PO TABS",
    "NALOXONE 0.4 MG/ML INJ SOLN",
    "PROPOFOL 10 MG/ML IV INJECTION",
    "LACTATED RINGERS IV SOLP",
    "LORAZEPAM 2 MG/ML INJ SOLN",
    "DIPHENHYDRAMINE HCL 25 MG PO CAPS",
    "HYDROCODONE-ACETAMINOPHEN 5-325 MG PO TABS",
    "LORAZEPAM 0.5 MG PO TABS",
    "TRIPLE MIX",
    "HYDROCODONE-ACETAMINOPHEN 5-500 MG PO TABS",
    "HYDROMORPHONE (PF) 2 MG/ML INJ SOLN",
    "LIDOCAINE (PF) 10 MG/ML (1 %) INJ SOLN",
    "PROMETHAZINE 25 MG/ML INJ SOLN",
    "DEXAMETHASONE SODIUM PHOSPHATE 4 MG/ML INJ SOLN",
    "FUROSEMIDE 10 MG/ML INJ SOLN",
    "LORAZEPAM 1 MG PO TABS",
    "FENTANYL CITRATE (PF) 50 MCG/ML INJ SOLN",
    "DOCUSATE SODIUM 100 MG PO CAPS",
    "PANTOPRAZOLE 40 MG PO TBEC",
    "POLYETHYLENE GLYCOL 3350 17 GRAM PO PWPK",
    "ACETAMINOPHEN 500 MG PO TABS",
    "ONDANSETRON HCL 8 MG PO TABS",
    "ASPIRIN 81 MG PO TBEC",
    "TPN BMT",
    "DOCUSATE SODIUM 250 MG PO CAPS",
    "SENNOSIDES 8.6 MG PO TABS",
    "GABAPENTIN 300 MG PO CAPS",
    "HYDROMORPHONE 1 MG/ML INJ SYRG",
    "ALTEPLASE 2 MG INTRA-CATHET SOLR",
    "OXYCODONE-ACETAMINOPHEN 5-325 MG PO TABS",
    "MAGNESIUM OXIDE-MG AA CHELATE 133 MG PO TABS",
    "CEFAZOLIN 1 GRAM INJ SOLR",
    "DEXAMETHASONE 4 MG PO TABS",
    "BISACODYL 10 MG PR SUPP",
    "METOCLOPRAMIDE HCL 5 MG/ML INJ SOLN",
    "ONDANSETRON 4 MG PO TBDL",
    "AMLODIPINE 5 MG PO TABS",
    "ZOLPIDEM 5 MG PO TABS",
    "ACETAMINOPHEN 1,000 MG/100 ML (10 MG/ML) IV SOLN",
    "LOPERAMIDE 2 MG PO CAPS",
    "CEFAZOLIN IN DEXTROSE (ISO-OS) 1 GRAM/50 ML IV PGBK",
    "METHYLPREDNISOLONE SOD SUC(PF) 125 MG/2 ML INJ SOLR",
    "LIDOCAINE HCL 10 MG/ML (1 %) INJ SOLN",
    "POTASSIUM CHLORIDE 20 MEQ PO TBTQ",
    "SODIUM CHLORIDE 0.9 % IV SOLP",
    "DEXTROSE 50 % IN WATER (D50W) IV SYRG",
    "FLUTICASONE 50 MCG/ACTUATION NASAL SPSN",
    "EPINEPHRINE 1 MG/ML (1 ML) INJ SOLN",
    "ALBUTEROL SULFATE 90 MCG/ACTUATION INH HFAA",
    "LIDOCAINE (PF) 20 MG/ML (2 %) INJ SOLN",
    "MAGNESIUM SULFATE IN 0.9 %NACL 2 GRAM/50 ML IV PGBK",
    "HYDROCORTISONE SOD SUCC (PF) 100 MG/2 ML INJ SOLR",
    "HYDROCHLOROTHIAZIDE 25 MG PO TABS",
    "ROCURONIUM 10 MG/ML IV SOLN",
    "HYDROCODONE-ACETAMINOPHEN 10-325 MG PO TABS",
    "TRAMADOL 50 MG PO TABS",
    "ALUM-MAG HYDROXIDE-SIMETH 200-200-20 MG/5 ML PO SUSP",
    "PHENYLEPHRINE HCL 10 MG/ML INJ SOLN",
    "METOPROLOL TARTRATE 25 MG PO TABS",
    "OMEPRAZOLE 20 MG PO CPDR",
    "FAMOTIDINE 20 MG PO TABS",
    "HEPARIN, PORCINE (PF) 5,000 UNIT/0.5 ML INJ SOLN",
    "ACETAMINOPHEN 650 MG/20.3 ML PO SOLN",
    "HYDROMORPHONE 2 MG/ML INJ SYRG",
    "LABETALOL 5 MG/ML IV SOLN",
    "VANCOMYCIN IVPB (CUSTOM DOSE)",
    "METOCLOPRAMIDE 5 MG/ML INJ SOLN",
    "ATORVASTATIN 40 MG PO TABS",
    "HEPARIN (PORCINE) 1,000 UNIT/ML INJ SOLN",
    "FUROSEMIDE 20 MG PO TABS",
    "TPN ADULT CYCLIC",
    "INSULIN LISPRO 100 UNIT/ML SC SOLN",
    "MAGNESIUM SULFATE IV SCALE ",
    "MAGNESIUM SULFATE IN 0.9 %NACL 1 GRAM/50 ML IV PGBK",
    "ALBUMIN, HUMAN 5 % 5 % IV SOLP",
    "NITRIC OXIDE GAS 800 PPM INH GAS",
    "LISINOPRIL 10 MG PO TABS",
    "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN",
    "ENOXAPARIN 40 MG/0.4 ML SC SYRG",
    "GLYCOPYRROLATE 0.2 MG/ML INJ SOLN",
    "HYDRALAZINE 20 MG/ML INJ SOLN",
    "MEPERIDINE (PF) 25 MG/ML INJ SYRG",
    "HYDROMORPHONE 1 MG/ML IV PCA",
    "POTASSIUM CHLORIDE IV SCALE",
    "IBUPROFEN 600 MG PO TABS",
    "CEPHALEXIN 500 MG PO CAPS",
    "ATORVASTATIN 10 MG PO TABS",
    "MAGNESIUM HYDROXIDE 400 MG/5 ML PO SUSP",
    "ATORVASTATIN 20 MG PO TABS",
    "TRAZODONE 50 MG PO TABS",
    "EPHEDRINE SULFATE 50 MG/ML INJ SOLN",
    "METFORMIN 500 MG PO TABS",
    "PREDNISONE 20 MG PO TABS",
    "SIMVASTATIN 20 MG PO TABS",
    "ASPIRIN 81 MG PO CHEW",
    "DIAZEPAM 5 MG PO TABS",
    "PANTOPRAZOLE 40 MG IV SOLR",
    "GLUCOSE 4 GRAM PO CHEW",
    "ZOLPIDEM 10 MG PO TABS",
    "POTASSIUM CHLORIDE ORAL SCALE",
    "TAMSULOSIN 0.4 MG PO CP24",
    "PREDNISONE 10 MG PO TABS",
    "INSULIN REGULAR HUMAN 100 UNIT/ML INJ SOLN",
    "FAMOTIDINE (PF) 20 MG/2 ML IV SOLN",
    "AMLODIPINE 10 MG PO TABS",
    "IPRATROPIUM-ALBUTEROL 0.5 MG-3 MG(2.5 MG BASE)/3 ML INH NEBU",
    "REMIFENTANIL 2 MG IV SOLR",
    "PROCHLORPERAZINE MALEATE 10 MG PO TABS",
    "ASPIRIN 325 MG PO TABS",
    "POTASSIUM CHLORIDE 10 MEQ PO TBTQ",
    "LISINOPRIL 20 MG PO TABS",
    "MORPHINE 2 MG/ML INJ SYRG",
    "POTASSIUM CHLORIDE ORAL TABLET REPLACEMENT SCALE",
    "DEXTROSE 5 % IN WATER (D5W) IV SOLP",
    "CEFAZOLIN IN DEXTROSE (ISO-OS) 2 GRAM/100 ML IV PGBK",
    "SULFAMETHOXAZOLE-TRIMETHOPRIM 800-160 MG PO TABS",
    "POTASSIUM CHLORIDE IV REPLACEMENT SCALE",
    "AMOXICILLIN-POT CLAVULANATE 875-125 MG PO TABS",
    "METOPROLOL SUCCINATE 25 MG PO TB24",
    "HEPARIN, PORCINE (PF) 1,000 UNIT/ML INJ SOLN",
    "MORPHINE 4 MG/ML INJ SYRG",
    "CLOPIDOGREL 75 MG PO TABS",
    "GABAPENTIN 100 MG PO CAPS",
    "FUROSEMIDE 40 MG PO TABS",
    "TACROLIMUS 1 MG PO CAPS",
    "LOSARTAN 50 MG PO TABS",
    "GLYCERIN-DIMETHICONE-PETRO, WH TP CREA",
    "OTHER DRUG",
    "AZITHROMYCIN 250 MG PO TABS",
    "SODIUM BICARBONATE 8.4 % IV SOLN",
    "POTASSIUM CHLORIDE 10 MEQ/100 ML IV PGBK",
    "PREDNISONE 5 MG PO TABS",
    "FAT EMULSION 20 % IV EMUL",
    "HYDROMORPHONE (PF) 1 MG/ML INJ SYRG",
    "LIDOCAINE 4 % TP CREA",
    "CEFAZOLIN 2 G IVPB",
    "ONDANSETRON (+DEXAMETHASONE) IVPB",
    "LEVOTHYROXINE 50 MCG PO TABS",
    "FERROUS SULFATE 325 MG (65 MG IRON) PO TABS",
    "CALCIUM GLUCONATE IN 0.9% NACL 1 GRAM/50 ML IV SOLN",
    "LIDOCAINE-EPINEPHRINE 1 %-1:100,000 INJ SOLN",
    "CIPROFLOXACIN HCL 500 MG PO TABS",
    "ALBUTEROL SULFATE 2.5 MG /3 ML (0.083 %) INH NEBU",
    "KETOROLAC 30 MG/ML (1 ML) INJ SOLN",
    "LISINOPRIL 5 MG PO TABS",
    "ONDANSETRON HCL 4 MG PO TABS",
    "NITROGLYCERIN 0.4 MG SL SUBL",
    "DIPHTH,PERTUS(ACELL),TETANUS 2.5-8-5 LF-MCG-LF/0.5ML IM SUSP (UHA)",
    "METOPROLOL SUCCINATE 50 MG PO TB24",
    "CIPROFLOXACIN 500 MG PO TABS",
    "PACLITAXEL IV CHEMO INFUSION",
    "SODIUM CHLORIDE 0.9 % IRRIG SOLN",
    "VITAMIN D3 PO",
    "1/2 NS WITH KCL AND MAGNESIUM SULFATE (+MANNITOL) IV INFUSION",
    "SPIRONOLACTONE 25 MG PO TABS",
    "PROAIR HFA 90 MCG/ACTUATION INH HFAA",
    "FOLIC ACID 1 MG PO TABS",
    "SUCCINYLCHOLINE CHLORIDE 20 MG/ML INJ SOLN",
    "POTASSIUM PHOSPHATE IVPB",
    "FILGRASTIM 300 MCG/0.5 ML INJ SYRG",
    "ATENOLOL 25 MG PO TABS",
    "POTASSIUM CHLORID-D5-0.45%NACL 20 MEQ/L IV SOLP",
    "GEMCITABINE IV CHEMO INFUSION",
    "MELATONIN 3 MG PO TABS",
    "BUPIVACAINE (PF) 0.25 % (2.5 MG/ML) INJ SOLN",
    "METFORMIN 1,000 MG PO TABS",
    "CARBOPLATIN (AUC DOSING) IV CHEMO INFUSION",
    "LEVOTHYROXINE 75 MCG PO TABS",
    "FLUMAZENIL 0.1 MG/ML IV SOLN",
    "LEVOTHYROXINE 100 MCG PO TABS",
    "MONTELUKAST 10 MG PO TABS",
    "ACYCLOVIR 400 MG PO TABS",
    "LIDOCAINE HCL 2 % VISCOUS ORAL SOLN",
    "VANCOMYCIN IN D5W 1 GRAM/200 ML IV PGBK",
    "AMIODARONE 200 MG PO TABS",
    "DEXTROSE 50% IN WATER (D50W) IV SYRG",
    "SUCRALFATE 1 GRAM PO TABS",
    "CYCLOBENZAPRINE 10 MG PO TABS",
    "CLONAZEPAM 0.5 MG PO TABS",
    "SIMVASTATIN 40 MG PO TABS",
    "METOPROLOL TARTRATE 50 MG PO TABS",
    "LACTATED RINGERS IV BOLUS",
    "LIDOCAINE HCL 20 MG/ML (2 %) INJ SOLN",
    "IBUPROFEN 800 MG PO TABS",
    "MORPHINE INJECTABLE SYRINGE",
    "PPN ADULT STANDARD",
    "PIPERACILLIN-TAZOBACTAM-DEXTRS 3.375 GRAM/50 ML IV PGBK",
    "WARFARIN 5 MG PO TABS",
    "CHLORHEXIDINE GLUCONATE 0.12 % MM MWSH",
    "LOSARTAN 25 MG PO TABS",
    "NS IV BOLUS - 1000 ML"
]

PROTOCOL_NAME = [
    " AMB URO URODYNAMICS",
    "(RETIRED PLEASE USE ORDERSET (SURGERY GENERAL POSTOP 801) IP SUR CHOLECYSTECTOMY",
    "(RETIRED) IP PICC LINE PLACEMENT / EXCHANGE",
    "AMB ALG XOLAIR MMC",
    "AMB AWCC WOUND CARE",
    "AMB CAR ATRIAL FIBRILLATION",
    "AMB CAR CONGESTIVE HEART FAILURE",
    "AMB CAR IC NEW",
    "AMB DERM ACNE",
    "AMB DERM DERMATITIS MMC",
    "AMB DERM EXCISION MMC",
    "AMB DERM PSORIASIS ",
    "AMB DERM SKIN BIOPSY",
    "AMB DERM SURG PRE-OPERATIVE CHECK SHEET",
    "AMB DERM SURG PROCEDURES",
    "AMB DIGESTIVE HEALTH INFLAMMATORY BOWEL DISEASE",
    "AMB DIGESTIVE HEALTH STOMACH",
    "AMB END DIABETES TYPE 1",
    "AMB END DIABETES TYPE 2",
    "AMB END THYROGEN STUDIES",
    "AMB ENDO DIABETES TYPE 1 MMC",
    "AMB ENDO DIABETES TYPE 2 MMC",
    "AMB ENDO THYROGEN STUDIES MMC",
    "AMB FLU CLINIC",
    "AMB GI ABDOMINAL PAIN",
    "AMB GI DIARRHEA MMC",
    "AMB GI PRE-OPERATIVE EVALUATION",
    "AMB GYN AMENORRHEA ",
    "AMB GYN ANNUAL WELL WOMAN EXAM",
    "AMB GYN COLPOSCOPY MMC",
    "AMB GYN MEDICAL AB VISIT #1",
    "AMB GYN ROUTINE ADOLESCENT EXAM",
    "AMB GYN VAGINITIS",
    "AMB HC CAR HYPERTENSION CENTER",
    "AMB HEART TRANSPLANT ANNUAL STANFORD RN ORDERS",
    "AMB HEART TRANSPLANT OUTPATIENT CLINIC EVALUATION STANFORD",
    "AMB HEART TRANSPLANT ROUTINE STANFORD RN ORDERS",
    "AMB HEP C TREATMENT PROTOCOL LAB ORDERS",
    "AMB HEP CHRONIC HEPATITIS C",
    "AMB HEP HEPATITIS B",
    "AMB HM SHC SUPER SMARTSET",
    "AMB HM UHA SUPER SMARTSET",
    "AMB IFD SKIN AND SOFT TISSUE INFECTION",
    "AMB IM ANNUAL FEMAL EXAM MMC",
    "AMB IM ANNUAL MALE EXAM MMC",
    "AMB IM COUGH/BRONCHITIS MMC",
    "AMB IM UPPER RESPIRATORY INFECTION MMC",
    "AMB IMM 19-49 YRS IMMUNIZATIONS",
    "AMB IMM 50-64 YRS IMMUNIZATIONS",
    "AMB IMM >=65 YRS IMMUNIZATIONS",
    "AMB IMM ADULT",
    "AMB IMM PEDS 11-12 YRS IMMUNIZATIONS",
    "AMB IMM PEDS 12 MO IMMUNIZATIONS",
    "AMB IMM PEDS 13-14, 16-18 YRS IMMUNIZATIONS (OVERDUE)",
    "AMB IMM PEDS 15 MO IMMUNIZATIONS",
    "AMB IMM PEDS 15 YRS IMMUNIZATIONS",
    "AMB IMM PEDS 18-23 MO IMMUNIZATIONS",
    "AMB IMM PEDS 2 MO IMMUNIZATIONS",
    "AMB IMM PEDS 2-3 YRS IMMUNIZATIONS",
    "AMB IMM PEDS 4 MONTH IMMUNIZATIONS",
    "AMB IMM PEDS 4-6 YRS IMMUNIZATIONS",
    "AMB IMM PEDS 6 MO IMMUNIZATIONS",
    "AMB IMM PEDS 7-10 YRS IMMUNIZATIONS",
    "AMB IMM PEDS BIRTH TO 1 MO IMMUNIZATIONS",
    "AMB IMM TRAVEL IMMUNIZATIONS",
    "AMB LAB TRANSFUSION SERVICE, STANDARD",
    "AMB LIV PRE-OP ORDERS",
    "AMB NEU CONCUSSION FOLLOW UP VISIT",
    "AMB NEU LUMBAR PUNCTURE",
    "AMB NEU MOVE PARKINSON'S",
    "AMB NEU MULTIPLE SCLEROSIS",
    "AMB NEU STROKE GENERAL",
    "AMB NEUROSCIENCE BOTOX SMARTSET",
    "AMB OAC ENCOUNTER",
    "AMB OPH CATARACT POST OP",
    "AMB OPH CLINIC GLAUCOMA LASER PROCEDURES",
    "AMB OPH CLINIC LASER PROCEDURES",
    "AMB OPH CORNEA ULCER",
    "AMB OPH INJECTIONS",
    "AMB OPH INTRAVITREAL AVASTIN INJECTION BOTH EYES",
    "AMB OPH INTRAVITREAL AVASTIN INJECTION LEFT EYE",
    "AMB OPH INTRAVITREAL AVASTIN INJECTION RIGHT EYE",
    "AMB OPH INTRAVITREAL AVASTIN/LUCENTIS INJECTION ",
    "AMB OPH INTRAVITREAL INJ LEFT EYE",
    "AMB OPH INTRAVITREAL INJ RIGHT EYE",
    "AMB OPH INTRAVITREAL INJ VISIT",
    "AMB OPH INTRAVITREAL LUCENTIS INJECTION BOTH EYES",
    "AMB OPH INTRAVITREAL LUCENTIS INJECTION LEFT EYE",
    "AMB OPH INTRAVITREAL LUCENTIS INJECTION RIGHT EYE",
    "AMB OPH INTRAVITREAL LUCENTIS/AVASTIN INJECTION",
    "AMB OPH INTRAVITREAL TRIESENCE INJECTION LEFT EYE",
    "AMB OPH INTRAVITREAL TRIESENCE INJECTION RIGHT EYE",
    "AMB OPH NEURO GENERAL",
    "AMB OPH POST OP RET LT EYE",
    "AMB OPH PRE OP VISIT",
    "AMB OPH PREOP CORNEA TRANSPLANT",
    "AMB OPH RET INJ",
    "AMB OPH RET POSTOP",
    "AMB OPH RETINA MASTER",
    "AMB OPHTH LASER",
    "AMB OPHTH LASER LASIK",
    "AMB OPHTH LASER LASIK ENHANCED",
    "AMB OPHTH LASER PRK",
    "AMB ORDER TRANSMITTAL PRINTING",
    "AMB ORT ARTHROCENTESIS MMC",
    "AMB ORT FOOT AND ANKLE INJECTION",
    "AMB ORT FOOT_ANKLE",
    "AMB ORT HAND ARTHRITIS",
    "AMB ORT HAND INJECTION",
    "AMB ORT HAND SOFT TISSUE",
    "AMB ORT HAND TRAUMA",
    "AMB ORT HAND_WRIST",
    "AMB ORT HUNT FOOT_ANKLE",
    "AMB ORT INJECTIONS HAND",
    "AMB ORT INJECTIONS JOINT",
    "AMB ORT INJECTIONS SPINE",
    "AMB ORT INJECTIONS SPORTS MED",
    "AMB ORT INJECTIONS TUMOR",
    "AMB ORT JOINT HIP",
    "AMB ORT JOINT HIP_GOODMAN",
    "AMB ORT JOINT INJECTION",
    "AMB ORT JOINT KNEE",
    "AMB ORT JOINT KNEE_GOODMAN",
    "AMB ORT PMR",
    "AMB ORT SHOULDER_ELBOW",
    "AMB ORT SPINE",
    "AMB ORT SPINE INJECTION",
    "AMB ORT SPINE PMR",
    "AMB ORT SPORTS INJECTION",
    "AMB ORT SPORTS MEDICINE_FANTON",
    "AMB ORT SPORTS MEDICINE_SAFRAN",
    "AMB ORT SPORTS_ELBOW",
    "AMB ORT SPORTS_FRACTURES",
    "AMB ORT SPORTS_HAND/WRIST",
    "AMB ORT SPORTS_HIP/THIGH",
    "AMB ORT SPORTS_KNEE",
    "AMB ORT SPORTS_LEG/ANKLE/FOOT",
    "AMB ORT SPORTS_SHOULDER",
    "AMB ORT SPORTS_SPINE",
    "AMB ORT TRAUMA _KNEE",
    "AMB ORT TRAUMA_HIP",
    "AMB ORT TRAUMA_INFECTION",
    "AMB ORT TRAUMA_PELVIS FX",
    "AMB ORT TUMOR BIOPSY/INJECTION",
    "AMB ORT TUMOR_SOFT TISSUE",
    "AMB PAIN BURSA INJECTION",
    "AMB PAIN INTRATHECAL PUMP REFILL / ADJUSTMENT",
    "AMB PAIN KETAMINE INFUSION",
    "AMB PAIN LIDOCAINE INFUSION",
    "AMB PAIN MANAGEMENT CHEMODENERVATION WITH BOTOX FOR EXTREMITIES/TRUNK",
    "AMB PAIN MANAGEMENT CHEMODENERVATION WITH BOTOX FOR HEAD/FACE",
    "AMB PAIN MANAGEMENT CHEMODENERVATION WITH BOTOX FOR NECK",
    "AMB PAIN MANAGEMENT INIITAL/OFFICE VISIT",
    "AMB PAIN MANAGEMENT PROCEDURE VISIT",
    "AMB PAIN OCCIPITAL NERVE BLOCK",
    "AMB PAIN PERIPHERAL NERVE BLOCK INJECTION",
    "AMB PAIN PREEMPT INJECTION FOR CHRONIC MIGRAINE",
    "AMB PAIN SCAR INJECTION WITH ALCOHOL",
    "AMB PAIN SCAR INJECTION WITH BOTOX",
    "AMB PAIN SCAR INJECTION WITH LOCAL ANESTHETIC",
    "AMB PAIN SCAR INJECTION WITH STEROID",
    "AMB PAIN TRIGGERPOINT INJECTION WITH BOTOX",
    "AMB PAIN TRIGGERPOINT INJECTION WITHOUT BOTOX",
    "AMB PC GEN ABDOMINAL PAIN",
    "AMB PC GEN ALLERGIC RHINITIS",
    "AMB PC GEN ANKLE SPRAIN",
    "AMB PC GEN ANNUAL FEMALE EXAM",
    "AMB PC GEN ANNUAL MALE EXAM",
    "AMB PC GEN ANXIETY",
    "AMB PC GEN ASTHMA (ADULT)",
    "AMB PC GEN BACK PAIN",
    "AMB PC GEN CERUMEN IMPACTION",
    "AMB PC GEN CHEST PAIN",
    "AMB PC GEN CHRONIC OBSTRUCTIVE PULMONARY  DISEASE (COPD)",
    "AMB PC GEN CONGESTIVE HEART FAILURE",
    "AMB PC GEN CONJUNCTIVITIS",
    "AMB PC GEN CONSTIPATION",
    "AMB PC GEN CONTRACEPTIVE VISIT",
    "AMB PC GEN COUGH / BRONCHITIS",
    "AMB PC GEN DEPRESSION",
    "AMB PC GEN DIABETES MELLITUS TYPE 2",
    "AMB PC GEN DIVERTICULITIS",
    "AMB PC GEN DIZZINESSS",
    "AMB PC GEN ELBOW PAIN",
    "AMB PC GEN ESOPHAGEAL REFLUX",
    "AMB PC GEN FOREIGN BODY",
    "AMB PC GEN GASTROENTERITIS",
    "AMB PC GEN HEADACHE",
    "AMB PC GEN HEMORRHOID",
    "AMB PC GEN HIP PAIN",
    "AMB PC GEN HYPERLIPIDEMIA",
    "AMB PC GEN HYPERTENSION",
    "AMB PC GEN HYPOTHYROIDISM",
    "AMB PC GEN KNEE PAIN",
    "AMB PC GEN NAUSEA/VOMITING",
    "AMB PC GEN NECK PAIN",
    "AMB PC GEN OTITIS EXTERNA",
    "AMB PC GEN OTITIS MEDIA",
    "AMB PC GEN PALPITATIONS",
    "AMB PC GEN PERIPHERAL VASCULAR DISEASE"
]

SS_SECTION_NAME = [
    None,
    " ",
    "  ",
    "2A. High Risk of Delirium: Management",
    "2A. High risk of delirium: Management",
    "2A. Hyperactive delirium: Management",
    "2B. Hyperactive Delirium: Management",
    "2B. Hyperactive delirium: Management",
    "2B. Hypoactive delirium: Management ",
    "2C. Hypoactive delirium: Management ",
    "ADULT MEDICATIONS",
    "ANALGESICS",
    "ANTI-EMETICS",
    "ANTIBIOTICS",
    "ANTICOAGULANTS",
    "APPLY TO WOUND",
    "Acute Ischemic Stroke",
    "Ad-hoc Orders",
    "Additional Medications",
    "Adjunction/Alternative Headache Treatments",
    "Adult Medications",
    "Adult Protocol",
    "After Visit Medications",
    "Allergy Testing",
    "Ambulatory Orders",
    "Analgesics",
    "Anti- Emetics",
    "Anti-rejection Medications",
    "Antibiotics",
    "Antibiotics - Community Acquired (Severe Sepsis)",
    "Antibiotics - Community Acquired (Severe Sepsis) ",
    "Antibiotics - Community Acquired (Severe sepsis)",
    "Antibiotics - Community Acquired (Simple Sepsis)",
    "Antibiotics - Healthcare Associated or Immunocompromised Sepsis ",
    "Antibiotics - Healthcare Associated or Immunocompromised Sepsis (Simple/Severe)",
    "Anticoagulants",
    "Antipsychotics ",
    "Anxiety/Agitation",
    "Approved Albumin Indications",
    "Argatroban - Left Ventricular Assist Device (LVAD) protocol",
    "Argatroban - Specific Infusion Parameters per MD",
    "Argatroban - Standard Protocol",
    "Ascites",
    "Aspirin",
    "BASAL/PRANDIAL/CORRECTIVE SCALES FOR CONTINUOUS FEEDS/NPO",
    "BASAL/PRANDIAL/CORRECTIVE SCALES FOR ORAL DIET/BOLUS FEEDS",
    "BASAL/PRANDIAL/CORRECTIVE Scales For Continuous FEEDS/NPO",
    "BASAL/PRANDIAL/CORRECTIVE Scales For Oral DIET/BOLUS Feeds",
    "BLOOD TRANSFUSION",
    "BOLUS",
    "Basal/Prandial/Corrective Scales For Continuous Feeds/NPO",
    "Basal/Prandial/Corrective Scales For Oral Diet/Bolus Feeds",
    "Basal/Prandial/Corrective Scales for Continuous Feeds/NPO",
    "Basal/Prandial/Corrective Scales for Continuous Feeds/NPO/TPN",
    "Basal/Prandial/Corrective Scales for Oral Diet/Bolus Feeds",
    "Blood Transfusion",
    "Bolus",
    "Bowel Regimen",
    "CONTINUOUS INTRAVENOUS INSULIN INFUSION",
    "CSF Leak Orders",
    "Calcium ",
    "Catch-up Orders",
    "Clinic-Administered Medications",
    "Cluster Headache",
    "Community Acquired Pneumonia",
    "Continuous Intravenous Insulin Infusion",
    "Contrast",
    "DEXAMETHASONE",
    "DIABETIC SUPPLIES",
    "DISCHARGE INSTRUCTIONS",
    "DISCHARGE ORDERS",
    "DISCONTINUE PREVIOUS INSULIN/ORAL ANTIDIABETIC ORDERS",
    "DVT PROPHYLAXIS",
    "Day of Surgery Orders",
    "Delirium",
    "Dexamethasone",
    "Dialysis Medications",
    "Dialysis Solutions",
    "Diptheria tetanus toxoid pertussis vaccine",
    "Discharge",
    "Discharge Orders",
    "ECMO Circuit Respiratory Parameters",
    "ELECTROLYTE REPLACEMENT",
    "EMERGENCY RELEASE BLOOD PRODUCTS",
    "Electrolyte Replacement",
    "Emergency Medications",
    "Encephalopathy",
    "Extremity Swelling/Deformity/or Open Fracture",
    "FLUID RESUSCITATION",
    "FULL INTENSITY HEPARIN PROTOCOL",
    "Fluid Resuscitation",
    "Fluids",
    "For Pharmacist Use ONLY",
    "Future Orders",
    "GI Bleeding",
    "General",
    "General Medications",
    "General Perioperative Orders",
    "HEMATOPOIETIC CELL INFUSION",
    "HEPARIN - ACUTE CORONARY SYNDROME",
    "HEPARIN - ATRIAL FIB",
    "HEPARIN - CARDIO ELECTROPHYSIOLOGY",
    "HEPARIN - DVT/PE",
    "HEPARIN - HIGH BLEEDING RISK",
    "HEPARIN - MECHANICAL HEART VALVE",
    "HEPARIN - NEURO",
    "HEPARIN - SPECIFIC BOLUS & INFUSION PARAMETERS PER MD ",
    "HEPARIN - VASCULAR SURGERY",
    "HYDROCORTISONE",
    "HYPOGLYCEMIA CONTROL",
    "HYPOGLYCEMIA CONTROL FOR INSULIN TRANSITION OFF IV INFUSION PROTOCOL",
    "HYPOGLYCEMIA CONTROL FOR SUBCUTANEOUS INSULIN PUMP PROTOCOL",
    "HYPOGLYCEMIA PROTOCOL FOR DKA",
    "HYPOGLYCEMIC PROTOCOL FOR IV INSULIN INFUSION",
    "Heparin - Acute Coronary Syndrome",
    "Heparin - Atrial FIB",
    "Heparin - Cardio Electrophysiology",
    "Heparin - DVT/PE",
    "Heparin - High Bleeding Risk",
    "Heparin - Left Ventricular Assist Device (LVAD)",
    "Heparin - Mechanical Heart Valve",
    "Heparin - Neuro",
    "Heparin - Specific Bolus & Infusion Parameters Per MD ",
    "Heparin - Vascular Surgery",
    "Heparin Infusion Protocols",
    "Hepatitis B vaccine. Administer40 mcg IM",
    "Hospital Acquired Or Ventilator Associated Pneumonia",
    "Hypoglycemia Control",
    "Hypoglycemia Control For Insulin Transition Off IV Infusion Protocol",
    "Hypoglycemia Control For Subcutaneous Insulin Pump Protocol",
    "Hypoglycemia Protocol For DKA",
    "Hypoglycemia Treatment",
    "Hypoglycemic Protocol For IV Insulin Infusion",
    "ICU Admission",
    "IMMUNIZATION",
    "IMMUNIZATIONS",
    "INFUSION",
    "INITIAL INTRAVENOUS FLUID AND KCL THERAPY",
    "INJECTION/MEDICATIONS",
    "INR = 1.2 to 1.5",
    "INR > Or = 1.6",
    "INR > or = 1.6",
    "INSULIN BASAL, PRANDIAL AND CORRECTIVE SCALES",
    "INSULIN BASAL, PRANDIAL AND CORRECTIVE SCALES (ORAL DIET/BOLUS FEEDS)",
    "INSULIN BASAL, PRANDIAL AND CORRECTIVE SCALES - CONTINUOUS FEEDS/NPO ",
    "INSULIN BASAL, PRANDIAL AND CORRECTIVE SUBCUTANEOUS  SCALES",
    "INSULIN BASAL, PRANDIAL AND CORRECTIVE SUBCUTANEOUS SCALES",
    "INSULIN BASAL, PRANDIAL AND CORRECTIVE SUBCUTANEOUS SCALES ",
    "INSULIN BASAL, PRANDIAL AND CORRRECTIVE SUBCUTANTEOUS SCALES",
    "INSULIN BASAL,PRANDIAL AND CORRECTIVE SUBCUTANEOUS SCALES",
    "INSULIN BASAL/PRANDIAL/CORRECTIVE SCALES FOR NPO PATIENT REMAINING NPO",
    "INSULIN BASAL/PRANDIAL/CORRECTIVE SCALES FOR NPO PATIENT TRANSITIONING TO ORAL DIET",
    "INSULIN BASAL/PRANDIAL/CORRECTIVE SCALES FOR PATIENT ON CONTINUOUS TUBE FEEDS BEFORE/AFTER TRANSITION OFF DRIP",
    "INSULIN BOLUS AND INFUSION",
    "INSULIN INFUSION AND BOLUS",
    "INSULIN INFUSION HYPOGLYCEMIC PROTOCOL",
    "INSULIN PUMP",
    "INTRA PROCEDURE",
    "INTRATHECAL CLONIDINE",
    "INTUBATION MEDICATIONS",
    "IP INSULIN CONTINUOUS IV INFUSION (For Cardiac Transplant)",
    "IP Insulin Continuous IV Infusion",
    "IP Insulin Continuous IV Infusion (For Cardiac Transplant)",
    "IV FLUID",
    "IV FLUIDS",
    "IV Fluid",
    "IV Fluids",
    "IV Fluids (age 65+)",
    "IV Fluids and Saline Lock",
    "IV SOLUTIONS",
    "IV Solutions",
    "IVIG Therapy",
    "If Patient to be Treated as an Inpatient",
    "If Patient to be Treated as an Outpatient",
    "Imaging",
    "Imm/Injections",
    "Immunization/Injection",
    "Immunizations",
    "Immunizations/Injections",
    "Influenza",
    "Influenza Treatment",
    "Influenza Vaccine 6-35 months",
    "Influenza Vaccine =>3 Years Old",
    "Initial INR 1.4 -1.6",
    "Initial INR 1.5 -1.6",
    "Initial INR 1.7 -1.9",
    "Initial INR > or = 2",
    "Initial IV Fluids",
    "Initial Intravenous Fluid And KCL Therapy",
    "Injectible Meds",
    "Injection/Medications",
    "Injections",
    "Injections/Medications",
    "Inpatient Admission",
    "Inpatient Pre-Op IV Fluids",
    "Inpatient Pre-Op Medications",
    "Inpatient Pre-Op VTE Prophylaxis",
    "Inpatient Pre-op Orders",
    "Insulin",
    "Insulin BASAL/PRANDIAL/CORRECTIVE Scales For NPO Patient REMAINING NPO"
]

SS_SG_NAME = [
    None,
    " ",
    " PCP Prophylaxis auto",
    " PONV TREATMENT ON THE FLOOR:  Please see PONV guidelines and if criteria are met, give one 5HT-3 Q12 Hr (max 48hr) and metoclopramide:",
    " PONV Treatment on the Floor:",
    " PONV Treatment on the Floor:  Please see PONV guidelines and if criteria are met, give one 5HT-3 Q12 Hr (max 48hr) and metoclopramide:",
    " Phosphate-Lowering Agents",
    " Regular Insulin Traditional Scales- Continuous Feeds/NPO (Non-ICU)",
    "(Adult) Blood Product and Transfuse Orders (weight greater than 50 kg)",
    "(Adult) Emergency Release Blood Products (weight greater than 50 kg)",
    "(Aliquot) Blood Product and Transfuse Orders (weight less than 50 kg)",
    "19-49 YRS IMMUNIZATIONS",
    "50-64 YRS IMMUNIZATIONS",
    ">=65 YRS IMMUNIZATIONS",
    "ABORTIFACIENT",
    "AC Chemotherapy",
    "ACE INHIBITORS",
    "ACE Inhibitor (ACEI)",
    "ACE Inhibitors",
    "ACEI or ARB or ARNI ",
    "ACEI: (Publicly reported indicator)",
    "ADULT IMMUNIZATIONS",
    "ADULT IMMUNIZATIONS FOR UHA DEPARTMENTS",
    "ADULT SERIES IMMUNIZATIONS",
    "ADULT SERIES IMMUNIZATIONS ",
    "ADULT SERIES IMMUNIZATIONS UHA",
    "ALL pre-op antibiotics will be administered by Anesthesiologists",
    "AMB IMM/INJ PED ORDERS ",
    "AMB IMM/INJ PED QUICK VISIT ",
    "AMB IMM/INJ PED WCC 15/18 MONTHS ",
    "AMB IMM/INJ PED WCC 4/5/6 YEARS",
    "AMB IMM/INJ PED WCC 4/5/6 YEARS ",
    "AMB IMM/INJ PED WCC 4/5/6 YEARS UHA",
    "AMB MED OPHTH LASER LASIK",
    "AMB MED OPHTH LASER PRK",
    "AMB MED OPHTH POST PROCEDURE",
    "AMB MED OPHTH PRE PROCEDURE",
    "AMB MED ORT SPORTS MEDICINE",
    "AMB MED PEDS VITAMINS DROPS 2WEEKS/1MONTH MMC",
    "AMB MED PEDS VITAMINS MMC",
    "AMB MED PEDS Vitamins Drops",
    "AMB MED REI VERBAL INTRA PROCEDURE MEDS",
    "AMB MED SLEEP STUDY",
    "AMB OPH ORDERS RET INJ",
    "AMB OPH RX RET POSTOP",
    "AMB PRO PED WCC 3 YEARS",
    "AMB PRO PED WCC 3-11 YEARS",
    "AMB PRO PED WCC 3/4/5/6 YEARS ",
    "AMB PRO REI INTRA-PROCEDURE MEDS",
    "AMB PRO REI PRE-PROCEDURE NURSING/MEDS",
    "AMB SNHC ALLERGY CLINIC ASPIRIN",
    "AMB SNHC ALLERGY CLINIC PREMEDS",
    "AMB SNHC ALLERGY CLINIC PRN MEDS",
    "ANALGESIC URINARY",
    "ANGIOTENSIN 2 RECEPTOR BLOCKERS",
    "ANTIACNE",
    "ANTIBIOTIC CEPHALOSPORINS",
    "ANTIBIOTIC MACROLIDES",
    "ANTIBIOTIC MACROLIDES MMC",
    "ANTIBIOTIC OTIC AGENTS",
    "ANTIBIOTIC PENICILLINS",
    "ANTIBIOTIC QUINOLONES",
    "ANTIBIOTIC QUINOLONES ",
    "ANTIBIOTIC, CEPHALOSPORIN",
    "ANTIBIOTIC, CEPHALOSPORINS",
    "ANTIBIOTIC, PENICILLIN",
    "ANTIBIOTICS MISC",
    "ANTIBIOTICS OCULAR",
    "ANTICATAPLETIC",
    "ANTIDEPRESSANTS (NON SSRI'S)",
    "ANTIDEPRESSANTS (SSRI'S)",
    "ANTIDIARRHEALS",
    "ANTIDIZZINESS MEDS",
    "ANTIEMETIC",
    "ANTIFUNGALS",
    "ANTIHISTAMINES",
    "ANTIHISTAMINES ALLERGY",
    "ANTIHISTAMINICS",
    "ANTILIPEMIC",
    "ANTIPRURITICS",
    "ANTIRETROVIRAL",
    "ANTITUSSIVES",
    "ANTITUSSIVES ",
    "ANTITUSSIVES MMC",
    "ANXIOLYTIC",
    "ANXIOLYTICS",
    "ARB: (Publicly reported indicator if ACEI contraindicated)",
    "ASPIRIN",
    "ATG",
    "AVASTIN",
    "Abatacept Infusion",
    "Abdominal",
    "Abdominal Cramp Medications",
    "Acetaminophen",
    "Acetylcysteine",
    "Acute Complicated UTI/Pyelonephritis",
    "Acute MI",
    "Acute Uncomplicated UTI",
    "Additional Diabetic Supplies",
    "Additional Medications",
    "Additional Meds",
    "Additional Post-Op Analgesics",
    "Additional treatments for Refractory Pain/Chronic Pain",
    "Aditional Analgesics",
    "Adjucnt Analgesics",
    "Adjunct Analgesic",
    "Adjunct Analgesics",
    "Adjunct Medications for Blood Pressure",
    "Adjunct Procedural Medications",
    "Adjunct Therapies",
    "Adjunct Therapies - Initiate only after GI consult",
    "Adjunctive Treatment:",
    "Adrenergic Agents",
    "Adult Antibiotics",
    "Adult Influenza Vaccination",
    "Adult Injectable Antibiotics",
    "Adult Oral Antibiotics",
    "Adult Tdap Vaccine",
    "Adult Tdap or Td Vaccine",
    "Afrin and Silver Nitrate",
    "After Visit / Pre-Admission Orders",
    "After Visit Orders",
    "Afterload reduction in cases of severe renal insufficiency:",
    "Agitation/delirium",
    "Albumin Prime",
    "Albumin Replacement (GREATER THAN 4 L removed with documented cirrhosis or any amount removed if creatinine is GREATER THAN 1.5 gm/dL) ",
    "Alcohol Withdrawal Therapy",
    "Alcohol Withdrawal Therapy (long-acting regimens)",
    "Alcohol Withdrawal Therapy (long-acting) - recommend long acting benzodiazepines for initial control of withdrawal symptoms",
    "Alcohol Withdrawal Therapy (short-acting regimens)",
    "Alcohol withdrawal therapy (short-acting) --recommend shorter acting agents for the elderly,  patients with severe or decompensated liver disease, or for maintenance for patients whose withdrawal syndrome is mostly controlled,  PO prefered over IV. Using",
    "Alcohol withdrawal therapy (short-acting) --recommend shorter acting agents for the elderly,  patients with severe or decompensated liver disease, or for maintenance for patients whose withdrawal syndrome is mostly controlled,  PO prefered over IV. Using the CIWA scale and symptom-triggered therapy reduces the duration of therapy and the total dose needed.",
    "Aldosterone Antagonist",
    "Alkali Therapy",
    "All Patients on Steroids before surgery",
    "All patients on Steroids before surgery",
    "Allergic Reaction",
    "Allo Routine Medications",
    "Alpha 1 Blocker",
    "Alpha 2 Receptor Agonists",
    "Alpha-2 Agonist agents",
    "Alteplase Protocol for Arterial and DVT Thrombolysis: High Dose (0.05 mg/mL)",
    "Alteplase Protocol for Arterial and DVT Thrombolysis: High-Volume; Low-Dose (0.01 mg/mL)",
    "Alteplase Protocol for Arterial and DVT Thrombolysis: High-Volume; Low-Dose (0.01mg/mL)",
    "Alteplase Protocol for Arterial and DVT Thrombolysis: Low-Volume; Low-Dose (0.02 mg/mL)",
    "Amb Pre-Operative Skin Preparation",
    "Aminoglycoside Therapy",
    "Amiodarone",
    "Ampicillin",
    "Anagesia/Sedation",
    "Analgesia",
    "Analgesia/Antipyretics",
    "Analgesia/Sedation",
    "Analgesia/Sedation/Paralysis",
    "Analgesic",
    "Analgesic Agents",
    "Analgesic/Antipyretic",
    "Analgesics",
    "Analgesics ",
    "Analgesics & Anti-Anxiety",
    "Analgesics & Anti-emetics",
    "Analgesics (Post-Intubation)",
    "Analgesics and Rescue Agents",
    "Analgesics/Antipyretic",
    "Analgesics/Antipyretics",
    "Analgesics/Sedatives",
    "Ancillary Medications",
    "Anemia Prevention",
    "Anesthetic for Foley Catheter Insertion",
    "Anesthetic for Venipuncture",
    "Anesthetics for Venipuncture",
    "Angiotensin Receptor Blockers",
    "Angiotensin-Converting Enzyme Inhibitors",
    "Angiotensin-Receptor Blockers",
    "Anit-infectives",
    "Antacid",
    "Antacids",
    "Antacids ",
    "Antacids/PPI",
    "Anti Inflammatory:",
    "Anti Ulcer Agents: Histamine-2 Receptor Antagonists",
    "Anti- depressants:  Non-SSRI",
    "Anti-Anxiety",
    "Anti-Anxiety & Anti-Nausea",
    "Anti-Anxiety & Nausea",
    "Anti-Anxiety/Hypnotics",
    "Anti-Anxiety:  Benzodiazepines",
    "Anti-Arrhythmic",
    "Anti-Coagulants: Low-Molecular Weight Heparins ",
    "Anti-Coagulation",
    "Anti-Diarrhea",
    "Anti-Emetic",
    "Anti-Emetics",
    "Anti-Emetics ",
    "Anti-Emetics/GI",
    "Anti-Epileptic Agents",
    "Anti-Epileptics",
    "Anti-Fungals",
    "Anti-Hypertensives",
    "Anti-Hypoglycemic Agents"
]

FREQ_NAMES = [
    None,
    "ONCE",
    "DAILY",
    "PRN",
    "2 TIMES DAILY",
    "EVERY 6 HOURS PRN",
    "EVERY 4 HOURS PRN",
    "CONTINUOUS",
    "PACU ONLY MULTIPLE PRN",
    "CONTINUOUS PARENTERAL NUTR",
    "ONCE PRN",
    "EVERY BEDTIME",
    "3 TIMES DAILY",
    "EVERY 8 HOURS",
    "EVERY 6 HOURS",
    "EVERY 12 HOURS",
    "PACU ONLY ONCE PRN",
    "ANESTHESIA CONTINUOUS",
    "EVERY 24 HOURS",
    "DAILY PRN",
    "EVERY BEDTIME PRN",
    "PACU ONLY CONTINUOUS",
    "EVERY 8 HOURS PRN",
    "PRE-OP ONCE",
    "4 TIMES DAILY",
    "ENDOSCOPY MULTIPLE PRN",
    "2 TIMES DAILY PRN",
    "5 TIMES DAILY PRN",
    "EVERY MORNING",
    "AS DIRECTED",
    "4 TIMES DAILY PRN",
    "EVERY 2 MIN PRN",
    "EVERY MORNING BEFORE BREAKFAST",
    "2 TIMES DAILY WITH MEALS",
    "EVERY EVENING",
    "ONCE TBD",
    "ONCE PRN, MAY REPEAT X1",
    "EVERY 2 HOURS PRN",
    "3 TIMES DAILY PRN",
    "EVERY MORNING WITH BREAKFAST",
    "EVERY NIGHT",
    "EVERY 3 HOURS PRN",
    "RADIOLOGY ONCE",
    "EVERY 7 DAYS",
    "EVERY 15 MIN PRN",
    "4 TIMES DAILY BEFORE MEALS & BEDTIME",
    "ENDOSCOPY CONTINUOUS",
    "EVERY 4 HOURS",
    "EVERY HOUR PRN",
    "3 TIMES DAILY WITH MEALS",
    "EVERY 12 HOURS PRN",
    "CATH ANGIO MULTIPLE PRN",
    "PRE-OP MULTIPLE",
    "PCA - Lockout 15 Minutes",
    "EVERY 1 HOUR",
    "EVERY 4-6 HOURS PRN",
    "3 TIMES DAILY BEFORE MEALS",
    "DIALYSIS ONCE",
    "ENDOSCOPY ONCE",
    "ONCE, MAY REPEAT X1",
    "DAILY AT BEDTIME",
    "ON CALL",
    "EVERY OTHER DAY",
    "2 TIMES DAILY BEFORE MEALS",
    "EVERY M W F",
    "ENDOSCOPY EVERY 2 MIN PRN",
    "DIALYSIS CONTINUOUS",
    "INTRA-OP ONCE",
    "PCA - Lockout 10 Minutes",
    "EVERY 5 MIN PRN",
    "EVERY HOUR",
    "PER PHARMACY PROTOCOL",
    "EVERY 2 HOURS",
    "EVERY 4 HOURS WHILE AWAKE",
    "SEE INSTRUCTIONS",
    "ED ONCE PRN, MAY REPEAT X1",
    "5 TIMES DAILY",
    "EVERY 72 HOURS",
    "EVERY 3 DAYS",
    "PRE-OP CONTINUOUS",
    "2 TIMES WEEKLY",
    "EVERY 48 HOURS",
    "PRIOR TO DISCHARGE",
    "DAILY WITH DINNER",
    "PRE-OP MULTIPLE PRN",
    "EVERY BEDTIME PRN, MR X 1",
    "3 TIMES WEEKLY",
    "ED EVERY 5 MIN PRN",
    "EVERY 22 HOURS",
    "PACU ONLY ONCE",
    "Once (code)",
    "4 TIMES DAILY WITH MEALS & BEDTIME",
    "DAILY BEFORE DINNER",
    "EVERY 3-4 HOURS PRN",
    "ONCE A WEEK",
    "6 TIMES DAILY",
    "4 TIMES DAILY AFTER MEALS & BEDTIME",
    "EVERY 3 MONTHS",
    "DAILY AT NIGHT",
    "EVENING",
    "EVERY 3 HOURS",
    "APHERESIS CONTINUOUS",
    "EVERY 2 WEEKS",
    "AM",
    "EVERY MONTH",
    "EVERY 30 MIN PRN",
    "EVERY 5 MIN",
    "MORNING",
    "2 TIMES PER WEEK",
    "3 TIMES DAILY AFTER MEALS",
    "EVERY 30 DAYS",
    "PCA - Lockout 20 Minutes",
    "CONTINUOUS PARENTERAL NUTR (VC)",
    "EVERY 14 DAYS",
    "Continuous (code)",
    "2 TIMES DAILY (FOR PAIN COCKTAILS)",
    "EVERY 28 DAYS",
    "EVERY 6-8 HOURS PRN",
    "DAILY AM WITH FOOD",
    "EVERY 30 MIN",
    "ED EVERY 15 MIN PRN",
    "ENDOSCOPY ONCE PRN, MAY REPEAT X1",
    "EVERY 2 HOURS WHILE AWAKE",
    "EVERY 24 HOURS PRN",
    "E1PRN",
    "2 TIMES DAILY AFTER MEALS",
    "EVERY 6 HOURS WHILE AWAKE",
    "EVERY 10 MIN PRN",
    "EVERY MORNING AFTER BREAKFAST",
    "EVERY SA SU BID",
    "EVERY 12 WEEKS",
    "EVERY 4 HOURS WHILE AWAKE RT",
    "OR Continuous ",
    "PROCEDURE ONLY MULTIPLE PRN",
    "PM",
    "3 TIMES DAILY WITH SNACKS",
    "EVERY 3 DAYS PRN",
    "EVERY 15 MIN",
    "EVERY 20 MIN PRN",
    "2 TIMES DAILY (0800,2200)",
    "2 TIMES DAILY RT",
    "EVERY M TH",
    "EVERY TU TH SA",
    "PCA - Lockout 12 Minutes",
    "MEDROL DOSEPAK BID BREAKFAST AND BEDTIME",
    "PCA - Lockout 30 Minutes",
    "EVERY 4-6 HOURS",
    "MEDROL DOSEPAK BID LUNCH AND DINNER",
    "EVERY SUNDAY",
    "EVERY FRIDAY",
    "E1ONCE",
    "DAILY WITH LUNCH",
    "PACU ONLY MULTIPLE",
    "EVERY MONDAY",
    "RX CUSTOM FREQUENCY",
    "2 TIMES DAILY FOR 7 DAYS",
    "EVERY 10 MIN",
    "PRE-OP ONCE PRN",
    "TID After Meals",
    "DIALYSIS MULTIPLE PRN",
    "2 TIMES DAILY FOR 10 DAYS",
    "QID (0900,1300,1700,2100)",
    "EVERY TU TH SA SU",
    "EVERY WEDNESDAY",
    "E1CONTINUOUS",
    "MEDROL DOSEPAK DAILY WITH BREAKFAST",
    "BEFORE MEALS",
    "EVERY SATURDAY",
    "1/2 HOUR BEFORE MEALS AND BEDTIME",
    "EVERY 8-12 HOURS PRN",
    "FIVE TIMES A WEEK",
    "EVERY 4 HOURS RT",
    "APPLY AS DIRECTED",
    "2 TIMES DAILY FOR 14 DAYS",
    "EVERY THURSDAY",
    "EVERY TUESDAY",
    "DAILY RT",
    "CYCLIC PARENTERAL NUTR (VC)",
    "RADIOLOGY MULTIPLE",
    "EVERY 3 WEEKS",
    "ONCE AFTER DIALYSIS",
    "DIALYSIS ONCE PRN",
    "PROCEDURE ONLY ONCE PRN",
    "EVERY SA SU",
    "3 TIMES DAILY FOR 7 DAYS",
    "EVERY 6 HOURS RT",
    "4 TIMES DAILY FOR 7 DAYS",
    "MEDROL DOSEPAK TID BRKFAST, LUNCH, BEDTIME",
    "MEDROL DOSEPAK DAILY AT BEDTIME",
    "BEFORE MEALS AND AT BEDTIME",
    "2 TIMES DAILY ON MO, WED & FR",
    "APHERESIS ONLY MULTIPLE PRN",
    "3 TIMES DAILY FOR 10 DAYS",
    "ED PRN",
    "EVERY M F",
    "EVERY 4 DAYS",
    "EVERY 3 HOURS WHILE AWAKE",
    "DAILY BEFORE LUNCH",
    "EVERY M W F SU",
    "EVERY 56 DAYS"
]


class TestSTARROrderMedConversion(DBTestCase):
    TEST_DATA_SIZE = 2 * len(MED_ROUTES)    # at least 2 rows per med route combined with inpatient vs outpatient

    ORDER_MED_HEADER = ['order_med_id_coded', 'jc_uid', 'pat_enc_csn_id_coded', 'medication_id', 'med_description',
                        'order_time_jittered', 'med_route', 'number_of_times', 'ordering_mode', 'freq_name']
    MED_ORDERSET_HEADER = ['order_med_id_coded', 'protocol_id', 'protocol_name', 'ss_section_id', 'ss_section_name',
                           'ss_sg_key', 'ss_sg_name']

    test_data = []
    orderset_data = []
    clinical_items = {}
    expected_data = []
    expected_orderset_data = []

    test_data_csv = tempfile.gettempdir() + '/test_starr_order_med_dummy_data.csv'
    orderset_data_csv = tempfile.gettempdir() + '/test_starr_order_med_orderset_data.csv'

    def setUp(self):
        log.setLevel(logging.INFO)  # without this no logs are printed

        """Prepare state for test cases"""
        DBTestCase.setUp(self)

        log.info("Sourcing from BigQuery DB")
        ClinicalItemDataLoader.build_clinical_item_psql_schemata()

        self.converter = STARROrderMedConversion.STARROrderMedConversion()  # Instance to test on
        self.bqConn = self.converter.bqConn
        self.starrUtil = STARRUtil.StarrCommonUtils(self.converter.bqClient)

        # point the converter to dummy source table
        STARROrderMedConversion.SOURCE_TABLE = TEST_SOURCE_TABLE
        STARROrderMedConversion.ORDERSET_TABLE = TEST_ORDERSET_TABLE

    def generate_test_and_expected_data(self, test_data_size, conv_options):
        # preload mapped_meds table
        rxcuiDataByMedId = self.converter.loadRXCUIData()

        self.generate_ordermed_and_orderset_data(test_data_size, rxcuiDataByMedId)

        # need to sort data to use the same clinical_item.descriptions as the duplicate clinical_items are not stored
        self.test_data.sort(key=lambda tup: (tup[0], tup[1], tup[2], tup[3]))
        self.orderset_data.sort(key=lambda row: row[0])

        # join test order_med and med_orderset data to create a test row
        joined_test_data = self.left_join_ordermed_and_orderset_data()

        for joined_test_data_row in joined_test_data:
            self.generate_expected_data_rows(joined_test_data_row[0], joined_test_data_row[1], rxcuiDataByMedId, conv_options)

        # pi.external_id desc, ci.external_id desc
        self.expected_data.sort(key=lambda tup: (-tup[0], tup[1], tup[2], -tup[4]))

        # pi.external_id, ci.external_id (medication_id)
        self.expected_orderset_data.sort(key=lambda tup: (tup[0], tup[1], tup[2], tup[3], tup[4]))

    def left_join_ordermed_and_orderset_data(self):
        joined_test_data = []
        for test_data_row in self.test_data:
            if self.ignore_row(test_data_row[3], test_data_row[9]):
                continue

            found_join_row = False
            for test_orderset_row in self.orderset_data:
                if test_data_row[0] == test_orderset_row[0]:
                    found_join_row = True
                    joined_test_data.append((test_data_row, test_orderset_row))
            if not found_join_row:
                joined_test_data.append((test_data_row, None))
        return joined_test_data

    def generate_ordermed_and_orderset_data(self, test_data_size, rxcuiDataByMedId):
        seen_test_data_rows = set()
        while len(self.test_data) < test_data_size:
            curr_row = len(self.test_data)
            patient_id = 'JC' + format(curr_row, '06')

            test_data_row = self.generate_test_data_row(curr_row, patient_id, rxcuiDataByMedId)

            test_data_row_unique_key = (test_data_row[0], test_data_row[1], test_data_row[2], test_data_row[3])
            if test_data_row_unique_key not in seen_test_data_rows:
                seen_test_data_rows.add(test_data_row_unique_key)
                self.test_data.append(test_data_row)

                # should generate at most 1 row of med_orderset per order_med row (tested code does LEFT OUTER JOIN)
                should_generate_orderset_row = random.randint(0, 1)
                if should_generate_orderset_row:
                    orderset_row = self.generate_orderset_row(test_data_row[0])
                    self.orderset_data.append(orderset_row)

    @staticmethod
    def ignore_row(medication_id, freq_name):
        # process only rows where med.medication_id <> 9000000 and freq_name not like '%PRN'
        return medication_id == 9000000 or (freq_name is not None and freq_name.endswith('PRN'))

    @staticmethod
    def generate_test_data_row(curr_row, patient_id, rxcuiDataByMedId):
        use_rxcui = random.randint(1, 5)
        if use_rxcui % 5 == 0:
            # use mapped_meds 20% of the time
            medication_id = rxcuiDataByMedId.keys()[random.randint(0, len(rxcuiDataByMedId) - 1)]
        else:
            # several times less than the test records count to have some medication_ids occur multiple times
            medication_id = random.randint(0, len(MED_ROUTES) / 5)

        return (
            random.randint(0, len(MED_ROUTES) / 10),  # order_med_id_coded - want some of them to repeat
            patient_id,
            curr_row,  # pat_enc_csn_id_coded
            medication_id,
            MED_DESCRIPTIONS[random.randint(0, len(MED_DESCRIPTIONS) - 1)],
            datetime.fromtimestamp(random.randint(1, int(time.time()))),  # random order_time_jittered
            MED_ROUTES[random.randint(0, len(MED_ROUTES) - 1)],
            random.randint(1, 180),  # number_of_times
            ORDERING_MODES[random.randint(0, len(ORDERING_MODES) - 1)],  # ordering_modes
            FREQ_NAMES[random.randint(0, len(FREQ_NAMES) - 1)]
        )

    @staticmethod
    def generate_orderset_row(order_med_id_coded):
        protocol_id = random.randint(1, len(PROTOCOL_NAME))
        ss_section_id = random.randint(0, len(SS_SECTION_NAME) - 1)
        ss_sg_key = random.randint(0, len(SS_SG_NAME) - 1)

        return (
            order_med_id_coded,  # to match the given order_med_row
            -protocol_id,
            PROTOCOL_NAME[protocol_id - 1],
            ss_section_id,
            SS_SECTION_NAME[ss_section_id],
            str(ss_sg_key),
            SS_SG_NAME[ss_sg_key]
        )

    def generate_expected_data_rows(self, row, orderset_row, rxcuiDataByMedId, conv_options):
        row_model = RowItemModel()
        row_model["medication_id"] = row[3]
        row_model["med_description"] = row[4]
        row_model["number_of_times"] = row[7]
        row_model["med_route"] = row[6]

        normalized_med_data = list(self.converter.normalizeMedData(rxcuiDataByMedId, row_model, conv_options))

        cic_description = STARROrderMedConversion.CATEGORY_TEMPLATE.format(row_model["med_route"], row[8])

        for normalized_model in normalized_med_data:
            ci_key = (TEST_SOURCE_TABLE, cic_description, normalized_model["code"])

            if ci_key not in self.clinical_items \
                    or len(normalized_model["med_description"]) < len(self.clinical_items[ci_key]) \
                    or self.clinical_items[ci_key].startswith(TEMPLATE_MEDICATION_PREFIX):
                self.clinical_items[ci_key] = normalized_model["med_description"]

                # replace previous ci_descriptions in expected_data
                for i in range(len(self.expected_data)):
                    if self.expected_data[i][3] == cic_description and self.expected_data[i][5] == normalized_model["code"]:
                        self.expected_data[i] = self.expected_data[i][:6] + (self.clinical_items[ci_key], self.expected_data[i][7])

                # replace previous ci_descriptions in expected_orderset_data
                for i in range(len(self.expected_orderset_data)):
                    if self.expected_orderset_data[i][2] == cic_description and self.expected_orderset_data[i][3] == normalized_model["code"]:
                        self.expected_orderset_data[i] = self.expected_orderset_data[i][:4] + (self.clinical_items[ci_key],) + self.expected_orderset_data[i][5:]

            ci_description = self.clinical_items[ci_key]

            expected_row = (
                row[0],                                                                             # external_id
                self.starrUtil.convertPatIdToSTRIDE(row[1]),                                        # patient_id
                row[2],                                                                             # encounter_id
                cic_description,                                                                    # cic_description
                normalized_model["medication_id"],                                                  # ci_external_id
                normalized_model["code"],                                                           # ci_name
                ci_description,                                                                     # ci_description
                row[5]                                                                              # pi_item_date
            )
            if expected_row not in self.expected_data:
                self.expected_data.append(expected_row)

            if orderset_row is not None:
                # generate expected data for orderset - in %item_collection% tables
                expected_orderset_row = (
                    row[0],
                    normalized_model["medication_id"],
                    cic_description,
                    normalized_model["code"],   # ci_name
                    ci_description,
                    orderset_row[1],            # protocol_id
                    orderset_row[2],            # protocol_name
                    orderset_row[4],            # ss_section_name
                    orderset_row[6]             # ss_sg_name
                )
                self.expected_orderset_data.append(expected_orderset_row)

    @staticmethod
    def prepare_conv_options(dose_count_limit, include_route_in_description, normalize_mixtures):
        conv_options = STARROrderMedConversion.ConversionOptions()
        conv_options.normalizeMixtures = normalize_mixtures
        conv_options.doseCountLimit = dose_count_limit
        conv_options.includeRouteInDescription = include_route_in_description
        return conv_options

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

    @parameterized.expand([
        ["with_denormalizeMixtures_noDoseCountLimit_includeRoute", False, None, True],
    ])
    def test_row_with_no_ingredient_is_processed(self, name, normalize_mixtures, dose_count_limit, include_route_in_description):
        log.info("Test the output is not empty even if active_ingredient is None in mapped_meds with since ingredient")

        # { medication_id -> { rxcui -> active_ingredient } }
        rxcuiDataByMedId = {1: {2: None}}

        row_model = RowItemModel()
        row_model["medication_id"] = 1
        row_model["med_description"] = "Med description"
        row_model["number_of_times"] = 10
        row_model["med_route"] = "Intravenous"

        conv_options = self.prepare_conv_options(dose_count_limit, include_route_in_description, normalize_mixtures)
        normalized_med_data = list(self.converter.normalizeMedData(rxcuiDataByMedId, row_model, conv_options))
        self.assertTrue(normalized_med_data)

    @parameterized.expand([
        ["with_denormalizeMixtures_noDoseCountLimit_includeRoute", False, None, True],
        ["with_denormalizeMixtures_noDoseCountLimit_excludeRoute", False, None, False],
        ["with_denormalizeMixtures_DoseCountLimit_includeRoute", False, 100, True],
        ["with_denormalizeMixtures_DoseCountLimit_excludeRoute", False, 100, False],
        ["with_normalizeMixtures_noDoseCountLimit_includeRoute", True, None, True],
        ["with_normalizeMixtures_noDoseCountLimit_excludeRoute", True, None, False],
        ["with_normalizeMixtures_DoseCountLimit_includeRoute", True, 100, True],
        ["with_normalizeMixtures_DoseCountLimit_excludeRoute", True, 100, False],
    ])
    def test_data_conversion(self, name, normalize_mixtures, dose_count_limit, include_route_in_description):
        log.info("Generating test source data")

        conv_options = self.prepare_conv_options(dose_count_limit, include_route_in_description, normalize_mixtures)

        self.generate_test_and_expected_data(self.TEST_DATA_SIZE, conv_options)

        # upload med_orderset
        self.starrUtil.dump_test_data_to_csv(self.MED_ORDERSET_HEADER, self.orderset_data, self.orderset_data_csv)
        self.starrUtil.upload_csv_to_bigquery('starr_datalake2018', 'med_orderset', TEST_DEST_DATASET,
                                              'starr_med_orderset', self.orderset_data_csv, self.MED_ORDERSET_HEADER)

        # upload order_med
        self.starrUtil.dump_test_data_to_csv(self.ORDER_MED_HEADER, self.test_data, self.test_data_csv)
        self.starrUtil.upload_csv_to_bigquery('starr_datalake2018', 'order_med', TEST_DEST_DATASET,
                                              'starr_order_med', self.test_data_csv, self.ORDER_MED_HEADER)

        log.debug("Run the conversion process...")
        temp_dir = tempfile.gettempdir()
        self.converter.convertAndUpload(conv_options, tempDir=temp_dir, target_dataset_id=TEST_DEST_DATASET, removeCsvs=True)

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
    test_suite.addTest(unittest.makeSuite(TestSTARROrderMedConversion))

    return test_suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
