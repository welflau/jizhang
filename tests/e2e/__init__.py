"""
E2E tests package for the visitor counter application.

This package contains end-to-end tests using Playwright to verify
the complete backup and restore workflow.
"""

import json
import os
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Page, expect, Download


# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"


@pytest.fixture(scope="session", autouse=True)
def setup_test_directories():
    """Create necessary test directories."""
    TEST_DATA_DIR.mkdir(exist_ok=True)
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    yield
    # Cleanup can be added here if needed


@pytest.fixture
def page_url(base_url: str) -> str:
    """Get the base URL for testing."""
    return base_url or "http://localhost:8080"


def wait_for_counter_update(page: Page, expected_count: int, timeout: int = 5000):
    """Wait for counter to update to expected value."""
    page.wait_for_function(
        f"document.querySelector('.counter').textContent.includes('{expected_count}')",
        timeout=timeout
    )


def get_counter_value(page: Page) -> int:
    """Extract current counter value from the page."""
    counter_text = page.locator(".counter").inner_text()
    # Extract number from text like "访问次数: 5"
    return int(''.join(filter(str.isdigit, counter_text)))


def verify_json_structure(data: dict) -> bool:
    """Verify the structure of exported JSON data."""
    if not isinstance(data, dict):
        return False
    
    if "visits" not in data or "metadata" not in data:
        return False
    
    visits = data["visits"]
    if not isinstance(visits, list):
        return False
    
    # Check each visit record
    for visit in visits:
        if not isinstance(visit, dict):
            return False
        required_fields = ["id", "timestamp", "ip", "user_agent"]
        if not all(field in visit for field in required_fields):
            return False
    
    # Check metadata
    metadata = data["metadata"]
    if not isinstance(metadata, dict):
        return False
    required_meta = ["total_count", "export_time", "version"]
    if not all(field in metadata for field in required_meta):
        return False
    
    return True


class TestBackupRestoreWorkflow:
    """E2E tests for backup and restore workflow."""
    
    def test_complete_backup_restore_flow(self, page: Page, page_url: str):
        """
        Test the complete backup and restore workflow:
        1. Generate test data by visiting page multiple times
        2. Export data and verify JSON format
        3. Clear data and verify
        4. Import data and verify restoration
        """
        # Step 1: Generate test data
        print("\n=== Step 1: Generating test data ===")
        page.goto(page_url)
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_initial_load.png"))
        
        initial_count = get_counter_value(page)
        print(f"Initial count: {initial_count}")
        
        # Visit page multiple times to generate data
        visits_to_generate = 5
        for i in range(visits_to_generate):
            page.reload()
            expected_count = initial_count + i + 1
            wait_for_counter_update(page, expected_count)
            current_count = get_counter_value(page)
            print(f"Visit {i + 1}: Counter = {current_count}")
            assert current_count == expected_count, f"Expected {expected_count}, got {current_count}"
        
        final_count = get_counter_value(page)
        page.screenshot(path=str(SCREENSHOTS_DIR / "02_after_visits.png"))
        print(f"Final count after visits: {final_count}")
        
        # Step 2: Export data
        print("\n=== Step 2: Exporting data ===")
        export_button = page.locator("button:has-text('导出数据')")
        expect(export_button).to_be_visible()
        
        with page.expect_download() as download_info:
            export_button.click()
        
        download: Download = download_info.value
        export_path = TEST_DATA_DIR / "exported_data.json"
        download.save_as(export_path)
        print(f"Data exported to: {export_path}")
        
        # Verify exported JSON
        assert export_path.exists(), "Export file not created"
        
        with open(export_path, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        
        print(f"Exported data structure: {list(exported_data.keys())}")
        assert verify_json_structure(exported_data), "Invalid JSON structure"
        assert exported_data["metadata"]["total_count"] == final_count, \
            f"Count mismatch: expected {final_count}, got {exported_data['metadata']['total_count']}"
        assert len(exported_data["visits"]) == final_count, \
            f"Records mismatch: expected {final_count}, got {len(exported_data['visits'])}"
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "03_after_export.png"))
        print(f"Verified: {final_count} records exported successfully")
        
        # Step 3: Clear data
        print("\n=== Step 3: Clearing data ===")
        clear_button = page.locator("button:has-text('清空数据')")
        expect(clear_button).to_be_visible()
        
        # Handle confirmation dialog
        page.on("dialog", lambda dialog: dialog.accept())
        clear_button.click()
        
        # Wait for page to update
        page.wait_for_timeout(1000)
        page.reload()
        
        cleared_count = get_counter_value(page)
        page.screenshot(path=str(SCREENSHOTS_DIR / "04_after_clear.png"))
        print(f"Count after clear: {cleared_count}")
        assert cleared_count == 1, f"Expected count 1 after clear, got {cleared_count}"
        
        # Step 4: Import data
        print("\n=== Step 4: Importing data ===")
        import_input = page.locator("input[type='file']")
        expect(import_input).to_be_attached()
        
        import_input.set_input_files(str(export_path))
        
        # Wait for import to complete
        page.wait_for_timeout(2000)
        page.reload()
        
        restored_count = get_counter_value(page)
        page.screenshot(path=str(SCREENSHOTS_DIR / "05_after_import.png"))
        print(f"Count after import: {restored_count}")
        
        # Verify restoration (should be original count + 1 from reload)
        assert restored_count == final_count + 1, \
            f"Expected count {final_count + 1} after restore, got {restored_count}"
        
        print("\n=== Test completed successfully ===")
    
    def test_export_with_no_data(self, page: Page, page_url: str):
        """Test exporting when there's minimal data."""
        page.goto(page_url)
        
        export_button = page.locator("button:has-text('导出数据')")
        expect(export_button).to_be_visible()
        
        with page.expect_download() as download_info:
            export_button.click()
        
        download: Download = download_info.value
        export_path = TEST_DATA_DIR / "minimal_export.json"
        download.save_as(export_path)
        
        with open(export_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert verify_json_structure(data), "Invalid JSON structure for minimal data"
        assert data["metadata"]["total_count"] >= 1, "Should have at least one visit"
    
    def test_import_invalid_json(self, page: Page, page_url: str):
        """Test importing invalid JSON file."""
        page.goto(page_url)
        
        # Create invalid JSON file
        invalid_json_path = TEST_DATA_DIR / "invalid.json"
        with open(invalid_json_path, 'w') as f:
            f.write("{ invalid json content }")
        
        import_input = page.locator("input[type='file']")
        
        # Listen for console errors or alerts
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("dialog", lambda dialog: dialog.accept())
        
        import_input.set_input_files(str(invalid_json_path))
        page.wait_for_timeout(1000)
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "06_invalid_json_import.png"))
        
        # Verify error handling (implementation dependent)
        # The page should either show an error or reject the import
        print(f"Console errors: {errors}")
    
    def test_import_wrong_format(self, page: Page, page_url: str):
        """Test importing JSON with wrong structure."""
        page.goto(page_url)
        
        # Create JSON with wrong structure
        wrong_format_path = TEST_DATA_DIR / "wrong_format.json"
        with open(wrong_format_path, 'w') as f:
            json.dump({"wrong": "format", "data": []}, f)
        
        import_input = page.locator("input[type='file']")
        page.on("dialog", lambda dialog: dialog.accept())
        
        import_input.set_input_files(str(wrong_format_path))
        page.wait_for_timeout(1000)
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "07_wrong_format_import.png"))
        
        # Verify the import was rejected or handled gracefully
    
    def test_clear_data_cancel(self, page: Page, page_url: str):
        """Test canceling the clear data operation."""
        page.goto(page_url)
        
        initial_count = get_counter_value(page)
        
        clear_button = page.locator("button:has-text('清空数据')")
        
        # Cancel the dialog
        page.on("dialog", lambda dialog: dialog.dismiss())
        clear_button.click()
        
        page.wait_for_timeout(500)
        
        # Verify count hasn't changed
        current_count = get_counter_value(page)
        assert current_count == initial_count, "Count should not change when dialog is canceled"
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "08_clear_canceled.png"))
    
    def test_multiple_exports(self, page: Page, page_url: str):
        """Test exporting data multiple times."""
        page.goto(page_url)
        
        export_button = page.locator("button:has-text('导出数据')")
        
        # First export
        with page.expect_download() as download1:
            export_button.click()
        
        download1.value.save_as(TEST_DATA_DIR / "export1.json")
        
        # Generate more data
        page.reload()
        page.wait_for_timeout(500)
        
        # Second export
        with page.expect_download() as download2:
            export_button.click()
        
        download2.value.save_as(TEST_DATA_DIR / "export2.json")
        
        # Verify both exports are valid
        with open(TEST_DATA_DIR / "export1.json", 'r') as f:
            data1 = json.load(f)
        
        with open(TEST_DATA_DIR / "export2.json", 'r') as f:
            data2 = json.load(f)
        
        assert verify_json_structure(data1), "First export invalid"
        assert verify_json_structure(data2), "Second export invalid"
        assert data2["metadata"]["total_count"] > data1["metadata"]["total_count"], \
            "Second export should have more records"
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "09_multiple_exports.png"))


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
