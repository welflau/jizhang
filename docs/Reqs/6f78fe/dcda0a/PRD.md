# PRD — 用户信息更新 API 开发

> 所属需求：用户个人中心

## 用户故事
As a registered user, I want to update my personal information (nickname, avatar, password) and preference settings, So that I can maintain accurate profile data and customize my experience.

## 功能需求
- **Update Nickname**: User can modify their display name
- **Update Avatar**: User can upload or select a new profile picture
- **Change Password**: User can update their login password with old password verification
- **Preference Settings**: User can configure default currency symbol and homepage display options
- **Data Persistence**: All changes must be saved to database and reflected immediately
- **Validation**: Input validation for nickname length, password strength, avatar file size/format
- **Security**: Password change requires old password verification; sensitive operations require re-authentication

## 验收标准
- [ ] POST `/api/user/profile` accepts `nickname` field (2-20 characters), returns updated user object within 500ms
- [ ] POST `/api/user/avatar` accepts multipart/form-data with image file (≤5MB, JPG/PNG/GIF), returns avatar URL within 2s
- [ ] POST `/api/user/password` requires `old_password` + `new_password` (≥8 characters, must contain letter+number), returns 200 on success or 400 with specific error message
- [ ] POST `/api/user/preferences` accepts JSON `{"default_currency": "USD|CNY|EUR", "homepage_display": "dashboard|charts|recent"}`, persists to database within 300ms
- [ ] All endpoints return 401 if user not authenticated, 422 if validation fails with field-level error details
- [ ] Password change triggers session invalidation for other devices (optional security enhancement)
- [ ] Avatar upload validates MIME type server-side, rejects non-image files with 400 error
- [ ] Nickname uniqueness check completes within 200ms, returns 409 if already taken
- [ ] API rate limit: max 10 requests per minute per user for profile updates
- [ ] All successful updates return complete user object including `updated_at` timestamp

## 边界条件（不做的事）
- **Not Included**: Email/phone number modification (requires separate verification flow)
- **Not Included**: Two-factor authentication (2FA) setup
- **Not Included**: Account deletion or deactivation
- **Not Included**: Social media account linking
- **Not Included**: Profile visibility settings (public/private)
- **Not Supported**: Batch updates (must update fields individually or in single request)
- **Out of Scope**: Avatar cropping/editing UI (frontend handles cropping before upload)
- **Out of Scope**: Password recovery/reset flow (separate feature)
- **Temporary Limitation**: Avatar stored locally, not CDN (CDN integration in future iteration)

## 资产需求线索
暂无（纯后端 API 开发，无 UI 资产需求）
