import json, re, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

with open('parsed_questions.json', encoding='utf-8') as f:
    data = json.load(f)

def extract_questions(data):
    section_a, section_bc = [], []
    for source, paper in data.items():
        year = paper['year']
        for section_name, questions in paper['sections'].items():
            for q in questions:
                main_text = q['text'].strip()
                subs = q.get('sub_questions', [])
                target = section_a if section_name == 'SECTION A' else section_bc
                if main_text and len(main_text) > 5:
                    sub_texts = ' '.join([s['text'].strip() for s in subs if s['text'].strip()])
                    combined = (main_text + ' ' + sub_texts).strip()
                    target.append({'original': combined, 'year': year, 'section': section_name, 'source': source})
                elif subs:
                    sub_texts = ' '.join([s['text'].strip() for s in subs if s['text'].strip()])
                    if len(sub_texts) > 5:
                        target.append({'original': sub_texts, 'year': year, 'section': section_name, 'source': source})
    return section_a, section_bc

section_a_qs, section_bc_qs = extract_questions(data)
print(f"Section A: {len(section_a_qs)} | Section B/C: {len(section_bc_qs)}")

STOPWORDS = {'what','is','are','the','a','an','of','in','on','at','to','for','with',
             'how','do','does','explain','describe','define','discuss','write','find',
             'calculate','give','list','state','differentiate','compare','elaborate',
             'short','note','notes','briefly','brief','following','between','and','or',
             'by','its','their','this','that','from','using','use','also','any','two',
             'three','each','mention','name'}

def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
    return ' '.join(words)

for q in section_a_qs: q['normalized'] = normalize(q['original'])
for q in section_bc_qs: q['normalized'] = normalize(q['original'])
print("Normalization done.")

def embed_tfidf(questions):
    texts = [q['normalized'] for q in questions]
    vec = TfidfVectorizer(ngram_range=(1,2), min_df=1)
    return vec.fit_transform(texts)

emb_a = embed_tfidf(section_a_qs)
emb_bc = embed_tfidf(section_bc_qs)
print("TF-IDF embeddings done.")

def cluster_by_similarity(questions, embeddings, threshold):
    n = len(questions)
    sim_matrix = cosine_similarity(embeddings)
    visited = [False]*n
    clusters = []
    for i in range(n):
        if visited[i]: continue
        cluster = [i]; visited[i] = True
        for j in range(i+1, n):
            if not visited[j] and sim_matrix[i][j] >= threshold:
                cluster.append(j); visited[j] = True
        clusters.append(cluster)
    return clusters

clusters_a = cluster_by_similarity(section_a_qs, emb_a, 0.25)
clusters_bc = cluster_by_similarity(section_bc_qs, emb_bc, 0.20)
print(f"Clusters - A: {len(clusters_a)}, BC: {len(clusters_bc)}")
print(f"Clusters with freq>1 - A: {sum(1 for c in clusters_a if len(c)>1)}, BC: {sum(1 for c in clusters_bc if len(c)>1)}")

def build_output(questions, clusters):
    result = []
    for indices in clusters:
        qs = [questions[i] for i in indices]
        canonical = max(qs, key=lambda q: len(q['original']))
        years = sorted(set(q['year'] for q in qs))
        result.append({
            'canonical_question': canonical['original'],
            'frequency': len(qs),
            'years': years,
            'questions_in_cluster': [{'text': q['original'], 'normalized': q['normalized'], 'year': q['year'], 'section': q['section'], 'source': q['source']} for q in qs]
        })
    result.sort(key=lambda x: x['frequency'], reverse=True)
    return result

output_a = build_output(section_a_qs, clusters_a)
output_bc = build_output(section_bc_qs, clusters_bc)

final = {
    'summary': {
        'total_section_a_questions': len(section_a_qs),
        'total_section_bc_questions': len(section_bc_qs),
        'section_a_clusters': len(output_a),
        'section_bc_clusters': len(output_bc),
        'section_a_clusters_with_repeats': sum(1 for c in output_a if c['frequency']>1),
        'section_bc_clusters_with_repeats': sum(1 for c in output_bc if c['frequency']>1),
    },
    'SECTION_A_clusters': output_a,
    'SECTION_BC_clusters': output_bc
}

with open('clustered_questions.json','w', encoding='utf-8') as f:
    json.dump(final, f, indent=2, ensure_ascii=False)

print("\n=== SECTION A: Repeated Question Clusters ===")
for i,c in enumerate(output_a):
    if c['frequency']>1:
        print(f"\n[A-Cluster #{i+1}] Freq:{c['frequency']} | Years:{', '.join(c['years'])}")
        print(f"  CANONICAL: {c['canonical_question'][:130]}")
        for q in c['questions_in_cluster']:
            print(f"  [{q['year']}] {q['text'][:100]}")

print("\n=== SECTION B/C: Repeated Question Clusters ===")
for i,c in enumerate(output_bc):
    if c['frequency']>1:
        print(f"\n[BC-Cluster #{i+1}] Freq:{c['frequency']} | Years:{', '.join(c['years'])}")
        print(f"  CANONICAL: {c['canonical_question'][:130]}")
        for q in c['questions_in_cluster']:
            print(f"  [{q['year']}] {q['text'][:100]}")

print("\n✅ Done. Output: clustered_questions.json")