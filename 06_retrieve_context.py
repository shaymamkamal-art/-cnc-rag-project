from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import Chroma

# 1. إعداد الـ Vector Retriever (ChromaDB)
# نفترض أنكِ قمتِ بتعريف الـ vectorstore مسبقاً
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 2. إعداد الـ Keyword Retriever (BM25)
# استخراج النصوص من الـ vectorstore لتغذية خوارزمية BM25
# (يتم تمرير قائمة الـ documents التي تم تقطيعها مسبقاً)
all_documents = vectorstore.get()['documents'] 
bm25_retriever = BM25Retriever.from_texts(all_documents)
bm25_retriever.k = 3 # جلب أفضل 3 نتائج تطابق الكلمات حرفياً

# 3. دمج الاثنين في مُسترجِع هجين (Hybrid)
# يتم تحديد الأوزان (weights): هنا أعطينا 50% للبحث الدلالي و 50% للبحث الحرفي
hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5] 
)

# 4. تنفيذ الاستعلام
query = "What CNC programs are referenced for the ZI 1 implant?"
hybrid_results = hybrid_retriever.invoke(query)

# طباعة النتائج للتأكد من جلب التشونك الصحيح
for i, doc in enumerate(hybrid_results):
    print(f"--- النتيجة {i+1} ---")
    print(doc.page_content)
    print("\n")
