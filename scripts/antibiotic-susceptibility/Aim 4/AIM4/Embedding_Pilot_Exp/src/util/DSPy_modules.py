import dspy
import pandas as pd
import json
import logging

# class ErrorIdentifierModule:
#     def __init__(self):
#         pass

#     def build_prompt(self, index, patient_message, llm_response, patient_info, clinical_notes, previous_messages, retrieved_pairs=""):
#         # logging.info(f"building prompt for patient_info: {patient_info}")
#         # logging.info(f"clinical_notes: {clinical_notes}")

#         broad_error_categories = """
# Common areas where errors may occur in clinical communication include:
# 1. Clinical Reasoning
# 2. Communication Quality & Readability
# 3. Privacy & Security
# 4. Accessibility
# 5. Bias & Stigmatization

# These are only examples—use your full expertise to spot *any* issues, including ones not explicitly listed here.
# """
#         instruction = f"""
# You are a clinical informatics reviewer. Your job is to evaluate the quality, safety, and appropriateness of an AI-generated response to a patient (or family/caregiver) message.

# You are provided:
# - The patient's message (which may sometimes be written by a family member on the patient’s behalf)
# - The AI-generated response
# - Basic patient info
# - Clinical notes (recent chart notes, context, pending actions, etc.)
# - Previous messgaes between this patient and the actual provider leading to this current message 
# - Optional: Reference message–response pairs from previous similar cases (use only as background context)

# INPUT STARTS
# {{
#   "index": {index}, 
#   "patient_message": "{patient_message}",
#   "llm_response": "{llm_response}",
#   "patient_info": "{patient_info}",
#   "clinical_notes": "{clinical_notes}",
#   "previous_messages": "{previous_messages}",
#   "retrieved_pairs": "{retrieved_pairs}",
# }}
# INPUT ENDS

# **Guidelines:**
# - Consider *who* is asking, *for whom*, and *why*—think practically and clinically.
# - Be sure to use all available context (patient info, clinical notes, previous messages, retrieved pairs, etc.) for your analysis and reasoning—use the full information even if any field is very long.
# - However, **only** the following fields may be truncated in your output JSON (and only if they are very long or contain content that could break JSON, such as unescaped line breaks or quotes): `patient_info`, `clinical_notes`, `previous_messages`, `retrieved_pairs`.
# - If you truncate any of these four fields in your output, indicate this clearly (e.g., by ending the field with [truncated]). But your reasoning and error assessment should always be based on the full information, never on the truncated text.
# - All other fields (such as index, patient_message, llm_response, error_present, error_summary, and reasoning) must be complete and valid in your output.
# - Look for any type of error—not just those in the list below.

# {broad_error_categories}

# **Instructions:**
# 1. Decide if there is *any* error in the AI response (think broadly and comprehensively).
# 2. If yes, summarize in detail what the error is. 
# 3. If no error, explain clearly why the response is safe, accurate, relevant, and appropriate for this situation.
# 4. Justify your answer using details from the case.

# Return ONLY this JSON, with all keys included no matter what (use "" for any field if needed):

# {{
#   "index": {index}, 
#   "patient_message": "{patient_message}",
#   "llm_response": "{llm_response}", 
#   "patient_info": "", // always include this key; leave blank or end with [truncated] if too long
#   "clinical_notes": "", // always include this key; leave blank or end with [truncated] if too long
#   "previous_messages": "", // always include this key; leave blank or end with [truncated] if too long
#   "retrieved_pairs": "", // always include this key; leave blank or end with [truncated] if too long
#   "error_present": true/false, // write true or false (no quotes)
#   "error_summary": "...",   // concise summary of error(s), or empty if none
#   "reasoning": "..."        // detailed justification and clinical reasoning
# }}
# """
#         return instruction
  

class ErrorIdentifierModule:
    def __init__(self):
        pass

    def build_prompt(self, index, patient_message, llm_response, patient_info, clinical_notes, previous_messages, retrieved_pairs=""):
        # logging.info(f"building prompt for patient_info: {patient_info}")
        # logging.info(f"clinical_notes: {clinical_notes}")

        broad_error_categories = """
Common areas where errors may occur in clinical communication include:
1. Clinical Reasoning
2. Communication Quality & Readability
3. Privacy & Security
4. Accessibility
5. Bias & Stigmatization

These are only examples—use your full expertise to spot *any* issues, including ones not explicitly listed here.
"""
        instruction = f"""
You are a clinical informatics reviewer. Your job is to evaluate the quality, safety, and appropriateness of an AI-generated response to a patient (or family/caregiver) message.

You are provided:
- The patient's message (which may sometimes be written by a family member on the patient’s behalf)
- The AI-generated response
- Basic patient info
- Clinical notes (recent chart notes, context, pending actions, etc.)
- Previous messgaes between this patient and the actual provider leading to this current message 
- Optional: Reference message–response pairs from previous similar cases (use only as background context)

**Guidelines:**
- Consider *who* is asking, *for whom*, and *why*—think practically and clinically.
- Be sure to use all available context (patient info, notes, previous messages, references) for your analysis and reasoning, even if a field is very long.
- In your output JSON, **only** the following fields may be truncated due to length: `patient_info`, `clinical_notes`, `previous_messages`, `retrieved_pairs`. If a field is truncated, indicate this clearly by ending the field with [truncated]. 
- Your reasoning and error assessment should always be based on the full information, never on the truncated text.
- Look for any type of error—not just those in the list below.

{broad_error_categories}

**Instructions:**
1. Decide if there is *any* error in the AI response (think broadly and comprehensively).
2. If yes, summarize in detail what the error is. 
3. If no error, explain clearly why the response is safe, accurate, relevant, and appropriate for this situation.
4. Justify your answer using details from the case.

Return ONLY this JSON, with all keys included no matter what (use "" for any field if needed):

{{
  "index": {index}, 
  "patient_message": "{patient_message}",
  "llm_response": "{llm_response}",
  "patient_info": "{patient_info}", // always keep this key; can be truncated if too long
  "clinical_notes": "{clinical_notes}", // always keep this key; can be truncated if too long
  "previous_messages": "{previous_messages}", // always keep this key; can be truncated if too long
  "retrieved_pairs": "{retrieved_pairs}", // always keep this key; can be truncated if too long
  "error_present": true/false,
  "error_summary": "...",   // concise summary of error(s), or empty if none
  "reasoning": "..."        // detailed justification and clinical reasoning
}}
"""
        return instruction

class ErrorLabelerModule:
    def __init__(self, domain: str, codebook: pd.DataFrame):
        self.domain = domain
        self.codebook = codebook

    def extract_example_pairs(self, sd, ec):
        """Return a list of {'patient_message', 'llm_response'} pairs for the (subdomain, error_code), or empty list."""
        example_list = []
        rows = self.codebook[(self.codebook["Dedup Subdomain"] == sd) & (self.codebook["Dedup Error Code"] == ec)]
        if not rows.empty:
            rep_examples_str = rows.iloc[0].get("Representative Examples", "")
            if rep_examples_str and rep_examples_str.strip() != "[]":
                try:
                    rep_examples = json.loads(rep_examples_str)
                    for ex in rep_examples:
                        patient_msg = ex.get("patient_message", "")
                        llm_resp = ex.get("LLM_generated_response", "")
                        if patient_msg or llm_resp:
                            example_list.append({
                                "patient_message": patient_msg,
                                "llm_response": llm_resp
                            })
                except Exception:
                    pass
        return example_list

    def extract_definition(self, sd, ec):
        """Return the definition string for the (subdomain, error_code), or empty string."""
        rows = self.codebook[(self.codebook["Dedup Subdomain"] == sd) & (self.codebook["Dedup Error Code"] == ec)]
        if not rows.empty:
            return rows.iloc[0].get("Dedup Definition", "")
        return ""

#     def build_prompt(self, index: int, error_summary: str):
#         subdomains = sorted(self.codebook["Subdomain"].unique())
#         subdomain_errorcodes = {
#             sd: self.codebook[self.codebook["Subdomain"] == sd]["Dedup Error Code"].tolist()
#             for sd in subdomains
#         }
#         subdomains.append("No subdomain matched")
#         for sd in subdomains:
#             if sd == "No subdomain matched":
#                 subdomain_errorcodes[sd] = ["No error code matched"]
#             elif "No error code matched" not in subdomain_errorcodes[sd]:
#                 subdomain_errorcodes[sd].append("No error code matched")

#         grid_str = ""
#         for sd in subdomains:
#             grid_str += f"\n- Subdomain: {sd}\n"
#             for ec in subdomain_errorcodes[sd]:
#                 definition = self.extract_definition(sd, ec)
#                 # examples = self.extract_example_pairs(sd, ec)
#                 examples = []
#                 grid_str += f"  - Error Code: {ec}\n"
#                 if definition:
#                     grid_str += f"    Definition: {definition}\n"
#                 grid_str += f"    Examples: {json.dumps(examples, ensure_ascii=False)}\n"
                
#         # print(f"printing grid_str: {grid_str}")

#         prompt = f"""
# You are a clinical informatics expert. Given an error summary, classify the error **hierarchically** using the following structure:

# Domain: {self.domain}
# {grid_str}

# Instructions:
# - For **every subdomain**, output a JSON dict with: subdomain name, yes/no if matches the error, concise but detailed rationale, and confidence (0–1).  
# - For each subdomain where yes==True, check ALL its error codes (output a dict per error code: subdomain, error code, yes/no if matches, rationale, confidence 0–1).
# - For subdomains that are not matched (yes==False), set all error codes to yes==False with rationale: "subdomain not matched."
# - If the error does **not** fit any subdomain, set "No subdomain matched" to yes==True, and for error code, only "No error code matched" to yes==True.
# - If the error does **not** fit any error code within a matched subdomain, set "No error code matched" for that subdomain to yes==True.
# - Always fill out every subdomain and every error code slot (full grid) as shown above.
# - Only output the following JSON format (do not add explanations outside JSON):

# {{
#   "index": {index},
#   "domain": "{self.domain}",
#   "error_summary": "{error_summary}",
#   "subdomains": [
#     {{"subdomain": "...", "yes": true/false, "rationale": "...", "confidence": ...}},
#     ...
#   ],
#   "error_codes": [
#     {{"subdomain": "...", "error_code": "...", "yes": true/false, "rationale": "...", "confidence": ...}},
#     ...
#   ],
#   "no_matching_subdomain": true/false,
#   "no_matching_error_code": true/false
# }}
# """
#         return prompt

    def build_prompt(self, index: int, error_summary: str):
        # Build subdomains and error codes (no "new subdomain" or "new error code")
        subdomains = sorted(self.codebook["Dedup Subdomain"].unique())
        subdomain_errorcodes = {}
        for sd in subdomains:
            existing_codes = set(self.codebook[self.codebook["Dedup Subdomain"] == sd]["Dedup Error Code"].tolist())
            subdomain_errorcodes[sd] = existing_codes

        # Build codebook grid for LLM reference
        grid_str = ""
        for sd in subdomains:
            grid_str += f"\n- Subdomain: {sd}\n"
            for ec in subdomain_errorcodes[sd]:
                definition = self.extract_definition(sd, ec)
                examples = []
                grid_str += f"  - Error Code: {ec}\n"
                if definition:
                    grid_str += f"    Definition: {definition}\n"
                grid_str += f"    Examples: {json.dumps(examples, ensure_ascii=False)}\n"

        prompt = f"""
    You are a clinical informatics expert. Given an error summary, classify the error *hierarchically* within the current major domain (**{self.domain}**) using the structure below.

    **Subdomains and error codes for this domain:**{grid_str}

    **Instructions:**
    - For each subdomain, output:
        - subdomain: subdomain name (string)
        - yes: whether this subdomain matches the error (true/false)
        - rationale: concise explanation for your choice
        - confidence: your confidence (0–1)
        - error_codes: a list of error code entries for this subdomain:
            - error_code: error code name (string)
            - yes: whether this error code matches (true/false)
            - rationale: concise explanation for your choice.
            - confidence: your confidence (0–1)
    - Always prioritize matching to existing subdomains and error codes.
    - For all unmatched subdomains or error codes, set yes=false and provide a brief rationale.
    - Do not propose any new subdomain or error code label.

    **Always fill out the entire grid:**  
    - For every subdomain listed, always include an entry in your output.  
    - For each subdomain, always include all its listed error codes in your output, regardless of whether they match.  
    - For any subdomain or error code that does not match, set `"yes": false` and provide a brief rationale.

    **Output Format:**  
    Return ONLY the following JSON (do not add any extra text):

    {{
    "index": {index},
    "domain": "{self.domain}",
    "error_summary": "{error_summary}",
    "subdomains": [
        {{
        "subdomain": "...",
        "yes": true/false,
        "rationale": "...",
        "confidence": ...,
        "error_codes": [
            {{
            "error_code": "...",
            "yes": true/false,
            "rationale": "...",
            "confidence": ...
            }},
            ...
        ]
        }},
        ...
    ]
    }}
    """
        return prompt

    