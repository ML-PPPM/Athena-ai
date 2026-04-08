#!/usr/bin/env python3
"""Test script for subject detection functionality."""

import sys
sys.path.append('.')

from subject_detector import subject_detector

def test_subject_detection():
    """Test the subject detection with various queries."""
    test_queries = [
        "How do I solve quadratic equations?",
        "Explain Newton's laws of motion",
        "What is the difference between ionic and covalent bonds?",
        "How does photosynthesis work?",
        "Write an argumentative essay about social media",
        "What is supply and demand?",
        "Explain plate tectonics and earthquakes",
        "How do I calculate the derivative of x²?",
        "What are the stages of mitosis?",
        "Explain the water cycle",
        "How do I balance chemical equations?",
        "What is the meaning of this poem?",
        "Calculate the GDP of Hong Kong",
        "Explain natural selection",
        "How do I use the subjunctive in French?",
        "What is the difference between AC and DC current?",
        "Explain the periodic table trends",
        "How do I write a literature analysis?",
        "What are the causes of World War I?",
        "How do I factor polynomials?"
    ]

    print("🧪 Testing Subject Detection")
    print("=" * 50)

    for query in test_queries:
        subject, confidence = subject_detector.detect_subject(query)
        confidence_pct = int(confidence * 100)
        status = "✅" if confidence > 0.3 else "❌"
        print(f"{status} '{query[:50]}...' → {subject or 'None'} ({confidence_pct}%)")

    print("\n" + "=" * 50)
    print("🎯 Subject Detection Test Complete!")

if __name__ == "__main__":
    test_subject_detection()