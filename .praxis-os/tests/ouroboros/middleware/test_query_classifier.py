"""
Test QueryClassifier middleware for angle detection.

Tests:
- Angle classification (definition, location, practical, best_practice, error_prevention)
- Multi-angle detection (queries can match multiple angles)
- Edge cases (empty queries, special characters)

Traceability:
    Phase 8, Task 8.1: Query classification tests
    FR-025: Query Classifier Middleware
"""

import pytest
from ouroboros.middleware.query_classifier import QueryClassifier


class TestQueryClassifier:
    """Test QueryClassifier middleware."""
    
    def test_initialization(self):
        """Test QueryClassifier initializes successfully."""
        classifier = QueryClassifier()
        assert classifier is not None
    
    def test_conceptual_angle_detection(self):
        """Test detection of 'conceptual' angle queries."""
        classifier = QueryClassifier()
        
        queries = [
            "What is a workflow?",
            "Define middleware pattern",
            "What does pos_search do?",
            "Explain RAG architecture"
        ]
        
        for query in queries:
            result = classifier.classify(query)
            assert result.primary == "conceptual" or "conceptual" in result.secondary, f"Failed for query: {query}"
    
    def test_location_angle_detection(self):
        """Test detection of 'location' angle queries."""
        classifier = QueryClassifier()
        
        queries = [
            "Where is the config file?",
            "Where do I find browser tools?",
            "Which file contains workflow logic?",
            "Where is error handling implemented?"
        ]
        
        for query in queries:
            result = classifier.classify(query)
            assert result.primary == "location" or "location" in result.secondary, f"Failed for query: {query}"
    
    def test_implementation_angle_detection(self):
        """Test detection of 'implementation' angle queries."""
        classifier = QueryClassifier()
        
        queries = [
            "How do I start a workflow?",
            "How to configure the browser?",
            "How do I search standards?",
            "How to implement validation?"
        ]
        
        for query in queries:
            result = classifier.classify(query)
            assert result.primary == "implementation" or "implementation" in result.secondary, f"Failed for query: {query}"
    
    def test_critical_angle_detection(self):
        """Test detection of 'critical' angle queries."""
        classifier = QueryClassifier()
        
        queries = [
            "Best practices for error handling",
            "What's the recommended approach?",
            "Required validation steps",
            "Recommended config settings"
        ]
        
        for query in queries:
            result = classifier.classify(query)
            assert result.primary == "critical" or "critical" in result.secondary, f"Failed for query: {query}"
    
    def test_troubleshooting_angle_detection(self):
        """Test detection of 'troubleshooting' angle queries."""
        classifier = QueryClassifier()
        
        queries = [
            "Common mistakes to avoid",
            "Anti-patterns in middleware",
            "What should I avoid when writing tests?",
            "Common pitfalls in config"
        ]
        
        for query in queries:
            result = classifier.classify(query)
            assert result.primary == "troubleshooting" or "troubleshooting" in result.secondary, f"Failed for query: {query}"
    
    def test_multi_angle_queries(self):
        """Test queries that match multiple angles."""
        classifier = QueryClassifier()
        
        query = "What is middleware and where do I implement it?"
        result = classifier.classify(query)
        
        # Should match both 'conceptual' and 'location'
        all_angles = {result.primary, *result.secondary}
        assert "conceptual" in all_angles
        assert "location" in all_angles
    
    def test_empty_query(self):
        """Test classifier handles empty queries gracefully."""
        classifier = QueryClassifier()
        
        result = classifier.classify("")
        
        # Should default to 'conceptual'
        assert result.primary == "conceptual"
    
    def test_special_characters(self):
        """Test classifier handles special characters."""
        classifier = QueryClassifier()
        
        query = "What's the @recommended $approach?"
        result = classifier.classify(query)
        
        # Should still classify despite special chars (looking for "recommended")
        assert result.primary == "critical" or "critical" in result.secondary
    
    def test_case_insensitivity(self):
        """Test classifier is case-insensitive."""
        classifier = QueryClassifier()
        
        queries = [
            "WHAT IS MIDDLEWARE?",
            "what is middleware?",
            "What Is Middleware?"
        ]
        
        # All should detect 'conceptual' angle
        for query in queries:
            result = classifier.classify(query)
            assert result.primary == "conceptual" or "conceptual" in result.secondary

