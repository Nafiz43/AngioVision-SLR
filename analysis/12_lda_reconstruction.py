"""Reconstructed (back-calculated) LDA over the extracted limitation and future-work statements of the included studies.
The original topic-model run was lost in a data migration; this script reruns the procedure in Methods 2.4.
Usage: python3 analysis/12_lda_reconstruction.py analysis-results/lda_reconstruction.json   (needs gensim, nltk)
Settings follow Methods 2.4: lowercase, strip URLs/HTML/refs, stopwords, WordNet lemmas, bigrams,
drop terms in <5% of docs, K=5..20 by C_v coherence, symmetric priors 1/K, 20 passes, 100 iterations, seed 42."""
import re,glob,json,sys,math,collections
from pathlib import Path
from gensim.corpora import Dictionary
from gensim.models import LdaModel, CoherenceModel, Phrases
from gensim.models.phrases import Phraser
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
SLR=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1])
ids=sorted(p.stem for p in (SLR/'extraction/out').glob('R*.json'))
CUE=re.compile(r'limitation|limited|future|further (work|stud|research|investigat)|remain|lack|not (yet|been|able)|could be (improved|extended)|we plan|should be|need(s|ed)? to|restricted|only (a|one|single)|small (sample|dataset|number)|single[- ](center|centre|institution|vendor)',re.I)
SEC=re.compile(r'^#+.*(discussion|limitation|future|conclusion)',re.I)
END=re.compile(r'^#+.*(reference|acknowledg|bibliograph|funding|declaration|conflict)',re.I)
def doc_text(rid):
    ex=json.load(open(SLR/f'extraction/out/{rid}.json'))
    fw=ex.get('future_work') or []
    fw=[fw] if isinstance(fw,str) else fw
    return ' '.join(map(str,list(ex.get('other_limitations') or [])+list(fw)))
SW=set(stopwords.words('english'))|{'et','al','fig','figure','table','also','may','might','use','used','using','study','studies','method','proposed','paper','work','however','would','could','one','two','well','e','g','eg','ie','x','show','result','results','based','limited','limitation','performance','image','images','patient','patients','clinical','dataset','datasets','data','model','models','approach','network','due','although','despite','remains','remaining','need','additional','various','less','improve','analysis','algorithm','accuracy','evaluate','assess','assessment','feature','information','future','further','first','include','including','number','different','current','within','still','case'}
L=WordNetLemmatizer()
def prep(t):
    t=t.lower(); t=re.sub(r'https?://\S+|www\.\S+|<[^>]+>|\[[0-9,\s\-–]+\]|\*\*?',' ',t)
    toks=re.findall(r'[a-z][a-z\-]+',t)
    return [L.lemmatize(w) for w in toks if w not in SW and len(w)>2]
docs=[prep(doc_text(r)) for r in ids]
bigram=Phraser(Phrases(docs,min_count=5,threshold=10)); docs=[bigram[d] for d in docs]
D=Dictionary(docs); D.filter_extremes(no_below=math.ceil(0.05*len(docs)),no_above=0.5)
corpus=[D.doc2bow(d) for d in docs]
res={}
for K in ([int(sys.argv[2])] if len(sys.argv)>2 and sys.argv[3:]==['only'] else range(5,21)):
    m=LdaModel(corpus,id2word=D,num_topics=K,alpha=[1/K]*K,eta=1/K,passes=20,iterations=100,random_state=42)
    c=CoherenceModel(model=m,texts=docs,dictionary=D,coherence='c_v',processes=1).get_coherence(); res[K]=(round(c,4),m)
    print(K,round(c,4),flush=True)
bestK=int(sys.argv[2]) if len(sys.argv)>2 else max(res,key=lambda k:res[k][0]); m=res[bestK][1]
gaps=[f'G{i}' for i in range(1,13)]
code={r:{g:json.load(open(SLR/f'extraction/out/{r}.json'))['gaps'][g]['status'] in('documents','both') for g in gaps} for r in ids}
theta=[dict(m.get_document_topics(b,minimum_probability=0)) for b in corpus]
dom=[max(t,key=t.get) for t in theta]
base={g:sum(code[r][g] for r in ids)/len(ids) for g in gaps}
topics=[]
for k in range(bestK):
    members=[ids[i] for i in range(len(ids)) if dom[i]==k]
    top=sorted(range(len(ids)),key=lambda i:-theta[i].get(k,0))[:3]
    import numpy as np
    th=np.array([theta[i].get(k,0) for i in range(len(ids))])
    # Pearson r between the topic's document weights and each gap's coding (documents/both)
    lift={g:float(np.corrcoef(th,[code[r][g] for r in ids])[0,1]) if base[g] else 0 for g in gaps}
    topics.append({'k':k+1,'terms':[w for w,_ in m.show_topic(k,10)],'n_dominant':len(members),
                   'rep':[ids[i] for i in top],'lift':{g:round(v,2) for g,v in lift.items()}})
json.dump({'coherence':{k:v[0] for k,v in res.items()},'bestK':bestK,'vocab':len(D),'docs':len(docs),'topics':topics},open(OUT,'w'),indent=1)
print('best',bestK)
