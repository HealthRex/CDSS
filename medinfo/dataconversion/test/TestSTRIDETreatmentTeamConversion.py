#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from io import StringIO
from datetime import datetime;
import unittest

from .Const import RUNNER_VERBOSITY;
from .Util import log;

from medinfo.db.test.Util import DBTestCase;
from stride.core.StrideLoader import StrideLoader;
from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.ResultsFormatter import TabDictReader;

from medinfo.dataconversion.STRIDETreatmentTeamConversion import STRIDETreatmentTeamConversion, ConversionOptions;

TEST_START_DATE = datetime(2100,1,1);   # Date in far future to start checking for test records to avoid including existing data in database

class TestSTRIDETreatmentTeamConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        StrideLoader.build_stride_psql_schemata()
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();

        dataTextStr = \
"""stride_treatment_team_id\tpat_id\tpat_enc_csn_id\ttrtmnt_tm_begin_date\ttrtmnt_tm_end_date\ttreatment_team\tprov_name
-100\t-2536\t-57\t\t\t\tAnonymous.
-200\t-117\t0\t10/5/2113 23:18\t10/6/2113 10:20\tAdditional Communicating Provider\tAnonymous.Additional Communicating Provider
-300\t-4845\t-60\t6/26/2113 8:11\t6/26/2113 8:13\tCare Coordinator\tAnonymous.Care Coordinator
-400\t-9194\t-26\t4/11/2109 8:39\t\tCase Manager\tAnonymous.Case Manager
-500\t-9519\t-69\t3/19/2113 12:10\t\tChief Resident\tAnonymous.Chief Resident
-600\t-8702\t-77\t4/10/2109 8:45\t\tClinical Dietician\tAnonymous.Clinical Dietician
-700\t-8307\t-92\t7/9/2113 0:21\t7/9/2113 2:16\tCo-Attending\tAnonymous.Co-Attending
-800\t-5474\t-78\t12/4/2113 9:47\t12/4/2113 12:55\tConsulting Attending\tAnonymous.Consulting Attending
-900\t-6015\t-47\t7/24/2113 2:29\t\tConsulting Fellow\tAnonymous.Consulting Fellow
-1000\t-3733\t-39\t7/9/2113 8:04\t7/9/2113 11:36\tConsulting Intern\tAnonymous.Consulting Intern
-1100\t-9597\t-78\t10/12/2109 18:48\t\tConsulting Med Student\tAnonymous.Consulting Med Student
-1200\t-1087\t-18\t1/14/2109 23:12\t\tConsulting Resident\tAnonymous.Consulting Resident
-1300\t-6467\t-14\t4/10/2109 11:55\t\tConsulting Service\tAnonymous.Consulting Service
-1400\t-1291\t-70\t12/31/2111 10:35\t1/7/2112 11:28\tDietician Intern\tAnonymous.Dietician Intern
-1500\t-5038\t-91\t9/12/2112 18:04\t9/12/2112 18:08\tED Registrar\tAnonymous.ED Registrar
-1600\t-8055\t-77\t5/4/2110 9:35\t5/4/2110 16:00\tED Tech\tAnonymous.ED Tech
-1700\t-2531\t-12\t5/8/2110 14:50\t5/8/2110 23:45\tED Unit Secretary\tAnonymous.ED Unit Secretary
-1800\t-54\t-14\t10/23/2109 11:51\t\tEmergency Resident\tAnonymous.Emergency Resident
-1900\t-6763\t-25\t5/7/2110 5:29\t5/7/2110 6:28\tLicensed Vocational Nurse\tAnonymous.Licensed Vocational Nurse
-2000\t-5668\t-56\t9/30/2109 12:58\t9/30/2109 12:59\tMedical Assistant\tAnonymous.Medical Assistant
-2100\t-5862\t-78\t3/22/2113 18:54\t\tNurse Coordinator\tAnonymous.Nurse Coordinator
-2200\t-4060\t-97\t1/1/2113 16:50\t1/3/2113 0:57\tNurse Practitioner\tAnonymous.Nurse Practitioner
-2300\t-7217\t-45\t4/27/2110 7:30\t\tNursing Assistant\tAnonymous.Nursing Assistant
-2400\t-4026\t-44\t4/12/2109 16:13\t4/14/2109 10:31\tOccupational Therapist\tAnonymous.Occupational Therapist
-2500\t-8387\t-39\t4/14/2109 12:09\t\tPhysical Therapist\tAnonymous.Physical Therapist
-2600\t-2160\t-42\t9/15/2113 9:46\t\tPhysical Therapist Assistant\tAnonymous.Physical Therapist Assistant
-2700\t-3237\t-81\t1/17/2113 17:49\t1/17/2113 23:36\tPhysician\'s Assistant\tAnonymous.Physician\'s Assistant
-2800\t-7645\t-88\t10/19/2109 16:41\t\tPrimary Fellow\tAnonymous.Primary Fellow
-2900\t-448\t-56\t10/24/2109 12:11\t\tPrimary Intern\tAnonymous.Primary Intern
-3000\t-5832\t-51\t9/30/2109 12:59\t\tPrimary Med Student\tAnonymous.Primary Med Student
-3100\t-3983\t-19\t4/21/2110 12:15\t\tPrimary Physician Assistant\tAnonymous.Primary Physician Assistant
-3200\t-1547\t-42\t10/24/2109 12:11\t\tPrimary Resident\tAnonymous.Primary Resident
-3300\t-6251\t-4\t9/16/2109 19:31\t\tPrimary Sub-Intern\tAnonymous.Primary Sub-Intern
-3400\t-1328\t-59\t10/24/2109 13:55\t10/24/2109 16:42\tPrimary Team\tAnonymous.Primary Team
-3500\t-6209\t-50\t8/6/2113 10:16\t\tPsychologist\tAnonymous.Psychologist
-3600\t-8067\t-95\t10/18/2109 6:47\t\tRegistered Nurse\tAnonymous.Registered Nurse
-3700\t-9956\t-50\t10/17/2109 7:49\t\tRespiratory Care Practitioner\tAnonymous.Respiratory Care Practitioner
-3800\t-4057\t-8\t11/9/2109 16:23\t\tSocial Worker\tAnonymous.Social Worker
-3900\t-8424\t-44\t11/22/2109 7:58\t\tSpeech Therapist\tAnonymous.Speech Therapist
-4000\t-6271\t-78\t4/6/2113 15:00\t\tSpiritual Care\tAnonymous.Spiritual Care
-4100\t-3251\t-79\t9/11/2113 13:34\t9/11/2113 19:15\tStudent Nurse\tAnonymous.Student Nurse
-4200\t-79\t-74\t3/1/2113 15:36\t3/1/2113 15:36\tTrauma Attending\tAnonymous.Trauma Attending
-4300\t-6671\t-77\t9/26/2113 6:28\t9/26/2113 9:52\tTrauma Resident \tAnonymous.Trauma Resident 
-4400\t-9911\t-27\t11/1/2111 6:58\t11/7/2111 8:54\tTriage Nurse\tAnonymous.Triage Nurse
-4500\t-4550\t-58\t7/4/2113 21:35\t7/4/2113 21:57\tConsulting Service\tCON CARD INTERVEN/AMI CONSULT
-4600\t-1959\t-90\t12/26/2113 9:38\t12/28/2113 6:21\tConsulting Service\tCON CARDIAC SURGERY
-4700\t-6120\t-19\t11/17/2113 11:39\t\tConsulting Fellow\tCON CARDIOL ARRHYTHMIA
-4800\t-9620\t-14\t5/10/2113 9:42\t\tPrimary Team\tCON CARDIOL TRANSPLANT
-4900\t-7389\t-82\t11/9/2109 13:58\t11/12/2109 14:08\tConsulting Service\tCON CARDIOLOGY
-5000\t-2570\t-34\t3/18/2111 9:34\t\tPrimary Team\tCON CARDIOTHROACIC SURGERY
-5100\t-8843\t-96\t3/1/2113 7:50\t\tPrimary Team\tCON COLORECTAL SURGERY
-5200\t-9515\t-31\t1/22/2114 19:09\t\tPrimary Team\tCON CYSTIC FIBROSIS ADULT
-5300\t-2229\t-86\t12/21/2113 16:26\t12/21/2113 16:27\tConsulting Service\tCON ENDOCRINOLOGY
-5400\t-9149\t-90\t6/21/2113 6:42\t\tConsulting Service\tCON GASTROENTEROLOGY
-5500\t-4935\t-32\t8/18/2110 3:51\t\tPrimary Team\tCON GENERAL SURGERY
-5600\t-4935\t-32\t5/31/2111 14:39\t\tConsulting Service\tCON GERIATRICS
-5700\t-4550\t-62\t10/18/2111 20:15\t\tConsulting Service\tCON GYNECOLOGY
-5800\t-3954\t-61\t3/8/2111 8:05\t\tConsulting Service\tCON HAND SURGERY
-5900\t-7078\t-76\t11/8/2113 9:51\t\tConsulting Service\tCON HEMATOLOGY
-6000\t-4568\t-1\t5/6/2113 14:41\t\tConsulting Service\tCON HEPATOLOGY
-6100\t-4568\t-42\t1/21/2113 14:01\t1/21/2113 14:02\tConsulting Resident\tCON ICU
-6200\t-4568\t-82\t1/27/2114 11:20\t\tConsulting Service\tCON INF DIS
-6300\t-8539\t-33\t1/8/2112 8:59\t\tConsulting Service\tCON INF DIS IMMUNOCOMP
-6400\t-1543\t-19\t5/29/2110 12:57\t\tConsulting Service\tCON INF DIS POSTITIVE CARE
-6500\t-1543\t-19\t4/21/2113 11:27\t4/21/2113 14:14\tConsulting Service\tCON INTERNAL MEDICINE CONSULT
-6600\t-1543\t-19\t7/21/2112 4:03\t\tConsulting Service\tCON INTERVENT RAD
-6700\t-4464\t-14\t8/15/2113 0:11\t8/15/2113 0:12\tConsulting Service\tCON KIDNEY TRANSPLANT
-6800\t-4464\t-42\t1/10/2113 8:33\t\tPrimary Team\tCON LIVER TRANSPLANT
-6900\t-4464\t-22\t9/5/2112 13:22\t\tConsulting Service\tCON MEDICAL GENETICS
-7000\t-9840\t-68\t9/27/2109 16:51\t\tConsulting Service\tCON MEDICINE
-7100\t-9840\t-68\t4/23/2113 12:42\t\tConsulting Service\tCON MICU ADMISSION REQUEST
-7200\t-4392\t-98\t8/14/2113 23:16\t8/14/2113 23:19\tConsulting Service\tCON MICU CONSULT
-7300\t-394\t-11\t9/17/2109 10:46\t\tConsulting Service\tCON NEPHROLOGY
-7400\t-7389\t-82\t10/19/2109 2:06\t\tConsulting Service\tCON NEPHROLOGY TRANSPLANT
-7500\t-5689\t-19\t12/4/2110 17:36\t\tConsulting Service\tCON NEURO ENDOCRINE CONSULT
-7600\t-714\t-33\t12/11/2113 1:07\t12/11/2113 1:09\tConsulting Service\tCON NEURO EPILEPSY CONSULT
-7700\t-1464\t-53\t10/8/2109 12:20\t10/9/2109 10:47\tConsulting Service\tCON NEURO ICU
-7800\t-3115\t-69\t7/25/2112 21:44\t\tConsulting Service\tCON NEURO IR
-7900\t-7516\t-84\t11/23/2112 12:00\t11/23/2112 12:00\tConsulting Resident\tCON NEURO ONCOLOGY
-8000\t-9726\t-91\t7/15/2109 22:20\t\tPrimary Team\tCON NEURO STROKE
-8100\t-9726\t-91\t7/27/2109 21:42\t\tConsulting Service\tCON NEUROLOGY GENERAL
-8200\t-3961\t-74\t4/10/2111 7:51\t\tPrimary Team\tCON NEUROSURGERY
-8300\t-4087\t-54\t8/2/2110 1:54\t\tConsulting Service\tCON OBSTETRICS
-8400\t-1266\t-12\t12/24/2113 10:19\t\tConsulting Service\tCON ONCOLOGY
-8500\t-2289\t-68\t6/21/2113 0:27\t\tConsulting Service\tCON OPHTHALMOLOGY
-8600\t-2591\t-79\t1/19/2112 12:15\t1/19/2112 13:22\tConsulting Service\tCON ORTHOPEDICS
-8700\t-6762\t-49\t12/3/2113 5:00\t\tConsulting Service\tCON ORTHOPEDICS HOSPITALIST
-8800\t-6762\t-59\t4/10/2109 11:55\t\tConsulting Service\tCON PAIN
-8900\t-211\t-87\t9/24/2113 10:15\t\tConsulting Service\tCON PALLIATIVE CARE
-9000\t-7621\t-85\t4/30/2113 6:49\t\tConsulting Service\tCON PAMF MEDICINE
-9100\t-3251\t-49\t6/14/2113 19:49\t\tConsulting Service\tCON PRIMARY CARE
-9200\t-2837\t-81\t1/19/2112 11:25\t\tConsulting Service\tCON PSYCHIATRY
-9300\t-2837\t-42\t10/23/2113 11:54\t\tConsulting Service\tCON PULM HYPERTENSION
-9400\t-2837\t-42\t8/9/2113 19:48\t\tPrimary Team\tCON PULM TRANSPLANT
-9500\t-2837\t-42\t11/4/2113 7:03\t\tConsulting Service\tCON PULMONARY
-9600\t-4295\t-35\t10/4/2113 9:36\t10/4/2113 10:14\tConsulting Service\tCON PULMONARY REHAB CONSULT
-9700\t-3433\t-44\t10/19/2112 9:31\t\tConsulting Service\tCON RHEUMATOLOGY
-9800\t-7612\t-25\t10/13/2111 18:11\t10/13/2111 18:12\tConsulting Service\tCON SPINE TRAUMA
-9900\t-4875\t-51\t8/28/2113 21:14\t\tConsulting Service\tCON THORACIC SURGERY
-10000\t-8813\t-79\t3/26/2113 20:26\t3/26/2113 21:15\tPrimary Team\tCON TRANSPLANT SURGERY
-10100\t-8813\t-79\t5/7/2112 10:35\t5/16/2112 9:01\tConsulting Service\tCON UROLOGY
-10200\t-8720\t-72\t1/14/2114 16:49\t1/18/2114 15:10\tConsulting Service\tCON VASCULAR SURGERY
-10300\t-8720\t-72\t11/30/2109 18:16\t\tPrimary Team\tTT ACUTE CARE SURGERY TRAUMA, PGR 12163
-10400\t-1365\t-79\t12/21/2113 9:19\t12/24/2113 12:46\tConsulting Service\tTT ACUTE PAIN, PGR 2PAIN
-10500\t-1365\t-79\t10/22/2113 7:58\t\tPrimary Team\tTT BMT T2, PGR 16019 (BMT)
-10600\t-8712\t-95\t9/13/2111 16:27\t9/13/2111 17:07\tPrimary Team\tTT BMT, .
-10700\t-7799\t-15\t7/11/2113 15:47\t\tPrimary Team\tTT BMT, PGR 27268 (27BMT)
-10800\t-2552\t-30\t11/21/2113 19:15\t\tConsulting Service\tTT BREAST SURGERY, PGR 12160
-10900\t-3644\t-25\t1/19/2113 13:25\t\tPrimary Team\tTT CARDIAC BLUE ADULT, PAGER 12175
-11000\t-3644\t-1\t1/31/2113 8:25\t\tPrimary Team\tTT CARDIAC GREEN ADULT, PAGER 12105
-11100\t-7289\t-58\t9/1/2109 15:16\t\tPrimary Team\tTT CARDIOLOGY 5A, .
-11200\t-8843\t-96\t11/1/2109 7:02\t\tPrimary Team\tTT CARDIOLOGY 5B, .
-11300\t-9515\t-31\t1/15/2110 20:02\t\tPrimary Team\tTT CARDIOLOGY 6A, .
-11400\t-394\t-58\t12/30/2110 17:29\t1/3/2111 23:30\tPrimary Team\tTT CARDIOLOGY 6B INTERN -- PGR 27074
-11500\t-7987\t-69\t5/25/2110 13:56\t\tPrimary Team\tTT CARDIOLOGY 6B, .
-11600\t-2446\t-72\t10/21/2111 7:25\t10/21/2111 16:20\tPrimary Team\tTT CARDIOLOGY ARRHYTHMIA, .
-11700\t-3127\t-94\t2/24/2113 17:11\t\tPrimary Team\tTT CARDIOLOGY EP A, PGR 27079
-11800\t-8832\t-55\t6/5/2113 16:51\t6/6/2113 20:06\tPrimary Team\tTT CARDIOLOGY EP B, PGR 27080
-11900\t-1826\t-61\t7/19/2110 15:03\t\tPrimary Resident\tTT CARDIOLOGY INTERVENTIONAL -- PGR 27080
-12000\t-345\t-8\t2/26/2113 5:24\t\tPrimary Team\tTT CCU/HF 1, PGR 27075
-12100\t-6351\t-89\t5/21/2113 6:10\t5/22/2113 4:25\tPrimary Team\tTT CCU/HF 2, PGR 27076
-12200\t-1851\t-54\t1/23/2113 23:16\t\tPrimary Team\tTT CCU/HF 3, PGR 27077
-12300\t-5563\t-18\t4/21/2113 7:47\t\tPrimary Team\tTT CCU/HF 4, PGR 27078
-12400\t-5752\t-91\t12/25/2113 9:33\t\tPrimary Team\tTT CHRIS MOW, (408)830-0905
-12500\t-7881\t-71\t6/17/2113 13:43\t6/18/2113 10:08\tConsulting Service\tTT CHRONIC PAIN, PGR 27150
-12600\t-7881\t-71\t12/2/2113 8:39\t\tPrimary Team\tTT COLORECTAL SURGERY, PGR 12029
-12700\t-7881\t-16\t7/23/2113 16:27\t\tPrimary Team\tTT CRANIOFACIAL SURGERY, PGR 27011
-12800\t-2270\t-17\t6/30/2109 15:23\t7/2/2109 17:15\tPrimary Team\tTT CVICU TEAM 1, SPECTRAS 4-2829,8-9218
-12900\t-9149\t-90\t4/21/2110 11:25\t\tPrimary Team\tTT CYSTIC FIBROSIS ADULT, .
-13000\t-4935\t-32\t9/26/2113 19:44\t\tPrimary Team\tTT CYSTIC FIBROSIS ADULT, PGR 27081
-13100\t-4935\t-32\t10/23/2113 15:06\t\tPrimary Team\tTT ENT HEAD AND NECK, PGR 27082
-13200\t-4935\t-32\t5/17/2110 8:38\t\tPrimary Team\tTT ENT HEAD NECK, .
-13300\t-4935\t-32\t5/12/2110 8:58\t\tConsulting Service\tTT ENT SPECIALTY, .
-13400\t-4540\t-63\t7/11/2113 18:25\t\tConsulting Service\tTT ENT SPECIALTY, PGR 27083
-13500\t-1614\t-42\t3/21/2113 19:53\t\tPrimary Team\tTT GEN CARDS 1, PGR 27070
-13600\t-1614\t-42\t4/23/2113 7:23\t\tPrimary Team\tTT GEN CARDS 2, PGR 27071
-13700\t-6824\t-84\t5/12/2113 7:15\t\tPrimary Team\tTT GEN CARDS 3, PGR 27073
-13800\t-3034\t-56\t5/9/2109 6:17\t\tPrimary Team\tTT GEN SURG GOLD - PAGER 12160
-13900\t-7232\t-51\t8/21/2109 8:03\t\tPrimary Team\tTT GEN SURG RED - PAGER 12029
-14000\t-4596\t-16\t8/21/2109 17:27\t8/24/2109 19:45\tConsulting Service\tTT GEN SURG WHITE - PAGER 12076
-14100\t-9210\t0\t11/8/2113 11:28\t\tConsulting Service\tTT GENERAL THORACIC, PGR 12060
-14200\t-7584\t-48\t3/29/2110 18:12\t\tPrimary Team\tTT GYN ONC, .
-14300\t-5374\t-7\t8/6/2113 5:24\t\tPrimary Team\tTT GYN ONC, PGR 12825
-14400\t-4331\t-81\t5/1/2113 9:40\t\tPrimary Team\tTT GYN PRIVATE, PGR 27095
-14500\t-8523\t-99\t10/22/2113 7:25\t\tPrimary Team\tTT GYN UNIV, PGR 12055
-14600\t-3827\t-55\t8/13/2110 1:56\t\tPrimary Team\tTT HAND SURGERY, .
-14700\t-7066\t-8\t3/1/2110 15:32\t\tPrimary Team\tTT HEART LUNG TRANSPLANT, .
-14800\t-8127\t-22\t6/28/2111 7:15\t\tPrimary Team\tTT HEART TRANSPLANT/VAD -- PGR 12098
-14900\t-4146\t-27\t6/23/2113 7:53\t\tPrimary Team\tTT HEARTTRANSPLANT SURGERY, PGR 12098
-15000\t-8501\t-58\t5/23/2113 6:47\t5/23/2113 6:51\tPrimary Team\tTT HEMATOLOGY NP A, PGR 27093
-15100\t-8961\t-39\t4/28/2113 11:10\t4/29/2113 6:58\tPrimary Team\tTT HEMATOLOGY RESIDENT A, PGR 27090
-15200\t-3215\t-96\t4/27/2113 7:08\t4/27/2113 10:50\tPrimary Team\tTT HEMATOLOGY RESIDENT B, PGR 27091
-15300\t-5112\t-25\t4/29/2113 6:58\t5/4/2113 7:13\tPrimary Team\tTT HEMATOLOGY RESIDENT C, PGR 27092
-15400\t-4659\t-77\t5/21/2110 15:36\t6/5/2110 22:26\tConsulting Service\tTT HEMATOLOGY, .
-15500\t-8230\t-95\t8/1/2113 11:37\t\tPrimary Team\tTT HPB SURGERY, PGR 25781
-15600\t-4122\t-28\t10/1/2109 15:49\t10/3/2109 10:39\tConsulting Service\tTT INTERVENTIONAL RADIOLOGY, .
-15700\t-8600\t-91\t8/26/2113 21:35\t8/27/2113 17:21\tConsulting Service\tTT INTERVENTIONAL RADIOLOGY, PGR 2RADS
-15800\t-5557\t-37\t10/19/2109 16:41\t\tPrimary Team\tTT KIDNEY PANCREAS TRANSPLANT, PGR 12164
-15900\t-2062\t-5\t3/26/2113 0:09\t\tPrimary Team\tTT LIVER TRANSPLANT, PGR 12164
-16000\t-5394\t-95\t12/6/2113 16:18\t\tPrimary Team\tTT LUNG TRANSPLANT, PGR 27127
-16100\t-3498\t-87\t12/8/2113 22:31\t\tPrimary Team\tTT MED NOCTURNIST, PGR 12012
-16200\t-2935\t-68\t4/18/2111 18:49\t\tPrimary Team\tTT MED PAMF NON RESI
-16300\t-12\t-58\t10/21/2112 21:48\t10/21/2112 4:49\tPrimary Team\tTT MED TEAM H1, PGR 26403
-16400\t-1078\t-22\t6/30/2111 13:55\t6/30/2111 14:01\tConsulting Service\tTT MED TEAM H2, PGR 26404
-16500\t-6187\t-96\t11/15/2113 15:20\t\tPrimary Team\tTT MED TX CARDS A, PGR 25901
-16600\t-3081\t-86\t12/14/2113 17:16\t12/14/2113 17:17\tPrimary Team\tTT MED TX CARDS B, PGR 25904
-16700\t-4592\t-52\t11/16/2113 17:43\t11/26/2113 6:54\tPrimary Team\tTT MED TX HEP A, PGR 25908
-16800\t-2790\t0\t11/26/2113 6:54\t\tPrimary Team\tTT MED TX HEP B, PGR 25909
-16900\t-6295\t-58\t5/21/2113 22:19\t\tPrimary Team\tTT MED TX HEP NP, PGR 26157
-17000\t-6269\t-39\t3/15/2111 11:24\t3/15/2111 11:33\tPrimary Team\tTT MED TX HEP RES A, PGR 25908
-17100\t-9903\t-24\t11/30/2111 5:55\t\tConsulting Service\tTT MED TX HEP RES B, PGR 25909
-17200\t-3857\t-21\t5/17/2113 22:58\t\tPrimary Team\tTT MED TX RENAL, PGR 26500
-17300\t-9724\t-72\t2/24/2110 20:49\t\tPrimary Team\tTT MED TX-HEP, .
-17400\t-7255\t-7\t10/23/2109 14:00\t\tPrimary Team\tTT MED UNIV A1, PGR 25902
-17500\t-8317\t-2\t5/17/2109 21:16\t\tPrimary Team\tTT MED UNIV A2, PGR 12010
-17600\t-1343\t-8\t8/24/2113 7:24\t\tPrimary Team\tTT MED UNIV A3, PGR 26102
-17700\t-7747\t-66\t1/16/2109 16:24\t\tPrimary Team\tTT MED UNIV B1, PGR 25903
-17800\t-6462\t-30\t11/23/2109 19:30\t11/23/2109 20:05\tPrimary Team\tTT MED UNIV B2, PGR 12023
-17900\t-9668\t-62\t9/16/2109 19:42\t9/19/2109 6:30\tPrimary Team\tTT MED UNIV B3, PGR 12869
-18000\t-9725\t-79\t7/28/2109 7:55\t\tPrimary Team\tTT MED UNIV C1, PGR 25906
-18100\t-9956\t-2\t2/10/2109 16:53\t\tPrimary Team\tTT MED UNIV C2, PGR 12087
-18200\t-7732\t-25\t9/7/2113 9:27\t9/8/2113 6:58\tPrimary Team\tTT MED UNIV C3, PGR 26199
-18300\t-5125\t-78\t2/4/2109 21:33\t\tPrimary Intern\tTT MED UNIV D1, PGR 25907
-18400\t-8355\t-50\t5/12/2109 23:58\t\tPrimary Team\tTT MED UNIV D2, PGR 12152
-18500\t-1888\t-80\t5/1/2113 14:52\t5/1/2113 18:49\tPrimary Team\tTT MED UNIV D3, PGR 26302
-18600\t-4768\t-11\t12/18/2113 16:00\t\tPrimary Team\tTT MED UNIV E1, PGR 26400
-18700\t-5946\t-98\t5/4/2113 17:20\t\tPrimary Team\tTT MED UNIV E2, PGR 26401
-18800\t-8631\t-78\t8/8/2113 11:48\t8/9/2113 7:15\tPrimary Team\tTT MED UNIV E3, PGR 26402
-18900\t-6561\t-64\t4/7/2109 8:29\t\tPrimary Team\tTT MED UNIV NON RESI, PGR 12012
-19000\t-6209\t-68\t1/22/2113 19:33\t\tPrimary Team\tTT MED9 NP A, PGR 27093
-19100\t-5810\t-31\t2/8/2113 19:58\t\tPrimary Team\tTT MED9 NP B, PGR 27141
-19200\t-223\t-19\t2/8/2113 12:27\t2/8/2113 19:58\tPrimary Team\tTT MED9 NP C, PGR 27183
-19300\t-1005\t-94\t6/23/2110 19:47\t6/24/2110 18:23\tPrimary Resident\tTT MICU BLUE RESIDENT A -- PGR 27095
-19400\t-6309\t-84\t10/24/2109 13:55\t10/24/2109 16:42\tPrimary Team\tTT MICU BLUE, .
-19500\t-5142\t-63\t7/21/2110 12:02\t7/22/2110 23:16\tPrimary Team\tTT MICU GREEN RESIDENT A -- PGR 27099
-19600\t-7779\t-8\t9/18/2109 20:55\t\tPrimary Team\tTT MICU GREEN, .
-19700\t-2417\t-76\t1/10/2114 20:58\t\tPrimary Team\tTT MINIMALLY INVASIVE SURGERY, PGR 27085
-19800\t-6697\t-4\t3/2/2110 18:52\t\tPrimary Team\tTT NEURO EPILEPSY MONITOR UNIT, .
-19900\t-3038\t-98\t1/19/2114 11:34\t\tPrimary Team\tTT NEURO EPILEPSY MONITOR UNIT, PGR 27086
-20000\t-3672\t-96\t10/16/2113 12:36\t\tPrimary Team\tTT NEURO STROKE RESIDENT A, PGR 27132
-20100\t-3014\t-56\t10/16/2113 6:11\t10/16/2113 12:36\tPrimary Team\tTT NEURO STROKE RESIDENT B, PGR 27133
-20200\t-9587\t-80\t10/15/2113 23:35\t10/16/2113 6:09\tPrimary Team\tTT NEUROLOGY RESIDENT A, PGR 27130
-20300\t-9618\t-81\t7/17/2113 23:38\t7/18/2113 5:48\tPrimary Team\tTT NEUROLOGY RESIDENT B, PGR 27131
-20400\t-7764\t-19\t10/26/2109 18:55\t\tPrimary Team\tTT NEUROLOGY, .
-20500\t-5985\t-40\t3/5/2113 7:32\t\tPrimary Team\tTT NEUROSURGERY A VASCULAR FLOOR, PGR 27134
-20600\t-3920\t-95\t4/15/2113 16:11\t4/15/2113 16:45\tConsulting Service\tTT NEUROSURGERY A VASCULAR ICU, PGR 27128
-20700\t-4463\t-59\t7/18/2110 13:30\t\tPrimary Team\tTT NEUROSURGERY A, .
-20800\t-7556\t-46\t6/18/2113 7:15\t\tPrimary Team\tTT NEUROSURGERY B TUMOR FLOOR, PGR 27135
-20900\t-5245\t-4\t4/27/2113 10:58\t4/28/2113 14:37\tPrimary Team\tTT NEUROSURGERY B TUMOR ICU, PGR 27129
-21000\t-2727\t-85\t3/26/2110 17:57\t\tPrimary Team\tTT NEUROSURGERY B, .
-21100\t-4073\t-25\t12/31/2112 20:55\t1/1/2113 10:05\tConsulting Service\tTT NEUROSURGERY C SPINE FLOOR, PGR 27136
-21200\t-4198\t-90\t5/31/2113 2:58\t6/2/2113 11:23\tConsulting Service\tTT NEUROSURGERY C SPINE ICU, PGR 27158
-21300\t-3735\t-48\t4/23/2110 13:04\t\tPrimary Team\tTT NEUROSURGERY C, .
-21400\t-732\t-41\t8/26/2113 21:00\t8/27/2113 5:24\tConsulting Service\tTT NEUROSURGERY FLOOR, PGR 27136
-21500\t-4812\t-19\t7/11/2113 12:19\t7/13/2113 21:31\tPrimary Team\tTT NEUROSURGERY ICU/RESIDENT ON-CALL, PGR 12019
-21600\t-4812\t-19\t7/6/2110 10:30\t\tPrimary Team\tTT NEUROSURGERY, .
-21700\t-3583\t-41\t11/24/2111 6:46\t\tPrimary Team\tTT OB SAN MATEO COUNTY, .
-21800\t-3229\t-93\t8/1/2113 21:43\t\tPrimary Team\tTT OB UNIVERSITY, .
-21900\t-3229\t-49\t3/26/2113 7:19\t3/26/2113 8:33\tPrimary Team\tTT ONCOLOGY NP, PGR 14038
-22000\t-6011\t-37\t7/1/2113 13:34\t7/3/2113 7:22\tPrimary Team\tTT ONCOLOGY RESIDENT A, PGR 27138
-22100\t-305\t-43\t1/14/2114 7:37\t\tPrimary Team\tTT ONCOLOGY RESIDENT B, PGR 27139
-22200\t-5666\t-98\t4/6/2113 7:24\t4/6/2113 7:24\tPrimary Team\tTT ONCOLOGY RESIDENT C, PGR 27140
-22300\t-9992\t-35\t12/3/2109 8:10\t\tPrimary Team\tTT ONCOLOGY, .
-22400\t-8288\t-32\t10/5/2113 12:01\t\tPrimary Team\tTT OPHTHALMOLOGY, .
-22500\t-7739\t-47\t9/12/2113 8:23\t\tPrimary Team\tTT ORTHO ARTHRITIS (JOINT), PGR 27143
-22600\t-9491\t-39\t1/22/2110 14:51\t\tPrimary Team\tTT ORTHO FOOT & ANKLE, .
-22700\t-4602\t-91\t12/22/2113 9:09\t\tPrimary Team\tTT ORTHO FOOT/ANKLE, PGR 27147
-22800\t-7546\t-78\t8/27/2113 0:41\t\tConsulting Service\tTT ORTHO HAND, PGR 27149
-22900\t-1266\t-66\t3/8/2111 7:32\t\tPrimary Team\tTT ORTHO JOINT, .
-23000\t-2426\t-46\t9/23/2113 16:34\t\tPrimary Team\tTT ORTHO ONCOLOGY, PGR 27145
-23100\t-2837\t-81\t1/23/2114 6:37\t\tPrimary Team\tTT ORTHO SHOULDER/ELBOW, PGR 27146
-23200\t-1365\t-79\t10/25/2109 22:02\t\tPrimary Team\tTT ORTHO SPINE, .
-23300\t-7799\t-15\t10/14/2113 18:11\t\tPrimary Team\tTT ORTHO SPINE, PGR 27144
-23400\t-8843\t-96\t9/4/2113 7:50\t\tPrimary Team\tTT ORTHO SPORTS, PGR 27148
-23500\t-6483\t-28\t5/9/2110 5:29\t\tPrimary Team\tTT ORTHO SURGERY, .
-23600\t-6483\t-28\t11/7/2111 8:57\t11/8/2111 7:07\tPrimary Team\tTT ORTHO TRAUMA, .
-23700\t-6483\t-28\t12/27/2113 5:02\t\tPrimary Team\tTT ORTHO TRAUMA, PGR 27156
-23800\t-6483\t-28\t4/4/2110 19:33\t\tPrimary Team\tTT ORTHO TUMOR, .
-23900\t-6434\t-31\t6/3/2111 17:15\t\tPrimary Team\tTT PAIN RESIDENT 2 -- PGR 27151
-24000\t-1874\t-70\t4/10/2110 12:17\t\tPrimary Team\tTT PAIN, .
-24100\t-9149\t-90\t4/26/2113 5:27\t4/26/2113 5:27\tPrimary Team\tTT PAMF (GEN SURG) ATTENDING ONLY, 321-4121
-24200\t-4935\t-32\t9/7/2113 7:38\t\tPrimary Team\tTT PAMF (NEUROSURG) ATTENDING ONLY, 321-4121
-24300\t-4935\t-32\t5/9/2109 7:30\t\tPrimary Team\tTT PAMF MED 1, PGR 23431
-24400\t-4935\t-32\t7/28/2109 8:05\t\tPrimary Team\tTT PAMF MED 2, PGR 23432
-24500\t-4550\t-62\t6/10/2109 23:47\t\tPrimary Team\tTT PAMF MED 3, PGR 23433
-24600\t-4550\t-62\t4/16/2113 7:00\t4/18/2113 7:00\tPrimary Team\tTT PAMF MED 4, PGR 23434
-24700\t-3954\t-61\t4/18/2113 7:00\t\tPrimary Team\tTT PAMF MED 5, PGR 23535
-24800\t-3954\t-61\t11/8/2113 13:52\t11/9/2113 6:00\tPrimary Team\tTT PAMF MED 6, PRG 23616
-24900\t-3954\t-61\t4/1/2113 7:00\t4/2/2113 7:47\tPrimary Team\tTT PAMF MED/CARDS ADMITTING, PGR 25900
-25000\t-3954\t-61\t3/7/2113 9:13\t\tPrimary Team\tTT PAMF(ENT) ATTENDING ONLY, 321-4121
-25100\t-3954\t-61\t2/17/2112 15:44\t\tPrimary Team\tTT PAMF(EP)  ATTENDING ONLY, 321-4121
-25200\t-1614\t-42\t9/11/2113 13:52\t\tPrimary Team\tTT PAMF(ORTHO) ATTENDING ONLY, 321-4121
-25300\t-1614\t-42\t9/2/2113 13:00\t\tPrimary Team\tTT PAMF(PLASTICS) ATTENDING ONLY, 321-4121
-25400\t-1614\t-42\t9/4/2113 13:59\t\tPrimary Team\tTT PAMF(UROLOGY) ATTENDING ONLY, 321-4121
-25500\t-1614\t-42\t1/6/2113 0:14\t1/6/2113 0:16\tPrimary Team\tTT PHYSICAL MED & REHAB, .
-25600\t-6234\t-95\t11/9/2113 20:33\t\tConsulting Service\tTT PLASTIC SURGERY CONSULTS, PGR 27154
-25700\t-900\t-45\t6/27/2111 9:34\t6/27/2111 10:59\tPrimary Team\tTT PLASTIC SURGERY, .
-25800\t-6187\t-3\t11/26/2113 9:40\t\tPrimary Team\tTT PLASTIC SURGERY, PGR 27153
-25900\t-1471\t-23\t4/14/2113 18:43\t\tConsulting Service\tTT PSYCHIATRY, .
-26000\t-9067\t-86\t10/29/2113 21:18\t\tPrimary Team\tTT PULM HTN A, PGR 25905
-26100\t-292\t-42\t1/24/2113 20:01\t1/24/2113 20:01\tPrimary Team\tTT PULM HTN B, PGR 27074
-26200\t-5490\t-12\t12/26/2111 14:41\t\tPrimary Team\tTT PULMONARY TRANSPLANT, .
-26300\t-577\t-64\t10/2/2109 19:07\t10/4/2109 11:33\tConsulting Service\tTT SICU, .
-26400\t-2476\t-94\t4/10/2113 18:41\t\tPrimary Team\tTT SURGICAL ONCOLOGY 1, PGR 12076
-26500\t-7826\t-60\t4/21/2113 1:06\t\tPrimary Team\tTT SURGICAL ONCOLOGY 2, PGR 27084
-26600\t-8138\t-95\t2/19/2110 0:37\t\tConsulting Service\tTT UROLOGY, .
-26700\t-8302\t-86\t8/26/2113 9:09\t\tPrimary Team\tTT UROLOGY, PGR 27155
-26800\t-8694\t-68\t11/6/2113 7:54\t\tPrimary Team\tTT VAD, PGR 12502
-26900\t-6011\t-84\t4/23/2113 5:59\t4/23/2113 10:29\tConsulting Service\tTT VASCULAR SURGERY, PGR 12166
"""
        # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "stride_treatment_team", delim="\t", dateColFormats={"trtmnt_tm_begin_date": None, "trtmnt_tm_end_date": None} );

        self.converter = STRIDETreatmentTeamConversion();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute \
        (   """delete from patient_item 
            where clinical_item_id in 
            (   select clinical_item_id
                from clinical_item as ci, clinical_item_category as cic
                where ci.clinical_item_category_id = cic.clinical_item_category_id
                and cic.source_table = 'stride_treatment_team'
            );
            """
        );
        DBUtil.execute \
        (   """delete from clinical_item 
            where clinical_item_category_id in 
            (   select clinical_item_category_id 
                from clinical_item_category 
                where source_table = 'stride_treatment_team'
            );
            """
        );
        DBUtil.execute("delete from clinical_item_category where source_table = 'stride_treatment_team';");

        DBUtil.execute("delete from stride_treatment_team where stride_treatment_team_id < 0");

        DBTestCase.tearDown(self);

    def test_dataConversion(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...");
        convOptions = ConversionOptions();
        convOptions.startDate = TEST_START_DATE;
        self.converter.convertSourceItems(convOptions);

        # Just query back for the same data, de-normalizing the data back to a general table
        testQuery = \
            """
            select 
                pi.external_id,
                pi.patient_id,
                pi.encounter_id,
                cic.description,
                ci.external_id,
                ci.name,
                ci.description,
                pi.item_date
            from
                patient_item as pi,
                clinical_item as ci,
                clinical_item_category as cic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = 'stride_treatment_team'
            order by
                pi.external_id desc, ci.external_id desc
            """;
        expectedData = \
            [   
[-200, -117, 0, "Treatment Team", None, "ACP", "Additional Communicating Provider", DBUtil.parseDateValue("10/5/2113 23:18"),],
[-300, -4845, -60, "Treatment Team", None, "CC", "Care Coordinator", DBUtil.parseDateValue("6/26/2113 8:11"),],
[-400, -9194, -26, "Treatment Team", None, "CM", "Case Manager", DBUtil.parseDateValue("4/11/2109 8:39"),],
[-500, -9519, -69, "Treatment Team", None, "CR", "Chief Resident", DBUtil.parseDateValue("3/19/2113 12:10"),],
[-600, -8702, -77, "Treatment Team", None, "CD", "Clinical Dietician", DBUtil.parseDateValue("4/10/2109 8:45"),],
[-700, -8307, -92, "Treatment Team", None, "C", "Co-Attending", DBUtil.parseDateValue("7/9/2113 0:21"),],
[-800, -5474, -78, "Treatment Team", None, "CA", "Consulting Attending", DBUtil.parseDateValue("12/4/2113 9:47"),],
[-900, -6015, -47, "Treatment Team", None, "CF", "Consulting Fellow", DBUtil.parseDateValue("7/24/2113 2:29"),],
[-1000, -3733, -39, "Treatment Team", None, "CI", "Consulting Intern", DBUtil.parseDateValue("7/9/2113 8:04"),],
[-1100, -9597, -78, "Treatment Team", None, "CMS", "Consulting Med Student", DBUtil.parseDateValue("10/12/2109 18:48"),],
[-1200, -1087, -18, "Treatment Team", None, "CR", "Consulting Resident", DBUtil.parseDateValue("1/14/2109 23:12"),],
[-1300, -6467, -14, "Treatment Team", None, "CS", "Consulting Service", DBUtil.parseDateValue("4/10/2109 11:55"),],
[-1400, -1291, -70, "Treatment Team", None, "DI", "Dietician Intern", DBUtil.parseDateValue("12/31/2111 10:35"),],
[-1500, -5038, -91, "Treatment Team", None, "ER", "ED Registrar", DBUtil.parseDateValue("9/12/2112 18:04"),],
[-1600, -8055, -77, "Treatment Team", None, "ET", "ED Tech", DBUtil.parseDateValue("5/4/2110 9:35"),],
[-1700, -2531, -12, "Treatment Team", None, "EUS", "ED Unit Secretary", DBUtil.parseDateValue("5/8/2110 14:50"),],
[-1800, -54, -14, "Treatment Team", None, "ER", "Emergency Resident", DBUtil.parseDateValue("10/23/2109 11:51"),],
[-1900, -6763, -25, "Treatment Team", None, "LVN", "Licensed Vocational Nurse", DBUtil.parseDateValue("5/7/2110 5:29"),],
[-2000, -5668, -56, "Treatment Team", None, "MA", "Medical Assistant", DBUtil.parseDateValue("9/30/2109 12:58"),],
[-2100, -5862, -78, "Treatment Team", None, "NC", "Nurse Coordinator", DBUtil.parseDateValue("3/22/2113 18:54"),],
[-2200, -4060, -97, "Treatment Team", None, "NP", "Nurse Practitioner", DBUtil.parseDateValue("1/1/2113 16:50"),],
[-2300, -7217, -45, "Treatment Team", None, "NA", "Nursing Assistant", DBUtil.parseDateValue("4/27/2110 7:30"),],
[-2400, -4026, -44, "Treatment Team", None, "OT", "Occupational Therapist", DBUtil.parseDateValue("4/12/2109 16:13"),],
[-2500, -8387, -39, "Treatment Team", None, "PT", "Physical Therapist", DBUtil.parseDateValue("4/14/2109 12:09"),],
[-2600, -2160, -42, "Treatment Team", None, "PTA", "Physical Therapist Assistant", DBUtil.parseDateValue("9/15/2113 9:46"),],
[-2700, -3237, -81, "Treatment Team", None, "PA", "Physician\'s Assistant", DBUtil.parseDateValue("1/17/2113 17:49"),],
[-2800, -7645, -88, "Treatment Team", None, "PF", "Primary Fellow", DBUtil.parseDateValue("10/19/2109 16:41"),],
[-2900, -448, -56, "Treatment Team", None, "PI", "Primary Intern", DBUtil.parseDateValue("10/24/2109 12:11"),],
[-3000, -5832, -51, "Treatment Team", None, "PMS", "Primary Med Student", DBUtil.parseDateValue("9/30/2109 12:59"),],
[-3100, -3983, -19, "Treatment Team", None, "PPA", "Primary Physician Assistant", DBUtil.parseDateValue("4/21/2110 12:15"),],
[-3200, -1547, -42, "Treatment Team", None, "PR", "Primary Resident", DBUtil.parseDateValue("10/24/2109 12:11"),],
[-3300, -6251, -4, "Treatment Team", None, "PS", "Primary Sub-Intern", DBUtil.parseDateValue("9/16/2109 19:31"),],
[-3400, -1328, -59, "Treatment Team", None, "PT", "Primary Team", DBUtil.parseDateValue("10/24/2109 13:55"),],
[-3500, -6209, -50, "Treatment Team", None, "P", "Psychologist", DBUtil.parseDateValue("8/6/2113 10:16"),],
[-3600, -8067, -95, "Treatment Team", None, "RN", "Registered Nurse", DBUtil.parseDateValue("10/18/2109 6:47"),],
[-3700, -9956, -50, "Treatment Team", None, "RCP", "Respiratory Care Practitioner", DBUtil.parseDateValue("10/17/2109 7:49"),],
[-3800, -4057, -8, "Treatment Team", None, "SW", "Social Worker", DBUtil.parseDateValue("11/9/2109 16:23"),],
[-3900, -8424, -44, "Treatment Team", None, "ST", "Speech Therapist", DBUtil.parseDateValue("11/22/2109 7:58"),],
[-4000, -6271, -78, "Treatment Team", None, "SC", "Spiritual Care", DBUtil.parseDateValue("4/6/2113 15:00"),],
[-4100, -3251, -79, "Treatment Team", None, "SN", "Student Nurse", DBUtil.parseDateValue("9/11/2113 13:34"),],
[-4200, -79, -74, "Treatment Team", None, "TA", "Trauma Attending", DBUtil.parseDateValue("3/1/2113 15:36"),],
[-4300, -6671, -77, "Treatment Team", None, "TR", "Trauma Resident", DBUtil.parseDateValue("9/26/2113 6:28"),],
[-4400, -9911, -27, "Treatment Team", None, "TN", "Triage Nurse", DBUtil.parseDateValue("11/1/2111 6:58"),],
[-4500, -4550, -58, "Treatment Team", None, "CCIC (CS)", "Con Card Interven/Ami Consult (Consulting Service)", DBUtil.parseDateValue("7/4/2113 21:35"),],
[-4600, -1959, -90, "Treatment Team", None, "CCS (CS)", "Con Cardiac Surgery (Consulting Service)", DBUtil.parseDateValue("12/26/2113 9:38"),],
[-4700, -6120, -19, "Treatment Team", None, "CCA (CF)", "Con Cardiol Arrhythmia (Consulting Fellow)", DBUtil.parseDateValue("11/17/2113 11:39"),],
[-4800, -9620, -14, "Treatment Team", None, "CCT (PT)", "Con Cardiol Transplant (Primary Team)", DBUtil.parseDateValue("5/10/2113 9:42"),],
[-4900, -7389, -82, "Treatment Team", None, "CC (CS)", "Con Cardiology (Consulting Service)", DBUtil.parseDateValue("11/9/2109 13:58"),],
[-5000, -2570, -34, "Treatment Team", None, "CCS (PT)", "Con Cardiothroacic Surgery (Primary Team)", DBUtil.parseDateValue("3/18/2111 9:34"),],
[-5100, -8843, -96, "Treatment Team", None, "CCS (PT)", "Con Colorectal Surgery (Primary Team)", DBUtil.parseDateValue("3/1/2113 7:50"),],
[-5200, -9515, -31, "Treatment Team", None, "CCFA (PT)", "Con Cystic Fibrosis Adult (Primary Team)", DBUtil.parseDateValue("1/22/2114 19:09"),],
[-5300, -2229, -86, "Treatment Team", None, "CE (CS)", "Con Endocrinology (Consulting Service)", DBUtil.parseDateValue("12/21/2113 16:26"),],
[-5400, -9149, -90, "Treatment Team", None, "CG (CS)", "Con Gastroenterology (Consulting Service)", DBUtil.parseDateValue("6/21/2113 6:42"),],
[-5500, -4935, -32, "Treatment Team", None, "CGS (PT)", "Con General Surgery (Primary Team)", DBUtil.parseDateValue("8/18/2110 3:51"),],
[-5600, -4935, -32, "Treatment Team", None, "CG (CS)", "Con Geriatrics (Consulting Service)", DBUtil.parseDateValue("5/31/2111 14:39"),],
[-5700, -4550, -62, "Treatment Team", None, "CG (CS)", "Con Gynecology (Consulting Service)", DBUtil.parseDateValue("10/18/2111 20:15"),],
[-5800, -3954, -61, "Treatment Team", None, "CHS (CS)", "Con Hand Surgery (Consulting Service)", DBUtil.parseDateValue("3/8/2111 8:05"),],
[-5900, -7078, -76, "Treatment Team", None, "CH (CS)", "Con Hematology (Consulting Service)", DBUtil.parseDateValue("11/8/2113 9:51"),],
[-6000, -4568, -1, "Treatment Team", None, "CH (CS)", "Con Hepatology (Consulting Service)", DBUtil.parseDateValue("5/6/2113 14:41"),],
[-6100, -4568, -42, "Treatment Team", None, "CI (CR)", "Con Icu (Consulting Resident)", DBUtil.parseDateValue("1/21/2113 14:01"),],
[-6200, -4568, -82, "Treatment Team", None, "CID (CS)", "Con Inf Dis (Consulting Service)", DBUtil.parseDateValue("1/27/2114 11:20"),],
[-6300, -8539, -33, "Treatment Team", None, "CIDI (CS)", "Con Inf Dis Immunocomp (Consulting Service)", DBUtil.parseDateValue("1/8/2112 8:59"),],
[-6400, -1543, -19, "Treatment Team", None, "CIDPC (CS)", "Con Inf Dis Postitive Care (Consulting Service)", DBUtil.parseDateValue("5/29/2110 12:57"),],
[-6500, -1543, -19, "Treatment Team", None, "CIMC (CS)", "Con Internal Medicine Consult (Consulting Service)", DBUtil.parseDateValue("4/21/2113 11:27"),],
[-6600, -1543, -19, "Treatment Team", None, "CIR (CS)", "Con Intervent Rad (Consulting Service)", DBUtil.parseDateValue("7/21/2112 4:03"),],
[-6700, -4464, -14, "Treatment Team", None, "CKT (CS)", "Con Kidney Transplant (Consulting Service)", DBUtil.parseDateValue("8/15/2113 0:11"),],
[-6800, -4464, -42, "Treatment Team", None, "CLT (PT)", "Con Liver Transplant (Primary Team)", DBUtil.parseDateValue("1/10/2113 8:33"),],
[-6900, -4464, -22, "Treatment Team", None, "CMG (CS)", "Con Medical Genetics (Consulting Service)", DBUtil.parseDateValue("9/5/2112 13:22"),],
[-7000, -9840, -68, "Treatment Team", None, "CM (CS)", "Con Medicine (Consulting Service)", DBUtil.parseDateValue("9/27/2109 16:51"),],
[-7100, -9840, -68, "Treatment Team", None, "CMAR (CS)", "Con Micu Admission Request (Consulting Service)", DBUtil.parseDateValue("4/23/2113 12:42"),],
[-7200, -4392, -98, "Treatment Team", None, "CMC (CS)", "Con Micu Consult (Consulting Service)", DBUtil.parseDateValue("8/14/2113 23:16"),],
[-7300, -394, -11, "Treatment Team", None, "CN (CS)", "Con Nephrology (Consulting Service)", DBUtil.parseDateValue("9/17/2109 10:46"),],
[-7400, -7389, -82, "Treatment Team", None, "CNT (CS)", "Con Nephrology Transplant (Consulting Service)", DBUtil.parseDateValue("10/19/2109 2:06"),],
[-7500, -5689, -19, "Treatment Team", None, "CNEC (CS)", "Con Neuro Endocrine Consult (Consulting Service)", DBUtil.parseDateValue("12/4/2110 17:36"),],
[-7600, -714, -33, "Treatment Team", None, "CNEC (CS)", "Con Neuro Epilepsy Consult (Consulting Service)", DBUtil.parseDateValue("12/11/2113 1:07"),],
[-7700, -1464, -53, "Treatment Team", None, "CNI (CS)", "Con Neuro Icu (Consulting Service)", DBUtil.parseDateValue("10/8/2109 12:20"),],
[-7800, -3115, -69, "Treatment Team", None, "CNI (CS)", "Con Neuro Ir (Consulting Service)", DBUtil.parseDateValue("7/25/2112 21:44"),],
[-7900, -7516, -84, "Treatment Team", None, "CNO (CR)", "Con Neuro Oncology (Consulting Resident)", DBUtil.parseDateValue("11/23/2112 12:00"),],
[-8000, -9726, -91, "Treatment Team", None, "CNS (PT)", "Con Neuro Stroke (Primary Team)", DBUtil.parseDateValue("7/15/2109 22:20"),],
[-8100, -9726, -91, "Treatment Team", None, "CNG (CS)", "Con Neurology General (Consulting Service)", DBUtil.parseDateValue("7/27/2109 21:42"),],
[-8200, -3961, -74, "Treatment Team", None, "CN (PT)", "Con Neurosurgery (Primary Team)", DBUtil.parseDateValue("4/10/2111 7:51"),],
[-8300, -4087, -54, "Treatment Team", None, "CO (CS)", "Con Obstetrics (Consulting Service)", DBUtil.parseDateValue("8/2/2110 1:54"),],
[-8400, -1266, -12, "Treatment Team", None, "CO (CS)", "Con Oncology (Consulting Service)", DBUtil.parseDateValue("12/24/2113 10:19"),],
[-8500, -2289, -68, "Treatment Team", None, "CO (CS)", "Con Ophthalmology (Consulting Service)", DBUtil.parseDateValue("6/21/2113 0:27"),],
[-8600, -2591, -79, "Treatment Team", None, "CO (CS)", "Con Orthopedics (Consulting Service)", DBUtil.parseDateValue("1/19/2112 12:15"),],
[-8700, -6762, -49, "Treatment Team", None, "COH (CS)", "Con Orthopedics Hospitalist (Consulting Service)", DBUtil.parseDateValue("12/3/2113 5:00"),],
[-8800, -6762, -59, "Treatment Team", None, "CP (CS)", "Con Pain (Consulting Service)", DBUtil.parseDateValue("4/10/2109 11:55"),],
[-8900, -211, -87, "Treatment Team", None, "CPC (CS)", "Con Palliative Care (Consulting Service)", DBUtil.parseDateValue("9/24/2113 10:15"),],
[-9000, -7621, -85, "Treatment Team", None, "CPM (CS)", "Con Pamf Medicine (Consulting Service)", DBUtil.parseDateValue("4/30/2113 6:49"),],
[-9100, -3251, -49, "Treatment Team", None, "CPC (CS)", "Con Primary Care (Consulting Service)", DBUtil.parseDateValue("6/14/2113 19:49"),],
[-9200, -2837, -81, "Treatment Team", None, "CP (CS)", "Con Psychiatry (Consulting Service)", DBUtil.parseDateValue("1/19/2112 11:25"),],
[-9300, -2837, -42, "Treatment Team", None, "CPH (CS)", "Con Pulm Hypertension (Consulting Service)", DBUtil.parseDateValue("10/23/2113 11:54"),],
[-9400, -2837, -42, "Treatment Team", None, "CPT (PT)", "Con Pulm Transplant (Primary Team)", DBUtil.parseDateValue("8/9/2113 19:48"),],
[-9500, -2837, -42, "Treatment Team", None, "CP (CS)", "Con Pulmonary (Consulting Service)", DBUtil.parseDateValue("11/4/2113 7:03"),],
[-9600, -4295, -35, "Treatment Team", None, "CPRC (CS)", "Con Pulmonary Rehab Consult (Consulting Service)", DBUtil.parseDateValue("10/4/2113 9:36"),],
[-9700, -3433, -44, "Treatment Team", None, "CR (CS)", "Con Rheumatology (Consulting Service)", DBUtil.parseDateValue("10/19/2112 9:31"),],
[-9800, -7612, -25, "Treatment Team", None, "CST (CS)", "Con Spine Trauma (Consulting Service)", DBUtil.parseDateValue("10/13/2111 18:11"),],
[-9900, -4875, -51, "Treatment Team", None, "CTS (CS)", "Con Thoracic Surgery (Consulting Service)", DBUtil.parseDateValue("8/28/2113 21:14"),],
[-10000, -8813, -79, "Treatment Team", None, "CTS (PT)", "Con Transplant Surgery (Primary Team)", DBUtil.parseDateValue("3/26/2113 20:26"),],
[-10100, -8813, -79, "Treatment Team", None, "CU (CS)", "Con Urology (Consulting Service)", DBUtil.parseDateValue("5/7/2112 10:35"),],
[-10200, -8720, -72, "Treatment Team", None, "CVS (CS)", "Con Vascular Surgery (Consulting Service)", DBUtil.parseDateValue("1/14/2114 16:49"),],
[-10300, -8720, -72, "Treatment Team", None, "TACST (PT)", "Tt Acute Care Surgery Trauma (Primary Team)", DBUtil.parseDateValue("11/30/2109 18:16"),],
[-10400, -1365, -79, "Treatment Team", None, "TAP2 (CS)", "Tt Acute Pain 2Pain (Consulting Service)", DBUtil.parseDateValue("12/21/2113 9:19"),],
[-10500, -1365, -79, "Treatment Team", None, "TBTB (PT)", "Tt Bmt T2 (Bmt) (Primary Team)", DBUtil.parseDateValue("10/22/2113 7:58"),],
[-10600, -8712, -95, "Treatment Team", None, "TB (PT)", "Tt Bmt (Primary Team)", DBUtil.parseDateValue("9/13/2111 16:27"),],
[-10700, -7799, -15, "Treatment Team", None, "TB (PT)", "Tt Bmt (Primary Team)", DBUtil.parseDateValue("7/11/2113 15:47"),],
[-10800, -2552, -30, "Treatment Team", None, "TBS (CS)", "Tt Breast Surgery (Consulting Service)", DBUtil.parseDateValue("11/21/2113 19:15"),],
[-10900, -3644, -25, "Treatment Team", None, "TCBA (PT)", "Tt Cardiac Blue Adult (Primary Team)", DBUtil.parseDateValue("1/19/2113 13:25"),],
[-11000, -3644, -1, "Treatment Team", None, "TCGA (PT)", "Tt Cardiac Green Adult (Primary Team)", DBUtil.parseDateValue("1/31/2113 8:25"),],
[-11100, -7289, -58, "Treatment Team", None, "TC5 (PT)", "Tt Cardiology 5A (Primary Team)", DBUtil.parseDateValue("9/1/2109 15:16"),],
[-11200, -8843, -96, "Treatment Team", None, "TC5 (PT)", "Tt Cardiology 5B (Primary Team)", DBUtil.parseDateValue("11/1/2109 7:02"),],
[-11300, -9515, -31, "Treatment Team", None, "TC6 (PT)", "Tt Cardiology 6A (Primary Team)", DBUtil.parseDateValue("1/15/2110 20:02"),],
[-11400, -394, -58, "Treatment Team", None, "TC6I (PT)", "Tt Cardiology 6B Intern (Primary Team)", DBUtil.parseDateValue("12/30/2110 17:29"),],
[-11500, -7987, -69, "Treatment Team", None, "TC6 (PT)", "Tt Cardiology 6B (Primary Team)", DBUtil.parseDateValue("5/25/2110 13:56"),],
[-11600, -2446, -72, "Treatment Team", None, "TCA (PT)", "Tt Cardiology Arrhythmia (Primary Team)", DBUtil.parseDateValue("10/21/2111 7:25"),],
[-11700, -3127, -94, "Treatment Team", None, "TCEA (PT)", "Tt Cardiology Ep A (Primary Team)", DBUtil.parseDateValue("2/24/2113 17:11"),],
[-11800, -8832, -55, "Treatment Team", None, "TCEB (PT)", "Tt Cardiology Ep B (Primary Team)", DBUtil.parseDateValue("6/5/2113 16:51"),],
[-11900, -1826, -61, "Treatment Team", None, "TCI (PR)", "Tt Cardiology Interventional (Primary Resident)", DBUtil.parseDateValue("7/19/2110 15:03"),],
[-12000, -345, -8, "Treatment Team", None, "TC1 (PT)", "Tt Ccu/Hf 1 (Primary Team)", DBUtil.parseDateValue("2/26/2113 5:24"),],
[-12100, -6351, -89, "Treatment Team", None, "TC2 (PT)", "Tt Ccu/Hf 2 (Primary Team)", DBUtil.parseDateValue("5/21/2113 6:10"),],
[-12200, -1851, -54, "Treatment Team", None, "TC3 (PT)", "Tt Ccu/Hf 3 (Primary Team)", DBUtil.parseDateValue("1/23/2113 23:16"),],
[-12300, -5563, -18, "Treatment Team", None, "TC4 (PT)", "Tt Ccu/Hf 4 (Primary Team)", DBUtil.parseDateValue("4/21/2113 7:47"),],
[-12400, -5752, -91, "Treatment Team", None, "TCM (PT)", "Tt Chris Mow (Primary Team)", DBUtil.parseDateValue("12/25/2113 9:33"),],
[-12500, -7881, -71, "Treatment Team", None, "TCP (CS)", "Tt Chronic Pain (Consulting Service)", DBUtil.parseDateValue("6/17/2113 13:43"),],
[-12600, -7881, -71, "Treatment Team", None, "TCS (PT)", "Tt Colorectal Surgery (Primary Team)", DBUtil.parseDateValue("12/2/2113 8:39"),],
[-12700, -7881, -16, "Treatment Team", None, "TCS (PT)", "Tt Craniofacial Surgery (Primary Team)", DBUtil.parseDateValue("7/23/2113 16:27"),],
[-12800, -2270, -17, "Treatment Team", None, "TCT1 (PT)", "Tt Cvicu Team 1 (Primary Team)", DBUtil.parseDateValue("6/30/2109 15:23"),],
[-12900, -9149, -90, "Treatment Team", None, "TCFA (PT)", "Tt Cystic Fibrosis Adult (Primary Team)", DBUtil.parseDateValue("4/21/2110 11:25"),],
[-13000, -4935, -32, "Treatment Team", None, "TCFA (PT)", "Tt Cystic Fibrosis Adult (Primary Team)", DBUtil.parseDateValue("9/26/2113 19:44"),],
[-13100, -4935, -32, "Treatment Team", None, "TEHAN (PT)", "Tt Ent Head And Neck (Primary Team)", DBUtil.parseDateValue("10/23/2113 15:06"),],
[-13200, -4935, -32, "Treatment Team", None, "TEHN (PT)", "Tt Ent Head Neck (Primary Team)", DBUtil.parseDateValue("5/17/2110 8:38"),],
[-13300, -4935, -32, "Treatment Team", None, "TES (CS)", "Tt Ent Specialty (Consulting Service)", DBUtil.parseDateValue("5/12/2110 8:58"),],
[-13400, -4540, -63, "Treatment Team", None, "TES (CS)", "Tt Ent Specialty (Consulting Service)", DBUtil.parseDateValue("7/11/2113 18:25"),],
[-13500, -1614, -42, "Treatment Team", None, "TGC1 (PT)", "Tt Gen Cards 1 (Primary Team)", DBUtil.parseDateValue("3/21/2113 19:53"),],
[-13600, -1614, -42, "Treatment Team", None, "TGC2 (PT)", "Tt Gen Cards 2 (Primary Team)", DBUtil.parseDateValue("4/23/2113 7:23"),],
[-13700, -6824, -84, "Treatment Team", None, "TGC3 (PT)", "Tt Gen Cards 3 (Primary Team)", DBUtil.parseDateValue("5/12/2113 7:15"),],
[-13800, -3034, -56, "Treatment Team", None, "TGSG (PT)", "Tt Gen Surg Gold (Primary Team)", DBUtil.parseDateValue("5/9/2109 6:17"),],
[-13900, -7232, -51, "Treatment Team", None, "TGSR (PT)", "Tt Gen Surg Red (Primary Team)", DBUtil.parseDateValue("8/21/2109 8:03"),],
[-14000, -4596, -16, "Treatment Team", None, "TGSW (CS)", "Tt Gen Surg White (Consulting Service)", DBUtil.parseDateValue("8/21/2109 17:27"),],
[-14100, -9210, 0, "Treatment Team", None, "TGT (CS)", "Tt General Thoracic (Consulting Service)", DBUtil.parseDateValue("11/8/2113 11:28"),],
[-14200, -7584, -48, "Treatment Team", None, "TGO (PT)", "Tt Gyn Onc (Primary Team)", DBUtil.parseDateValue("3/29/2110 18:12"),],
[-14300, -5374, -7, "Treatment Team", None, "TGO (PT)", "Tt Gyn Onc (Primary Team)", DBUtil.parseDateValue("8/6/2113 5:24"),],
[-14400, -4331, -81, "Treatment Team", None, "TGP (PT)", "Tt Gyn Private (Primary Team)", DBUtil.parseDateValue("5/1/2113 9:40"),],
[-14500, -8523, -99, "Treatment Team", None, "TGU (PT)", "Tt Gyn Univ (Primary Team)", DBUtil.parseDateValue("10/22/2113 7:25"),],
[-14600, -3827, -55, "Treatment Team", None, "THS (PT)", "Tt Hand Surgery (Primary Team)", DBUtil.parseDateValue("8/13/2110 1:56"),],
[-14700, -7066, -8, "Treatment Team", None, "THLT (PT)", "Tt Heart Lung Transplant (Primary Team)", DBUtil.parseDateValue("3/1/2110 15:32"),],
[-14800, -8127, -22, "Treatment Team", None, "THT (PT)", "Tt Heart Transplant/Vad (Primary Team)", DBUtil.parseDateValue("6/28/2111 7:15"),],
[-14900, -4146, -27, "Treatment Team", None, "THS (PT)", "Tt Hearttransplant Surgery (Primary Team)", DBUtil.parseDateValue("6/23/2113 7:53"),],
[-15000, -8501, -58, "Treatment Team", None, "THNA (PT)", "Tt Hematology Np A (Primary Team)", DBUtil.parseDateValue("5/23/2113 6:47"),],
[-15100, -8961, -39, "Treatment Team", None, "THRA (PT)", "Tt Hematology Resident A (Primary Team)", DBUtil.parseDateValue("4/28/2113 11:10"),],
[-15200, -3215, -96, "Treatment Team", None, "THRB (PT)", "Tt Hematology Resident B (Primary Team)", DBUtil.parseDateValue("4/27/2113 7:08"),],
[-15300, -5112, -25, "Treatment Team", None, "THRC (PT)", "Tt Hematology Resident C (Primary Team)", DBUtil.parseDateValue("4/29/2113 6:58"),],
[-15400, -4659, -77, "Treatment Team", None, "TH (CS)", "Tt Hematology (Consulting Service)", DBUtil.parseDateValue("5/21/2110 15:36"),],
[-15500, -8230, -95, "Treatment Team", None, "THS (PT)", "Tt Hpb Surgery (Primary Team)", DBUtil.parseDateValue("8/1/2113 11:37"),],
[-15600, -4122, -28, "Treatment Team", None, "TIR (CS)", "Tt Interventional Radiology (Consulting Service)", DBUtil.parseDateValue("10/1/2109 15:49"),],
[-15700, -8600, -91, "Treatment Team", None, "TIR2 (CS)", "Tt Interventional Radiology 2Rads (Consulting Service)", DBUtil.parseDateValue("8/26/2113 21:35"),],
[-15800, -5557, -37, "Treatment Team", None, "TKPT (PT)", "Tt Kidney Pancreas Transplant (Primary Team)", DBUtil.parseDateValue("10/19/2109 16:41"),],
[-15900, -2062, -5, "Treatment Team", None, "TLT (PT)", "Tt Liver Transplant (Primary Team)", DBUtil.parseDateValue("3/26/2113 0:09"),],
[-16000, -5394, -95, "Treatment Team", None, "TLT (PT)", "Tt Lung Transplant (Primary Team)", DBUtil.parseDateValue("12/6/2113 16:18"),],
[-16100, -3498, -87, "Treatment Team", None, "TMN (PT)", "Tt Med Nocturnist (Primary Team)", DBUtil.parseDateValue("12/8/2113 22:31"),],
[-16200, -2935, -68, "Treatment Team", None, "TMPNR (PT)", "Tt Med Pamf Non Resi (Primary Team)", DBUtil.parseDateValue("4/18/2111 18:49"),],
[-16300, -12, -58, "Treatment Team", None, "TMTH (PT)", "Tt Med Team H1 (Primary Team)", DBUtil.parseDateValue("10/21/2112 21:48"),],
[-16400, -1078, -22, "Treatment Team", None, "TMTH (CS)", "Tt Med Team H2 (Consulting Service)", DBUtil.parseDateValue("6/30/2111 13:55"),],
[-16500, -6187, -96, "Treatment Team", None, "TMTCA (PT)", "Tt Med Tx Cards A (Primary Team)", DBUtil.parseDateValue("11/15/2113 15:20"),],
[-16600, -3081, -86, "Treatment Team", None, "TMTCB (PT)", "Tt Med Tx Cards B (Primary Team)", DBUtil.parseDateValue("12/14/2113 17:16"),],
[-16700, -4592, -52, "Treatment Team", None, "TMTHA (PT)", "Tt Med Tx Hep A (Primary Team)", DBUtil.parseDateValue("11/16/2113 17:43"),],
[-16800, -2790, 0, "Treatment Team", None, "TMTHB (PT)", "Tt Med Tx Hep B (Primary Team)", DBUtil.parseDateValue("11/26/2113 6:54"),],
[-16900, -6295, -58, "Treatment Team", None, "TMTHN (PT)", "Tt Med Tx Hep Np (Primary Team)", DBUtil.parseDateValue("5/21/2113 22:19"),],
[-17000, -6269, -39, "Treatment Team", None, "TMTHRA (PT)", "Tt Med Tx Hep Res A (Primary Team)", DBUtil.parseDateValue("3/15/2111 11:24"),],
[-17100, -9903, -24, "Treatment Team", None, "TMTHRB (CS)", "Tt Med Tx Hep Res B (Consulting Service)", DBUtil.parseDateValue("11/30/2111 5:55"),],
[-17200, -3857, -21, "Treatment Team", None, "TMTR (PT)", "Tt Med Tx Renal (Primary Team)", DBUtil.parseDateValue("5/17/2113 22:58"),],
[-17300, -9724, -72, "Treatment Team", None, "TMT (PT)", "Tt Med Tx-Hep (Primary Team)", DBUtil.parseDateValue("2/24/2110 20:49"),],
[-17400, -7255, -7, "Treatment Team", None, "TMUA (PT)", "Tt Med Univ A1 (Primary Team)", DBUtil.parseDateValue("10/23/2109 14:00"),],
[-17500, -8317, -2, "Treatment Team", None, "TMUA (PT)", "Tt Med Univ A2 (Primary Team)", DBUtil.parseDateValue("5/17/2109 21:16"),],
[-17600, -1343, -8, "Treatment Team", None, "TMUA (PT)", "Tt Med Univ A3 (Primary Team)", DBUtil.parseDateValue("8/24/2113 7:24"),],
[-17700, -7747, -66, "Treatment Team", None, "TMUB (PT)", "Tt Med Univ B1 (Primary Team)", DBUtil.parseDateValue("1/16/2109 16:24"),],
[-17800, -6462, -30, "Treatment Team", None, "TMUB (PT)", "Tt Med Univ B2 (Primary Team)", DBUtil.parseDateValue("11/23/2109 19:30"),],
[-17900, -9668, -62, "Treatment Team", None, "TMUB (PT)", "Tt Med Univ B3 (Primary Team)", DBUtil.parseDateValue("9/16/2109 19:42"),],
[-18000, -9725, -79, "Treatment Team", None, "TMUC (PT)", "Tt Med Univ C1 (Primary Team)", DBUtil.parseDateValue("7/28/2109 7:55"),],
[-18100, -9956, -2, "Treatment Team", None, "TMUC (PT)", "Tt Med Univ C2 (Primary Team)", DBUtil.parseDateValue("2/10/2109 16:53"),],
[-18200, -7732, -25, "Treatment Team", None, "TMUC (PT)", "Tt Med Univ C3 (Primary Team)", DBUtil.parseDateValue("9/7/2113 9:27"),],
[-18300, -5125, -78, "Treatment Team", None, "TMUD (PI)", "Tt Med Univ D1 (Primary Intern)", DBUtil.parseDateValue("2/4/2109 21:33"),],
[-18400, -8355, -50, "Treatment Team", None, "TMUD (PT)", "Tt Med Univ D2 (Primary Team)", DBUtil.parseDateValue("5/12/2109 23:58"),],
[-18500, -1888, -80, "Treatment Team", None, "TMUD (PT)", "Tt Med Univ D3 (Primary Team)", DBUtil.parseDateValue("5/1/2113 14:52"),],
[-18600, -4768, -11, "Treatment Team", None, "TMUE (PT)", "Tt Med Univ E1 (Primary Team)", DBUtil.parseDateValue("12/18/2113 16:00"),],
[-18700, -5946, -98, "Treatment Team", None, "TMUE (PT)", "Tt Med Univ E2 (Primary Team)", DBUtil.parseDateValue("5/4/2113 17:20"),],
[-18800, -8631, -78, "Treatment Team", None, "TMUE (PT)", "Tt Med Univ E3 (Primary Team)", DBUtil.parseDateValue("8/8/2113 11:48"),],
[-18900, -6561, -64, "Treatment Team", None, "TMUNR (PT)", "Tt Med Univ Non Resi (Primary Team)", DBUtil.parseDateValue("4/7/2109 8:29"),],
[-19000, -6209, -68, "Treatment Team", None, "TMNA (PT)", "Tt Med9 Np A (Primary Team)", DBUtil.parseDateValue("1/22/2113 19:33"),],
[-19100, -5810, -31, "Treatment Team", None, "TMNB (PT)", "Tt Med9 Np B (Primary Team)", DBUtil.parseDateValue("2/8/2113 19:58"),],
[-19200, -223, -19, "Treatment Team", None, "TMNC (PT)", "Tt Med9 Np C (Primary Team)", DBUtil.parseDateValue("2/8/2113 12:27"),],
[-19300, -1005, -94, "Treatment Team", None, "TMBRA (PR)", "Tt Micu Blue Resident A (Primary Resident)", DBUtil.parseDateValue("6/23/2110 19:47"),],
[-19400, -6309, -84, "Treatment Team", None, "TMB (PT)", "Tt Micu Blue (Primary Team)", DBUtil.parseDateValue("10/24/2109 13:55"),],
[-19500, -5142, -63, "Treatment Team", None, "TMGRA (PT)", "Tt Micu Green Resident A (Primary Team)", DBUtil.parseDateValue("7/21/2110 12:02"),],
[-19600, -7779, -8, "Treatment Team", None, "TMG (PT)", "Tt Micu Green (Primary Team)", DBUtil.parseDateValue("9/18/2109 20:55"),],
[-19700, -2417, -76, "Treatment Team", None, "TMIS (PT)", "Tt Minimally Invasive Surgery (Primary Team)", DBUtil.parseDateValue("1/10/2114 20:58"),],
[-19800, -6697, -4, "Treatment Team", None, "TNEMU (PT)", "Tt Neuro Epilepsy Monitor Unit (Primary Team)", DBUtil.parseDateValue("3/2/2110 18:52"),],
[-19900, -3038, -98, "Treatment Team", None, "TNEMU (PT)", "Tt Neuro Epilepsy Monitor Unit (Primary Team)", DBUtil.parseDateValue("1/19/2114 11:34"),],
[-20000, -3672, -96, "Treatment Team", None, "TNSRA (PT)", "Tt Neuro Stroke Resident A (Primary Team)", DBUtil.parseDateValue("10/16/2113 12:36"),],
[-20100, -3014, -56, "Treatment Team", None, "TNSRB (PT)", "Tt Neuro Stroke Resident B (Primary Team)", DBUtil.parseDateValue("10/16/2113 6:11"),],
[-20200, -9587, -80, "Treatment Team", None, "TNRA (PT)", "Tt Neurology Resident A (Primary Team)", DBUtil.parseDateValue("10/15/2113 23:35"),],
[-20300, -9618, -81, "Treatment Team", None, "TNRB (PT)", "Tt Neurology Resident B (Primary Team)", DBUtil.parseDateValue("7/17/2113 23:38"),],
[-20400, -7764, -19, "Treatment Team", None, "TN (PT)", "Tt Neurology (Primary Team)", DBUtil.parseDateValue("10/26/2109 18:55"),],
[-20500, -5985, -40, "Treatment Team", None, "TNAVF (PT)", "Tt Neurosurgery A Vascular Floor (Primary Team)", DBUtil.parseDateValue("3/5/2113 7:32"),],
[-20600, -3920, -95, "Treatment Team", None, "TNAVI (CS)", "Tt Neurosurgery A Vascular Icu (Consulting Service)", DBUtil.parseDateValue("4/15/2113 16:11"),],
[-20700, -4463, -59, "Treatment Team", None, "TNA (PT)", "Tt Neurosurgery A (Primary Team)", DBUtil.parseDateValue("7/18/2110 13:30"),],
[-20800, -7556, -46, "Treatment Team", None, "TNBTF (PT)", "Tt Neurosurgery B Tumor Floor (Primary Team)", DBUtil.parseDateValue("6/18/2113 7:15"),],
[-20900, -5245, -4, "Treatment Team", None, "TNBTI (PT)", "Tt Neurosurgery B Tumor Icu (Primary Team)", DBUtil.parseDateValue("4/27/2113 10:58"),],
[-21000, -2727, -85, "Treatment Team", None, "TNB (PT)", "Tt Neurosurgery B (Primary Team)", DBUtil.parseDateValue("3/26/2110 17:57"),],
[-21100, -4073, -25, "Treatment Team", None, "TNCSF (CS)", "Tt Neurosurgery C Spine Floor (Consulting Service)", DBUtil.parseDateValue("12/31/2112 20:55"),],
[-21200, -4198, -90, "Treatment Team", None, "TNCSI (CS)", "Tt Neurosurgery C Spine Icu (Consulting Service)", DBUtil.parseDateValue("5/31/2113 2:58"),],
[-21300, -3735, -48, "Treatment Team", None, "TNC (PT)", "Tt Neurosurgery C (Primary Team)", DBUtil.parseDateValue("4/23/2110 13:04"),],
[-21400, -732, -41, "Treatment Team", None, "TNF (CS)", "Tt Neurosurgery Floor (Consulting Service)", DBUtil.parseDateValue("8/26/2113 21:00"),],
[-21500, -4812, -19, "Treatment Team", None, "TNIO (PT)", "Tt Neurosurgery Icu/Resident On-Call (Primary Team)", DBUtil.parseDateValue("7/11/2113 12:19"),],
[-21600, -4812, -19, "Treatment Team", None, "TN (PT)", "Tt Neurosurgery (Primary Team)", DBUtil.parseDateValue("7/6/2110 10:30"),],
[-21700, -3583, -41, "Treatment Team", None, "TOSMC (PT)", "Tt Ob San Mateo County (Primary Team)", DBUtil.parseDateValue("11/24/2111 6:46"),],
[-21800, -3229, -93, "Treatment Team", None, "TOU (PT)", "Tt Ob University (Primary Team)", DBUtil.parseDateValue("8/1/2113 21:43"),],
[-21900, -3229, -49, "Treatment Team", None, "TON (PT)", "Tt Oncology Np (Primary Team)", DBUtil.parseDateValue("3/26/2113 7:19"),],
[-22000, -6011, -37, "Treatment Team", None, "TORA (PT)", "Tt Oncology Resident A (Primary Team)", DBUtil.parseDateValue("7/1/2113 13:34"),],
[-22100, -305, -43, "Treatment Team", None, "TORB (PT)", "Tt Oncology Resident B (Primary Team)", DBUtil.parseDateValue("1/14/2114 7:37"),],
[-22200, -5666, -98, "Treatment Team", None, "TORC (PT)", "Tt Oncology Resident C (Primary Team)", DBUtil.parseDateValue("4/6/2113 7:24"),],
[-22300, -9992, -35, "Treatment Team", None, "TO (PT)", "Tt Oncology (Primary Team)", DBUtil.parseDateValue("12/3/2109 8:10"),],
[-22400, -8288, -32, "Treatment Team", None, "TO (PT)", "Tt Ophthalmology (Primary Team)", DBUtil.parseDateValue("10/5/2113 12:01"),],
[-22500, -7739, -47, "Treatment Team", None, "TOAJ (PT)", "Tt Ortho Arthritis (Joint) (Primary Team)", DBUtil.parseDateValue("9/12/2113 8:23"),],
[-22600, -9491, -39, "Treatment Team", None, "TOFA (PT)", "Tt Ortho Foot Ankle (Primary Team)", DBUtil.parseDateValue("1/22/2110 14:51"),],
[-22700, -4602, -91, "Treatment Team", None, "TOF (PT)", "Tt Ortho Foot/Ankle (Primary Team)", DBUtil.parseDateValue("12/22/2113 9:09"),],
[-22800, -7546, -78, "Treatment Team", None, "TOH (CS)", "Tt Ortho Hand (Consulting Service)", DBUtil.parseDateValue("8/27/2113 0:41"),],
[-22900, -1266, -66, "Treatment Team", None, "TOJ (PT)", "Tt Ortho Joint (Primary Team)", DBUtil.parseDateValue("3/8/2111 7:32"),],
[-23000, -2426, -46, "Treatment Team", None, "TOO (PT)", "Tt Ortho Oncology (Primary Team)", DBUtil.parseDateValue("9/23/2113 16:34"),],
[-23100, -2837, -81, "Treatment Team", None, "TOS (PT)", "Tt Ortho Shoulder/Elbow (Primary Team)", DBUtil.parseDateValue("1/23/2114 6:37"),],
[-23200, -1365, -79, "Treatment Team", None, "TOS (PT)", "Tt Ortho Spine (Primary Team)", DBUtil.parseDateValue("10/25/2109 22:02"),],
[-23300, -7799, -15, "Treatment Team", None, "TOS (PT)", "Tt Ortho Spine (Primary Team)", DBUtil.parseDateValue("10/14/2113 18:11"),],
[-23400, -8843, -96, "Treatment Team", None, "TOS (PT)", "Tt Ortho Sports (Primary Team)", DBUtil.parseDateValue("9/4/2113 7:50"),],
[-23500, -6483, -28, "Treatment Team", None, "TOS (PT)", "Tt Ortho Surgery (Primary Team)", DBUtil.parseDateValue("5/9/2110 5:29"),],
[-23600, -6483, -28, "Treatment Team", None, "TOT (PT)", "Tt Ortho Trauma (Primary Team)", DBUtil.parseDateValue("11/7/2111 8:57"),],
[-23700, -6483, -28, "Treatment Team", None, "TOT (PT)", "Tt Ortho Trauma (Primary Team)", DBUtil.parseDateValue("12/27/2113 5:02"),],
[-23800, -6483, -28, "Treatment Team", None, "TOT (PT)", "Tt Ortho Tumor (Primary Team)", DBUtil.parseDateValue("4/4/2110 19:33"),],
[-23900, -6434, -31, "Treatment Team", None, "TPR2 (PT)", "Tt Pain Resident 2 (Primary Team)", DBUtil.parseDateValue("6/3/2111 17:15"),],
[-24000, -1874, -70, "Treatment Team", None, "TP (PT)", "Tt Pain (Primary Team)", DBUtil.parseDateValue("4/10/2110 12:17"),],
[-24100, -9149, -90, "Treatment Team", None, "TPGSAO (PT)", "Tt Pamf (Gen Surg) Attending Only (Primary Team)", DBUtil.parseDateValue("4/26/2113 5:27"),],
[-24200, -4935, -32, "Treatment Team", None, "TPNAO (PT)", "Tt Pamf (Neurosurg) Attending Only (Primary Team)", DBUtil.parseDateValue("9/7/2113 7:38"),],
[-24300, -4935, -32, "Treatment Team", None, "TPM1 (PT)", "Tt Pamf Med 1 (Primary Team)", DBUtil.parseDateValue("5/9/2109 7:30"),],
[-24400, -4935, -32, "Treatment Team", None, "TPM2 (PT)", "Tt Pamf Med 2 (Primary Team)", DBUtil.parseDateValue("7/28/2109 8:05"),],
[-24500, -4550, -62, "Treatment Team", None, "TPM3 (PT)", "Tt Pamf Med 3 (Primary Team)", DBUtil.parseDateValue("6/10/2109 23:47"),],
[-24600, -4550, -62, "Treatment Team", None, "TPM4 (PT)", "Tt Pamf Med 4 (Primary Team)", DBUtil.parseDateValue("4/16/2113 7:00"),],
[-24700, -3954, -61, "Treatment Team", None, "TPM5 (PT)", "Tt Pamf Med 5 (Primary Team)", DBUtil.parseDateValue("4/18/2113 7:00"),],
[-24800, -3954, -61, "Treatment Team", None, "TPM6 (PT)", "Tt Pamf Med 6 (Primary Team)", DBUtil.parseDateValue("11/8/2113 13:52"),],
[-24900, -3954, -61, "Treatment Team", None, "TPMA (PT)", "Tt Pamf Med/Cards Admitting (Primary Team)", DBUtil.parseDateValue("4/1/2113 7:00"),],
[-25000, -3954, -61, "Treatment Team", None, "TPAO (PT)", "Tt Pamf(Ent) Attending Only (Primary Team)", DBUtil.parseDateValue("3/7/2113 9:13"),],
[-25100, -3954, -61, "Treatment Team", None, "TPAO (PT)", "Tt Pamf(Ep) Attending Only (Primary Team)", DBUtil.parseDateValue("2/17/2112 15:44"),],
[-25200, -1614, -42, "Treatment Team", None, "TPAO (PT)", "Tt Pamf(Ortho) Attending Only (Primary Team)", DBUtil.parseDateValue("9/11/2113 13:52"),],
[-25300, -1614, -42, "Treatment Team", None, "TPAO (PT)", "Tt Pamf(Plastics) Attending Only (Primary Team)", DBUtil.parseDateValue("9/2/2113 13:00"),],
[-25400, -1614, -42, "Treatment Team", None, "TPAO (PT)", "Tt Pamf(Urology) Attending Only (Primary Team)", DBUtil.parseDateValue("9/4/2113 13:59"),],
[-25500, -1614, -42, "Treatment Team", None, "TPMR (PT)", "Tt Physical Med Rehab (Primary Team)", DBUtil.parseDateValue("1/6/2113 0:14"),],
[-25600, -6234, -95, "Treatment Team", None, "TPSC (CS)", "Tt Plastic Surgery Consults (Consulting Service)", DBUtil.parseDateValue("11/9/2113 20:33"),],
[-25700, -900, -45, "Treatment Team", None, "TPS (PT)", "Tt Plastic Surgery (Primary Team)", DBUtil.parseDateValue("6/27/2111 9:34"),],
[-25800, -6187, -3, "Treatment Team", None, "TPS (PT)", "Tt Plastic Surgery (Primary Team)", DBUtil.parseDateValue("11/26/2113 9:40"),],
[-25900, -1471, -23, "Treatment Team", None, "TP (CS)", "Tt Psychiatry (Consulting Service)", DBUtil.parseDateValue("4/14/2113 18:43"),],
[-26000, -9067, -86, "Treatment Team", None, "TPHA (PT)", "Tt Pulm Htn A (Primary Team)", DBUtil.parseDateValue("10/29/2113 21:18"),],
[-26100, -292, -42, "Treatment Team", None, "TPHB (PT)", "Tt Pulm Htn B (Primary Team)", DBUtil.parseDateValue("1/24/2113 20:01"),],
[-26200, -5490, -12, "Treatment Team", None, "TPT (PT)", "Tt Pulmonary Transplant (Primary Team)", DBUtil.parseDateValue("12/26/2111 14:41"),],
[-26300, -577, -64, "Treatment Team", None, "TS (CS)", "Tt Sicu (Consulting Service)", DBUtil.parseDateValue("10/2/2109 19:07"),],
[-26400, -2476, -94, "Treatment Team", None, "TSO1 (PT)", "Tt Surgical Oncology 1 (Primary Team)", DBUtil.parseDateValue("4/10/2113 18:41"),],
[-26500, -7826, -60, "Treatment Team", None, "TSO2 (PT)", "Tt Surgical Oncology 2 (Primary Team)", DBUtil.parseDateValue("4/21/2113 1:06"),],
[-26600, -8138, -95, "Treatment Team", None, "TU (CS)", "Tt Urology (Consulting Service)", DBUtil.parseDateValue("2/19/2110 0:37"),],
[-26700, -8302, -86, "Treatment Team", None, "TU (PT)", "Tt Urology (Primary Team)", DBUtil.parseDateValue("8/26/2113 9:09"),],
[-26800, -8694, -68, "Treatment Team", None, "TV (PT)", "Tt Vad (Primary Team)", DBUtil.parseDateValue("11/6/2113 7:54"),],
[-26900, -6011, -84, "Treatment Team", None, "TVS (CS)", "Tt Vascular Surgery (Consulting Service)", DBUtil.parseDateValue("4/23/2113 5:59"),],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );


    def test_dataConversion_aggregate(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...");
        convOptions = ConversionOptions();
        convOptions.startDate = TEST_START_DATE;
        convOptions.aggregate = True;
        self.converter.convertSourceItems(convOptions);

        # Just query back for the same data, de-normalizing the data back to a general table
        testQuery = \
            """
            select 
                pi.external_id,
                pi.patient_id,
                pi.encounter_id,
                cic.description,
                ci.external_id,
                ci.name,
                ci.description,
                pi.item_date
            from
                patient_item as pi,
                clinical_item as ci,
                clinical_item_category as cic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = 'stride_treatment_team'
            order by
                pi.external_id desc, ci.external_id desc
            """;
        expectedData = \
            [   
[-200, -117, 0, "Treatment Team", None, "ACP", "Additional Communicating Provider", DBUtil.parseDateValue("10/5/2113 23:18"),],
[-300, -4845, -60, "Treatment Team", None, "CC", "Care Coordinator", DBUtil.parseDateValue("6/26/2113 8:11"),],
[-400, -9194, -26, "Treatment Team", None, "CM", "Case Manager", DBUtil.parseDateValue("4/11/2109 8:39"),],
[-500, -9519, -69, "Treatment Team", None, "C", "Chief", DBUtil.parseDateValue("3/19/2113 12:10"),],
[-600, -8702, -77, "Treatment Team", None, "CD", "Clinical Dietician", DBUtil.parseDateValue("4/10/2109 8:45"),],
[-700, -8307, -92, "Treatment Team", None, "C", "Co-Attending", DBUtil.parseDateValue("7/9/2113 0:21"),],
[-800, -5474, -78, "Treatment Team", None, "C", "Consulting", DBUtil.parseDateValue("12/4/2113 9:47"),],
[-900, -6015, -47, "Treatment Team", None, "C", "Consulting", DBUtil.parseDateValue("7/24/2113 2:29"),],
[-1000, -3733, -39, "Treatment Team", None, "C", "Consulting", DBUtil.parseDateValue("7/9/2113 8:04"),],
[-1100, -9597, -78, "Treatment Team", None, "C", "Consulting", DBUtil.parseDateValue("10/12/2109 18:48"),],
[-1200, -1087, -18, "Treatment Team", None, "C", "Consulting", DBUtil.parseDateValue("1/14/2109 23:12"),],
[-1300, -6467, -14, "Treatment Team", None, "C", "Consulting", DBUtil.parseDateValue("4/10/2109 11:55"),],
[-1400, -1291, -70, "Treatment Team", None, "D", "Dietician", DBUtil.parseDateValue("12/31/2111 10:35"),],
[-1500, -5038, -91, "Treatment Team", None, "ER", "ED Registrar", DBUtil.parseDateValue("9/12/2112 18:04"),],
[-1600, -8055, -77, "Treatment Team", None, "ET", "ED Tech", DBUtil.parseDateValue("5/4/2110 9:35"),],
[-1700, -2531, -12, "Treatment Team", None, "EUS", "ED Unit Secretary", DBUtil.parseDateValue("5/8/2110 14:50"),],
[-1800, -54, -14, "Treatment Team", None, "E", "Emergency", DBUtil.parseDateValue("10/23/2109 11:51"),],
[-1900, -6763, -25, "Treatment Team", None, "LVN", "Licensed Vocational Nurse", DBUtil.parseDateValue("5/7/2110 5:29"),],
[-2000, -5668, -56, "Treatment Team", None, "MA", "Medical Assistant", DBUtil.parseDateValue("9/30/2109 12:58"),],
[-2100, -5862, -78, "Treatment Team", None, "NC", "Nurse Coordinator", DBUtil.parseDateValue("3/22/2113 18:54"),],
[-2200, -4060, -97, "Treatment Team", None, "P", "Primary", DBUtil.parseDateValue("1/1/2113 16:50"),],
[-2300, -7217, -45, "Treatment Team", None, "NA", "Nursing Assistant", DBUtil.parseDateValue("4/27/2110 7:30"),],
[-2400, -4026, -44, "Treatment Team", None, "OT", "Occupational Therapist", DBUtil.parseDateValue("4/12/2109 16:13"),],
[-2500, -8387, -39, "Treatment Team", None, "PT", "Physical Therapist", DBUtil.parseDateValue("4/14/2109 12:09"),],
[-2600, -2160, -42, "Treatment Team", None, "PTA", "Physical Therapist Assistant", DBUtil.parseDateValue("9/15/2113 9:46"),],
[-2700, -3237, -81, "Treatment Team", None, "P", "Primary", DBUtil.parseDateValue("1/17/2113 17:49"),],
[-2800, -7645, -88, "Treatment Team", None, "P", "Primary", DBUtil.parseDateValue("10/19/2109 16:41"),],
[-2900, -448, -56, "Treatment Team", None, "P", "Primary", DBUtil.parseDateValue("10/24/2109 12:11"),],
[-3000, -5832, -51, "Treatment Team", None, "P", "Primary", DBUtil.parseDateValue("9/30/2109 12:59"),],
[-3100, -3983, -19, "Treatment Team", None, "P", "Primary", DBUtil.parseDateValue("4/21/2110 12:15"),],
[-3200, -1547, -42, "Treatment Team", None, "P", "Primary", DBUtil.parseDateValue("10/24/2109 12:11"),],
[-3300, -6251, -4, "Treatment Team", None, "P", "Primary", DBUtil.parseDateValue("9/16/2109 19:31"),],
[-3400, -1328, -59, "Treatment Team", None, "P", "Primary", DBUtil.parseDateValue("10/24/2109 13:55"),],
[-3500, -6209, -50, "Treatment Team", None, "P", "Psychologist", DBUtil.parseDateValue("8/6/2113 10:16"),],
[-3600, -8067, -95, "Treatment Team", None, "RN", "Registered Nurse", DBUtil.parseDateValue("10/18/2109 6:47"),],
[-3700, -9956, -50, "Treatment Team", None, "RCP", "Respiratory Care Practitioner", DBUtil.parseDateValue("10/17/2109 7:49"),],
[-3800, -4057, -8, "Treatment Team", None, "SW", "Social Worker", DBUtil.parseDateValue("11/9/2109 16:23"),],
[-3900, -8424, -44, "Treatment Team", None, "ST", "Speech Therapist", DBUtil.parseDateValue("11/22/2109 7:58"),],
[-4000, -6271, -78, "Treatment Team", None, "SC", "Spiritual Care", DBUtil.parseDateValue("4/6/2113 15:00"),],
[-4100, -3251, -79, "Treatment Team", None, "SN", "Student Nurse", DBUtil.parseDateValue("9/11/2113 13:34"),],
[-4200, -79, -74, "Treatment Team", None, "T", "Trauma", DBUtil.parseDateValue("3/1/2113 15:36"),],
[-4300, -6671, -77, "Treatment Team", None, "T", "Trauma", DBUtil.parseDateValue("9/26/2113 6:28"),],
[-4400, -9911, -27, "Treatment Team", None, "TN", "Triage Nurse", DBUtil.parseDateValue("11/1/2111 6:58"),],
[-4500, -4550, -58, "Treatment Team", None, "CCIC (C)", "Con Card Interven/Ami Consult (Consulting)", DBUtil.parseDateValue("7/4/2113 21:35"),],
[-4600, -1959, -90, "Treatment Team", None, "CCS (C)", "Con Cardiac Surgery (Consulting)", DBUtil.parseDateValue("12/26/2113 9:38"),],
[-4700, -6120, -19, "Treatment Team", None, "CCA (C)", "Con Cardiol Arrhythmia (Consulting)", DBUtil.parseDateValue("11/17/2113 11:39"),],
[-4800, -9620, -14, "Treatment Team", None, "CCT (P)", "Con Cardiol Transplant (Primary)", DBUtil.parseDateValue("5/10/2113 9:42"),],
[-4900, -7389, -82, "Treatment Team", None, "CC (C)", "Con Cardiology (Consulting)", DBUtil.parseDateValue("11/9/2109 13:58"),],
[-5000, -2570, -34, "Treatment Team", None, "CCS (P)", "Con Cardiothroacic Surgery (Primary)", DBUtil.parseDateValue("3/18/2111 9:34"),],
[-5100, -8843, -96, "Treatment Team", None, "CCS (P)", "Con Colorectal Surgery (Primary)", DBUtil.parseDateValue("3/1/2113 7:50"),],
[-5200, -9515, -31, "Treatment Team", None, "CCFA (P)", "Con Cystic Fibrosis Adult (Primary)", DBUtil.parseDateValue("1/22/2114 19:09"),],
[-5300, -2229, -86, "Treatment Team", None, "CE (C)", "Con Endocrinology (Consulting)", DBUtil.parseDateValue("12/21/2113 16:26"),],
[-5400, -9149, -90, "Treatment Team", None, "CG (C)", "Con Gastroenterology (Consulting)", DBUtil.parseDateValue("6/21/2113 6:42"),],
[-5500, -4935, -32, "Treatment Team", None, "CGS (P)", "Con General Surgery (Primary)", DBUtil.parseDateValue("8/18/2110 3:51"),],
[-5600, -4935, -32, "Treatment Team", None, "CG (C)", "Con Geriatrics (Consulting)", DBUtil.parseDateValue("5/31/2111 14:39"),],
[-5700, -4550, -62, "Treatment Team", None, "CG (C)", "Con Gynecology (Consulting)", DBUtil.parseDateValue("10/18/2111 20:15"),],
[-5800, -3954, -61, "Treatment Team", None, "CHS (C)", "Con Hand Surgery (Consulting)", DBUtil.parseDateValue("3/8/2111 8:05"),],
[-5900, -7078, -76, "Treatment Team", None, "CH (C)", "Con Hematology (Consulting)", DBUtil.parseDateValue("11/8/2113 9:51"),],
[-6000, -4568, -1, "Treatment Team", None, "CH (C)", "Con Hepatology (Consulting)", DBUtil.parseDateValue("5/6/2113 14:41"),],
[-6100, -4568, -42, "Treatment Team", None, "CI (C)", "Con Icu (Consulting)", DBUtil.parseDateValue("1/21/2113 14:01"),],
[-6200, -4568, -82, "Treatment Team", None, "CID (C)", "Con Inf Dis (Consulting)", DBUtil.parseDateValue("1/27/2114 11:20"),],
[-6300, -8539, -33, "Treatment Team", None, "CIDI (C)", "Con Inf Dis Immunocomp (Consulting)", DBUtil.parseDateValue("1/8/2112 8:59"),],
[-6400, -1543, -19, "Treatment Team", None, "CIDPC (C)", "Con Inf Dis Postitive Care (Consulting)", DBUtil.parseDateValue("5/29/2110 12:57"),],
[-6500, -1543, -19, "Treatment Team", None, "CIMC (C)", "Con Internal Medicine Consult (Consulting)", DBUtil.parseDateValue("4/21/2113 11:27"),],
[-6600, -1543, -19, "Treatment Team", None, "CIR (C)", "Con Intervent Rad (Consulting)", DBUtil.parseDateValue("7/21/2112 4:03"),],
[-6700, -4464, -14, "Treatment Team", None, "CKT (C)", "Con Kidney Transplant (Consulting)", DBUtil.parseDateValue("8/15/2113 0:11"),],
[-6800, -4464, -42, "Treatment Team", None, "CLT (P)", "Con Liver Transplant (Primary)", DBUtil.parseDateValue("1/10/2113 8:33"),],
[-6900, -4464, -22, "Treatment Team", None, "CMG (C)", "Con Medical Genetics (Consulting)", DBUtil.parseDateValue("9/5/2112 13:22"),],
[-7000, -9840, -68, "Treatment Team", None, "CM (C)", "Con Medicine (Consulting)", DBUtil.parseDateValue("9/27/2109 16:51"),],
[-7100, -9840, -68, "Treatment Team", None, "CMAR (C)", "Con Micu Admission Request (Consulting)", DBUtil.parseDateValue("4/23/2113 12:42"),],
[-7200, -4392, -98, "Treatment Team", None, "CMC (C)", "Con Micu Consult (Consulting)", DBUtil.parseDateValue("8/14/2113 23:16"),],
[-7300, -394, -11, "Treatment Team", None, "CN (C)", "Con Nephrology (Consulting)", DBUtil.parseDateValue("9/17/2109 10:46"),],
[-7400, -7389, -82, "Treatment Team", None, "CNT (C)", "Con Nephrology Transplant (Consulting)", DBUtil.parseDateValue("10/19/2109 2:06"),],
[-7500, -5689, -19, "Treatment Team", None, "CNEC (C)", "Con Neuro Endocrine Consult (Consulting)", DBUtil.parseDateValue("12/4/2110 17:36"),],
[-7600, -714, -33, "Treatment Team", None, "CNEC (C)", "Con Neuro Epilepsy Consult (Consulting)", DBUtil.parseDateValue("12/11/2113 1:07"),],
[-7700, -1464, -53, "Treatment Team", None, "CNI (C)", "Con Neuro Icu (Consulting)", DBUtil.parseDateValue("10/8/2109 12:20"),],
[-7800, -3115, -69, "Treatment Team", None, "CNI (C)", "Con Neuro Ir (Consulting)", DBUtil.parseDateValue("7/25/2112 21:44"),],
[-7900, -7516, -84, "Treatment Team", None, "CNO (C)", "Con Neuro Oncology (Consulting)", DBUtil.parseDateValue("11/23/2112 12:00"),],
[-8000, -9726, -91, "Treatment Team", None, "CNS (P)", "Con Neuro Stroke (Primary)", DBUtil.parseDateValue("7/15/2109 22:20"),],
[-8100, -9726, -91, "Treatment Team", None, "CNG (C)", "Con Neurology General (Consulting)", DBUtil.parseDateValue("7/27/2109 21:42"),],
[-8200, -3961, -74, "Treatment Team", None, "CN (P)", "Con Neurosurgery (Primary)", DBUtil.parseDateValue("4/10/2111 7:51"),],
[-8300, -4087, -54, "Treatment Team", None, "CO (C)", "Con Obstetrics (Consulting)", DBUtil.parseDateValue("8/2/2110 1:54"),],
[-8400, -1266, -12, "Treatment Team", None, "CO (C)", "Con Oncology (Consulting)", DBUtil.parseDateValue("12/24/2113 10:19"),],
[-8500, -2289, -68, "Treatment Team", None, "CO (C)", "Con Ophthalmology (Consulting)", DBUtil.parseDateValue("6/21/2113 0:27"),],
[-8600, -2591, -79, "Treatment Team", None, "CO (C)", "Con Orthopedics (Consulting)", DBUtil.parseDateValue("1/19/2112 12:15"),],
[-8700, -6762, -49, "Treatment Team", None, "COH (C)", "Con Orthopedics Hospitalist (Consulting)", DBUtil.parseDateValue("12/3/2113 5:00"),],
[-8800, -6762, -59, "Treatment Team", None, "CP (C)", "Con Pain (Consulting)", DBUtil.parseDateValue("4/10/2109 11:55"),],
[-8900, -211, -87, "Treatment Team", None, "CPC (C)", "Con Palliative Care (Consulting)", DBUtil.parseDateValue("9/24/2113 10:15"),],
[-9000, -7621, -85, "Treatment Team", None, "CPM (C)", "Con Pamf Medicine (Consulting)", DBUtil.parseDateValue("4/30/2113 6:49"),],
[-9100, -3251, -49, "Treatment Team", None, "CPC (C)", "Con Primary Care (Consulting)", DBUtil.parseDateValue("6/14/2113 19:49"),],
[-9200, -2837, -81, "Treatment Team", None, "CP (C)", "Con Psychiatry (Consulting)", DBUtil.parseDateValue("1/19/2112 11:25"),],
[-9300, -2837, -42, "Treatment Team", None, "CPH (C)", "Con Pulm Hypertension (Consulting)", DBUtil.parseDateValue("10/23/2113 11:54"),],
[-9400, -2837, -42, "Treatment Team", None, "CPT (P)", "Con Pulm Transplant (Primary)", DBUtil.parseDateValue("8/9/2113 19:48"),],
[-9500, -2837, -42, "Treatment Team", None, "CP (C)", "Con Pulmonary (Consulting)", DBUtil.parseDateValue("11/4/2113 7:03"),],
[-9600, -4295, -35, "Treatment Team", None, "CPRC (C)", "Con Pulmonary Rehab Consult (Consulting)", DBUtil.parseDateValue("10/4/2113 9:36"),],
[-9700, -3433, -44, "Treatment Team", None, "CR (C)", "Con Rheumatology (Consulting)", DBUtil.parseDateValue("10/19/2112 9:31"),],
[-9800, -7612, -25, "Treatment Team", None, "CST (C)", "Con Spine Trauma (Consulting)", DBUtil.parseDateValue("10/13/2111 18:11"),],
[-9900, -4875, -51, "Treatment Team", None, "CTS (C)", "Con Thoracic Surgery (Consulting)", DBUtil.parseDateValue("8/28/2113 21:14"),],
[-10000, -8813, -79, "Treatment Team", None, "CTS (P)", "Con Transplant Surgery (Primary)", DBUtil.parseDateValue("3/26/2113 20:26"),],
[-10100, -8813, -79, "Treatment Team", None, "CU (C)", "Con Urology (Consulting)", DBUtil.parseDateValue("5/7/2112 10:35"),],
[-10200, -8720, -72, "Treatment Team", None, "CVS (C)", "Con Vascular Surgery (Consulting)", DBUtil.parseDateValue("1/14/2114 16:49"),],
[-10300, -8720, -72, "Treatment Team", None, "TACST (P)", "Tt Acute Care Surgery Trauma (Primary)", DBUtil.parseDateValue("11/30/2109 18:16"),],
[-10400, -1365, -79, "Treatment Team", None, "TAP2 (C)", "Tt Acute Pain 2Pain (Consulting)", DBUtil.parseDateValue("12/21/2113 9:19"),],
[-10500, -1365, -79, "Treatment Team", None, "TBB (P)", "Tt Bmt (Bmt) (Primary)", DBUtil.parseDateValue("10/22/2113 7:58"),],
[-10600, -8712, -95, "Treatment Team", None, "TB (P)", "Tt Bmt (Primary)", DBUtil.parseDateValue("9/13/2111 16:27"),],
[-10700, -7799, -15, "Treatment Team", None, "TB (P)", "Tt Bmt (Primary)", DBUtil.parseDateValue("7/11/2113 15:47"),],
[-10800, -2552, -30, "Treatment Team", None, "TBS (C)", "Tt Breast Surgery (Consulting)", DBUtil.parseDateValue("11/21/2113 19:15"),],
[-10900, -3644, -25, "Treatment Team", None, "TCA (P)", "Tt Cardiac Adult (Primary)", DBUtil.parseDateValue("1/19/2113 13:25"),],
[-11000, -3644, -1, "Treatment Team", None, "TCA (P)", "Tt Cardiac Adult (Primary)", DBUtil.parseDateValue("1/31/2113 8:25"),],
[-11100, -7289, -58, "Treatment Team", None, "TC (P)", "Tt Cardiology (Primary)", DBUtil.parseDateValue("9/1/2109 15:16"),],
[-11200, -8843, -96, "Treatment Team", None, "TC (P)", "Tt Cardiology (Primary)", DBUtil.parseDateValue("11/1/2109 7:02"),],
[-11300, -9515, -31, "Treatment Team", None, "TC (P)", "Tt Cardiology (Primary)", DBUtil.parseDateValue("1/15/2110 20:02"),],
[-11400, -394, -58, "Treatment Team", None, "TC (P)", "Tt Cardiology (Primary)", DBUtil.parseDateValue("12/30/2110 17:29"),],
[-11500, -7987, -69, "Treatment Team", None, "TC (P)", "Tt Cardiology (Primary)", DBUtil.parseDateValue("5/25/2110 13:56"),],
[-11600, -2446, -72, "Treatment Team", None, "TCA (P)", "Tt Cardiology Arrhythmia (Primary)", DBUtil.parseDateValue("10/21/2111 7:25"),],
[-11700, -3127, -94, "Treatment Team", None, "TCE (P)", "Tt Cardiology Ep (Primary)", DBUtil.parseDateValue("2/24/2113 17:11"),],
[-11800, -8832, -55, "Treatment Team", None, "TCE (P)", "Tt Cardiology Ep (Primary)", DBUtil.parseDateValue("6/5/2113 16:51"),],
[-11900, -1826, -61, "Treatment Team", None, "TCI (P)", "Tt Cardiology Interventional (Primary)", DBUtil.parseDateValue("7/19/2110 15:03"),],
[-12000, -345, -8, "Treatment Team", None, "TC (P)", "Tt Ccu/Hf (Primary)", DBUtil.parseDateValue("2/26/2113 5:24"),],
[-12100, -6351, -89, "Treatment Team", None, "TC (P)", "Tt Ccu/Hf (Primary)", DBUtil.parseDateValue("5/21/2113 6:10"),],
[-12200, -1851, -54, "Treatment Team", None, "TC (P)", "Tt Ccu/Hf (Primary)", DBUtil.parseDateValue("1/23/2113 23:16"),],
[-12300, -5563, -18, "Treatment Team", None, "TC (P)", "Tt Ccu/Hf (Primary)", DBUtil.parseDateValue("4/21/2113 7:47"),],
[-12400, -5752, -91, "Treatment Team", None, "TCM (P)", "Tt Chris Mow (Primary)", DBUtil.parseDateValue("12/25/2113 9:33"),],
[-12500, -7881, -71, "Treatment Team", None, "TCP (C)", "Tt Chronic Pain (Consulting)", DBUtil.parseDateValue("6/17/2113 13:43"),],
[-12600, -7881, -71, "Treatment Team", None, "TCS (P)", "Tt Colorectal Surgery (Primary)", DBUtil.parseDateValue("12/2/2113 8:39"),],
[-12700, -7881, -16, "Treatment Team", None, "TCS (P)", "Tt Craniofacial Surgery (Primary)", DBUtil.parseDateValue("7/23/2113 16:27"),],
[-12800, -2270, -17, "Treatment Team", None, "TCT (P)", "Tt Cvicu Team (Primary)", DBUtil.parseDateValue("6/30/2109 15:23"),],
[-12900, -9149, -90, "Treatment Team", None, "TCFA (P)", "Tt Cystic Fibrosis Adult (Primary)", DBUtil.parseDateValue("4/21/2110 11:25"),],
[-13000, -4935, -32, "Treatment Team", None, "TCFA (P)", "Tt Cystic Fibrosis Adult (Primary)", DBUtil.parseDateValue("9/26/2113 19:44"),],
[-13100, -4935, -32, "Treatment Team", None, "TEHAN (P)", "Tt Ent Head And Neck (Primary)", DBUtil.parseDateValue("10/23/2113 15:06"),],
[-13200, -4935, -32, "Treatment Team", None, "TEHN (P)", "Tt Ent Head Neck (Primary)", DBUtil.parseDateValue("5/17/2110 8:38"),],
[-13300, -4935, -32, "Treatment Team", None, "TES (C)", "Tt Ent Specialty (Consulting)", DBUtil.parseDateValue("5/12/2110 8:58"),],
[-13400, -4540, -63, "Treatment Team", None, "TES (C)", "Tt Ent Specialty (Consulting)", DBUtil.parseDateValue("7/11/2113 18:25"),],
[-13500, -1614, -42, "Treatment Team", None, "TGC (P)", "Tt Gen Cards (Primary)", DBUtil.parseDateValue("3/21/2113 19:53"),],
[-13600, -1614, -42, "Treatment Team", None, "TGC (P)", "Tt Gen Cards (Primary)", DBUtil.parseDateValue("4/23/2113 7:23"),],
[-13700, -6824, -84, "Treatment Team", None, "TGC (P)", "Tt Gen Cards (Primary)", DBUtil.parseDateValue("5/12/2113 7:15"),],
[-13800, -3034, -56, "Treatment Team", None, "TGS (P)", "Tt Gen Surg (Primary)", DBUtil.parseDateValue("5/9/2109 6:17"),],
[-13900, -7232, -51, "Treatment Team", None, "TGS (P)", "Tt Gen Surg (Primary)", DBUtil.parseDateValue("8/21/2109 8:03"),],
[-14000, -4596, -16, "Treatment Team", None, "TGS (C)", "Tt Gen Surg (Consulting)", DBUtil.parseDateValue("8/21/2109 17:27"),],
[-14100, -9210, 0, "Treatment Team", None, "TGT (C)", "Tt General Thoracic (Consulting)", DBUtil.parseDateValue("11/8/2113 11:28"),],
[-14200, -7584, -48, "Treatment Team", None, "TGO (P)", "Tt Gyn Onc (Primary)", DBUtil.parseDateValue("3/29/2110 18:12"),],
[-14300, -5374, -7, "Treatment Team", None, "TGO (P)", "Tt Gyn Onc (Primary)", DBUtil.parseDateValue("8/6/2113 5:24"),],
[-14400, -4331, -81, "Treatment Team", None, "TGP (P)", "Tt Gyn Private (Primary)", DBUtil.parseDateValue("5/1/2113 9:40"),],
[-14500, -8523, -99, "Treatment Team", None, "TGU (P)", "Tt Gyn Univ (Primary)", DBUtil.parseDateValue("10/22/2113 7:25"),],
[-14600, -3827, -55, "Treatment Team", None, "THS (P)", "Tt Hand Surgery (Primary)", DBUtil.parseDateValue("8/13/2110 1:56"),],
[-14700, -7066, -8, "Treatment Team", None, "THLT (P)", "Tt Heart Lung Transplant (Primary)", DBUtil.parseDateValue("3/1/2110 15:32"),],
[-14800, -8127, -22, "Treatment Team", None, "THT (P)", "Tt Heart Transplant/Vad (Primary)", DBUtil.parseDateValue("6/28/2111 7:15"),],
[-14900, -4146, -27, "Treatment Team", None, "THS (P)", "Tt Hearttransplant Surgery (Primary)", DBUtil.parseDateValue("6/23/2113 7:53"),],
[-15000, -8501, -58, "Treatment Team", None, "TH (P)", "Tt Hematology (Primary)", DBUtil.parseDateValue("5/23/2113 6:47"),],
[-15100, -8961, -39, "Treatment Team", None, "TH (P)", "Tt Hematology (Primary)", DBUtil.parseDateValue("4/28/2113 11:10"),],
[-15200, -3215, -96, "Treatment Team", None, "TH (P)", "Tt Hematology (Primary)", DBUtil.parseDateValue("4/27/2113 7:08"),],
[-15300, -5112, -25, "Treatment Team", None, "TH (P)", "Tt Hematology (Primary)", DBUtil.parseDateValue("4/29/2113 6:58"),],
[-15400, -4659, -77, "Treatment Team", None, "TH (C)", "Tt Hematology (Consulting)", DBUtil.parseDateValue("5/21/2110 15:36"),],
[-15500, -8230, -95, "Treatment Team", None, "THS (P)", "Tt Hpb Surgery (Primary)", DBUtil.parseDateValue("8/1/2113 11:37"),],
[-15600, -4122, -28, "Treatment Team", None, "TIR (C)", "Tt Interventional Radiology (Consulting)", DBUtil.parseDateValue("10/1/2109 15:49"),],
[-15700, -8600, -91, "Treatment Team", None, "TIR2 (C)", "Tt Interventional Radiology 2Rads (Consulting)", DBUtil.parseDateValue("8/26/2113 21:35"),],
[-15800, -5557, -37, "Treatment Team", None, "TKPT (P)", "Tt Kidney Pancreas Transplant (Primary)", DBUtil.parseDateValue("10/19/2109 16:41"),],
[-15900, -2062, -5, "Treatment Team", None, "TLT (P)", "Tt Liver Transplant (Primary)", DBUtil.parseDateValue("3/26/2113 0:09"),],
[-16000, -5394, -95, "Treatment Team", None, "TLT (P)", "Tt Lung Transplant (Primary)", DBUtil.parseDateValue("12/6/2113 16:18"),],
[-16100, -3498, -87, "Treatment Team", None, "TMN (P)", "Tt Med Nocturnist (Primary)", DBUtil.parseDateValue("12/8/2113 22:31"),],
[-16200, -2935, -68, "Treatment Team", None, "TMP (P)", "Tt Med Pamf (Primary)", DBUtil.parseDateValue("4/18/2111 18:49"),],
[-16300, -12, -58, "Treatment Team", None, "TMT (P)", "Tt Med Team (Primary)", DBUtil.parseDateValue("10/21/2112 21:48"),],
[-16400, -1078, -22, "Treatment Team", None, "TMT (C)", "Tt Med Team (Consulting)", DBUtil.parseDateValue("6/30/2111 13:55"),],
[-16500, -6187, -96, "Treatment Team", None, "TMTC (P)", "Tt Med Tx Cards (Primary)", DBUtil.parseDateValue("11/15/2113 15:20"),],
[-16600, -3081, -86, "Treatment Team", None, "TMTC (P)", "Tt Med Tx Cards (Primary)", DBUtil.parseDateValue("12/14/2113 17:16"),],
[-16700, -4592, -52, "Treatment Team", None, "TMTH (P)", "Tt Med Tx Hep (Primary)", DBUtil.parseDateValue("11/16/2113 17:43"),],
[-16800, -2790, 0, "Treatment Team", None, "TMTH (P)", "Tt Med Tx Hep (Primary)", DBUtil.parseDateValue("11/26/2113 6:54"),],
[-16900, -6295, -58, "Treatment Team", None, "TMTH (P)", "Tt Med Tx Hep (Primary)", DBUtil.parseDateValue("5/21/2113 22:19"),],
[-17000, -6269, -39, "Treatment Team", None, "TMTH (P)", "Tt Med Tx Hep (Primary)", DBUtil.parseDateValue("3/15/2111 11:24"),],
[-17100, -9903, -24, "Treatment Team", None, "TMTH (C)", "Tt Med Tx Hep (Consulting)", DBUtil.parseDateValue("11/30/2111 5:55"),],
[-17200, -3857, -21, "Treatment Team", None, "TMTR (P)", "Tt Med Tx Renal (Primary)", DBUtil.parseDateValue("5/17/2113 22:58"),],
[-17300, -9724, -72, "Treatment Team", None, "TMT (P)", "Tt Med Tx-Hep (Primary)", DBUtil.parseDateValue("2/24/2110 20:49"),],
[-17400, -7255, -7, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("10/23/2109 14:00"),],
[-17500, -8317, -2, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("5/17/2109 21:16"),],
[-17600, -1343, -8, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("8/24/2113 7:24"),],
[-17700, -7747, -66, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("1/16/2109 16:24"),],
[-17800, -6462, -30, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("11/23/2109 19:30"),],
[-17900, -9668, -62, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("9/16/2109 19:42"),],
[-18000, -9725, -79, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("7/28/2109 7:55"),],
[-18100, -9956, -2, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("2/10/2109 16:53"),],
[-18200, -7732, -25, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("9/7/2113 9:27"),],
[-18300, -5125, -78, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("2/4/2109 21:33"),],
[-18400, -8355, -50, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("5/12/2109 23:58"),],
[-18500, -1888, -80, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("5/1/2113 14:52"),],
[-18600, -4768, -11, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("12/18/2113 16:00"),],
[-18700, -5946, -98, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("5/4/2113 17:20"),],
[-18800, -8631, -78, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("8/8/2113 11:48"),],
[-18900, -6561, -64, "Treatment Team", None, "TMU (P)", "Tt Med Univ (Primary)", DBUtil.parseDateValue("4/7/2109 8:29"),],
[-19000, -6209, -68, "Treatment Team", None, "TM (P)", "Tt Med9 (Primary)", DBUtil.parseDateValue("1/22/2113 19:33"),],
[-19100, -5810, -31, "Treatment Team", None, "TM (P)", "Tt Med9 (Primary)", DBUtil.parseDateValue("2/8/2113 19:58"),],
[-19200, -223, -19, "Treatment Team", None, "TM (P)", "Tt Med9 (Primary)", DBUtil.parseDateValue("2/8/2113 12:27"),],
[-19300, -1005, -94, "Treatment Team", None, "TM (P)", "Tt Micu (Primary)", DBUtil.parseDateValue("6/23/2110 19:47"),],
[-19400, -6309, -84, "Treatment Team", None, "TM (P)", "Tt Micu (Primary)", DBUtil.parseDateValue("10/24/2109 13:55"),],
[-19500, -5142, -63, "Treatment Team", None, "TM (P)", "Tt Micu (Primary)", DBUtil.parseDateValue("7/21/2110 12:02"),],
[-19600, -7779, -8, "Treatment Team", None, "TM (P)", "Tt Micu (Primary)", DBUtil.parseDateValue("9/18/2109 20:55"),],
[-19700, -2417, -76, "Treatment Team", None, "TMIS (P)", "Tt Minimally Invasive Surgery (Primary)", DBUtil.parseDateValue("1/10/2114 20:58"),],
[-19800, -6697, -4, "Treatment Team", None, "TNEMU (P)", "Tt Neuro Epilepsy Monitor Unit (Primary)", DBUtil.parseDateValue("3/2/2110 18:52"),],
[-19900, -3038, -98, "Treatment Team", None, "TNEMU (P)", "Tt Neuro Epilepsy Monitor Unit (Primary)", DBUtil.parseDateValue("1/19/2114 11:34"),],
[-20000, -3672, -96, "Treatment Team", None, "TNS (P)", "Tt Neuro Stroke (Primary)", DBUtil.parseDateValue("10/16/2113 12:36"),],
[-20100, -3014, -56, "Treatment Team", None, "TNS (P)", "Tt Neuro Stroke (Primary)", DBUtil.parseDateValue("10/16/2113 6:11"),],
[-20200, -9587, -80, "Treatment Team", None, "TN (P)", "Tt Neurology (Primary)", DBUtil.parseDateValue("10/15/2113 23:35"),],
[-20300, -9618, -81, "Treatment Team", None, "TN (P)", "Tt Neurology (Primary)", DBUtil.parseDateValue("7/17/2113 23:38"),],
[-20400, -7764, -19, "Treatment Team", None, "TN (P)", "Tt Neurology (Primary)", DBUtil.parseDateValue("10/26/2109 18:55"),],
[-20500, -5985, -40, "Treatment Team", None, "TNVF (P)", "Tt Neurosurgery Vascular Floor (Primary)", DBUtil.parseDateValue("3/5/2113 7:32"),],
[-20600, -3920, -95, "Treatment Team", None, "TNVI (C)", "Tt Neurosurgery Vascular Icu (Consulting)", DBUtil.parseDateValue("4/15/2113 16:11"),],
[-20700, -4463, -59, "Treatment Team", None, "TN (P)", "Tt Neurosurgery (Primary)", DBUtil.parseDateValue("7/18/2110 13:30"),],
[-20800, -7556, -46, "Treatment Team", None, "TNTF (P)", "Tt Neurosurgery Tumor Floor (Primary)", DBUtil.parseDateValue("6/18/2113 7:15"),],
[-20900, -5245, -4, "Treatment Team", None, "TNTI (P)", "Tt Neurosurgery Tumor Icu (Primary)", DBUtil.parseDateValue("4/27/2113 10:58"),],
[-21000, -2727, -85, "Treatment Team", None, "TN (P)", "Tt Neurosurgery (Primary)", DBUtil.parseDateValue("3/26/2110 17:57"),],
[-21100, -4073, -25, "Treatment Team", None, "TNSF (C)", "Tt Neurosurgery Spine Floor (Consulting)", DBUtil.parseDateValue("12/31/2112 20:55"),],
[-21200, -4198, -90, "Treatment Team", None, "TNSI (C)", "Tt Neurosurgery Spine Icu (Consulting)", DBUtil.parseDateValue("5/31/2113 2:58"),],
[-21300, -3735, -48, "Treatment Team", None, "TN (P)", "Tt Neurosurgery (Primary)", DBUtil.parseDateValue("4/23/2110 13:04"),],
[-21400, -732, -41, "Treatment Team", None, "TNF (C)", "Tt Neurosurgery Floor (Consulting)", DBUtil.parseDateValue("8/26/2113 21:00"),],
[-21500, -4812, -19, "Treatment Team", None, "TNIO (P)", "Tt Neurosurgery Icu/Resident On-Call (Primary)", DBUtil.parseDateValue("7/11/2113 12:19"),],
[-21600, -4812, -19, "Treatment Team", None, "TN (P)", "Tt Neurosurgery (Primary)", DBUtil.parseDateValue("7/6/2110 10:30"),],
[-21700, -3583, -41, "Treatment Team", None, "TOSMC (P)", "Tt Ob San Mateo County (Primary)", DBUtil.parseDateValue("11/24/2111 6:46"),],
[-21800, -3229, -93, "Treatment Team", None, "TOU (P)", "Tt Ob University (Primary)", DBUtil.parseDateValue("8/1/2113 21:43"),],
[-21900, -3229, -49, "Treatment Team", None, "TO (P)", "Tt Oncology (Primary)", DBUtil.parseDateValue("3/26/2113 7:19"),],
[-22000, -6011, -37, "Treatment Team", None, "TO (P)", "Tt Oncology (Primary)", DBUtil.parseDateValue("7/1/2113 13:34"),],
[-22100, -305, -43, "Treatment Team", None, "TO (P)", "Tt Oncology (Primary)", DBUtil.parseDateValue("1/14/2114 7:37"),],
[-22200, -5666, -98, "Treatment Team", None, "TO (P)", "Tt Oncology (Primary)", DBUtil.parseDateValue("4/6/2113 7:24"),],
[-22300, -9992, -35, "Treatment Team", None, "TO (P)", "Tt Oncology (Primary)", DBUtil.parseDateValue("12/3/2109 8:10"),],
[-22400, -8288, -32, "Treatment Team", None, "TO (P)", "Tt Ophthalmology (Primary)", DBUtil.parseDateValue("10/5/2113 12:01"),],
[-22500, -7739, -47, "Treatment Team", None, "TOAJ (P)", "Tt Ortho Arthritis (Joint) (Primary)", DBUtil.parseDateValue("9/12/2113 8:23"),],
[-22600, -9491, -39, "Treatment Team", None, "TOFA (P)", "Tt Ortho Foot Ankle (Primary)", DBUtil.parseDateValue("1/22/2110 14:51"),],
[-22700, -4602, -91, "Treatment Team", None, "TOF (P)", "Tt Ortho Foot/Ankle (Primary)", DBUtil.parseDateValue("12/22/2113 9:09"),],
[-22800, -7546, -78, "Treatment Team", None, "TOH (C)", "Tt Ortho Hand (Consulting)", DBUtil.parseDateValue("8/27/2113 0:41"),],
[-22900, -1266, -66, "Treatment Team", None, "TOJ (P)", "Tt Ortho Joint (Primary)", DBUtil.parseDateValue("3/8/2111 7:32"),],
[-23000, -2426, -46, "Treatment Team", None, "TOO (P)", "Tt Ortho Oncology (Primary)", DBUtil.parseDateValue("9/23/2113 16:34"),],
[-23100, -2837, -81, "Treatment Team", None, "TOS (P)", "Tt Ortho Shoulder/Elbow (Primary)", DBUtil.parseDateValue("1/23/2114 6:37"),],
[-23200, -1365, -79, "Treatment Team", None, "TOS (P)", "Tt Ortho Spine (Primary)", DBUtil.parseDateValue("10/25/2109 22:02"),],
[-23300, -7799, -15, "Treatment Team", None, "TOS (P)", "Tt Ortho Spine (Primary)", DBUtil.parseDateValue("10/14/2113 18:11"),],
[-23400, -8843, -96, "Treatment Team", None, "TOS (P)", "Tt Ortho Sports (Primary)", DBUtil.parseDateValue("9/4/2113 7:50"),],
[-23500, -6483, -28, "Treatment Team", None, "TOS (P)", "Tt Ortho Surgery (Primary)", DBUtil.parseDateValue("5/9/2110 5:29"),],
[-23600, -6483, -28, "Treatment Team", None, "TOT (P)", "Tt Ortho Trauma (Primary)", DBUtil.parseDateValue("11/7/2111 8:57"),],
[-23700, -6483, -28, "Treatment Team", None, "TOT (P)", "Tt Ortho Trauma (Primary)", DBUtil.parseDateValue("12/27/2113 5:02"),],
[-23800, -6483, -28, "Treatment Team", None, "TOT (P)", "Tt Ortho Tumor (Primary)", DBUtil.parseDateValue("4/4/2110 19:33"),],
[-23900, -6434, -31, "Treatment Team", None, "TP (P)", "Tt Pain (Primary)", DBUtil.parseDateValue("6/3/2111 17:15"),],
[-24000, -1874, -70, "Treatment Team", None, "TP (P)", "Tt Pain (Primary)", DBUtil.parseDateValue("4/10/2110 12:17"),],
[-24100, -9149, -90, "Treatment Team", None, "TPGS (P)", "Tt Pamf (Gen Surg) (Primary)", DBUtil.parseDateValue("4/26/2113 5:27"),],
[-24200, -4935, -32, "Treatment Team", None, "TPN (P)", "Tt Pamf (Neurosurg) (Primary)", DBUtil.parseDateValue("9/7/2113 7:38"),],
[-24300, -4935, -32, "Treatment Team", None, "TPM (P)", "Tt Pamf Med (Primary)", DBUtil.parseDateValue("5/9/2109 7:30"),],
[-24400, -4935, -32, "Treatment Team", None, "TPM (P)", "Tt Pamf Med (Primary)", DBUtil.parseDateValue("7/28/2109 8:05"),],
[-24500, -4550, -62, "Treatment Team", None, "TPM (P)", "Tt Pamf Med (Primary)", DBUtil.parseDateValue("6/10/2109 23:47"),],
[-24600, -4550, -62, "Treatment Team", None, "TPM (P)", "Tt Pamf Med (Primary)", DBUtil.parseDateValue("4/16/2113 7:00"),],
[-24700, -3954, -61, "Treatment Team", None, "TPM (P)", "Tt Pamf Med (Primary)", DBUtil.parseDateValue("4/18/2113 7:00"),],
[-24800, -3954, -61, "Treatment Team", None, "TPM (P)", "Tt Pamf Med (Primary)", DBUtil.parseDateValue("11/8/2113 13:52"),],
[-24900, -3954, -61, "Treatment Team", None, "TPMA (P)", "Tt Pamf Med/Cards Admitting (Primary)", DBUtil.parseDateValue("4/1/2113 7:00"),],
[-25000, -3954, -61, "Treatment Team", None, "TP (P)", "Tt Pamf(Ent) (Primary)", DBUtil.parseDateValue("3/7/2113 9:13"),],
[-25100, -3954, -61, "Treatment Team", None, "TP (P)", "Tt Pamf(Ep) (Primary)", DBUtil.parseDateValue("2/17/2112 15:44"),],
[-25200, -1614, -42, "Treatment Team", None, "TP (P)", "Tt Pamf(Ortho) (Primary)", DBUtil.parseDateValue("9/11/2113 13:52"),],
[-25300, -1614, -42, "Treatment Team", None, "TP (P)", "Tt Pamf(Plastics) (Primary)", DBUtil.parseDateValue("9/2/2113 13:00"),],
[-25400, -1614, -42, "Treatment Team", None, "TP (P)", "Tt Pamf(Urology) (Primary)", DBUtil.parseDateValue("9/4/2113 13:59"),],
[-25500, -1614, -42, "Treatment Team", None, "TPMR (P)", "Tt Physical Med Rehab (Primary)", DBUtil.parseDateValue("1/6/2113 0:14"),],
[-25600, -6234, -95, "Treatment Team", None, "TPSC (C)", "Tt Plastic Surgery Consults (Consulting)", DBUtil.parseDateValue("11/9/2113 20:33"),],
[-25700, -900, -45, "Treatment Team", None, "TPS (P)", "Tt Plastic Surgery (Primary)", DBUtil.parseDateValue("6/27/2111 9:34"),],
[-25800, -6187, -3, "Treatment Team", None, "TPS (P)", "Tt Plastic Surgery (Primary)", DBUtil.parseDateValue("11/26/2113 9:40"),],
[-25900, -1471, -23, "Treatment Team", None, "TP (C)", "Tt Psychiatry (Consulting)", DBUtil.parseDateValue("4/14/2113 18:43"),],
[-26000, -9067, -86, "Treatment Team", None, "TPH (P)", "Tt Pulm Htn (Primary)", DBUtil.parseDateValue("10/29/2113 21:18"),],
[-26100, -292, -42, "Treatment Team", None, "TPH (P)", "Tt Pulm Htn (Primary)", DBUtil.parseDateValue("1/24/2113 20:01"),],
[-26200, -5490, -12, "Treatment Team", None, "TPT (P)", "Tt Pulmonary Transplant (Primary)", DBUtil.parseDateValue("12/26/2111 14:41"),],
[-26300, -577, -64, "Treatment Team", None, "TS (C)", "Tt Sicu (Consulting)", DBUtil.parseDateValue("10/2/2109 19:07"),],
[-26400, -2476, -94, "Treatment Team", None, "TSO (P)", "Tt Surgical Oncology (Primary)", DBUtil.parseDateValue("4/10/2113 18:41"),],
[-26500, -7826, -60, "Treatment Team", None, "TSO (P)", "Tt Surgical Oncology (Primary)", DBUtil.parseDateValue("4/21/2113 1:06"),],
[-26600, -8138, -95, "Treatment Team", None, "TU (C)", "Tt Urology (Consulting)", DBUtil.parseDateValue("2/19/2110 0:37"),],
[-26700, -8302, -86, "Treatment Team", None, "TU (P)", "Tt Urology (Primary)", DBUtil.parseDateValue("8/26/2113 9:09"),],
[-26800, -8694, -68, "Treatment Team", None, "TV (P)", "Tt Vad (Primary)", DBUtil.parseDateValue("11/6/2113 7:54"),],
[-26900, -6011, -84, "Treatment Team", None, "TVS (C)", "Tt Vascular Surgery (Consulting)", DBUtil.parseDateValue("4/23/2113 5:59"),],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestSTRIDETreatmentTeamConversion("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestSTRIDETreatmentTeamConversion("test_insertFile_skipErrors"));
    #suite.addTest(TestSTRIDETreatmentTeamConversion('test_executeIterator'));
    #suite.addTest(TestSTRIDETreatmentTeamConversion('test_dataConversion_aggregate'));
    suite.addTest(unittest.makeSuite(TestSTRIDETreatmentTeamConversion));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
