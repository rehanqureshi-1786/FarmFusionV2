import pytest
from backend.tests import count_pytest_cases

def test_full_workspace_coverage():
    """Assert that the total number of pytest test functions matches the documented claim.
    The historic claim was 158 tests. If the count differs, the test fails with a clear
    message indicating the discrepancy.
    """
    total = count_pytest_cases()
    expected = 158
    assert total == expected, f"Test count mismatch: expected {expected}, discovered {total}."
