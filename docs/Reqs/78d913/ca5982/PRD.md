# PRD — Implement transaction CRUD API endpoints

> 所属需求：收支记录管理（核心功能）

## 用户故事
As a 记账应用用户，I want to 通过 API 创建、查询、修改和删除我的收支记录，So that 前端可以实现完整的记账功能，并确保数据安全（只能操作自己的记录）。

## 功能需求
- POST /api/transactions：创建收支记录，接收参数 type(income/expense)、amount、category_id、date、note、payment_method，返回创建的记录（含 id、created_at）
- GET /api/transactions：查询当前用户的记录列表，支持分页参数 page/page_size（默认 1/20），支持筛选参数 type、category_id、start_date、end_date、payment_method，返回 {items: [], total: N, page: N, page_size: N}
- PUT /api/transactions/:id：更新指定记录，仅允许修改 amount、category_id、date、note、payment_method，返回更新后的完整记录
- DELETE /api/transactions/:id：删除指定记录，返回 {success: true, deleted_id: N}
- 权限校验：所有接口必须验证 user_id，确保用户只能操作自己的记录，越权访问返回 403
- 参数验证：amount 必须 > 0，type 必须为 income/expense 枚举值，date 格式 YYYY-MM-DD，category_id 必须存在于 categories 表且属于当前用户
- 错误处理：参数错误返回 400 + 具体字段错误信息，记录不存在返回 404，数据库错误返回 500 + 通用错误提示（不暴露内部细节）

## 验收标准
- [ ] POST /api/transactions 创建成功后返回 201 状态码，响应体包含 id、user_id、type、amount、category_id、date、note、payment_method、created_at、updated_at 共 10 个字段
- [ ] POST 时 amount ≤ 0 返回 400 + {"error": "amount must be greater than 0"}，type 非 income/expense 返回 400 + {"error": "type must be income or expense"}
- [ ] POST 时 category_id 不存在或不属于当前用户返回 400 + {"error": "invalid category_id"}
- [ ] GET /api/transactions 不传分页参数时默认返回第 1 页、每页 20 条，响应体包含 items 数组、total（总记录数）、page、page_size 四个字段
- [ ] GET 时传入 start_date=2025-01-01&end_date=2025-01-31 仅返回该日期范围内的记录（date 字段在 [start_date, end_date] 闭区间）
- [ ] GET 时传入 type=income 仅返回收入记录，type=expense 仅返回支出记录，不传则返回全部
- [ ] GET 时传入 category_id=5 仅返回该分类下的记录，支持同时筛选多个条件（如 type + category_id + 日期范围）
- [ ] GET 时传入 page=999（超出实际页数）返回空数组 items: []，total 仍为实际总数
- [ ] PUT /api/transactions/:id 更新成功返回 200 + 完整记录（含 updated_at 字段更新为当前时间）
- [ ] PUT 时尝试修改不存在的记录返回 404 + {"error": "transaction not found"}
- [ ] PUT 时尝试修改其他用户的记录返回 403 + {"error": "permission denied"}
- [ ] PUT 时不允许修改 id、user_id、type、created_at 字段，传入这些字段应被忽略（不报错但不生效）
- [ ] DELETE /api/transactions/:id 删除成功返回 200 + {"success": true, "deleted_id": N}
- [ ] DELETE 时记录不存在返回 404，尝试删除其他用户记录返回 403
- [ ] 所有接口未传 Authorization header 或 token 无效时返回 401 + {"error": "unauthorized"}
- [ ] 所有接口响应时间 P95 ≤ 200ms（单表查询场景，数据量 < 10000 条）
- [ ] 数据库错误（如连接失败）时返回 500 + {"error": "internal server error"}，不暴露 SQL 语句或堆栈信息
- [ ] 所有日期参数格式错误（非 YYYY-MM-DD）返回 400 + {"error": "invalid date format, expected YYYY-MM-DD"}
- [ ] GET 接口返回的记录按 date 降序排列（最新记录在前），date 相同时按 created_at 降序

## 边界条件（不做的事）
- 不包含：批量创建/删除接口（单条操作即可满足需求）
- 不包含：记录的软删除（deleted_at 字段），DELETE 直接物理删除
- 不包含：记录的审计日志（操作历史记录），仅保留 created_at 和 updated_at
- 不包含：导出功能（CSV/Excel），由前端或独立工单实现
- 不包含：统计接口（按分类汇总金额、月度趋势等），由独立的统计 API 工单实现
- 暂不支持：附件上传（发票照片等），后续扩展
- 暂不支持：定时重复记账（如每月固定支出），后续扩展
- 超出范围：分类管理接口（categories CRUD 由独立工单实现）
- 超出范围：支付方式管理（payment_method 当前为字符串字段，枚举值由前端定义）

## 资产需求线索
暂无（纯后端 API 接口，无 UI 资产需求）
