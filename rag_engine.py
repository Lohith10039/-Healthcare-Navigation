import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./rag_db")
embedding_func = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="clinical_navigation_rag",
    embedding_function=embedding_func
)

def populate_knowledge_base():
    """Ingests non-diagnostic clinical navigation chunks into vector space."""
    docs = [
        "Cardiovascular Red-Flag Protocol: Crushing retrosternal pain, radiating to jaw/left arm, with diaphoresis and dyspnea signals acute coronary ischemia. Absolute ER escalation required.",
        "Ophthalmic Care Guidance: Sudden monocular vision reduction, orbital trauma, acute photophobia, or chemical ocular contact requires immediate triage at an Ophthalmology clinic.",
        "Musculoskeletal Protocol: Non-deformed joint pain, chronic arthritis, sports-related ligament sprains, and ambulatory limb injuries should be routed to Orthopedics.",
        "Dermatologic Care Pathway: Non-febrile cutaneous eruptions, localized erythema, chronic dermatitis, and pruritus without systemic distress are managed by Outpatient Dermatology.",
        "Otolaryngology Standard: Persistent tinnitus, unilateral vestibular vertigo, otalgia, and purulent tonsillar exudates without respiratory compromise belong to ENT clinics.",
        "Emergency Escalation Protocol: Unresponsiveness, acute hemiparesis, sudden speech impairment, and massive hemorrhage require immediate emergency dispatch."
    ]
    
    metadatas = [
        {"department": "Emergency Medicine", "source": "WHO Critical Guidelines", "urgency": "High"},
        {"department": "Ophthalmology", "source": "NHS Ophthalmic Triage", "urgency": "Medium"},
        {"department": "Orthopedics", "source": "Clinical Care Pathway", "urgency": "Low"},
        {"department": "Dermatology", "source": "Ambulatory Protocols", "urgency": "Low"},
        {"department": "ENT", "source": "Otolaryngology Standards", "urgency": "Medium"},
        {"department": "Emergency Medicine", "source": "Emergency Triage Standards", "urgency": "Critical"}
    ]
    
    ids = [f"guideline_{i}" for i in range(len(docs))]
    collection.upsert(documents=docs, metadatas=metadatas, ids=ids)
    print(f"[*] RAG Vector Store loaded with {collection.count()} embedded chunks.")

def semantic_rag_search(query: str, top_k: int = 2):
    """Performs real vector similarity search."""
    results = collection.query(query_texts=[query], n_results=top_k)
    retrieved_chunks = []
    
    for i in range(len(results["documents"][0])):
        retrieved_chunks.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })
    return retrieved_chunks

if __name__ == "__main__":
    populate_knowledge_base()