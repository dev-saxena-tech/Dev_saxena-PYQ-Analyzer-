# 📚 PYQ Analyzer

A Streamlit web app that analyzes **Previous Year Question (PYQ) papers**. Upload PDFs, and the app extracts the text, splits it into individual questions, groups similar questions together, and shows which questions repeat the most, so you can study smarter.

---

## ✨ Features

- 📄 **PDF text extraction** from multiple PYQ papers
- 🧩 **Question parsing** into sections and 2-mark / 10-mark questions
- 🔍 **Clustering** of similar or repeated questions across years
- 📊 **Frequency analysis** to find the most repeated questions
- 📥 **PDF export** of the analysis results
- 🌙 **Dark-themed UI** with a fixed sidebar

---

## 📁 Project Structure

```
Dev_saxena-PYQ-Analyzer-/
├── .gitignore
├── analysis.py        # Clustering and frequency analysis
├── extractor.py       # PDF → raw text
├── main.py            # Streamlit app (UI)
├── parsing.py         # Raw text → sections and questions
├── README.md
└── requirements.txt
```

The folders `upload/` and the files `output.json`, `parsed_questions.json`, `clustered_questions.json` are created automatically when you run the app.

---

## ⚙️ How It Works

```
PDF(s) → extractor.py → parsing.py → analysis.py → main.py (UI)
         raw text      questions    clusters &     interactive
                                    frequency      results
```

1. **Extract**: `extractor.py` reads every PDF in the `upload/` folder and saves the text to `output.json`.
2. **Parse**: `parsing.py` detects sections and questions and saves them to `parsed_questions.json`.
3. **Analyze**: `analysis.py` groups similar questions (TF-IDF similarity) and saves them to `clustered_questions.json`.
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

Run this from inside the project folder:

```bash
python -m streamlit run main.py
```

The app opens at `http://localhost:8501`.

> If `streamlit run main.py` gives "command not found", use `python -m streamlit run main.py` as shown above.

---

## 🧑‍💻 Usage

1. Open the **Upload PDFs** page and upload one or more question paper PDFs.
2. Click **Analyze PDFs** and wait for processing to finish.
3. Open the **Analysis Results** page to see repeated questions grouped into clusters.

You can also run the pipeline manually from the terminal, after placing PDFs in the `upload/` folder:

```bash
python extractor.py
python parsing.py
python analysis.py
```

---

## 📄 Supported PDF Format

The parser is built for **AKTU-style papers**:

- Sections labelled `SECTION A`, `SECTION B`, `SECTION C`
- Questions labelled `(a)`, `(b)`, `(c)` …
- **Text-based PDFs** only (scanned/photo PDFs need OCR first)

Papers in other formats may need changes in `parsing.py`.

---

## 📦 Tech Stack

- [Streamlit](https://streamlit.io/): web UI
- [PyMuPDF](https://pymupdf.readthedocs.io/): PDF text extraction
- [scikit-learn](https://scikit-learn.org/): TF-IDF and clustering
- [NumPy](https://numpy.org/): numerical operations
- [ReportLab](https://www.reportlab.com/): PDF export of results

---

## ⚠️ Limitations

- Clustering is based on word similarity, so very similar topics (e.g. "binary search tree" and "binary search") may sometimes be grouped together.
- Question parsing depends on the paper format described above.

---

## 🛣️ Future Improvements

- [ ] OCR support for scanned papers
- [ ] Semantic similarity using sentence-transformers
- [ ] Support for more paper formats
- [ ] Topic and unit-wise grouping

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, create a new branch, make your changes, and open a pull request.

---

## 👤 Author

**Dev Saxena**
GitHub: [@dev-saxena-tech](https://github.com/dev-saxena-tech)