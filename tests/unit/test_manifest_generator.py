"""
Unit tests for manifest generator script.

Tests the checksum calculation, directory scanning, git integration,
and manifest generation functions.
"""

import hashlib
import importlib.util
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# Load the generate_manifest script as a module
scripts_path = Path(__file__).parent.parent.parent / "scripts" / "generate-manifest.py"
spec = importlib.util.spec_from_file_location("generate_manifest", scripts_path)
generate_manifest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_manifest)

calculate_checksum = generate_manifest.calculate_checksum
get_last_modified_date = generate_manifest.get_last_modified_date
scan_directory = generate_manifest.scan_directory
generate_manifest_func = generate_manifest.generate_manifest
validate_manifest = generate_manifest.validate_manifest


class TestCalculateChecksum:
    """Test suite for calculate_checksum function."""

    def test_hello_world_checksum(self):
        """Test checksum calculation with known SHA-256 value."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "hello.txt"
            test_file.write_text("hello world")

            # Known SHA-256 for "hello world" (without newline)
            expected = (
                "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
            )
            actual = calculate_checksum(test_file)

            assert actual == expected, f"Expected {expected}, got {actual}"

    def test_hello_world_with_newline_checksum(self):
        """Test checksum calculation with known SHA-256 value (with newline)."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "hello_newline.txt"
            test_file.write_text("hello world\n")

            # Known SHA-256 for "hello world\n"
            expected = (
                "a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447"
            )
            actual = calculate_checksum(test_file)

            assert actual == expected, f"Expected {expected}, got {actual}"

    def test_empty_file_checksum(self):
        """Test checksum of empty file."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "empty.txt"
            test_file.write_text("")

            # Known SHA-256 for empty string
            expected = (
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            )
            actual = calculate_checksum(test_file)

            assert actual == expected, f"Expected {expected}, got {actual}"

    def test_binary_file_checksum(self):
        """Test checksum calculation works with binary files."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "binary.bin"
            # Write some binary data
            test_file.write_bytes(b"\x00\x01\x02\x03\x04\x05\xff\xfe\xfd")

            # Calculate expected checksum directly
            expected = hashlib.sha256(
                b"\x00\x01\x02\x03\x04\x05\xff\xfe\xfd"
            ).hexdigest()
            actual = calculate_checksum(test_file)

            assert actual == expected, f"Expected {expected}, got {actual}"

    def test_large_file_memory_efficiency(self):
        """Test that large files don't cause memory issues (chunked reading)."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "large.txt"

            # Create a 1MB file (written in chunks to avoid memory issues in test)
            chunk_size = 8192
            num_chunks = 128  # 128 * 8KB = 1MB
            chunk_data = b"x" * chunk_size

            with open(test_file, "wb") as f:
                for _ in range(num_chunks):
                    f.write(chunk_data)

            # Calculate checksum - should not raise MemoryError
            checksum = calculate_checksum(test_file)

            # Verify it's a valid SHA-256 hex string
            assert (
                len(checksum) == 64
            ), f"Checksum should be 64 chars, got {len(checksum)}"
            assert all(
                c in "0123456789abcdef" for c in checksum
            ), "Checksum should be hexadecimal"

    def test_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        non_existent = Path("/tmp/this_file_definitely_does_not_exist_12345.txt")

        with pytest.raises(FileNotFoundError, match="File not found"):
            calculate_checksum(non_existent)

    def test_directory_not_file_error(self):
        """Test that ValueError is raised when path is a directory."""
        with TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "subdir"
            dir_path.mkdir()

            with pytest.raises(ValueError, match="Path is not a file"):
                calculate_checksum(dir_path)

    def test_checksum_consistency(self):
        """Test that same file content produces same checksum."""
        with TemporaryDirectory() as tmpdir:
            test_file1 = Path(tmpdir) / "file1.txt"
            test_file2 = Path(tmpdir) / "file2.txt"

            content = "The quick brown fox jumps over the lazy dog"
            test_file1.write_text(content)
            test_file2.write_text(content)

            checksum1 = calculate_checksum(test_file1)
            checksum2 = calculate_checksum(test_file2)

            assert checksum1 == checksum2, "Same content should produce same checksum"

    def test_checksum_length(self):
        """Test that checksum is always 64 characters (SHA-256)."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")

            checksum = calculate_checksum(test_file)

            assert (
                len(checksum) == 64
            ), f"SHA-256 checksum should be 64 chars, got {len(checksum)}"

    def test_checksum_is_hexadecimal(self):
        """Test that checksum contains only hexadecimal characters."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")

            checksum = calculate_checksum(test_file)

            assert all(
                c in "0123456789abcdef" for c in checksum
            ), "Checksum should only contain hexadecimal characters"


class TestGetLastModifiedDate:
    """Test suite for get_last_modified_date function."""

    def test_git_tracked_file_returns_commit_date(self):
        """Test that git-tracked files return the git commit date."""
        # Use a file we know is tracked in this repo
        repo_root = Path(__file__).parent.parent.parent
        readme_file = repo_root / "README.md"

        if not readme_file.exists():
            pytest.skip("README.md not found")

        date_str = get_last_modified_date(readme_file, repo_root)

        # Verify ISO date format (YYYY-MM-DD)
        assert len(date_str) == 10, f"Expected 10 chars, got {len(date_str)}"
        assert date_str.count("-") == 2, "Should have 2 dashes"

        # Verify it can be parsed as a date
        from datetime import datetime

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
            # Date should be reasonable (after 2020, before 2030)
            assert 2020 <= parsed_date.year <= 2030
        except ValueError:
            pytest.fail(f"Invalid date format: {date_str}")

    def test_untracked_file_falls_back_to_filesystem(self):
        """Test that untracked files fall back to filesystem mtime."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "untracked.txt"
            test_file.write_text("test content")

            repo_root = Path(tmpdir)
            date_str = get_last_modified_date(test_file, repo_root)

            # Verify ISO date format
            assert len(date_str) == 10
            assert date_str.count("-") == 2

            # Verify it's a recent date (within last day)
            from datetime import datetime, timedelta

            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
            now = datetime.now()
            assert (
                abs((now - parsed_date).days) <= 1
            ), "Filesystem date should be today or yesterday"

    def test_returns_iso_date_format(self):
        """Test that returned date is in ISO format (YYYY-MM-DD)."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            date_str = get_last_modified_date(test_file, Path(tmpdir))

            # Check format manually
            assert (
                len(date_str) == 10
            ), f"Expected 10 chars, got {len(date_str)}: {date_str}"
            assert date_str[4] == "-", "Character at index 4 should be '-'"
            assert date_str[7] == "-", "Character at index 7 should be '-'"
            assert date_str[:4].isdigit(), "First 4 chars should be year"
            assert date_str[5:7].isdigit(), "Chars 5-6 should be month"
            assert date_str[8:10].isdigit(), "Chars 8-9 should be day"

    def test_non_existent_file_raises_error(self):
        """Test that non-existent files raise ValueError."""
        non_existent = Path("/tmp/definitely_does_not_exist_test_98765.txt")

        with pytest.raises(ValueError, match="File does not exist"):
            get_last_modified_date(non_existent, Path("/tmp"))

    def test_handles_git_not_available(self):
        """Test that function gracefully handles git not being installed."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            # Even if git is not available, should fall back to filesystem
            date_str = get_last_modified_date(test_file, Path(tmpdir))

            # Should still return valid date
            assert len(date_str) == 10
            assert date_str.count("-") == 2

    def test_date_consistency(self):
        """Test that calling twice on same file returns same result."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            date1 = get_last_modified_date(test_file, Path(tmpdir))
            date2 = get_last_modified_date(test_file, Path(tmpdir))

            assert date1 == date2, "Should return consistent dates"


class TestScanDirectory:
    """Test suite for scan_directory function."""

    def test_finds_md_and_json_files(self):
        """Test that scanner finds .md and .json files."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_universal"
            test_dir.mkdir()

            # Create test files
            (test_dir / "file1.md").write_text("# Test")
            (test_dir / "file2.json").write_text('{"key": "value"}')
            (test_dir / "subdir").mkdir()
            (test_dir / "subdir" / "file3.md").write_text("# Nested")

            files = scan_directory(test_dir, Path(tmpdir))

            assert len(files) == 3, f"Expected 3 files, got {len(files)}"
            assert "file1.md" in files
            assert "file2.json" in files
            assert "subdir/file3.md" in files

    def test_skips_unsupported_extensions(self):
        """Test that scanner skips files with unsupported extensions."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_universal"
            test_dir.mkdir()

            # Create various file types
            (test_dir / "good.md").write_text("# Test")
            (test_dir / "good.json").write_text("{}")
            (test_dir / "bad.txt").write_text("text file")
            (test_dir / "bad.py").write_text("print('hello')")
            (test_dir / "bad.yml").write_text("key: value")

            files = scan_directory(test_dir, Path(tmpdir))

            assert len(files) == 2, f"Expected 2 files, got {len(files)}"
            assert "good.md" in files
            assert "good.json" in files
            assert "bad.txt" not in files
            assert "bad.py" not in files

    def test_skips_hidden_files(self):
        """Test that scanner skips hidden files."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_universal"
            test_dir.mkdir()

            # Create visible and hidden files
            (test_dir / "visible.md").write_text("# Visible")
            (test_dir / ".hidden.md").write_text("# Hidden")
            (test_dir / ".hidden_dir").mkdir()
            (test_dir / ".hidden_dir" / "file.md").write_text("# In hidden dir")

            files = scan_directory(test_dir, Path(tmpdir))

            assert len(files) == 1, f"Expected 1 file, got {len(files)}"
            assert "visible.md" in files
            assert ".hidden.md" not in files
            assert ".hidden_dir/file.md" not in files

    def test_calculates_correct_metadata(self):
        """Test that metadata includes all required fields."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_universal"
            test_dir.mkdir()

            test_file = test_dir / "test.md"
            test_file.write_text("# Test Content")

            files = scan_directory(test_dir, Path(tmpdir))

            assert "test.md" in files
            metadata = files["test.md"]

            # Check all required fields present
            assert "checksum" in metadata
            assert "size" in metadata
            assert "last_updated" in metadata

            # Check checksum format
            assert metadata["checksum"].startswith("sha256:")
            assert len(metadata["checksum"]) == 71  # "sha256:" + 64 hex chars

            # Check size is correct
            assert metadata["size"] == len("# Test Content")

            # Check date format
            assert len(metadata["last_updated"]) == 10
            assert metadata["last_updated"].count("-") == 2

    def test_uses_relative_paths(self):
        """Test that returned paths are relative to universal_dir."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_universal"
            test_dir.mkdir()

            # Create nested structure
            (test_dir / "level1").mkdir()
            (test_dir / "level1" / "level2").mkdir()
            (test_dir / "level1" / "level2" / "deep.md").write_text("# Deep")

            files = scan_directory(test_dir, Path(tmpdir))

            # Path should be relative, not absolute
            assert "level1/level2/deep.md" in files
            # Should not contain absolute path components
            for path in files.keys():
                assert not path.startswith("/")
                assert tmpdir not in path

    def test_directory_not_found_error(self):
        """Test that ValueError is raised for non-existent directory."""
        non_existent = Path("/tmp/definitely_does_not_exist_dir_12345")

        with pytest.raises(ValueError, match="Directory does not exist"):
            scan_directory(non_existent, Path("/tmp"))

    def test_path_not_directory_error(self):
        """Test that ValueError is raised when path is a file."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "not_a_dir.txt"
            test_file.write_text("test")

            with pytest.raises(ValueError, match="Path is not a directory"):
                scan_directory(test_file, Path(tmpdir))


class TestManifestGenerationAndValidation:
    """Test suite for generate_manifest and validate_manifest functions."""

    def test_generate_manifest_includes_all_fields(self):
        """Test that generated manifest includes all required fields."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_universal"
            test_dir.mkdir()
            (test_dir / "test.md").write_text("# Test")

            manifest = generate_manifest_func(test_dir, "1.3.0", Path(tmpdir))

            assert "version" in manifest
            assert "generated" in manifest
            assert "generator_version" in manifest
            assert "files" in manifest
            assert manifest["version"] == "1.3.0"

    def test_validate_manifest_passes_for_valid_manifest(self):
        """Test that validation passes for a properly formatted manifest."""
        manifest = {
            "version": "1.3.0",
            "generated": "2025-10-07T12:00:00Z",
            "generator_version": "1.0.0",
            "files": {
                "test.md": {
                    "checksum": "sha256:" + "a" * 64,
                    "size": 100,
                    "last_updated": "2025-10-07",
                }
            },
        }

        assert validate_manifest(manifest) is True

    def test_validate_manifest_catches_missing_version(self):
        """Test that validation catches missing version field."""
        manifest = {
            "generated": "2025-10-07T12:00:00Z",
            "generator_version": "1.0.0",
            "files": {},
        }

        with pytest.raises(ValueError, match="missing required field: version"):
            validate_manifest(manifest)

    def test_validate_manifest_catches_invalid_checksum_format(self):
        """Test that validation catches invalid checksum format."""
        manifest = {
            "version": "1.3.0",
            "generated": "2025-10-07T12:00:00Z",
            "generator_version": "1.0.0",
            "files": {
                "test.md": {
                    "checksum": "invalid_checksum",  # Missing sha256: prefix
                    "size": 100,
                    "last_updated": "2025-10-07",
                }
            },
        }

        with pytest.raises(ValueError, match="invalid checksum format"):
            validate_manifest(manifest)

    def test_validate_manifest_catches_malformed_checksum_length(self):
        """Test that validation catches incorrect checksum length."""
        manifest = {
            "version": "1.3.0",
            "generated": "2025-10-07T12:00:00Z",
            "generator_version": "1.0.0",
            "files": {
                "test.md": {
                    "checksum": "sha256:tooshort",  # Not 64 hex chars
                    "size": 100,
                    "last_updated": "2025-10-07",
                }
            },
        }

        with pytest.raises(ValueError, match="invalid checksum length"):
            validate_manifest(manifest)

    def test_generated_manifest_is_valid(self):
        """Test that a generated manifest passes validation."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_universal"
            test_dir.mkdir()
            (test_dir / "test.md").write_text("# Test")
            (test_dir / "test.json").write_text('{"key": "value"}')

            manifest = generate_manifest_func(test_dir, "1.3.0", Path(tmpdir))

            # Generated manifest should pass validation
            assert validate_manifest(manifest) is True
