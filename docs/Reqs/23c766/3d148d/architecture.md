# 架构设计 - Frontend: Add data backup and restore UI

## 架构模式
Frontend UI Extension

## 技术栈

- **framework**: Vanilla JavaScript (consistent with existing Flask app)
- **http_client**: Fetch API
- **ui_components**: Native HTML5 (file input, buttons, modal dialog)
- **styling**: CSS (to be added or extended from existing styles)
- **state_management**: DOM manipulation with async/await

## 模块设计

### 
职责: Render data backup/restore control panel in frontend

## 关键决策
- {'decision': 'Use native File API instead of third-party upload library', 'rationale': 'Keep frontend lightweight, no external dependencies needed for simple file operations'}
- {'decision': 'Implement modal as custom component rather than using alert()', 'rationale': 'Better UX with styled modal, prevents accidental data loss, allows customization'}
- {'decision': 'Filename format: visits_backup_YYYYMMDD_HHMMSS.json', 'rationale': 'Sortable by date, avoids filename conflicts, clearly indicates content and timestamp'}
- {'decision': 'Refresh visit count after import/clear operations', 'rationale': 'Immediate visual feedback that operation succeeded, keeps UI state consistent'}
- {'decision': 'Use toast notifications instead of alert() for feedback', 'rationale': 'Non-blocking, better UX, can show multiple messages, auto-dismiss'}
- {'decision': "Set file input accept attribute to '.json,application/json'", 'rationale': 'Guides user to select correct file type, reduces invalid upload attempts'}
