# 📚 PYQ Analyzer

A Streamlit web app that analyzes **Previous Year Question (PYQ) papers**. Upload PDFs, and the app extracts the text, splits it into individual questions, groups similar questions together, and shows which topics and questions repeat the most, so you can study smarter.

---

## ✨ Features

- 📄 **PDF text extraction** from multiple PYQ papers
- 🧩 **Question parsing** that splits raw text into individual questions
- 🔍 **Clustering** of similar or repeated questions
- 📊 **Frequency analysis** to find the most important and most repeated questions
- 🌙 **Dark-themed UI** with a fixed sidebar for easy navigation
- 💾 **JSON outputs** at every stage for easy debugging and reuse

---

## 🖼️ Screenshots

| Home | Upload | Analysis |
|------|--------|----------|
| ![Home](images/home_page.png) | ![Upload](images/upload_page.png) | ![Analysis](images/analysis_page.png) |

---

## 📁 Project Structure

```
Dev_saxena-PYQ-Analyzer-/
├── images/                     # Screenshots used in README
│   ├── home_page.png
│   ├── upload_page.png
│   └── analysis_page.png
├── sample_outputs/             # Example outputs of each pipeline stage
│   ├── extracted_text.json
│   ├── parsed_questions.json
│   └── clustered_questions.json
├── .gitignore
├── analysis.py                 # Clustering and frequency analysis
├── extractor.py                # PDF → raw text
├── main.py                     # Streamlit app (UI)
├── parsing.py                  # Raw text → individual questions
├── README.md
└── requirements.txt
```

---

## ⚙️ How It Works

```
PDF(s) → extractor.py → parsing.py → analysis.py → main.py (UI)
         raw text      questions    clusters &     interactive
                                    frequency      results
```

1. **Extract**: `extractor.py` reads each uploaded PDF and pulls out the text.
2. **Parse**: `parsing.py` detects question boundaries (e.g. `Q1.`, `1)`, `(a)`) and builds a clean list of questions.
3. **Analyze**: `analysis.py` vectorizes the questions (TF-IDF) and clusters similar ones, then counts how often each cluster appears across papers.
4. **Display**: `main.py` shows everything in a Streamlit interface.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/dev-saxena-tech/Dev_saxena-PYQ-Analyzer-.git
cd Dev_saxena-PYQ-Analyzer-

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run main.py
```

The app will open at `http://localhost:8501`.

---

## 🧑‍💻 Usage

1. Open the **Upload** page and add one or more PYQ PDF files.
2. Wait while the text is extracted and questions are parsed.
3. Go to the **Analysis** page to see clusters of similar questions and how often each one repeated.
4. Use the results to prioritize topics for your exam preparation.

---

## 📦 Tech Stack

- [Streamlit](https://streamlit.io/): web UI
- [pdfplumber](https://github.com/jsvine/pdfplumber): PDF text extraction
- [scikit-learn](https://scikit-learn.org/): TF-IDF and clustering
- [pandas](https://pandas.pydata.org/): data handling

---

## 📝 Sample Outputs

The `sample_outputs/` folder contains example JSON files produced at each stage:

| File | Description |
|------|-------------|
| `extracted_text.json` | Raw text extracted from the PDFs |
| `parsed_questions.json` | Questions split out from the raw text |
| `clustered_questions.json` | Questions grouped by similarity |

---

## ⚠️ Limitations

- Works best with **text-based PDFs**. Scanned PDFs need OCR first.
- Question parsing depends on common numbering formats, so unusual layouts may need tweaks in `parsing.py`.
- Clustering quality depends on how similar the wording is between papers.

---

## 🛣️ Future Improvements

- [ ] OCR support for scanned papers
- [ ] Semantic similarity using sentence-transformers
- [ ] Topic and unit-wise grouping
- [ ] Export results to CSV / PDF
- [ ] Marks-weightage analysis

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, create a new branch, make your changes, and open a pull request.

---

## 👤 Author

**Dev Saxena**
GitHub: [@dev-saxena-tech](https://github.com/dev-saxena-tech)
