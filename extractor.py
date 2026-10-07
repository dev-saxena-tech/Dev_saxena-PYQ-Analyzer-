import fitz  # PyMuPDF
import os
import json

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = []

    for page in doc:
        text = page.get_text()
        if text:
            full_text.append(text.strip())

    doc.close()

    # Join all pages into one text
    return "\n".join(full_text)


def process_pdfs_in_folder(folder_path):
    all_pdfs_data = {}

    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing: {file_name}")

            extracted_text = extract_text_from_pdf(file_path)

            # Store as single string instead of pages
            all_pdfs_data[file_name] = extracted_text

    return all_pdfs_data


if __name__ == "__main__":
    folder_path = "upload"
    output_file = "output.json"

    result = process_pdfs_in_folder(folder_path)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Extraction completed. Output saved to {output_file}")
    