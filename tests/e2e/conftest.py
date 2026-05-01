import json
import pytest
from pathlib import Path
from playwright.sync_api import Page, expect, Browser
from typing import Generator


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """配置浏览器上下文参数"""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
    }


@pytest.fixture(scope="function")
def page(browser: Browser) -> Generator[Page, None, None]:
    """为每个测试创建新的页面实例"""
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def screenshots_dir() -> Path:
    """创建截图目录"""
    screenshots_path = Path("tests/e2e/screenshots")
    screenshots_path.mkdir(parents=True, exist_ok=True)
    return screenshots_path


@pytest.fixture
def test_data_dir() -> Path:
    """创建测试数据目录"""
    data_path = Path("tests/e2e/test_data")
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path


@pytest.fixture
def base_url() -> str:
    """返回应用的基础URL"""
    return "http://localhost:8000"


@pytest.fixture
def sample_valid_data() -> dict:
    """返回有效的测试数据"""
    return {
        "visits": [
            {
                "timestamp": "2024-01-01T10:00:00.000Z",
                "userAgent": "Mozilla/5.0 Test Browser",
                "ip": "192.168.1.1"
            },
            {
                "timestamp": "2024-01-01T11:00:00.000Z",
                "userAgent": "Mozilla/5.0 Another Browser",
                "ip": "192.168.1.2"
            }
        ]
    }


@pytest.fixture
def sample_invalid_data() -> list:
    """返回各种无效的测试数据"""
    return [
        # 空对象
        {},
        # 缺少visits字段
        {"data": []},
        # visits不是数组
        {"visits": "not an array"},
        # visits包含无效记录
        {"visits": [{"invalid": "data"}]},
        # 无效的JSON字符串
        "not json",
        # 空数组
        {"visits": []},
    ]


@pytest.fixture
def create_temp_json_file(test_data_dir: Path):
    """创建临时JSON文件的辅助函数"""
    def _create_file(data: dict | str, filename: str = "temp_data.json") -> Path:
        file_path = test_data_dir / filename
        if isinstance(data, str):
            file_path.write_text(data, encoding="utf-8")
        else:
            file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return file_path
    return _create_file


def wait_for_page_load(page: Page, base_url: str):
    """等待页面完全加载"""
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    expect(page.locator("#visit-count")).to_be_visible()


def get_visit_count(page: Page) -> int:
    """获取当前访问计数"""
    count_text = page.locator("#visit-count").inner_text()
    return int(count_text)


def click_and_confirm_clear(page: Page):
    """点击清空按钮并确认对话框"""
    page.locator("#clear-btn").click()
    page.on("dialog", lambda dialog: dialog.accept())
    page.wait_for_timeout(500)


def download_and_verify_json(page: Page, screenshots_dir: Path, step_name: str) -> dict:
    """下载JSON文件并验证格式"""
    with page.expect_download() as download_info:
        page.locator("#export-btn").click()
    
    download = download_info.value
    download_path = screenshots_dir / f"{step_name}_{download.suggested_filename}"
    download.save_as(download_path)
    
    # 验证文件存在且可读
    assert download_path.exists(), "下载的文件不存在"
    
    # 验证JSON格式
    with open(download_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert "visits" in data, "JSON数据缺少visits字段"
    assert isinstance(data["visits"], list), "visits字段不是数组"
    
    return data


def upload_json_file(page: Page, file_path: Path):
    """上传JSON文件"""
    page.locator("#import-input").set_input_files(file_path)
    page.wait_for_timeout(1000)


def take_screenshot(page: Page, screenshots_dir: Path, name: str):
    """截图并保存"""
    screenshot_path = screenshots_dir / f"{name}.png"
    page.screenshot(path=str(screenshot_path), full_page=True)


def verify_visit_records(page: Page, expected_count: int):
    """验证访问记录数量"""
    actual_count = get_visit_count(page)
    assert actual_count == expected_count, f"期望计数 {expected_count}，实际计数 {actual_count}"


def verify_table_rows(page: Page, expected_rows: int):
    """验证表格行数"""
    rows = page.locator("#visit-table tbody tr")
    actual_rows = rows.count()
    assert actual_rows == expected_rows, f"期望 {expected_rows} 行，实际 {actual_rows} 行"
