# 开发笔记 — E2E: Test data backup and restore workflow

> 2026-05-02 01:43 | LLM

## 产出文件
- [tests/e2e/test_backup_restore.py](/app#repo?file=tests/e2e/test_backup_restore.py) (7920 chars)
- [tests/e2e/conftest.py](/app#repo?file=tests/e2e/conftest.py) (4563 chars)
- [tests/e2e/__init__.py](/app#repo?file=tests/e2e/__init__.py) (11434 chars)
- [pytest.ini](/app#repo?file=pytest.ini) (436 chars)
- [requirements-test.txt](/app#repo?file=requirements-test.txt) (102 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 5 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 5 个文件已落盘 |

## 代码变更 (Diff)

### tests/e2e/test_backup_restore.py (新建, 7920 chars)
```
+ import json
+ import os
+ import tempfile
+ from pathlib import Path
+ from playwright.sync_api import Page, expect
+ 
+ 
+ def test_backup_restore_workflow(page: Page):
+     """测试完整的备份恢复流程"""
+     
+     # 1. 访问页面多次，生成测试数据
+     page.goto("http://localhost:8000")
+     page.wait_for_load_state("networkidle")
+     
+     # 访问 5 次以生成测试数据
+     visit_count = 5
+     for i in range(visit_count):
+         page.reload()
+         page.wait_for_load_state("networkidle")
+     
+ ... (更多)
```

### tests/e2e/conftest.py (新建, 4563 chars)
```
+ import json
+ import pytest
+ from pathlib import Path
+ from playwright.sync_api import Page, expect, Browser
+ from typing import Generator
+ 
+ 
+ @pytest.fixture(scope="session")
+ def browser_context_args(browser_context_args):
+     """配置浏览器上下文参数"""
+     return {
+         **browser_context_args,
+         "viewport": {"width": 1280, "height": 720},
+         "locale": "zh-CN",
+         "timezone_id": "Asia/Shanghai",
+     }
+ 
+ 
+ @pytest.fixture(scope="function")
+ def page(browser: Browser) -> Generator[Page, None, None]:
+ ... (更多)
```

### tests/e2e/__init__.py (新建, 11434 chars)
```
+ """
+ E2E tests package for the visitor counter application.
+ 
+ This package contains end-to-end tests using Playwright to verify
+ the complete backup and restore workflow.
+ """
+ 
+ import json
+ import os
+ from pathlib import Path
+ from typing import Generator
+ 
+ import pytest
+ from playwright.sync_api import Page, expect, Download
+ 
+ 
+ # Test data directory
+ TEST_DATA_DIR = Path(__file__).parent / "test_data"
+ SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
+ 
+ ... (更多)
```

### pytest.ini (新建, 436 chars)
```
+ [pytest]
+ testpaths = tests
+ python_files = test_*.py
+ python_classes = Test*
+ python_functions = test_*
+ addopts = 
+     -v
+     --strict-markers
+     --tb=short
+     --capture=no
+ markers =
+     e2e: End-to-end tests
+     backup: Backup and restore workflow tests
+     slow: Slow running tests
+ asyncio_mode = auto
+ log_cli = true
+ log_cli_level = INFO
+ log_cli_format = %(asctime)s [%(levelname)8s] %(message)s
+ log_cli_date_format = %Y-%m-%d %H:%M:%S
```
