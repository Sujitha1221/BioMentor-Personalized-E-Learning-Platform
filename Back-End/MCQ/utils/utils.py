TOPIC_KEYWORDS = {
    "Introduction to Biology": ["biology", "living", "life", "organism", "cells"],
    "Chemical and Cellular Basis of Life": ["cell", "water", "microscope", "mitochondria", "nucleus", "enzyme", "photosynthesis", "respiration"],
    "Evolution and Diversity of Organisms": ["evolution", "natural selection", "taxonomy", "bacteria", "protista", "fungi", "chordata"],
    "Plant Form and Function": ["plant", "photosynthesis", "root", "leaf", "flower", "transpiration", "hormones"],
    "Animal Form and Function": ["animal", "digestive", "circulatory", "blood", "immune", "respiration", "skeleton", "reproduction"],
    "Genetics": ["genetics", "DNA", "RNA", "gene", "chromosome", "inheritance", "Mendel", "mutation"],
    "Molecular Biology and DNA Technology": ["chromosome", "DNA", "RNA", "mutation", "GMO", "cloning"],
    "Environmental Biology": ["ecosystem", "biodiversity", "biome", "climate change"],
    "Microbiology": ["bacteria", "virus", "fungi", "microorganism"],
    "Applied Biology": ["aquaculture", "nanotechnology", "stem cell", "genome"]
}

def classify_topic(question_text):
    """Assigns a topic to a question based on predefined keywords, with improved accuracy."""
    question_text_lower = question_text.lower()
    matched_topics = []

    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in question_text_lower for keyword in keywords):
            matched_topics.append(topic)

    return matched_topics[0] if matched_topics else "General Biology"  # Assign the first matched topic

