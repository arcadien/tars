"""TECH-BUILD acceptance criteria (requirements/technical.md)."""
import os
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.req('TECH-BUILD-ARTIFACTS-001')
def test_tech_build_artifacts_001_print_files_are_not_versioned():
    # Given the repository
    tracked = subprocess.run(['git', 'ls-files', 'mechanical/stl', 'mechanical/3mf/tars4_plate*'], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.split()
    # Then no STL and no raw plate is tracked
    assert tracked == []
    # And both paths are ignored
    ignore = open(os.path.join(ROOT, '.gitignore'), encoding='utf-8').read().splitlines()
    assert 'mechanical/stl/' in ignore and 'mechanical/3mf/tars4_plate*.3mf' in ignore
