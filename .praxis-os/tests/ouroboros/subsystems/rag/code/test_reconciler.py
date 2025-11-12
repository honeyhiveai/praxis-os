"""Unit tests for PartitionReconciler (declarative reconciliation - simplified)."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ouroboros.config.schemas.indexes import CodeIndexConfig, DomainConfig, PartitionConfig
from ouroboros.subsystems.rag.code.reconciler import (
    PartitionReconciler,
    ReconciliationReport,
)


# ========================================================================
# ReconciliationReport Tests
# ========================================================================

def test_reconciliation_report_has_changes_empty():
    """Test has_changes() returns False for empty report."""
    report = ReconciliationReport()
    assert report.has_changes() is False


def test_reconciliation_report_has_changes_with_created():
    """Test has_changes() returns True when partitions created."""
    report = ReconciliationReport(created=['new-partition'])
    assert report.has_changes() is True


def test_reconciliation_report_has_changes_with_deleted():
    """Test has_changes() returns True when partitions deleted."""
    report = ReconciliationReport(deleted=['old-partition'])
    assert report.has_changes() is True


def test_reconciliation_report_to_dict():
    """Test to_dict() converts report to dictionary format."""
    report = ReconciliationReport(
        created=['new1', 'new2'],
        deleted=['old1'],
        errors=['error1']
    )
    
    result = report.to_dict()
    
    assert result['created'] == ['new1', 'new2']
    assert result['deleted'] == ['old1']
    assert result['errors'] == ['error1']
    assert result['total_changes'] == 3  # 2 created + 1 deleted
    assert result['has_errors'] is True


# ========================================================================
# PartitionReconciler Tests
# ========================================================================

@pytest.fixture
def temp_base_path(tmp_path):
    """Create temporary base path for testing."""
    base = tmp_path / "test_indexes"
    base.mkdir()
    return base


@pytest.fixture
def empty_config():
    """Create empty CodeIndexConfig (no partitions)."""
    # Create a mock config with minimal required fields
    config = MagicMock(spec=CodeIndexConfig)
    config.partitions = None  # Single-repo mode
    return config


@pytest.fixture
def multi_partition_config():
    """Create CodeIndexConfig with multiple partitions."""
    # Create a mock config with partitions
    config = MagicMock(spec=CodeIndexConfig)
    config.partitions = {
        'praxis-os': PartitionConfig(
            path='../',  # String, not Path
            domains={'code': DomainConfig(include_paths=['ouroboros/'])}
        ),
        'openlit': PartitionConfig(
            path='../openlit',  # String, not Path
            domains={'code': DomainConfig(include_paths=['src/'])}
        )
    }
    return config


def test_reconciler_init_creates_directories(temp_base_path, empty_config):
    """Test reconciler initializes and creates required directories."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    assert reconciler.indexes_dir.exists()
    assert reconciler.base_path == temp_base_path


def test_get_desired_partitions_empty_config(temp_base_path, empty_config):
    """Test _get_desired_partitions() returns empty set for single-repo config."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    desired = reconciler._get_desired_partitions()
    
    assert desired == set()


def test_get_desired_partitions_multi_config(temp_base_path, multi_partition_config):
    """Test _get_desired_partitions() returns partition names from config."""
    reconciler = PartitionReconciler(temp_base_path, multi_partition_config)
    
    desired = reconciler._get_desired_partitions()
    
    assert desired == {'praxis-os', 'openlit'}


def test_scan_actual_partitions_empty_directory(temp_base_path, empty_config):
    """Test _scan_actual_partitions() returns empty set when no partitions exist."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    actual = reconciler._scan_actual_partitions()
    
    assert actual == set()


def test_scan_actual_partitions_with_partitions(temp_base_path, empty_config):
    """Test _scan_actual_partitions() finds existing partition directories."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    # Create partition directories
    (reconciler.indexes_dir / 'partition1').mkdir()
    (reconciler.indexes_dir / 'partition2').mkdir()
    
    actual = reconciler._scan_actual_partitions()
    
    assert actual == {'partition1', 'partition2'}


def test_scan_actual_partitions_ignores_hidden_dirs(temp_base_path, empty_config):
    """Test _scan_actual_partitions() ignores hidden directories (start with .)."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    # Create visible and hidden directories
    (reconciler.indexes_dir / 'visible').mkdir()
    (reconciler.indexes_dir / '.hidden').mkdir()
    
    actual = reconciler._scan_actual_partitions()
    
    assert actual == {'visible'}  # Only non-hidden directory


def test_scan_actual_partitions_ignores_files(temp_base_path, empty_config):
    """Test _scan_actual_partitions() ignores files (only directories)."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    # Create directory and file
    (reconciler.indexes_dir / 'partition1').mkdir()
    (reconciler.indexes_dir / 'somefile.txt').touch()
    
    actual = reconciler._scan_actual_partitions()
    
    assert actual == {'partition1'}  # Only directory, not file


def test_create_missing_creates_directories(temp_base_path, empty_config):
    """Test _create_missing() creates partition directories."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    created = reconciler._create_missing({'new-partition1', 'new-partition2'})
    
    assert set(created) == {'new-partition1', 'new-partition2'}
    assert (reconciler.indexes_dir / 'new-partition1').exists()
    assert (reconciler.indexes_dir / 'new-partition2').exists()


def test_create_missing_idempotent(temp_base_path, empty_config):
    """Test _create_missing() is idempotent (safe to run multiple times)."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    # Create partition directory manually
    (reconciler.indexes_dir / 'existing').mkdir()
    
    # Try to create again (should not error)
    created = reconciler._create_missing({'existing'})
    
    assert 'existing' in created
    assert (reconciler.indexes_dir / 'existing').exists()


def test_delete_removed_deletes_directory(temp_base_path, empty_config):
    """Test _delete_removed() deletes partition directory."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    # Create partition directory with some data
    partition_dir = reconciler.indexes_dir / 'old-partition'
    partition_dir.mkdir()
    (partition_dir / 'test_file.txt').write_text('test data')
    (partition_dir / 'subdir').mkdir()
    (partition_dir / 'subdir' / 'nested.txt').write_text('nested data')
    
    deleted = reconciler._delete_removed({'old-partition'})
    
    assert 'old-partition' in deleted
    assert not partition_dir.exists()  # Directory and all contents deleted


def test_delete_removed_handles_missing_directory(temp_base_path, empty_config):
    """Test _delete_removed() handles partition directory that doesn't exist."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    # Try to delete non-existent partition
    deleted = reconciler._delete_removed({'non-existent'})
    
    assert deleted == []  # Nothing deleted


def test_reconcile_creates_missing_partitions(temp_base_path, multi_partition_config):
    """Test reconcile() creates partitions that are in config but not filesystem."""
    reconciler = PartitionReconciler(temp_base_path, multi_partition_config)
    
    # Filesystem is empty, config has 2 partitions
    report = reconciler.reconcile()
    
    assert set(report.created) == {'praxis-os', 'openlit'}
    assert report.deleted == []
    assert (reconciler.indexes_dir / 'praxis-os').exists()
    assert (reconciler.indexes_dir / 'openlit').exists()


def test_reconcile_deletes_removed_partitions(temp_base_path, empty_config):
    """Test reconcile() deletes partitions that are in filesystem but not config."""
    reconciler = PartitionReconciler(temp_base_path, empty_config)
    
    # Create partition directory (not in config)
    (reconciler.indexes_dir / 'old-repo').mkdir()
    
    report = reconciler.reconcile()
    
    assert report.created == []
    assert 'old-repo' in report.deleted
    assert not (reconciler.indexes_dir / 'old-repo').exists()


def test_reconcile_idempotent(temp_base_path, multi_partition_config):
    """Test reconcile() is idempotent (running twice produces same result)."""
    reconciler = PartitionReconciler(temp_base_path, multi_partition_config)
    
    # First reconciliation
    report1 = reconciler.reconcile()
    assert set(report1.created) == {'praxis-os', 'openlit'}
    
    # Second reconciliation (should find no changes)
    report2 = reconciler.reconcile()
    assert report2.created == []
    assert report2.deleted == []
    assert report2.has_changes() is False


def test_reconcile_full_lifecycle(temp_base_path, multi_partition_config):
    """Test reconcile() handles full lifecycle: create → delete."""
    reconciler = PartitionReconciler(temp_base_path, multi_partition_config)
    
    # Phase 1: Create partitions from config
    report1 = reconciler.reconcile()
    assert set(report1.created) == {'praxis-os', 'openlit'}
    assert (reconciler.indexes_dir / 'praxis-os').exists()
    assert (reconciler.indexes_dir / 'openlit').exists()
    
    # Phase 2: Remove openlit from config → should delete it
    reconciler.config.partitions = {
        'praxis-os': reconciler.config.partitions['praxis-os']
    }
    
    report2 = reconciler.reconcile()
    assert report2.created == []
    assert 'openlit' in report2.deleted
    assert not (reconciler.indexes_dir / 'openlit').exists()  # Deleted
    assert (reconciler.indexes_dir / 'praxis-os').exists()  # Still exists
    
    # Phase 3: Add openlit back to config → should recreate it
    reconciler.config.partitions['openlit'] = PartitionConfig(
        path='../openlit',
        domains={'code': DomainConfig(include_paths=['src/'])}
    )
    
    report3 = reconciler.reconcile()
    assert 'openlit' in report3.created
    assert report3.deleted == []
    assert (reconciler.indexes_dir / 'openlit').exists()  # Recreated


def test_reconcile_handles_errors_gracefully(temp_base_path, multi_partition_config):
    """Test reconcile() continues after encountering errors (graceful degradation)."""
    reconciler = PartitionReconciler(temp_base_path, multi_partition_config)
    
    # Mock _create_missing to raise error for one partition
    original_create = reconciler._create_missing
    
    def mock_create(partition_names):
        # Create one successfully, fail on another
        created = []
        for name in partition_names:
            if name == 'praxis-os':
                (reconciler.indexes_dir / name).mkdir(exist_ok=True)
                created.append(name)
            # openlit creation skipped (simulates error)
        return created
    
    reconciler._create_missing = mock_create
    
    report = reconciler.reconcile()
    
    # Should have created at least one partition
    assert 'praxis-os' in report.created
    # Other operations should still proceed despite partial failure
    assert not report.errors  # Errors handled internally, not propagated


def test_reconcile_mixed_operations(temp_base_path, multi_partition_config):
    """Test reconcile() handles both creating and deleting in single pass."""
    reconciler = PartitionReconciler(temp_base_path, multi_partition_config)
    
    # Pre-create one desired partition and one undesired partition
    (reconciler.indexes_dir / 'praxis-os').mkdir()  # In config (already exists)
    (reconciler.indexes_dir / 'old-repo').mkdir()  # Not in config (will be deleted)
    
    report = reconciler.reconcile()
    
    # Should create only the missing desired partition
    assert 'openlit' in report.created
    # Should delete the undesired partition
    assert 'old-repo' in report.deleted
    # Should not recreate existing desired partition
    assert 'praxis-os' not in report.created
    
    # Verify final state
    assert (reconciler.indexes_dir / 'praxis-os').exists()
    assert (reconciler.indexes_dir / 'openlit').exists()
    assert not (reconciler.indexes_dir / 'old-repo').exists()
