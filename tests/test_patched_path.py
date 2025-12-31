"""Test the _patched_path function to ensure it only adds paths with kernels directories"""
import os
from pathlib import Path
from unittest import mock

import pytest

from a2km.operations import _patched_path
from jupyter_core import paths


def test_patched_path_only_includes_dirs_with_kernels(tmp_path):
    """Test that _patched_path only includes directories that have a kernels subdirectory"""
    # Create a mock PATH with various directories
    bin_with_kernels = tmp_path / "prefix1" / "bin"
    bin_with_kernels.mkdir(parents=True)
    
    # Create share/jupyter/kernels for this prefix
    kernels_dir1 = tmp_path / "prefix1" / "share" / "jupyter" / "kernels"
    kernels_dir1.mkdir(parents=True)
    
    # Create another prefix with share/jupyter but NO kernels subdirectory
    bin_without_kernels = tmp_path / "prefix2" / "bin"
    bin_without_kernels.mkdir(parents=True)
    
    # Create share/jupyter but NOT the kernels subdirectory
    jupyter_dir_no_kernels = tmp_path / "prefix2" / "share" / "jupyter"
    jupyter_dir_no_kernels.mkdir(parents=True)
    
    # Create a third prefix with no share/jupyter at all
    bin_no_jupyter = tmp_path / "prefix3" / "bin"
    bin_no_jupyter.mkdir(parents=True)
    
    # Build the mock PATH
    mock_path = os.pathsep.join([
        str(bin_with_kernels),
        str(bin_without_kernels),
        str(bin_no_jupyter),
    ])
    
    # Mock the environment and jupyter paths
    with (
        mock.patch.dict(os.environ, {"PATH": mock_path}),
        mock.patch("jupyter_core.paths.SYSTEM_JUPYTER_PATH", []),
        mock.patch("jupyter_core.paths.jupyter_path", return_value=[]),
        _patched_path() as _,
    ):
        # After patching, SYSTEM_JUPYTER_PATH should only contain the path with kernels
        patched_paths = paths.SYSTEM_JUPYTER_PATH
        
        # Convert to strings for comparison
        patched_paths_str = [str(p) for p in patched_paths]
        
        # Should include prefix1/share/jupyter (which has kernels subdirectory)
        expected_path = str(tmp_path / "prefix1" / "share" / "jupyter")
        assert expected_path in patched_paths_str, f"Expected {expected_path} in {patched_paths_str}"
        
        # Should NOT include prefix2/share/jupyter (which has no kernels subdirectory)
        unexpected_path = str(tmp_path / "prefix2" / "share" / "jupyter")
        assert unexpected_path not in patched_paths_str, f"Did not expect {unexpected_path} in {patched_paths_str}"
