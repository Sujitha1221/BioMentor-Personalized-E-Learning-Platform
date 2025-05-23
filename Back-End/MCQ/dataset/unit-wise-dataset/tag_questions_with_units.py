import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Step 1: Load dataset
dataset_path = "dataset/merged_mcq_dataset.csv"
df = pd.read_csv(dataset_path, encoding="latin1").fillna("")

# Step 2: Define unit-topic mappings
unit_topics = {
    "Unit 01": [
        "Introduction to Biology", "nature and scope", "organizational patterns", "challenges faced"
    ],
    "Unit 02": [
        "Elemental composition", "properties of water", "organic compounds", "microscope", "cell", "cell division",
        "metabolic processes", "enzymes", "photosynthesis", "respiration"
    ],
    "Unit 03": [
        "evolution", "origin of life", "natural selection", "taxonomy", "diversity", "Bacteria", "Protista",
        "Plantae", "Fungi", "Animalia", "Chordata"
    ],
    "Unit 04": [
        "plant structure", "plant tissues", "growth", "shoot", "gaseous exchange", "transport", "nutrition", 
        "life cycles", "reproduction", "stimuli", "hormones", "plant stress"
    ],
    "Unit 05": [
        "animal tissues", "nutrition in animals", "digestive system", "circulatory system", "gas exchange", 
        "immunity", "excretion", "coordination", "nervous system", "endocrine", "reproduction", 
        "skeletal system", "joints"
    ],
    "Unit 06": [
        "genetics", "monohybrid", "dihybrid", "Mendel", "inheritance", "testcross", "polyallelism", "breeding"
    ],
    "Unit 07": [
        "chromosomes", "DNA", "genes", "mutation", "recombinant", "GMO", "biosafety"
    ],
    "Unit 08": [
        "environment", "biome", "ecosystem", "biodiversity", "climate change", "legislation"
    ],
    "Unit 09": [
        "microorganisms", "laboratory techniques", "soil microorganisms", "wastewater", "food microbiology"
    ],
    "Unit 10": [
        "aquaculture", "ornamental fish", "food preservation", "nanotechnology", "stem cell", "human genome"
    ]
}

# Step 3: Load model and encode topics
print("Loading sentence transformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Encoding unit topics...")
unit_embeddings = {
    unit: model.encode(topics, convert_to_tensor=True) for unit, topics in unit_topics.items()
}

# Step 4: Tag each question
def assign_unit(question_text):
    question_embedding = model.encode(question_text, convert_to_tensor=True)
    max_score = 0
    selected_unit = "Unassigned"
    
    for unit, embeddings in unit_embeddings.items():
        cosine_scores = util.cos_sim(question_embedding, embeddings)
        unit_score = cosine_scores.max().item()
        if unit_score > max_score:
            max_score = unit_score
            selected_unit = unit
    
    return selected_unit

print("Tagging questions with units...")
df["Assigned_Unit"] = df["Question Text"].apply(assign_unit)

# Step 5: Save updated dataset
output_path = "dataset/unit_tagged_mcq_dataset.csv"
df.to_csv(output_path, index=False)
print(f"✅ Dataset saved with units → {output_path}")
