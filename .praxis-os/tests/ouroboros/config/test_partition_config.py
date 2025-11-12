"""Unit tests for partition configuration models.

Tests the new DomainConfig and PartitionConfig Pydantic models for multi-repo
code intelligence with simplified architecture.
"""

import pytest
from pydantic import ValidationError

from ouroboros.config.schemas.indexes import DomainConfig, PartitionConfig


class TestDomainConfig:
    """Test DomainConfig Pydantic model."""
    
    def test_valid_domain_minimal(self):
        """Test creating domain with minimal required fields."""
        domain = DomainConfig(
            include_paths=["src/"]
        )
        
        assert domain.include_paths == ["src/"]
        assert domain.exclude_patterns is None
        assert domain.metadata is None
    
    def test_valid_domain_with_metadata(self):
        """Test creating domain with metadata for filtering."""
        domain = DomainConfig(
            include_paths=["instrumentation/openai/"],
            exclude_patterns=["generated/"],
            metadata={
                "framework": "openai",
                "type": "instrumentor",
                "provider": "openlit"
            }
        )
        
        assert domain.include_paths == ["instrumentation/openai/"]
        assert domain.exclude_patterns == ["generated/"]
        assert domain.metadata == {
            "framework": "openai",
            "type": "instrumentor",
            "provider": "openlit"
        }
    
    def test_invalid_empty_include_paths(self):
        """Test that empty include_paths is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            DomainConfig(include_paths=[])
        
        assert "at least 1 item" in str(exc_info.value).lower()
    
    def test_invalid_missing_include_paths(self):
        """Test that missing include_paths is invalid."""
        with pytest.raises(ValidationError):
            DomainConfig()  # type: ignore


class TestPartitionConfig:
    """Test PartitionConfig Pydantic model."""
    
    def test_valid_partition_single_domain(self):
        """Test creating partition with single domain."""
        partition = PartitionConfig(
            path="../",
            domains={
                "code": DomainConfig(include_paths=["src/"])
            }
        )
        
        assert partition.path == "../"
        assert len(partition.domains) == 1
        assert "code" in partition.domains
        assert partition.domains["code"].include_paths == ["src/"]
    
    def test_valid_partition_multiple_domains(self):
        """Test creating partition with multiple domains."""
        partition = PartitionConfig(
            path="../",
            domains={
                "code": DomainConfig(
                    include_paths=["ouroboros/", "scripts/"],
                    metadata=None
                ),
                "tests": DomainConfig(
                    include_paths=["tests/"],
                    metadata={"type": "tests"}
                )
            }
        )
        
        assert partition.path == "../"
        assert len(partition.domains) == 2
        assert "code" in partition.domains
        assert "tests" in partition.domains
        assert partition.domains["tests"].metadata == {"type": "tests"}
    
    def test_invalid_empty_domains(self):
        """Test that empty domains dict is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            PartitionConfig(
                path="../",
                domains={}
            )
        
        assert "at least 1 item" in str(exc_info.value).lower()
    
    def test_invalid_domain_name_with_spaces(self):
        """Test that domain names with spaces are invalid."""
        with pytest.raises(ValidationError) as exc_info:
            PartitionConfig(
                path="../",
                domains={
                    "my code": DomainConfig(include_paths=["src/"])
                }
            )
        
        error_str = str(exc_info.value)
        assert "valid Python identifier" in error_str or "my code" in error_str
    
    def test_invalid_domain_name_with_hyphens(self):
        """Test that domain names with hyphens are invalid."""
        with pytest.raises(ValidationError) as exc_info:
            PartitionConfig(
                path="../",
                domains={
                    "my-code": DomainConfig(include_paths=["src/"])
                }
            )
        
        error_str = str(exc_info.value)
        assert "valid Python identifier" in error_str or "my-code" in error_str
    
    def test_valid_domain_name_with_underscores(self):
        """Test that domain names with underscores are valid."""
        partition = PartitionConfig(
            path="../",
            domains={
                "my_code": DomainConfig(include_paths=["src/"])
            }
        )
        
        assert "my_code" in partition.domains
    
    def test_invalid_missing_path(self):
        """Test that missing path is invalid."""
        with pytest.raises(ValidationError):
            PartitionConfig(  # type: ignore
                domains={
                    "code": DomainConfig(include_paths=["src/"])
                }
            )
    
    def test_invalid_empty_path(self):
        """Test that empty path is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            PartitionConfig(
                path="",
                domains={
                    "code": DomainConfig(include_paths=["src/"])
                }
            )
        
        assert "at least 1 character" in str(exc_info.value).lower()


class TestPartitionConfigIntegration:
    """Integration tests for realistic partition configurations."""
    
    def test_single_repo_simple(self):
        """Test simple single-repo configuration."""
        config = {
            "praxis-os": PartitionConfig(
                path="../",
                domains={
                    "code": DomainConfig(include_paths=["ouroboros/", "scripts/"]),
                    "tests": DomainConfig(include_paths=["tests/"])
                }
            )
        }
        
        assert len(config) == 1
        assert "praxis-os" in config
        assert len(config["praxis-os"].domains) == 2
    
    def test_instrumentor_with_metadata(self):
        """Test instrumentor configuration with rich metadata."""
        config = {
            "openlit": PartitionConfig(
                path="../deps/openlit",
                domains={
                    "openai_instrumentor": DomainConfig(
                        include_paths=["instrumentation/openai/"],
                        metadata={
                            "framework": "openai",
                            "type": "instrumentor",
                            "provider": "openlit"
                        }
                    ),
                    "anthropic_instrumentor": DomainConfig(
                        include_paths=["instrumentation/anthropic/"],
                        metadata={
                            "framework": "anthropic",
                            "type": "instrumentor",
                            "provider": "openlit"
                        }
                    )
                }
            )
        }
        
        assert len(config) == 1
        openlit = config["openlit"]
        assert len(openlit.domains) == 2
        assert openlit.domains["openai_instrumentor"].metadata["framework"] == "openai"
        assert openlit.domains["anthropic_instrumentor"].metadata["framework"] == "anthropic"
    
    def test_multi_repo_config(self):
        """Test multi-repository configuration."""
        config = {
            "praxis-os": PartitionConfig(
                path="../",
                domains={
                    "code": DomainConfig(include_paths=["ouroboros/"])
                }
            ),
            "python-sdk": PartitionConfig(
                path="../python-sdk",
                domains={
                    "code": DomainConfig(include_paths=["src/"])
                }
            ),
            "openlit": PartitionConfig(
                path="../deps/openlit",
                domains={
                    "instrumentors": DomainConfig(include_paths=["instrumentation/"])
                }
            )
        }
        
        assert len(config) == 3
        assert all(name in config for name in ["praxis-os", "python-sdk", "openlit"])

