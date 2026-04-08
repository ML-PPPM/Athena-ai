"""Intelligent subject detection for Athena AI."""

import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# DSE subjects and their keywords
SUBJECT_KEYWORDS = {
    "Mathematics": [
        # Core concepts - high priority
        "calculus", "algebra", "geometry", "trigonometry", "statistics", "probability",
        "differential", "integral", "derivative", "function", "equation", "inequality",
        "matrix", "vector", "coordinate", "graph", "plot", "axis", "slope", "intercept",
        # Specific topics
        "quadratic", "polynomial", "logarithm", "exponential", "sequence", "series",
        "permutation", "combination", "binomial", "normal distribution", "hypothesis",
        "correlation", "regression", "integration", "differentiation", "limit", "continuity",
        # Problem types - very specific
        "solve for", "find the", "calculate", "prove that", "show that", "determine",
        "simplify", "factor", "expand", "differentiate", "integrate", "derive",
        # Mathematical notation and terms
        "sin", "cos", "tan", "log", "ln", "sqrt", "pi", "sigma", "delta", "theta",
        "alpha", "beta", "gamma", "infinity", "summation", "integral", "derivative",
        # Common math phrases
        "math", "mathematics", "maths", "arithmetic", "geometry", "algebra", "calculus"
    ],

    "Physics": [
        # Core concepts
        "force", "energy", "power", "work", "momentum", "velocity", "acceleration",
        "mass", "weight", "gravity", "friction", "pressure", "density", "temperature",
        "heat", "thermodynamics", "electricity", "magnetism", "wave", "light", "sound",
        "nuclear", "radiation", "quantum", "mechanics", "dynamics", "kinematics",
        # Specific topics
        "newton's law", "kinetic energy", "potential energy", "conservation",
        "ohms law", "circuit", "resistance", "capacitance", "inductance",
        "reflection", "refraction", "diffraction", "interference", "lens", "mirror",
        "radioactive", "half-life", "fusion", "fission", "photon", "electron",
        # Units and measurements - very specific
        "newton", "joule", "watt", "pascal", "volt", "ampere", "coulomb", "farad", "henry",
        "hertz", "meter", "second", "kilogram", "kelvin", "celsius", "fahrenheit",
        # Physics-specific phrases
        "physics", "physical", "mechanical", "electrical", "magnetic", "optical",
        "thermal", "nuclear physics", "quantum physics", "relativity"
    ],

    "Chemistry": [
        # Core concepts
        "atom", "molecule", "compound", "element", "reaction", "bond", "acid", "base",
        "salt", "organic", "inorganic", "electrolysis", "redox", "equilibrium", "kinetics",
        "thermochemistry", "electrochemistry", "periodicity", "metal", "non-metal",
        # Specific topics
        "periodic table", "atomic structure", "chemical bonding", "stoichiometry",
        "energetics", "chemical equilibrium", "acid-base", "solubility", "ionic", "covalent",
        "metallic", "hydrogen bond", "van der waals", "hybridization", "isomerism",
        "polymer", "biochemistry", "environmental chemistry",
        # Reactions and processes
        "combustion", "neutralization", "precipitation", "displacement", "decomposition",
        "synthesis", "oxidation", "reduction", "hydrolysis", "esterification",
        # Laboratory terms
        "titration", "spectroscopy", "chromatography", "distillation", "filtration",
        "molarity", "molality", "mole", "molecular", "empirical formula",
        # Chemistry-specific phrases
        "chemistry", "chemical", "reaction", "compound", "element", "molecule",
        "catalyst", "enzyme", "activation energy", "endothermic", "exothermic", "balance"
    ],

    "Biology": [
        # Core concepts
        "cell", "tissue", "organ", "system", "organism", "ecosystem", "evolution",
        "genetics", "dna", "rna", "protein", "enzyme", "metabolism", "photosynthesis",
        "respiration", "homeostasis", "immunity", "reproduction", "development",
        # Specific topics
        "mitosis", "meiosis", "transcription", "translation", "mutation", "natural selection",
        "ecology", "food chain", "biome", "biodiversity", "conservation", "pollution",
        "nervous system", "endocrine", "circulatory", "respiratory", "digestive", "excretory",
        "muscular", "skeletal", "reproductive", "immune system", "pathogen", "vaccine",
        "hormone", "neuron", "synapse", "reflex", "osmosis", "diffusion", "active transport",
        # Classification
        "kingdom", "phylum", "class", "order", "family", "genus", "species",
        "prokaryote", "eukaryote", "vertebrate", "invertebrate", "mammal", "reptile", "amphibian",
        # Biology-specific phrases
        "biology", "biological", "organism", "species", "evolution", "genetic",
        "cellular", "molecular biology", "ecology", "physiology", "anatomy"
    ],

    "English": [
        # Literature and language
        "literature", "poetry", "novel", "drama", "prose", "essay", "analysis",
        "theme", "character", "plot", "setting", "conflict", "resolution", "narrative",
        "metaphor", "simile", "personification", "alliteration", "assonance", "rhyme",
        "stanza", "verse", "sonnet", "ballad", "ode", "epic", "tragedy", "comedy",
        # Language features
        "grammar", "syntax", "semantics", "pragmatics", "phonology", "morphology",
        "tense", "mood", "voice", "aspect", "clause", "phrase", "sentence structure",
        "punctuation", "spelling", "vocabulary", "idiom", "collocation", "register",
        # Writing skills
        "argument", "persuasion", "exposition", "description", "narration", "summary",
        "paraphrase", "synthesis", "evaluation", "comparison", "contrast", "analysis",
        # English-specific phrases
        "english", "language", "linguistics", "literary", "rhetoric", "composition",
        "creative writing", "academic writing", "essay writing", "literature analysis"
    ],

    "Chinese": [
        # Language aspects
        "文言文", "白話文", "詩詞", "散文", "小說", "戲劇", "修辭", "語法", "詞彙",
        "成語", "諺語", "典故", "對仗", "押韻", "平仄", "文體", "風格", "主題",
        # Classical Chinese
        "古文", "文言", "經典", "詩經", "論語", "孟子", "莊子", "史記", "唐詩", "宋詞",
        # Modern Chinese
        "現代文", "白話", "語體", "文學", "散文", "小說", "新詩", "現代詩", "戲劇", "電影",
        # Language skills
        "閱讀", "寫作", "聽力", "說話", "翻譯", "摘要", "分析", "批評", "欣賞", "創作",
        # Chinese-specific phrases
        "中文", "漢語", "國語", "文學", "詩歌", "古典", "現代", "寫作", "閱讀理解"
    ],

    "Economics": [
        # Core concepts
        "supply", "demand", "market", "price", "equilibrium", "elasticity", "utility",
        "cost", "revenue", "profit", "competition", "monopoly", "oligopoly", "market structure",
        "macroeconomics", "microeconomics", "fiscal policy", "monetary policy", "inflation",
        "unemployment", "economic growth", "trade", "exchange rate", "balance of payments",
        # Specific topics
        "perfect competition", "monopolistic competition", "monopoly", "oligopoly",
        "price discrimination", "externalities", "public goods", "market failure",
        "aggregate demand", "aggregate supply", "multiplier effect", "business cycle",
        "fiscal deficit", "national debt", "quantitative easing", "interest rate",
        "comparative advantage", "protectionism", "tariff", "quota", "subsidy",
        # Economics-specific phrases
        "economics", "economic", "market", "economy", "finance", "business", "trade",
        "commerce", "industry", "consumer", "producer", "scarcity", "opportunity cost", "gdp"
    ],

    "Physics": [
        # Core concepts
        "force", "energy", "power", "work", "momentum", "velocity", "acceleration",
        "mass", "weight", "gravity", "friction", "pressure", "density", "temperature",
        "heat", "thermodynamics", "electricity", "magnetism", "wave", "light", "sound",
        "nuclear", "radiation", "quantum", "relativity", "mechanics", "dynamics",
        # Specific topics
        "newton's law", "kinetic energy", "potential energy", "conservation",
        "ohms law", "circuit", "resistance", "capacitance", "inductance",
        "reflection", "refraction", "diffraction", "interference", "lens", "mirror",
        "radioactive", "half-life", "fusion", "fission", "photon", "electron",
        # Units and measurements
        "newton", "joule", "watt", "pascal", "volt", "ampere", "coulomb", "farad", "henry",
        "hertz", "meter", "second", "kilogram", "kelvin"
    ],

    "Chemistry": [
        # Core concepts
        "atom", "molecule", "compound", "element", "reaction", "bond", "acid", "base",
        "salt", "organic", "inorganic", "electrolysis", "redox", "equilibrium", "kinetics",
        "thermochemistry", "electrochemistry", "periodicity", "metal", "non-metal",
        # Specific topics
        "periodic table", "atomic structure", "chemical bonding", "stoichiometry",
        "energetics", "chemical equilibrium", "acid-base", "solubility", "ionic", "covalent",
        "metallic", "hydrogen bond", "van der waals", "hybridization", "isomerism",
        "polymer", "biochemistry", "environmental chemistry",
        # Reactions and processes
        "combustion", "neutralization", "precipitation", "displacement", "decomposition",
        "synthesis", "oxidation", "reduction", "hydrolysis", "esterification",
        # Laboratory terms
        "titration", "spectroscopy", "chromatography", "distillation", "filtration"
    ],

    "Biology": [
        # Core concepts
        "cell", "tissue", "organ", "system", "organism", "ecosystem", "evolution",
        "genetics", "dna", "rna", "protein", "enzyme", "metabolism", "photosynthesis",
        "respiration", "homeostasis", "immunity", "reproduction", "development",
        # Specific topics
        "mitosis", "meiosis", "transcription", "translation", "mutation", "natural selection",
        "ecology", "food chain", "biome", "biodiversity", "conservation", "pollution",
        "nervous system", "endocrine", "circulatory", "respiratory", "digestive", "excretory",
        "muscular", "skeletal", "reproductive", "immune system", "pathogen", "vaccine",
        "hormone", "neuron", "synapse", "reflex", "osmosis", "diffusion", "active transport",
        # Classification
        "kingdom", "phylum", "class", "order", "family", "genus", "species",
        "prokaryote", "eukaryote", "vertebrate", "invertebrate", "mammal", "reptile", "amphibian"
    ],

    "English": [
        # Literature and language
        "literature", "poetry", "novel", "drama", "prose", "essay", "analysis",
        "theme", "character", "plot", "setting", "conflict", "resolution", "narrative",
        "metaphor", "simile", "personification", "alliteration", "assonance", "rhyme",
        "stanza", "verse", "sonnet", "ballad", "ode", "epic", "tragedy", "comedy",
        # Language features
        "grammar", "syntax", "semantics", "pragmatics", "phonology", "morphology",
        "tense", "mood", "voice", "aspect", "clause", "phrase", "sentence structure",
        "punctuation", "spelling", "vocabulary", "idiom", "collocation", "register",
        # Writing skills
        "argument", "persuasion", "exposition", "description", "narration", "summary",
        "paraphrase", "synthesis", "evaluation", "comparison", "contrast", "analysis"
    ],

    "Chinese": [
        # Language aspects
        "文言文", "白話文", "詩詞", "散文", "小說", "戲劇", "修辭", "語法", "詞彙",
        "成語", "諺語", "典故", "對仗", "押韻", "平仄", "文體", "風格", "主題",
        # Classical Chinese
        "古文", "文言", "經典", "詩經", "論語", "孟子", "莊子", "史記", "唐詩", "宋詞",
        # Modern Chinese
        "現代文", "白話", "語體", "文學", "小說", "散文", "新詩", "現代詩", "戲劇", "電影",
        # Language skills
        "閱讀", "寫作", "聽力", "說話", "翻譯", "摘要", "分析", "批評", "欣賞", "創作"
    ],

    "Economics": [
        # Core concepts
        "supply", "demand", "market", "price", "equilibrium", "elasticity", "utility",
        "cost", "revenue", "profit", "competition", "monopoly", "oligopoly", "market structure",
        "macroeconomics", "microeconomics", "fiscal policy", "monetary policy", "inflation",
        "unemployment", "economic growth", "trade", "exchange rate", "balance of payments",
        # Specific topics
        "perfect competition", "monopolistic competition", "monopoly", "oligopoly",
        "price discrimination", "externalities", "public goods", "market failure",
        "aggregate demand", "aggregate supply", "multiplier effect", "business cycle",
        "fiscal deficit", "national debt", "quantitative easing", "interest rate",
        "comparative advantage", "protectionism", "tariff", "quota", "subsidy"
    ],

    "Geography": [
        # Physical geography
        "plate tectonics", "earthquake", "volcano", "mountain", "river", "coast", "weather",
        "climate", "atmosphere", "ocean", "soil", "erosion", "deposition", "weathering",
        "glacier", "desert", "rainforest", "grassland", "tundra", "biome", "ecosystem",
        # Human geography
        "population", "migration", "urbanization", "rural", "development", "globalization",
        "cultural", "economic", "political", "social", "sustainable", "resource", "energy",
        "transport", "communication", "tourism", "agriculture", "industry", "trade",
        # Geographic skills
        "map", "scale", "projection", "grid reference", "contour", "relief", "drainage",
        "land use", "settlement", "case study", "fieldwork", "data analysis", "graph",
        # Geography-specific phrases
        "geography", "geographic", "geographical", "terrain", "landscape", "environment",
        "sustainability", "conservation", "natural resources", "human impact", "water cycle"
    ]
}

# Subject priorities (higher number = higher priority)
SUBJECT_PRIORITIES = {
    "Mathematics": 10,
    "Physics": 9,
    "Chemistry": 8,
    "Biology": 7,
    "English": 6,
    "Chinese": 5,
    "Economics": 4,
    "Geography": 3
}

class SubjectDetector:
    """Intelligent subject detection for user queries."""

    def __init__(self):
        self.subject_keywords = SUBJECT_KEYWORDS
        self.subject_priorities = SUBJECT_PRIORITIES

    def detect_subject(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect the most relevant DSE subject from text.

        Returns:
            Tuple of (subject_name, confidence_score) or (None, 0.0) if no subject detected
        """
        text_lower = text.lower().strip()

        # Remove common question words and punctuation for better matching
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
        words = text_clean.split()
        words_set = set(words)  # Create set for fast lookups

        subject_scores = {}

        # Calculate scores for each subject using multiple factors
        for subject, keywords in self.subject_keywords.items():
            score = 0
            matched_keywords = []
            exact_matches = 0
            partial_matches = 0

            for keyword in keywords:
                keyword_lower = keyword.lower()

                # Exact word match (weighted by keyword specificity)
                if keyword_lower in words_set:
                    # More specific keywords get higher scores
                    if len(keyword) > 6:  # Longer, more specific words
                        score += 6
                    elif len(keyword) > 4:  # Medium length words
                        score += 5
                    else:  # Short/common words
                        score += 3
                    matched_keywords.append(keyword)
                    exact_matches += 1

                # Check for compound keywords (multi-word)
                elif ' ' in keyword_lower:
                    compound_words = keyword_lower.split()
                    if all(word in words_set for word in compound_words):
                        score += 8  # High score for compound matches
                        matched_keywords.append(keyword)
                        exact_matches += 1

                # Partial match in text (for word variations like earthquake/earthquakes)
                elif keyword_lower in text_lower:
                    score += 2  # Lower weight for partial matches
                    matched_keywords.append(keyword)
                    partial_matches += 1
                    score += 1.5  # Increased weight
                    matched_keywords.append(keyword)
                    partial_matches += 1

            # Bonus scoring for subject relevance
            if score > 0:
                # Bonus for multiple exact matches (shows strong subject relevance)
                if exact_matches > 1:
                    score += exact_matches * 2

                # Bonus for subject-specific question patterns
                subject_indicators = {
                    "Mathematics": ["solve", "calculate", "find", "prove", "equation", "formula"],
                    "Physics": ["force", "energy", "velocity", "acceleration", "experiment"],
                    "Chemistry": ["reaction", "compound", "element", "molecule", "laboratory"],
                    "Biology": ["cell", "organism", "evolution", "genetics", "ecosystem"],
                    "English": ["essay", "write", "analyze", "literature", "language"],
                    "Chinese": ["寫作", "閱讀", "文言", "詩詞", "中文"],
                    "Economics": ["market", "price", "economy", "trade", "cost"],
                    "Geography": ["map", "climate", "population", "environment", "location"]
                }

                if subject in subject_indicators:
                    for indicator in subject_indicators[subject]:
                        if indicator in words_set:
                            score += 3  # Strong indicator bonus

                # Apply subject priority as small additive boost
                priority_boost = (self.subject_priorities.get(subject, 1) - 1) * 0.5  # 0-3.5 boost
                final_score = score + priority_boost

                subject_scores[subject] = {
                    'score': final_score,
                    'matches': matched_keywords,
                    'exact_matches': exact_matches,
                    'partial_matches': partial_matches,
                    'priority_boost': priority_boost
                }

        if not subject_scores:
            return None, 0.0

        # Find the subject with highest score
        best_subject = max(subject_scores.items(), key=lambda x: x[1]['score'])
        best_data = best_subject[1]

        # Calculate confidence with improved algorithm
        # Base confidence on score relative to expected maximum
        max_possible_score = max(self.subject_priorities.values()) * 4 + 20  # Adjusted for new additive scoring
        raw_confidence = min(best_data['score'] / max_possible_score, 1.0)

        # Boost confidence for strong indicators
        if best_data['exact_matches'] >= 2:
            raw_confidence = min(raw_confidence * 1.4, 1.0)  # 40% boost for multiple exact matches
        elif best_data['exact_matches'] >= 1:
            raw_confidence = min(raw_confidence * 1.2, 1.0)  # 20% boost for single exact match

        # Boost for multiple partial matches
        if best_data['partial_matches'] >= 3:
            raw_confidence = min(raw_confidence * 1.15, 1.0)

        # Penalize very low match counts
        if best_data['exact_matches'] == 0 and best_data['partial_matches'] < 2:
            raw_confidence *= 0.8  # Reduce confidence for weak matches

        confidence = max(raw_confidence, 0.0)

        # Lower threshold for detection - be more permissive for DSE subjects
        if confidence < 0.08:  # Very low confidence threshold
            return None, 0.0

        logger.info(f"Detected subject: {best_subject[0]} (confidence: {confidence:.2f}) - "
                   f"exact: {best_data['exact_matches']}, partial: {best_data['partial_matches']}, "
                   f"matches: {best_data['matches'][:3]}")

        return best_subject[0], confidence

    def get_subject_hints(self, subject: str) -> List[str]:
        """Get example topics/questions for a subject."""
        hints = {
            "Mathematics": [
                "Solve the quadratic equation x² + 5x + 6 = 0",
                "Find the derivative of f(x) = x³ + 2x² - x + 1",
                "Calculate the probability of rolling a 6 on a fair die",
                "Prove that the sum of angles in a triangle is 180°"
            ],
            "Physics": [
                "Explain Newton's laws of motion",
                "Calculate the work done when lifting a 10kg box 2m",
                "Describe how a lens forms an image",
                "Explain the difference between AC and DC current"
            ],
            "Chemistry": [
                "Balance the equation: H₂ + O₂ → H₂O",
                "Explain the periodic table trends",
                "Describe the process of electrolysis",
                "What is the difference between ionic and covalent bonds?"
            ],
            "Biology": [
                "Explain how photosynthesis works",
                "Describe the structure of DNA",
                "What are the stages of mitosis?",
                "Explain natural selection and evolution"
            ],
            "English": [
                "Analyze the theme of love in Shakespeare's Romeo and Juliet",
                "Write an argumentative essay on social media's impact",
                "Identify literary devices in a poem",
                "Compare character development in two novels"
            ],
            "Chinese": [
                "分析《論語》中的仁的概念",
                "寫一篇關於環境保護的議論文",
                "解釋文言文的翻譯技巧",
                "分析現代詩的修辭手法"
            ],
            "Economics": [
                "Explain supply and demand curves",
                "What are the advantages of free trade?",
                "Describe fiscal policy tools",
                "Analyze market structures and competition"
            ],
            "Geography": [
                "Explain plate tectonics and earthquakes",
                "Describe the water cycle",
                "Analyze population growth patterns",
                "Explain sustainable development"
            ]
        }
        return hints.get(subject, ["Ask me anything about this subject!"])

    def suggest_related_subjects(self, detected_subject: str) -> List[str]:
        """Suggest related subjects that might also be relevant."""
        related = {
            "Mathematics": ["Physics", "Economics"],
            "Physics": ["Mathematics", "Chemistry"],
            "Chemistry": ["Physics", "Biology"],
            "Biology": ["Chemistry", "Geography"],
            "English": ["Chinese"],
            "Chinese": ["English"],
            "Economics": ["Mathematics", "Geography"],
            "Geography": ["Biology", "Economics"]
        }
        return related.get(detected_subject, [])

# Global subject detector instance
subject_detector = SubjectDetector()