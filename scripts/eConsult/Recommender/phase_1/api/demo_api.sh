#!/bin/bash

# Medical Recommender API - Live cURL Demo (User Input)
# ========================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_step() {
    echo -e "${YELLOW}$1${NC}"
}

print_json() {
    if command -v jq &>/dev/null; then
        echo "$1" | jq
    else
        echo "$1"
    fi
}

# === Prompt user for input ===
echo -e "${YELLOW}Please enter the clinical question:${NC}"
read -r CLINICAL_QUESTION

echo -e "${YELLOW}Please enter the clinical notes:${NC}"
read -r CLINICAL_NOTES

# Escape quotes and newlines for JSON
CLINICAL_QUESTION_ESCAPED=$(printf '%s' "$CLINICAL_QUESTION" | python3 -c 'import sys, json; print(json.dumps(sys.stdin.read().strip()))')
CLINICAL_NOTES_ESCAPED=$(printf '%s' "$CLINICAL_NOTES" | python3 -c 'import sys, json; print(json.dumps(sys.stdin.read().strip()))')

# 1. Process a clinical case
print_header "Step 1: Process a Clinical Case"
print_step "POST /process_clinical_case"

RESPONSE=$(curl -s -X POST "$BASE_URL/process_clinical_case" \
    -H 'Content-Type: application/json' \
    -d '{
        "clinical_question": '"$CLINICAL_QUESTION_ESCAPED"',
        "clinical_notes": '"$CLINICAL_NOTES_ESCAPED"'
    }')

print_json "$RESPONSE"

ICD10_CODE=$(echo "$RESPONSE" | jq -r .icd10_code 2>/dev/null)
PATIENT_AGE=$(echo "$RESPONSE" | jq -r .patient_age 2>/dev/null)
PATIENT_GENDER=$(echo "$RESPONSE" | jq -r .patient_gender 2>/dev/null)

if [[ "$ICD10_CODE" == "null" || -z "$ICD10_CODE" ]]; then
    echo -e "${RED}Clinical case failed. Error: $(echo "$RESPONSE" | jq -r .error 2>/dev/null)${NC}"
    exit 1
fi

# 2. Get recommended orders for this case (all types)
print_header "Step 2: Get Recommended Orders"
print_step "POST /get_orders"

ORDERS_PAYLOAD=$(cat <<EOF
{
    "icd10_code": "$ICD10_CODE",
    "patient_age": $PATIENT_AGE,
    "patient_gender": "$PATIENT_GENDER",
    "result_type": null,
    "limit": 5
}
EOF
)

ORDERS_RESPONSE=$(curl -s -X POST "$BASE_URL/get_orders" \
    -H 'Content-Type: application/json' \
    -d "$ORDERS_PAYLOAD")

print_json "$ORDERS_RESPONSE"

echo -e "${GREEN}Demo completed.${NC}"
