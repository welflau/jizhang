export interface User {
  id: string;
  username: string;
  email: string;
  avatar?: string;
  nickname?: string;
  phone?: string;
  bio?: string;
  gender?: 'male' | 'female' | 'other';
  birthday?: string;
  location?: string;
  website?: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserProfile extends User {
  followersCount?: number;
  followingCount?: number;
  postsCount?: number;
}

export interface UpdateUserProfileDto {
  nickname?: string;
  email?: string;
  phone?: string;
  bio?: string;
  gender?: 'male' | 'female' | 'other';
  birthday?: string;
  location?: string;
  website?: string;
  avatar?: string;
}

export interface ChangePasswordDto {
  oldPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface UserPreferences {
  theme?: 'light' | 'dark' | 'auto';
  language?: string;
  timezone?: string;
  emailNotifications?: boolean;
  pushNotifications?: boolean;
  smsNotifications?: boolean;
  privacySettings?: {
    profileVisibility?: 'public' | 'private' | 'friends';
    showEmail?: boolean;
    showPhone?: boolean;
    showBirthday?: boolean;
    showLocation?: boolean;
  };
}

export interface UserStats {
  postsCount: number;
  followersCount: number;
  followingCount: number;
  likesCount: number;
  commentsCount: number;
}

export interface UserFormData {
  nickname: string;
  email: string;
  phone: string;
  bio: string;
  gender: 'male' | 'female' | 'other' | '';
  birthday: string;
  location: string;
  website: string;
}

export interface PasswordFormData {
  oldPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface PreferencesFormData {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  emailNotifications: boolean;
  pushNotifications: boolean;
  smsNotifications: boolean;
  profileVisibility: 'public' | 'private' | 'friends';
  showEmail: boolean;
  showPhone: boolean;
  showBirthday: boolean;
  showLocation: boolean;
}