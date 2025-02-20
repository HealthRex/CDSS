import os
from docx import Document


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    extracted_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            extracted_text.append(para.text.strip())
    return extracted_text


if __name__ == "__main__":
    # ✅ Directory where all .docx templates are stored
    data_dir = "data"

    # ✅ Get all .docx files in the directory
    docx_files = [f for f in os.listdir(data_dir) if f.endswith(".docx")]

    # ✅ Loop through each .docx file
    for docx_file in docx_files:
        docx_path = os.path.join(data_dir, docx_file)
        extracted_text = extract_text_from_docx(docx_path)

        # ✅ Create a corresponding .txt file
        txt_filename = docx_file.replace(".docx", "_extracted.txt")
        txt_path = os.path.join(data_dir, txt_filename)

        # ✅ Save the extracted text
        with open(txt_path, "w") as f:
            for line in extracted_text:
                f.write(line + "\n")

        print(f"✅ Extracted text saved to '{txt_filename}'")
