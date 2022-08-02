README.txt

Inpatient Cost Variability

# loading data into BigQuery: TechIPbyGL_CostCategory (FY20, FY21)
1. Modify raw data: remove last row (totals)
2. Modify raw data: all columns A through BE: replace " -   " with ""
3. Modify raw data: all columns A through BE: format cells as "General" (ensure no commas delimiting thousands for #'s)
4. Upload parameters: Header rows to skip: 2
5. Upload instructions: upload to BigQuery (use schema below). NOTE: columns (and schema) vary between years, see below.
6. Upload instructions: First upload FY20 data. Check schema with raw data to ensure columns match.
7. Upload instructions: Now go into table on BigQuery and edit schema, add any missing columns from FY21 data (ie. VCCPharmacy)
8. Upload instructions: Now upload FY21 data with its respective schema (ensure schema matches data)


# loading data into BigQuery: TechIPbyUB_CostBucket (FY20, FY21) (UB = universal billing)
1. Modify raw data: format first two columns (admit & discharge dates) in Excel as YYYY-MM-DD (req for BigQuery "date" field)
2. Modify raw data: columns L through AD (costs): replace " -   " with ""
3. Modify raw data: columns L through AD (costs): format cells as "General" (ensure no commas delimiting thousands for #'s)
4. Modify raw data: column D (MRN): replace "<E" and ">" with ""
5. Modify raw data: Split .XLSX files containing multiple sheets into multiple .csv files (size <100MB each)
6. Upload parameters: upload to BigQuery (use schema below)
7. Upload parameters: Header rows to skip: 1
8. Upload parameters: Number of errors allowed: 500. Skip extraneous outlier rows that have unsupported decimals (>9 decimals, which exceed BigQuery "NUMERIC" datatype restrictions). NUMERIC will suffice for >99.99% of data rows. We COULD circumvent this by altering the table schema to cast all Cost columns as BIGNUMERIC, however table alterations aren't supported in BigQuery and require workarounds (ie. copying data into new, redefined table). Better to exclude the rare edge cases.
9. Upload parameters: Write preferences: Append to pre-existing table (if already created)

# table schema: TechIPbyGL (FY21)
[
  {
    "name": "Account",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "Depreciation_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Depreciation of 500P. Total Direct Cost."
  },
  {
    "name": "Benefits_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Clinical_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "COVID19_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "COVID19vaccine_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "CV_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"CVH APP\" (cardiovascular health). Total Direct Cost."
  },
  {
    "name": "Facilities_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Housestaff_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Inpatient_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"IP APP\" (inpatient). Total Direct Cost."
  },
  {
    "name": "Management_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Supplies_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Medical Supplies\". Total Direct Cost."
  },
  {
    "name": "NonClinical_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Nursing_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Oncology_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Onc APP\". Total Direct Cost."
  },
  {
    "name": "OtherExpense_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Other Expense\". Total Direct Cost."
  },
  {
    "name": "OtherRevenue_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Other Revenue\" Total Direct Cost."
  },
  {
    "name": "OtherSupplies_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Pharmacy_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Physician_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Physician Services. Total Direct Cost."
  },
  {
    "name": "ProductLine_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Product Line\". Total Direct Cost."
  },
  {
    "name": "Prosthesis_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "PurchasedServices_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Purchased Services\". Total Direct Cost."
  },
  {
    "name": "Physician_Tier1_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Tier 1 Physician Services\". Total Direct Cost."
  },
  {
    "name": "Transplant_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "VCCImplant_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"VCCImplant\". Total Direct Cost."
  },
  {
    "name": "VCCMedSupp_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"VCCMedSupp\". Total Direct Cost."
  },
  {
    "name": "VCCPharmacy_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Depreciation_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Depreciation of 500P. Total Indirect Cost."
  },
  {
    "name": "Benefits_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Clinical_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "COVID19_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "COVID19vaccine_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "CV_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"CVH APP\" (cardiovascular health). Total Indirect Cost."
  },
  {
    "name": "Facilities_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Housestaff_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Inpatient_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"IP APP\" (inpatient). Total Indirect Cost."
  },
  {
    "name": "Management_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Supplies_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Medical Supplies\". Total Indirect Cost."
  },
  {
    "name": "NonClinical_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Nursing_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Oncology_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Onc APP\". Total Indirect Cost."
  },
  {
    "name": "OtherExpense_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Other Expense\". Total Indirect Cost."
  },
  {
    "name": "OtherRevenue_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Other Revenue\" Total Indirect Cost."
  },
  {
    "name": "OtherSupplies_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Pharmacy_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Physician_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Physician Services. Total Indirect Cost."
  },
  {
    "name": "ProductLine_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Product Line\". Total Indirect Cost."
  },
  {
    "name": "Prosthesis_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "PurchasedServices_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Purchased Services\". Total Indirect Cost."
  },
  {
    "name": "Physician_Tier1_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Tier 1 Physician Services\". Total Indirect Cost."
  },
  {
    "name": "Transplant_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "VCCImplant_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"VCCImplant\". Total Indirect Cost."
  },
  {
    "name": "VCCMedSupp_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"VCCMedSupp\". Total Indirect Cost."
  },
  {
    "name": "VCCPharmacy_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "TotalCost_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Sum of Total Direct Costs."
  },
  {
    "name": "TotalCost_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Sum of Total Indirect Costs."
  }
]

# table schema: TechIPbyGL (FY20)
[
  {
    "name": "Account",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "Depreciation_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Depreciation of 500P. Total Direct Cost."
  },
  {
    "name": "BadDebt_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Benefits_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Clinical_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "COVID19_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "COVID19vaccine_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "CV_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"CVH APP\" (cardiovascular health). Total Direct Cost."
  },
  {
    "name": "Facilities_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Housestaff_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Inpatient_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"IP APP\" (inpatient). Total Direct Cost."
  },
  {
    "name": "Management_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Supplies_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Medical Supplies\". Total Direct Cost."
  },
  {
    "name": "NonClinical_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Nursing_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Oncology_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Onc APP\". Total Direct Cost."
  },
  {
    "name": "OtherExpense_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Other Expense\". Total Direct Cost."
  },
  {
    "name": "OtherRevenue_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Other Revenue\" Total Direct Cost."
  },
  {
    "name": "OtherSupplies_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Pharmacy_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "Physician_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Physician Services. Total Direct Cost."
  },
  {
    "name": "ProductLine_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Product Line\". Total Direct Cost."
  },
  {
    "name": "Prosthesis_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "PurchasedServices_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Purchased Services\". Total Direct Cost."
  },
  {
    "name": "Physician_Tier1_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Tier 1 Physician Services\". Total Direct Cost."
  },
  {
    "name": "Transplant_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Direct Cost."
  },
  {
    "name": "VCCImplant_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"VCCImplant\". Total Direct Cost."
  },
  {
    "name": "VCCMedSupp_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"VCCMedSupp\". Total Direct Cost."
  },
  {
    "name": "Depreciation_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Depreciation of 500P. Total Indirect Cost."
  },
  {
    "name": "BadDebt_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Benefits_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Clinical_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "COVID19_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "COVID19vaccine_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "CV_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"CVH APP\" (cardiovascular health). Total Indirect Cost."
  },
  {
    "name": "Facilities_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Housestaff_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Inpatient_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"IP APP\" (inpatient). Total Indirect Cost."
  },
  {
    "name": "Management_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Supplies_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Medical Supplies\". Total Indirect Cost."
  },
  {
    "name": "NonClinical_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Nursing_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Oncology_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Onc APP\". Total Indirect Cost."
  },
  {
    "name": "OtherExpense_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Other Expense\". Total Indirect Cost."
  },
  {
    "name": "OtherRevenue_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Other Revenue\" Total Indirect Cost."
  },
  {
    "name": "OtherSupplies_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Pharmacy_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "Physician_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Physician Services. Total Indirect Cost."
  },
  {
    "name": "ProductLine_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Product Line\". Total Indirect Cost."
  },
  {
    "name": "Prosthesis_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "PurchasedServices_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Purchased Services\". Total Indirect Cost."
  },
  {
    "name": "Physician_Tier1_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"Tier 1 Physician Services\". Total Indirect Cost."
  },
  {
    "name": "Transplant_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Total Indirect Cost."
  },
  {
    "name": "VCCImplant_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"VCCImplant\". Total Indirect Cost."
  },
  {
    "name": "VCCMedSupp_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "\"VCCMedSupp\". Total Indirect Cost."
  },
  {
    "name": "TotalCost_Direct",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Sum of Total Direct Costs."
  },
  {
    "name": "TotalCost_Indirect",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Sum of Total Indirect Costs."
  }
]

# table schema: TechIPbyUB
[
    {
        "name": "AdmitDate",
        "type": "DATE",
        "mode": "NULLABLE"
    },
    {
        "name": "DischargeDate",
        "type": "DATE",
        "mode": "NULLABLE"
    },
    {
        "name": "LOS",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "MRN",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "VisitCount",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "MSDRGweight",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Weighting for Medical Severity (MS) DRG per encounter"
    },
    {
        "name": "Account",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "Inpatient_C",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "O (outpatient), I (inpatient)"
    },
    {
        "name": "Inpatient",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Outpatient, Inpatient"
    },
    {
        "name": "ServiceCategory_C",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "P (professional), T (technical)"
    },
    {
        "name": "ServiceCategory",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Professional, Technical"
    },
    {
        "name": "Cost_Direct",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Costs (UB = universal billing): Total Direct"
    },
    {
        "name": "Cost_Indirect",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Costs (UB = universal billing): Total Indirect"
    },
    {
        "name": "Cost_Total",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Costs (UB = universal billing): Grand Total"
    },
    {
        "name": "Cost_Breakdown_Blood",
        "type": "NUMERIC",
        "mode": "NULLABLE"
    },
    {
        "name": "Cost_Breakdown_Cardiac",
        "type": "NUMERIC",
        "mode": "NULLABLE"
    },
    {
        "name": "Cost_Breakdown_ED",
        "type": "NUMERIC",
        "mode": "NULLABLE"
    },
    {
        "name": "Cost_Breakdown_ICU",
        "type": "NUMERIC",
        "mode": "NULLABLE"
    },
    {
        "name": "Cost_Breakdown_IICU",
        "type": "NUMERIC",
        "mode": "NULLABLE"
    },
    {
        "name": "Cost_Breakdown_Imaging",
        "type": "NUMERIC",
        "mode": "NULLABLE"
    },
    {
        "name": "Cost_Breakdown_Labs",
        "type": "NUMERIC",
        "mode": "NULLABLE"
    },
    {
        "name": "Cost_Breakdown_Implants",
        "type": "NUMERIC",
        "mode": "NULLABLE"
    },
    {
        "name": "Cost_Breakdown_Supplies",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "UB M/S Supplies w/o Implants"
    },
    {
        "name": "Cost_Breakdown_OR",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Operating Room services"
    },
    {
        "name": "Cost_Breakdown_OrganAcq",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Organ acquisition"
    },
    {
        "name": "Cost_Breakdown_Other",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Costs: Other (alternate)"
    },
    {
        "name": "Cost_Breakdown_PTOT",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Costs: PT/OT/ST"
    },
    {
        "name": "Cost_Breakdown_Resp",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Costs: Resp therapy"
    },
    {
        "name": "Cost_Breakdown_Accom",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Costs: Routine Accommodation"
    },
    {
        "name": "Cost_Breakdown_Pharmacy",
        "type": "NUMERIC",
        "mode": "NULLABLE",
        "description": "Costs d/t RX & IV therapy"
    },
    {
        "name": "BillingStatus_C",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "F (final billed)"
    },
    {
        "name": "BillingStatus",
        "type": "STRING",
        "mode": "NULLABLE"
    }
]

