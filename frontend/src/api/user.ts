import request from '@/utils/request';

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  avatar?: string;
  nickname?: string;
  phone?: string;
  gender?: number;
  birthday?: string;
  bio?: string;
  createdAt: string;
  updatedAt: string;
}

export interface UpdateUserInfoParams {
  nickname?: string;
  email?: string;
  phone?: string;
  gender?: number;
  birthday?: string;
  bio?: string;
  avatar?: string;
}

export interface ChangePasswordParams {
  oldPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface UserPreferences {
  theme?: 'light' | 'dark' | 'auto';
  language?: string;
  emailNotification?: boolean;
  smsNotification?: boolean;
  timezone?: string;
}

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 获取用户信息
export function getUserInfo() {
  return request<ApiResponse<UserInfo>>({
    url: '/api/user/info',
    method: 'get',
  });
}

// 更新用户信息
export function updateUserInfo(data: UpdateUserInfoParams) {
  return request<ApiResponse<UserInfo>>({
    url: '/api/user/info',
    method: 'put',
    data,
  });
}

// 修改密码
export function changePassword(data: ChangePasswordParams) {
  return request<ApiResponse<null>>({
    url: '/api/user/password',
    method: 'put',
    data,
  });
}

// 上传头像
export function uploadAvatar(file: File) {
  const formData = new FormData();
  formData.append('avatar', file);
  return request<ApiResponse<{ url: string }>>({
    url: '/api/user/avatar',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}

// 获取用户偏好设置
export function getUserPreferences() {
  return request<ApiResponse<UserPreferences>>({
    url: '/api/user/preferences',
    method: 'get',
  });
}

// 更新用户偏好设置
export function updateUserPreferences(data: UserPreferences) {
  return request<ApiResponse<UserPreferences>>({
    url: '/api/user/preferences',
    method: 'put',
    data,
  });
}

// 注销账号
export function deleteAccount(password: string) {
  return request<ApiResponse<null>>({
    url: '/api/user/account',
    method: 'delete',
    data: { password },
  });
}