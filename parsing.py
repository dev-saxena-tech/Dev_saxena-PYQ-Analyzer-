"""
parser.py
---------
Parses output.json (extracted text from Computer Networks PYQ PDFs)
into structured questions grouped by section.

Hierarchy rules:
  SECTION A / B / C              -> section
  1.  2.  3.  …                  -> top-level question (numbered)
  (a)  a.                        -> question inside that section (new Question)
  (i)  i.  •  -  *  (1)  1.     -> sub-question / bullet inside a question
  Lines starting with 1. or (1)
  that are instructions           -> trash

Output schema per PDF:
{
  "source": "filename.pdf",
  "sections": {
    "SECTION A": [
      {
        "question_number": "1",        # top-level ordinal kept for reference
        "label": "a",                  # (a)/(b)/… label
        "text": "Full question text",
        "sub_questions": [
          {"label": "i",  "text": "..."},
          {"label": "ii", "text": "..."}
        ]
      },
      ...
    ],
    ...
  }
}

Usage:
    python3 parser.py [input.json] [output.json]
"""

import json
import re
import sys

# ──────────────────────────────────────────────────────────────────────────────
# 1. Noise / trash patterns  (applied line-by-line before any parsing)
# ──────────────────────────────────────────────────────────────────────────────

_TRASH = [
    re.compile(r'^(QP\d+EP\d+_\d+|DR\s+[A-Z])',         re.I),  # watermarks
    re.compile(r'^\d+\s*\|\s*P\s*a\s*g\s*e',            re.I),  # "1 | P a g e"
    re.compile(r'^Printed\s+Page',                        re.I),
    re.compile(r'^Sub(?:ject)?\s+Code:',                  re.I),
    re.compile(r'^Paper\s+Id',                            re.I),
    re.compile(r'^\|?\s*\d{2}[-]\w{2,3}[-]\d{4}',        re.I),  # date stamps
    re.compile(r'^(0Roll|BTECH|B\.?TECH)\b',              re.I),
    re.compile(r'^\(SEM[\s\-]VI\)',                       re.I),
    re.compile(r'^THEORY\s+EXAMINATION',                  re.I),
    re.compile(r'^COMPUTER\s+NETWORK',                    re.I),
    re.compile(r'^Time\s*:\s*\d+',                        re.I),
    re.compile(r'^Total\s+Marks',                         re.I),
    re.compile(r'^TIME\s*:\s*\d+',                        re.I),
    re.compile(r'^M\.?MARKS',                             re.I),
    re.compile(r'^Note\s*:',                              re.I),
    re.compile(r'^\d+\s*[xX*]\s*\d+\s*=\s*\d+$'),        # "2 x 7 = 14"
    re.compile(r'^\d+\s*\*\s*\d+\s*=\s*\d+$'),           # "10*1 = 10"
    re.compile(r'^CO\s*$',                                re.I),  # CO column header
    re.compile(r'^Qno\s*$',                               re.I),  # Qno split line
    re.compile(r'^Questions\s*$',                         re.I),  # Questions split
    re.compile(r'^Qno\s+Questions',                       re.I),
    re.compile(r'^[0\s\xa0]+$'),                                   # blank / zero rows
    re.compile(r'^\d{1,2}\s*$'),                                   # lone mark digit
]

# Instruction lines – "Attempt all …", "Attempt any three …"
_INSTRUCTION = re.compile(
    r'^Attempt\s+(all|any\s+(one|two|three)|following)', re.I
)

# Lines that look like "1." or "(1)" and are instructions (not question labels)
# We detect these contextually: if they appear before the first (a) in a section
# they are instructions and should be discarded.
_NUMBERED_INSTRUCTION = re.compile(r'^\d+\.\s+|^\(\d+\)\s+')


def _is_trash(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    for p in _TRASH:
        if p.match(s):
            return True
    return False


def _strip_watermark(text: str) -> str:
    """Remove trailing ' | DD-MM-YYYY ...' PDF watermarks embedded in text."""
    return re.sub(r'\s*\|\s*\d{2}[-]\w{2,3}[-]\d{4}.*$', '', text).strip()


def _clean_lines(raw_text: str) -> list[str]:
    """Return stripped, non-trash lines."""
    result = []
    for line in raw_text.splitlines():
        s = line.strip()
        if not _is_trash(s):
            result.append(s)
    return result


# ──────────────────────────────────────────────────────────────────────────────
# 2. Token classifier
# ──────────────────────────────────────────────────────────────────────────────

_SECTION_RE = re.compile(r'^SECTION\s+([A-C])\s*$', re.I)

# Top-level ordinal: "3." "4." etc.   (these are just grouping numbers, not questions)
_TOP_NUM_RE = re.compile(r'^(\d+)\.\s*$')

# NEW QUESTION marker: (a) or a.   — alpha only, NOT roman numerals
# We deliberately exclude single letters that are also roman (i, v, x, l, c)
# by checking the letter is outside that set when it appears as 'a.' style.
_ALPHA_LABELS  = set('abcdefghjkmnopqrstuwyz')   # all alpha minus roman-only: i,v,x,l,c
_ROMAN_LETTERS = set('ivxlc')

_QUESTION_RE = re.compile(
    r'^(?:'
    r'\(([a-zA-Z])\)'    # (a)  group 1
    r'|([a-zA-Z])\.'     # a.   group 2
    r')\s*(.*)',
    re.I
)

# SUB-QUESTION marker: (i) / i.  roman numerals  OR  bullet • - *
_ROMAN_RE = re.compile(
    r'^(?:'
    r'\(([ivxlIVXL]+)\)'   # (i)  group 1
    r'|([ivxlIVXL]+)\.'    # i.   group 2
    r')\s*(.*)',
    re.I
)

_BULLET_RE = re.compile(r'^([•\-\*])\s+(.*)')

# Numbered instruction lines like "1." or "(1)" at start of section
_NUM_INSTR_RE = re.compile(r'^(\d+)\.\s+(.*)|^\((\d+)\)\s+(.*)')


def _is_roman(label: str) -> bool:
    """Return True if label looks like a roman numeral (i, ii, iv, v, vi …)."""
    return bool(re.fullmatch(r'[ivxlc]+', label, re.I))


def classify(line: str):
    """
    Returns one of:
      ('section',     letter)
      ('top_num',     number)           # ordinal grouping line e.g. "3."
      ('question',    label, rest)      # (a) / a.
      ('subquestion', label, rest)      # (i) / i. / bullet
      ('instruction', text)            # Attempt all… / 1. Attempt…
      ('text',        text)
    """
    s = line.strip()

    m = _SECTION_RE.match(s)
    if m:
        return ('section', m.group(1).upper())

    # Pure ordinal grouping line like "3." with nothing after
    m = _TOP_NUM_RE.match(s)
    if m:
        return ('top_num', m.group(1))

    # Instruction lines
    if _INSTRUCTION.match(s):
        return ('instruction', s)

    # "1. Attempt …" or "(1) …" style numbered instructions
    m = _NUM_INSTR_RE.match(s)
    if m:
        rest = (m.group(2) or m.group(4) or '').strip()
        # If the rest is an instruction keyword, treat whole line as instruction
        if _INSTRUCTION.match(rest) or not rest:
            return ('instruction', s)
        # Otherwise it's a real numbered question marker — treat as top_num + text
        num = m.group(1) or m.group(3)
        return ('top_num_text', num, rest)

    # Roman sub-question: must check BEFORE alpha-question so 'i.' goes here
    m = _ROMAN_RE.match(s)
    if m:
        label = (m.group(1) or m.group(2)).lower()
        rest  = m.group(3).strip()
        return ('subquestion', label, rest)

    # Alpha question: (a) or a.
    m = _QUESTION_RE.match(s)
    if m:
        label = (m.group(1) or m.group(2)).lower()
        rest  = m.group(3).strip()
        # If the label is ALSO a valid roman numeral single letter (i,v,x,l,c)
        # and the roman pattern already matched above, we'd never get here.
        # But as safety: if label in roman set AND context unclear, treat as subquestion.
        # We leave this as question — roman was already caught above.
        return ('question', label, rest)

    # Bullet sub-question
    m = _BULLET_RE.match(s)
    if m:
        return ('subquestion', m.group(1), m.group(2).strip())

    return ('text', s)


# ──────────────────────────────────────────────────────────────────────────────
# 3. Section parser  →  list of question objects
# ──────────────────────────────────────────────────────────────────────────────

def parse_section(lines: list[str]) -> list[dict]:
    """
    Each question object:
    {
      "question_number": "3",    # top-level ordinal (from "3." line)
      "label":           "a",    # alpha label
      "text":            "...",
      "sub_questions":   [{"label": "i", "text": "..."}, ...]
    }
    """
    questions:   list[dict] = []
    current_num: str        = ""       # current top-level ordinal
    current_q:   dict|None  = None
    current_sub: dict|None  = None
    q_buf:       list[str]  = []
    sub_buf:     list[str]  = []

    def _flush_sub():
        nonlocal current_sub, sub_buf
        if current_sub is not None:
            current_sub['text'] = _strip_watermark(' '.join(sub_buf)).strip()
            if current_q is not None:
                current_q['sub_questions'].append(current_sub)
        current_sub = None
        sub_buf = []

    def _flush_q():
        nonlocal current_q, q_buf
        _flush_sub()
        if current_q is not None:
            current_q['text'] = _strip_watermark(' '.join(q_buf)).strip()
            questions.append(current_q)
        current_q = None
        q_buf = []

    for line in lines:
        tok = classify(line)
        kind = tok[0]

        if kind == 'section':
            # Shouldn't appear inside a section block — ignore
            continue

        elif kind in ('top_num', 'instruction'):
            if kind == 'top_num':
                current_num = tok[1]
            # Instructions and pure ordinal lines: flush current question
            # but do NOT start a new one yet — wait for the (a) label
            _flush_q()

        elif kind == 'top_num_text':
            # e.g. "1. Some real question text" (rare, no alpha label)
            _flush_q()
            current_num = tok[1]
            current_q = {
                'question_number': current_num,
                'label': '',
                'text': '',
                'sub_questions': []
            }
            if tok[2]:
                q_buf.append(tok[2])

        elif kind == 'question':
            # (a) / a.  → start a new question
            _flush_q()
            current_q = {
                'question_number': current_num,
                'label': tok[1],
                'text': '',
                'sub_questions': []
            }
            if tok[2]:
                q_buf.append(tok[2])

        elif kind == 'subquestion':
            # (i) / i. / bullet → sub-question inside current question.
            # EXCEPTION 1: no active question yet → must be a top-level question label.
            # EXCEPTION 2: label is a single roman letter that is the alphabetic successor
            #   of current_q's label (e.g. 'i' after 'h') → it is a question, not a sub.
            label = tok[1]
            is_next_alpha = (
                current_q is not None
                and len(current_q['label']) == 1
                and len(label) == 1
                and ord(label) == ord(current_q['label']) + 1
            )
            if current_q is None or is_next_alpha:
                _flush_q()
                current_q = {
                    'question_number': current_num,
                    'label': label,
                    'text': '',
                    'sub_questions': []
                }
                if tok[2]:
                    q_buf.append(tok[2])
            else:
                _flush_sub()
                current_sub = {'label': label, 'text': ''}
                if tok[2]:
                    sub_buf.append(tok[2])

        elif kind == 'text':
            s = _strip_watermark(tok[1])
            if not s:
                continue
            if current_sub is not None:
                sub_buf.append(s)
            elif current_q is not None:
                q_buf.append(s)
            # else: preamble before first question — discard

    _flush_q()
    return questions

def extract_year(text: str, filename: str) -> str:
    """
    Extract year from text or filename
    Priority:
    1. Date patterns in text
    2. Standalone year in text
    3. Filename
    """

    # 1. Match date formats like 12-May-2021
    m = re.search(r'\b\d{1,2}[-/][A-Za-z]{3,9}[-/](20\d{2})\b', text)
    if m:
        return m.group(1)

    # 2. Match Month Year like May 2022
    m = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(20\d{2})\b', text, re.I)
    if m:
        return m.group(1)

    # 3. Match standalone year
    m = re.search(r'\b(20\d{2})\b', text)
    if m:
        return m.group(1)

    # 4. From filename
    m = re.search(r'(20\d{2})', filename)
    if m:
        return m.group(1)

    return "Unknown"

# ──────────────────────────────────────────────────────────────────────────────
# 4. Full PDF text  →  sections dict
# ──────────────────────────────────────────────────────────────────────────────

def parse_pdf(text: str) -> dict[str, list]:
    lines = _clean_lines(text)

    # Bucket lines into sections
    buckets: dict[str, list[str]] = {}
    current_sec = None
    for line in lines:
        m = _SECTION_RE.match(line)
        if m:
            current_sec = 'SECTION ' + m.group(1).upper()
            buckets.setdefault(current_sec, [])
        elif current_sec:
            buckets[current_sec].append(line)

    # Parse each section
    parsed: dict[str, list] = {}
    for sec, sec_lines in buckets.items():
        qs = parse_section(sec_lines)
        qs = [q for q in qs if q['text'] or q['sub_questions']]
        if qs:
            parsed[sec] = qs

    return parsed


# ──────────────────────────────────────────────────────────────────────────────
# 5. Main driver
# ──────────────────────────────────────────────────────────────────────────────

def main(input_path: str, output_path: str) -> None:
    with open(input_path, 'r', encoding='utf-8') as f:
        raw: dict[str, str] = json.load(f)

    result: dict = {}
    for pdf_name, text in raw.items():
        print(f'  Parsing: {pdf_name}')
        year = extract_year(text, pdf_name)
        sections = parse_pdf(text)
        total_q  = sum(len(v) for v in sections.values())

        print(f'    -> {len(sections)} section(s), {total_q} question(s), Year: {year}')

        result[pdf_name] = {
            'source': pdf_name,
            'year': year,
            'sections': sections
        }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f'\nDone. Written to: {output_path}')


if __name__ == '__main__':
    INPUT  = sys.argv[1] if len(sys.argv) > 1 else 'output.json'
    OUTPUT = sys.argv[2] if len(sys.argv) > 2 else 'parsed_questions.json'
    print(f"Parsing '{INPUT}' -> '{OUTPUT}' ...\n")
    main(INPUT, OUTPUT)
    