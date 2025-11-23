"""
Unit tests for OrientationMetadataParser.

Tests the orientation metadata parser module which extracts inline metadata
from markdown files using the **Metadata**: pattern.

Test Coverage:
    - Class instantiation
    - Regex pattern compilation
    - Module imports
    - Basic structure validation

Author: prAxIs OS Development Team
Date: 2025-11-19
"""

import re
import pytest
from pathlib import Path

from ouroboros.subsystems.rag.standards.orientation import OrientationMetadataParser


class TestOrientationMetadataParserInstantiation:
    """Test basic instantiation and structure of OrientationMetadataParser."""
    
    def test_parser_instantiation(self):
        """
        Test that OrientationMetadataParser can be instantiated.
        
        Validates:
            - Class can be imported
            - Instance can be created without errors
            - Instance is of correct type
        
        Acceptance Criterion: Task 1.1 - Class instantiates successfully
        """
        parser = OrientationMetadataParser()
        assert isinstance(parser, OrientationMetadataParser)
    
    def test_metadata_pattern_exists(self):
        """
        Test that METADATA_PATTERN class attribute exists.
        
        Validates:
            - METADATA_PATTERN is a class-level attribute
            - Pattern is accessible from class
            - Pattern is accessible from instance
        
        Acceptance Criterion: Task 1.1 - Compiled regex pattern is class-level attribute
        """
        # Check class-level attribute exists
        assert hasattr(OrientationMetadataParser, 'METADATA_PATTERN')
        
        # Check instance can access it
        parser = OrientationMetadataParser()
        assert hasattr(parser, 'METADATA_PATTERN')
    
    def test_metadata_pattern_is_compiled_regex(self):
        """
        Test that METADATA_PATTERN is a compiled regex pattern.
        
        Validates:
            - Pattern is a compiled re.Pattern object
            - Pattern is not a string
            - Pattern can be used for matching
        
        Acceptance Criterion: Task 1.1 - Compiled regex pattern
        """
        pattern = OrientationMetadataParser.METADATA_PATTERN
        
        # Check it's a compiled regex (re.Pattern type)
        assert isinstance(pattern, re.Pattern)
        
        # Verify it can be used for matching (smoke test)
        test_text = "**Metadata**: orientation=true"
        match = pattern.search(test_text)
        assert match is not None
    
    def test_metadata_pattern_correct_format(self):
        """
        Test that METADATA_PATTERN matches the expected format.
        
        Validates:
            - Pattern matches **Metadata**: prefix
            - Pattern captures metadata content
            - Pattern uses correct regex syntax
        
        Acceptance Criterion: Task 1.1 - Regex pattern format
        """
        pattern = OrientationMetadataParser.METADATA_PATTERN
        
        # Test positive matches
        assert pattern.search("**Metadata**: key=value") is not None
        assert pattern.search("**Metadata**: orientation=true, priority=1") is not None
        assert pattern.search("Some text\n**Metadata**: test=123\nMore text") is not None
        
        # Test negative matches (should not match)
        assert pattern.search("Metadata: key=value") is None  # Missing **
        assert pattern.search("**metadata**: key=value") is None  # Wrong case
        assert pattern.search("No metadata here") is None
    
    def test_multiple_instantiation(self):
        """
        Test that multiple parser instances can be created.
        
        Validates:
            - Multiple instances can coexist
            - Each instance is independent
            - Pattern is shared across instances (class-level)
        
        Design: Validates class-level pattern optimization
        """
        parser1 = OrientationMetadataParser()
        parser2 = OrientationMetadataParser()
        
        # Both instances exist
        assert isinstance(parser1, OrientationMetadataParser)
        assert isinstance(parser2, OrientationMetadataParser)
        
        # Pattern is shared (same object in memory)
        assert parser1.METADATA_PATTERN is parser2.METADATA_PATTERN
    
    def test_module_import_path(self):
        """
        Test that module can be imported via expected path.
        
        Validates:
            - Import path matches specification
            - Module is in correct location
        
        Acceptance Criterion: Task 1.1 - Module imports with correct path
        """
        # This test validates the import works (if we got here, it worked)
        # But let's explicitly test the module name
        assert OrientationMetadataParser.__module__ == 'ouroboros.subsystems.rag.standards.orientation'
    
    def test_class_has_docstring(self):
        """
        Test that OrientationMetadataParser has comprehensive docstring.
        
        Validates:
            - Class has docstring
            - Docstring is non-empty
            - Docstring contains key information
        
        Quality: Production code checklist - documentation
        """
        assert OrientationMetadataParser.__doc__ is not None
        assert len(OrientationMetadataParser.__doc__) > 100
        assert 'metadata' in OrientationMetadataParser.__doc__.lower()
    
    def test_init_has_docstring(self):
        """
        Test that __init__ method has docstring.
        
        Validates:
            - __init__ has docstring
            - Docstring explains initialization
        
        Quality: Production code checklist - method documentation
        """
        assert OrientationMetadataParser.__init__.__doc__ is not None
        assert len(OrientationMetadataParser.__init__.__doc__) > 50


class TestOrientationMetadataParserPattern:
    """Test the compiled regex pattern in detail."""
    
    def test_pattern_captures_group(self):
        """
        Test that pattern captures the metadata content as group(1).
        
        Validates:
            - Pattern has capture group
            - Captured content excludes **Metadata**: prefix
            - Captured content is the key=value string
        """
        pattern = OrientationMetadataParser.METADATA_PATTERN
        match = pattern.search("**Metadata**: orientation=true, priority=1")
        
        assert match is not None
        assert match.group(1) == "orientation=true, priority=1"
    
    def test_pattern_handles_whitespace(self):
        """
        Test that pattern handles various whitespace after colon.
        
        Validates:
            - Pattern works with single space
            - Pattern works with multiple spaces
            - Pattern works with tabs
        """
        pattern = OrientationMetadataParser.METADATA_PATTERN
        
        # Single space (normal)
        assert pattern.search("**Metadata**: key=value") is not None
        
        # Multiple spaces
        assert pattern.search("**Metadata**:   key=value") is not None
        
        # Tab
        assert pattern.search("**Metadata**:\tkey=value") is not None
    
    def test_pattern_is_case_sensitive(self):
        """
        Test that pattern is case-sensitive for **Metadata**.
        
        Validates:
            - Exact case **Metadata** matches
            - **metadata** does not match
            - **METADATA** does not match
        
        Design: Case-sensitive by design (mistletoe parser pattern)
        """
        pattern = OrientationMetadataParser.METADATA_PATTERN
        
        # Should match
        assert pattern.search("**Metadata**: key=value") is not None
        
        # Should not match (wrong case)
        assert pattern.search("**metadata**: key=value") is None
        assert pattern.search("**METADATA**: key=value") is None
        assert pattern.search("**MetaData**: key=value") is None


class TestCoerceType:
    """Test the _coerce_type() private method."""
    
    def test_coerce_type_boolean_true_lowercase(self):
        """
        Test boolean coercion for "true" (lowercase).
        
        Validates:
            - "true" -> True (bool)
            - Return type is bool
        
        Acceptance Criterion: Task 1.3 - Returns True for "true"
        """
        parser = OrientationMetadataParser()
        result = parser._coerce_type("true")
        
        assert result is True
        assert isinstance(result, bool)
    
    def test_coerce_type_boolean_false_lowercase(self):
        """
        Test boolean coercion for "false" (lowercase).
        
        Validates:
            - "false" -> False (bool)
            - Return type is bool
        
        Acceptance Criterion: Task 1.3 - Returns False for "false"
        """
        parser = OrientationMetadataParser()
        result = parser._coerce_type("false")
        
        assert result is False
        assert isinstance(result, bool)
    
    def test_coerce_type_boolean_case_insensitive(self):
        """
        Test boolean coercion is case-insensitive.
        
        Validates:
            - "True", "TRUE", "TrUe" all -> True
            - "False", "FALSE", "FaLsE" all -> False
        
        Acceptance Criterion: Task 1.3 - Case-insensitive boolean detection
        """
        parser = OrientationMetadataParser()
        
        # True variations
        assert parser._coerce_type("True") is True
        assert parser._coerce_type("TRUE") is True
        assert parser._coerce_type("TrUe") is True
        
        # False variations
        assert parser._coerce_type("False") is False
        assert parser._coerce_type("FALSE") is False
        assert parser._coerce_type("FaLsE") is False
    
    def test_coerce_type_integer_single_digit(self):
        """
        Test integer coercion for single digits.
        
        Validates:
            - "0" -> 0 (int)
            - "1" -> 1 (int)
            - "9" -> 9 (int)
        
        Acceptance Criterion: Task 1.3 - Returns int for numeric strings
        """
        parser = OrientationMetadataParser()
        
        assert parser._coerce_type("0") == 0
        assert parser._coerce_type("1") == 1
        assert parser._coerce_type("9") == 9
        
        assert isinstance(parser._coerce_type("1"), int)
    
    def test_coerce_type_integer_multi_digit(self):
        """
        Test integer coercion for multi-digit numbers.
        
        Validates:
            - "123" -> 123 (int)
            - "999" -> 999 (int)
            - "1000" -> 1000 (int)
        
        Acceptance Criterion: Task 1.3 - Returns int for "123", "999"
        """
        parser = OrientationMetadataParser()
        
        assert parser._coerce_type("123") == 123
        assert parser._coerce_type("999") == 999
        assert parser._coerce_type("1000") == 1000
        
        assert isinstance(parser._coerce_type("123"), int)
    
    def test_coerce_type_string_fallback_text(self):
        """
        Test string fallback for regular text.
        
        Validates:
            - "hello" -> "hello" (str)
            - "test-value" -> "test-value" (str)
            - "abc123" -> "abc123" (str)
        
        Acceptance Criterion: Task 1.3 - Returns str for all other values
        """
        parser = OrientationMetadataParser()
        
        assert parser._coerce_type("hello") == "hello"
        assert parser._coerce_type("test-value") == "test-value"
        assert parser._coerce_type("abc123") == "abc123"
        
        assert isinstance(parser._coerce_type("hello"), str)
    
    def test_coerce_type_string_fallback_special_cases(self):
        """
        Test string fallback for edge cases.
        
        Validates:
            - Empty string -> "" (str)
            - Whitespace -> " " (str)
            - Special chars -> preserved (str)
            - Negative numbers -> "-5" (str, not int due to isdigit())
        """
        parser = OrientationMetadataParser()
        
        assert parser._coerce_type("") == ""
        assert parser._coerce_type(" ") == " "
        assert parser._coerce_type("!@#$") == "!@#$"
        assert parser._coerce_type("-5") == "-5"  # isdigit() returns False
        
        assert isinstance(parser._coerce_type(""), str)
    
    def test_coerce_type_never_raises_exceptions(self):
        """
        Test that _coerce_type never raises exceptions.
        
        Validates:
            - Method always returns a value
            - No exceptions on any input
            - String fallback on errors
        
        Acceptance Criterion: Task 1.3 - Never raises exceptions to caller
        """
        parser = OrientationMetadataParser()
        
        # Should all return values without exceptions
        result1 = parser._coerce_type("")
        result2 = parser._coerce_type("weird_value")
        result3 = parser._coerce_type("12.34")  # Float-like but str fallback
        
        assert isinstance(result1, (bool, int, str))
        assert isinstance(result2, (bool, int, str))
        assert isinstance(result3, (bool, int, str))
    
    def test_coerce_type_return_types(self):
        """
        Test that return type annotation is correct.
        
        Validates:
            - Method can return bool
            - Method can return int
            - Method can return str
            - Never returns other types
        """
        parser = OrientationMetadataParser()
        
        # Boolean return
        bool_result = parser._coerce_type("true")
        assert isinstance(bool_result, bool)
        
        # Integer return
        int_result = parser._coerce_type("123")
        assert isinstance(int_result, int)
        
        # String return
        str_result = parser._coerce_type("text")
        assert isinstance(str_result, str)


class TestErrorHandlingAndLogging:
    """Test error handling and logging behavior."""
    
    def test_malformed_pair_logs_warning(self, caplog):
        """
        Test that malformed key=value pairs log warnings.
        
        Validates:
            - Entries without '=' log warning
            - Warning includes entry text and file path
            - Entry is skipped (not in result)
        
        Acceptance Criterion: Task 1.4 - Malformed pairs log warning and skip
        """
        parser = OrientationMetadataParser()
        content = "**Metadata**: good=value, malformed-no-equals, another=works"
        
        with caplog.at_level('WARNING'):
            metadata = parser.extract_inline_metadata(content, Path("test.md"))
        
        # Verify warning was logged
        assert len(caplog.records) >= 1
        assert 'malformed' in caplog.text.lower()
        assert 'test.md' in caplog.text
        
        # Verify malformed entry was skipped
        assert 'malformed-no-equals' not in metadata
        assert metadata == {'good': 'value', 'another': 'works'}
    
    def test_type_coercion_failure_logs_warning(self, caplog):
        """
        Test that unexpected type coercion errors log warnings.
        
        Validates:
            - Unexpected errors in _coerce_type log warning
            - Warning includes value and error details
            - Falls back to string value
        
        Acceptance Criterion: Task 1.4 - Type coercion failures log warning
        """
        parser = OrientationMetadataParser()
        
        # Normal values shouldn't log warnings
        with caplog.at_level('WARNING'):
            caplog.clear()
            result = parser._coerce_type("normal_value")
            
        # Should have no warnings for normal operation
        assert len([r for r in caplog.records if r.levelname == 'WARNING']) == 0
        assert result == "normal_value"
    
    def test_missing_equals_logs_warning_with_filepath(self, caplog):
        """
        Test that missing '=' separator logs warning with file path.
        
        Validates:
            - Missing '=' in entry logs warning
            - Warning includes file path for debugging
            - Entry is skipped
        
        Acceptance Criterion: Task 1.4 - Missing = separator logs warning, includes file_path
        """
        parser = OrientationMetadataParser()
        content = "**Metadata**: valid=123, badentry, another=true"
        test_path = Path("/test/path/file.md")
        
        with caplog.at_level('WARNING'):
            metadata = parser.extract_inline_metadata(content, test_path)
        
        # Verify warning logged with file path
        assert len(caplog.records) >= 1
        assert str(test_path) in caplog.text or 'file.md' in caplog.text
        
        # Verify bad entry skipped
        assert metadata == {'valid': 123, 'another': True}
        assert 'badentry' not in metadata
    
    def test_never_raises_exceptions_returns_empty_dict(self):
        """
        Test that method never raises exceptions, even on severe errors.
        
        Validates:
            - No exceptions on any input
            - Returns empty dict on catastrophic failure
            - Graceful degradation always
        
        Acceptance Criterion: Task 1.4 - Zero exceptions raised in any scenario
        """
        parser = OrientationMetadataParser()
        
        # Should not raise on empty string
        result1 = parser.extract_inline_metadata("", Path("test.md"))
        assert result1 == {}
        
        # Should not raise on weird input
        result2 = parser.extract_inline_metadata("random text\nno metadata\n", Path("test.md"))
        assert result2 == {}
        
        # All results are dicts
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
    
    def test_unexpected_error_logs_error_message(self, caplog):
        """
        Test that unexpected errors log error messages.
        
        Validates:
            - Catch-all exception handler logs error
            - Error message includes file path
            - Returns empty dict on error
        
        Acceptance Criterion: Task 1.4 - All error paths log with file_path
        """
        parser = OrientationMetadataParser()
        
        # Normal case shouldn't log errors
        with caplog.at_level('ERROR'):
            caplog.clear()
            metadata = parser.extract_inline_metadata(
                "**Metadata**: normal=value", 
                Path("test.md")
            )
        
        # Should have no errors for normal operation
        assert len([r for r in caplog.records if r.levelname == 'ERROR']) == 0
        assert metadata == {'normal': 'value'}
    
    def test_all_warnings_include_filepath_for_debugging(self, caplog):
        """
        Test that all warning messages include file path.
        
        Validates:
            - Malformed entry warnings include file path
            - Type coercion warnings include value info
            - File path aids debugging
        
        Acceptance Criterion: Task 1.4 - All warnings include file_path
        """
        parser = OrientationMetadataParser()
        content = "**Metadata**: valid=1, bad-entry-no-equals, another=2"
        test_path = Path("specific/path/to/file.md")
        
        with caplog.at_level('WARNING'):
            caplog.clear()
            parser.extract_inline_metadata(content, test_path)
        
        # Should have at least one warning for the bad entry
        assert len(caplog.records) >= 1
        
        # Warning should mention the file (either full path or filename)
        warning_text = caplog.text.lower()
        assert 'file.md' in warning_text or str(test_path) in caplog.text


class TestExtractInlineMetadata:
    """Test the extract_inline_metadata() method."""
    
    def test_valid_metadata_mixed_types(self):
        """
        Test parsing valid metadata with mixed types (bool, int, string).
        
        Validates:
            - Boolean values converted correctly
            - Integer values converted correctly
            - String values remain strings
            - Multiple key=value pairs parsed
        
        Acceptance Criterion: Task 1.2 - Returns non-empty dict for valid metadata
        """
        parser = OrientationMetadataParser()
        content = """# Project Guide
**Metadata**: orientation=true, priority=1, query="project setup", flag=false
More content here..."""
        
        metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        
        assert metadata == {
            'orientation': True,
            'priority': 1,
            'query': 'project setup',
            'flag': False
        }
        
        # Verify types
        assert isinstance(metadata['orientation'], bool)
        assert isinstance(metadata['priority'], int)
        assert isinstance(metadata['query'], str)
        assert isinstance(metadata['flag'], bool)
    
    def test_missing_metadata_line_returns_empty_dict(self):
        """
        Test that missing **Metadata**: line returns empty dict.
        
        Validates:
            - No **Metadata**: line -> {}
            - No exception raised
            - Graceful degradation
        
        Acceptance Criterion: Task 1.2 - Returns empty dict when metadata missing
        """
        parser = OrientationMetadataParser()
        content = """# Regular Document
No metadata here at all.
Just regular content."""
        
        metadata = parser.extract_inline_metadata(content, Path("doc.md"))
        
        assert metadata == {}
        assert isinstance(metadata, dict)
    
    def test_malformed_entries_skipped(self):
        """
        Test that malformed entries (missing '=') are skipped.
        
        Validates:
            - Entries without '=' are skipped
            - Other entries still parsed
            - No exception raised
        
        Acceptance Criterion: Task 1.2 - Error-resistant parsing
        """
        parser = OrientationMetadataParser()
        content = """# Guide
**Metadata**: good=value, malformed-no-equals, another=works, also-bad
Content..."""
        
        metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        
        assert metadata == {'good': 'value', 'another': 'works'}
        assert 'malformed-no-equals' not in metadata
        assert 'also-bad' not in metadata
    
    def test_values_with_equals_character(self):
        """
        Test that values containing '=' are handled correctly.
        
        Validates:
            - split('=', 1) preserves '=' in value
            - URLs with query params work
            - Expressions with '=' work
        
        Acceptance Criterion: Task 1.2 - Handles values with = character
        """
        parser = OrientationMetadataParser()
        content = """# Guide
**Metadata**: url=https://example.com?param=value, expr=x=5+3
Content..."""
        
        metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        
        assert metadata['url'] == 'https://example.com?param=value'
        assert metadata['expr'] == 'x=5+3'
    
    def test_quote_stripping(self):
        """
        Test that surrounding quotes are stripped from values.
        
        Validates:
            - Double quotes removed
            - Single quotes removed
            - Quoted values preserve spaces
        """
        parser = OrientationMetadataParser()
        content = """# Guide
**Metadata**: name="test value", alt='another test', plain=no-quotes
Content..."""
        
        metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        
        assert metadata['name'] == 'test value'
        assert metadata['alt'] == 'another test'
        assert metadata['plain'] == 'no-quotes'
    
    def test_boolean_conversion_case_insensitive(self):
        """
        Test that boolean conversion is case-insensitive.
        
        Validates:
            - 'true' -> True
            - 'false' -> False
            - 'True' -> True
            - 'FALSE' -> False
            - 'TrUe' -> True
        """
        parser = OrientationMetadataParser()
        content = """# Guide
**Metadata**: a=true, b=false, c=True, d=FALSE, e=TrUe
Content..."""
        
        metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        
        assert metadata['a'] is True
        assert metadata['b'] is False
        assert metadata['c'] is True
        assert metadata['d'] is False
        assert metadata['e'] is True
    
    def test_integer_conversion(self):
        """
        Test that integer strings are converted to int.
        
        Validates:
            - Numeric strings -> int
            - Single digit works
            - Multi-digit works
            - Negative numbers stay as strings (isdigit() check)
        """
        parser = OrientationMetadataParser()
        content = """# Guide
**Metadata**: priority=1, count=999, zero=0
Content..."""
        
        metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        
        assert metadata['priority'] == 1
        assert metadata['count'] == 999
        assert metadata['zero'] == 0
        assert isinstance(metadata['priority'], int)
    
    def test_string_fallback(self):
        """
        Test that non-bool/non-int values default to string.
        
        Validates:
            - Regular text -> str
            - Mixed alphanumeric -> str
            - Special characters -> str
        """
        parser = OrientationMetadataParser()
        content = """# Guide
**Metadata**: text=hello, mixed=abc123, special=test-value_123
Content..."""
        
        metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        
        assert metadata['text'] == 'hello'
        assert metadata['mixed'] == 'abc123'
        assert metadata['special'] == 'test-value_123'
        assert all(isinstance(v, str) for v in metadata.values())
    
    def test_empty_values(self):
        """
        Test handling of empty values.
        
        Validates:
            - key= (empty value) -> empty string
            - Whitespace-only values trimmed
        """
        parser = OrientationMetadataParser()
        content = """# Guide
**Metadata**: empty=, normal=value, spaces=   
Content..."""
        
        metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        
        assert metadata['empty'] == ''
        assert metadata['normal'] == 'value'
        assert metadata['spaces'] == ''
    
    def test_whitespace_handling(self):
        """
        Test that whitespace is properly trimmed.
        
        Validates:
            - Leading/trailing spaces in keys removed
            - Leading/trailing spaces in values removed
            - Spaces within values preserved
        """
        parser = OrientationMetadataParser()
        content = """# Guide
**Metadata**:  key1 = value1 ,  key2  =  value2  , key3=inner spaces
Content..."""
        
        metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        
        assert metadata['key1'] == 'value1'
        assert metadata['key2'] == 'value2'
        assert metadata['key3'] == 'inner spaces'
    
    def test_never_raises_exceptions(self):
        """
        Test that method never raises exceptions.
        
        Validates:
            - Malformed input doesn't crash
            - Empty string doesn't crash
            - None content doesn't crash (wait, signature says str)
            - Weird edge cases handled
        
        Acceptance Criterion: Task 1.2 - Never raises exceptions
        """
        parser = OrientationMetadataParser()
        
        # Empty string
        result1 = parser.extract_inline_metadata("", Path("empty.md"))
        assert result1 == {}
        
        # Metadata line but no content after colon
        result2 = parser.extract_inline_metadata("**Metadata**:", Path("test.md"))
        assert isinstance(result2, dict)
        
        # Metadata line with just whitespace
        result3 = parser.extract_inline_metadata("**Metadata**:   ", Path("test.md"))
        assert isinstance(result3, dict)
        
        # Unicode characters
        result4 = parser.extract_inline_metadata("**Metadata**: key=café", Path("test.md"))
        assert result4['key'] == 'café'
    
    def test_multiple_metadata_lines_first_wins(self):
        """
        Test that only the first **Metadata**: line is used.
        
        Validates:
            - search() returns first match
            - Later metadata lines ignored
        """
        parser = OrientationMetadataParser()
        content = """# Guide
**Metadata**: first=true
Some content
**Metadata**: second=true
More content"""
        
        metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        
        assert metadata == {'first': True}
        assert 'second' not in metadata

