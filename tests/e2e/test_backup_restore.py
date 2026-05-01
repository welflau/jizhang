import json
import os
import tempfile
from pathlib import Path
from playwright.sync_api import Page, expect


def test_backup_restore_workflow(page: Page):
    """测试完整的备份恢复流程"""
    
    # 1. 访问页面多次，生成测试数据
    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")
    
    # 访问 5 次以生成测试数据
    visit_count = 5
    for i in range(visit_count):
        page.reload()
        page.wait_for_load_state("networkidle")
    
    # 验证访问计数
    count_element = page.locator("#visit-count")
    expect(count_element).to_have_text(str(visit_count))
    
    # 截图：初始数据状态
    page.screenshot(path="tests/screenshots/backup_restore_01_initial_data.png")
    
    # 2. 点击导出按钮，验证下载的 JSON 文件
    with page.expect_download() as download_info:
        page.click("#export-btn")
    
    download = download_info.value
    
    # 保存下载的文件到临时目录
    temp_dir = tempfile.mkdtemp()
    export_file_path = os.path.join(temp_dir, "exported_data.json")
    download.save_as(export_file_path)
    
    # 验证文件存在
    assert os.path.exists(export_file_path), "导出文件不存在"
    
    # 验证 JSON 格式正确
    with open(export_file_path, 'r', encoding='utf-8') as f:
        exported_data = json.load(f)
    
    assert "visits" in exported_data, "导出数据缺少 visits 字段"
    assert isinstance(exported_data["visits"], list), "visits 应该是列表"
    assert len(exported_data["visits"]) == visit_count, f"导出的记录数不正确，期望 {visit_count}，实际 {len(exported_data['visits'])}"
    
    # 验证每条记录包含必要字段
    for visit in exported_data["visits"]:
        assert "timestamp" in visit, "记录缺少 timestamp 字段"
        assert "ip" in visit, "记录缺少 ip 字段"
        assert "user_agent" in visit, "记录缺少 user_agent 字段"
    
    # 截图：导出成功
    page.screenshot(path="tests/screenshots/backup_restore_02_exported.png")
    
    # 3. 点击清空按钮，确认对话框，验证数据被清空
    page.on("dialog", lambda dialog: dialog.accept())
    page.click("#clear-btn")
    
    # 等待页面更新
    page.wait_for_timeout(500)
    
    # 验证计数归零
    expect(count_element).to_have_text("0")
    
    # 验证表格为空
    table_body = page.locator("#visit-table tbody")
    expect(table_body.locator("tr")).to_have_count(0)
    
    # 截图：清空后状态
    page.screenshot(path="tests/screenshots/backup_restore_03_cleared.png")
    
    # 4. 上传之前导出的 JSON 文件，验证数据恢复
    file_input = page.locator("#import-file")
    file_input.set_input_files(export_file_path)
    
    # 等待导入完成
    page.wait_for_timeout(1000)
    
    # 验证计数恢复
    expect(count_element).to_have_text(str(visit_count))
    
    # 验证表格数据恢复
    table_rows = table_body.locator("tr")
    expect(table_rows).to_have_count(visit_count)
    
    # 截图：恢复后状态
    page.screenshot(path="tests/screenshots/backup_restore_04_restored.png")
    
    # 清理临时文件
    os.remove(export_file_path)
    os.rmdir(temp_dir)


def test_import_invalid_json(page: Page):
    """测试上传非法 JSON 文件"""
    
    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")
    
    # 创建一个非法的 JSON 文件
    temp_dir = tempfile.mkdtemp()
    invalid_file_path = os.path.join(temp_dir, "invalid.json")
    
    with open(invalid_file_path, 'w', encoding='utf-8') as f:
        f.write("{ invalid json content")
    
    # 监听 alert 对话框
    dialog_message = []
    page.on("dialog", lambda dialog: (
        dialog_message.append(dialog.message),
        dialog.accept()
    ))
    
    # 上传非法文件
    file_input = page.locator("#import-file")
    file_input.set_input_files(invalid_file_path)
    
    # 等待错误提示
    page.wait_for_timeout(500)
    
    # 验证显示了错误提示
    assert len(dialog_message) > 0, "应该显示错误提示"
    assert "错误" in dialog_message[0] or "失败" in dialog_message[0] or "invalid" in dialog_message[0].lower(), "错误提示内容不正确"
    
    # 截图：错误状态
    page.screenshot(path="tests/screenshots/backup_restore_05_invalid_json.png")
    
    # 清理临时文件
    os.remove(invalid_file_path)
    os.rmdir(temp_dir)


def test_import_invalid_format(page: Page):
    """测试上传格式不正确的 JSON 文件"""
    
    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")
    
    # 创建一个格式不正确的 JSON 文件（缺少 visits 字段）
    temp_dir = tempfile.mkdtemp()
    invalid_format_path = os.path.join(temp_dir, "invalid_format.json")
    
    with open(invalid_format_path, 'w', encoding='utf-8') as f:
        json.dump({"data": []}, f)
    
    # 监听 alert 对话框
    dialog_message = []
    page.on("dialog", lambda dialog: (
        dialog_message.append(dialog.message),
        dialog.accept()
    ))
    
    # 上传格式不正确的文件
    file_input = page.locator("#import-file")
    file_input.set_input_files(invalid_format_path)
    
    # 等待错误提示
    page.wait_for_timeout(500)
    
    # 验证显示了错误提示
    assert len(dialog_message) > 0, "应该显示错误提示"
    
    # 截图：格式错误状态
    page.screenshot(path="tests/screenshots/backup_restore_06_invalid_format.png")
    
    # 清理临时文件
    os.remove(invalid_format_path)
    os.rmdir(temp_dir)


def test_import_empty_data(page: Page):
    """测试导入空数据"""
    
    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")
    
    # 先生成一些数据
    for i in range(3):
        page.reload()
        page.wait_for_load_state("networkidle")
    
    count_element = page.locator("#visit-count")
    expect(count_element).to_have_text("3")
    
    # 创建一个空数据的 JSON 文件
    temp_dir = tempfile.mkdtemp()
    empty_data_path = os.path.join(temp_dir, "empty_data.json")
    
    with open(empty_data_path, 'w', encoding='utf-8') as f:
        json.dump({"visits": []}, f)
    
    # 上传空数据文件
    file_input = page.locator("#import-file")
    file_input.set_input_files(empty_data_path)
    
    # 等待导入完成
    page.wait_for_timeout(1000)
    
    # 验证数据被清空
    expect(count_element).to_have_text("0")
    
    # 验证表格为空
    table_body = page.locator("#visit-table tbody")
    expect(table_body.locator("tr")).to_have_count(0)
    
    # 截图：导入空数据后状态
    page.screenshot(path="tests/screenshots/backup_restore_07_empty_import.png")
    
    # 清理临时文件
    os.remove(empty_data_path)
    os.rmdir(temp_dir)


def test_export_with_no_data(page: Page):
    """测试在没有数据时导出"""
    
    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")
    
    # 清空所有数据
    page.on("dialog", lambda dialog: dialog.accept())
    page.click("#clear-btn")
    page.wait_for_timeout(500)
    
    # 验证计数为 0
    count_element = page.locator("#visit-count")
    expect(count_element).to_have_text("0")
    
    # 导出空数据
    with page.expect_download() as download_info:
        page.click("#export-btn")
    
    download = download_info.value
    
    # 保存下载的文件
    temp_dir = tempfile.mkdtemp()
    export_file_path = os.path.join(temp_dir, "empty_export.json")
    download.save_as(export_file_path)
    
    # 验证文件内容
    with open(export_file_path, 'r', encoding='utf-8') as f:
        exported_data = json.load(f)
    
    assert "visits" in exported_data, "导出数据缺少 visits 字段"
    assert len(exported_data["visits"]) == 0, "空数据导出应该包含空列表"
    
    # 截图：空数据导出
    page.screenshot(path="tests/screenshots/backup_restore_08_empty_export.png")
    
    # 清理临时文件
    os.remove(export_file_path)
    os.rmdir(temp_dir)


def test_clear_with_cancel(page: Page):
    """测试取消清空操作"""
    
    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")
    
    # 生成一些数据
    visit_count = 3
    for i in range(visit_count):
        page.reload()
        page.wait_for_load_state("networkidle")
    
    count_element = page.locator("#visit-count")
    expect(count_element).to_have_text(str(visit_count))
    
    # 点击清空按钮但取消操作
    page.on("dialog", lambda dialog: dialog.dismiss())
    page.click("#clear-btn")
    
    # 等待对话框处理
    page.wait_for_timeout(500)
    
    # 验证数据未被清空
    expect(count_element).to_have_text(str(visit_count))
    
    # 验证表格数据仍然存在
    table_body = page.locator("#visit-table tbody")
    expect(table_body.locator("tr")).to_have_count(visit_count)
    
    # 截图：取消清空后状态
    page.screenshot(path="tests/screenshots/backup_restore_09_cancel_clear.png")
