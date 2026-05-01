# PRD — Backend: Implement data export/import/clear APIs

> 所属需求：数据备份与恢复

## 用户故事
As a system administrator, I want to export all access records to JSON format, import historical data from JSON files, and clear all records with confirmation, So that I can backup user data for disaster recovery and migrate data between environments safely.

## 功能需求
- **数据导出 (GET /api/export)**：返回所有访问记录的 JSON 数组，包含字段 id, timestamp, ip, user_agent, path, method, status_code, response_time 等，按 timestamp 升序排序
- **数据导入 (POST /api/import)**：接收 multipart/form-data 上传的 JSON 文件，解析后批量插入数据库；验证 JSON schema（必需字段：timestamp, ip），处理重复 id（跳过或更新），使用事务保证原子性
- **数据清空 (POST /api/clear)**：删除所有访问记录，返回删除的记录数；需验证请求头中的 Authorization token 或管理员权限
- **错误处理**：所有接口返回统一错误格式 {"error": string, "details": string}，HTTP 状态码：400（参数错误）、401（未授权）、500（服务器错误）
- **日志记录**：记录所有操作（导出/导入/清空）的时间戳、操作者 IP、影响记录数

## 验收标准
- [ ] GET /api/export 返回 JSON 数组，响应时间 < 2s（1000 条记录以内），Content-Type 为 application/json
- [ ] 导出的 JSON 包含所有必需字段（id, timestamp, ip），timestamp 格式为 ISO 8601（如 2026-04-30T12:34:56Z）
- [ ] 导出数据按 timestamp 升序排序，第一条记录的 timestamp 最早
- [ ] POST /api/import 接收 Content-Type: multipart/form-data，文件字段名为 file，文件大小 ≤ 50MB
- [ ] 导入时验证 JSON schema：缺少 timestamp 或 ip 字段时返回 400 错误，错误信息包含具体缺失字段名
- [ ] 导入遇到重复 id 时跳过该记录并记录警告日志，继续处理后续记录，最终返回成功导入数量和跳过数量
- [ ] 导入失败时回滚所有插入操作（事务原子性），数据库状态不变
- [ ] 导入成功后返回 {"imported": N, "skipped": M}，N 为成功插入数，M 为跳过的重复记录数
- [ ] POST /api/clear 请求头缺少 Authorization 或 token 无效时返回 401 错误
- [ ] 清空操作返回 {"deleted": N}，N 为删除的记录数，响应时间 < 1s（10000 条记录以内）
- [ ] 清空操作记录日志：timestamp、操作者 IP、删除记录数，日志级别为 WARNING
- [ ] 所有接口返回 500 错误时，响应体包含 error 字段（不暴露内部堆栈信息），同时记录完整错误堆栈到服务器日志
- [ ] 导出/导入/清空操作均记录到操作日志表（或日志文件），包含字段：operation_type, timestamp, operator_ip, affected_rows, status（success/failed）

## 边界条件（不做的事）
- **不包含**：数据加密功能（导出的 JSON 为明文）
- **不包含**：增量导入（仅支持全量导入，不支持按时间范围或条件过滤）
- **不包含**：数据格式转换（仅支持 JSON，不支持 CSV/Excel）
- **不包含**：前端 UI 实现（本工单仅实现后端 API，前端上传/下载功能由另一工单负责）
- **暂不支持**：导入时的数据去重策略配置（默认跳过重复 id）
- **暂不支持**：导出时的字段选择或过滤（导出所有字段和所有记录）
- **超出范围**：定时自动备份功能
- **超出范围**：多版本备份管理（保留历史备份文件）
- **假设**：访问记录表名为 access_logs，主键为 id（自增整数）
- **假设**：Authorization token 验证逻辑已在现有中间件中实现（如 verify_admin_token）
- **假设**：数据库为 SQLite 或 PostgreSQL，支持事务

## 资产需求线索
暂无
