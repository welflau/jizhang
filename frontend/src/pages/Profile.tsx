import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Avatar,
  Button,
  TextField,
  Grid,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  IconButton,
  Tabs,
  Tab,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  Edit as EditIcon,
  PhotoCamera as PhotoCameraIcon,
  Lock as LockIcon,
  Settings as SettingsIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Notifications as NotificationsIcon,
  Language as LanguageIcon,
  Palette as PaletteIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

interface UserInfo {
  id: string;
  username: string;
  email: string;
  phone: string;
  avatar: string;
  bio: string;
  createdAt: string;
}

interface Preferences {
  emailNotifications: boolean;
  pushNotifications: boolean;
  language: string;
  theme: string;
  autoSave: boolean;
}

const Profile: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');

  const [userInfo, setUserInfo] = useState<UserInfo>({
    id: '1',
    username: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+1 234 567 8900',
    avatar: '',
    bio: 'Software developer passionate about creating amazing user experiences.',
    createdAt: '2023-01-15',
  });

  const [editedUserInfo, setEditedUserInfo] = useState<UserInfo>(userInfo);

  const [preferences, setPreferences] = useState<Preferences>({
    emailNotifications: true,
    pushNotifications: false,
    language: 'zh-CN',
    theme: 'light',
    autoSave: true,
  });

  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [passwordErrors, setPasswordErrors] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  useEffect(() => {
    // 模拟从 API 加载用户数据
    loadUserData();
  }, []);

  const loadUserData = async () => {
    // TODO: 实际从 API 加载数据
    // const response = await fetch('/api/user/profile');
    // const data = await response.json();
    // setUserInfo(data.userInfo);
    // setPreferences(data.preferences);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleEditToggle = () => {
    if (isEditing) {
      setEditedUserInfo(userInfo);
    }
    setIsEditing(!isEditing);
  };

  const handleInputChange = (field: keyof UserInfo) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setEditedUserInfo({
      ...editedUserInfo,
      [field]: event.target.value,
    });
  };

  const handleSaveProfile = async () => {
    try {
      // TODO: 实际保存到 API
      // await fetch('/api/user/profile', {
      //   method: 'PUT',
      //   body: JSON.stringify(editedUserInfo),
      // });
      
      setUserInfo(editedUserInfo);
      setIsEditing(false);
      showSnackbar('个人信息更新成功', 'success');
    } catch (error) {
      showSnackbar('更新失败，请重试', 'error');
    }
  };

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setEditedUserInfo({
          ...editedUserInfo,
          avatar: reader.result as string,
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePasswordDialogOpen = () => {
    setPasswordDialogOpen(true);
    setPasswordForm({
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    });
    setPasswordErrors({
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    });
  };

  const handlePasswordDialogClose = () => {
    setPasswordDialogOpen(false);
  };

  const validatePasswordForm = (): boolean => {
    const errors = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    };

    if (!passwordForm.currentPassword) {
      errors.currentPassword = '请输入当前密码';
    }

    if (!passwordForm.newPassword) {
      errors.newPassword = '请输入新密码';
    } else if (passwordForm.newPassword.length < 6) {
      errors.newPassword = '密码长度至少为 6 位';
    }

    if (!passwordForm.confirmPassword) {
      errors.confirmPassword = '请确认新密码';
    } else if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      errors.confirmPassword = '两次输入的密码不一致';
    }

    setPasswordErrors(errors);
    return !errors.currentPassword && !errors.newPassword && !errors.confirmPassword;
  };

  const handlePasswordChange = async () => {
    if (!validatePasswordForm()) {
      return;
    }

    try {
      // TODO: 实际调用 API
      // await fetch('/api/user/change-password', {
      //   method: 'POST',
      //   body: JSON.stringify({
      //     currentPassword: passwordForm.currentPassword,
      //     newPassword: passwordForm.newPassword,
      //   }),
      // });

      handlePasswordDialogClose();
      showSnackbar('密码修改成功', 'success');
    } catch (error) {
      showSnackbar('密码修改失败，请检查当前密码是否正确', 'error');
    }
  };

  const handlePreferenceChange = (field: keyof Preferences) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const newPreferences = {
      ...preferences,
      [field]: event.target.checked,
    };
    setPreferences(newPreferences);
    savePreferences(newPreferences);
  };

  const savePreferences = async (newPreferences: Preferences) => {
    try {
      // TODO: 实际保存到 API
      // await fetch('/api/user/preferences', {
      //   method: 'PUT',
      //   body: JSON.stringify(newPreferences),
      // });
      
      showSnackbar('偏好设置已保存', 'success');
    } catch (error) {
      showSnackbar('保存失败，请重试', 'error');
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ overflow: 'hidden' }}>
        {/* 头部信息区 */}
        <Box
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            p: 4,
            position: 'relative',
          }}
        >
          <Grid container spacing={3} alignItems="center">
            <Grid item>
              <Box sx={{ position: 'relative' }}>
                <Avatar
                  src={editedUserInfo.avatar}
                  sx={{ width: 120, height: 120, border: '4px solid white' }}
                >
                  {userInfo.username.charAt(0).toUpperCase()}
                </Avatar>
                {isEditing && (
                  <IconButton
                    component="label"
                    sx={{
                      position: 'absolute',
                      bottom: 0,
                      right: 0,
                      backgroundColor: 'white',
                      '&:hover': { backgroundColor: 'grey.200' },
                    }}
                  >
                    <PhotoCameraIcon color="primary" />
                    <input
                      type="file"
                      hidden
                      accept="image/*"
                      onChange={handleAvatarChange}
                    />
                  </IconButton>
                )}
              </Box>
            </Grid>
            <Grid item xs>
              <Typography variant="h4" gutterBottom>
                {userInfo.username}
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                {userInfo.email}
              </Typography>
              <Chip
                label={`加入于 ${userInfo.createdAt}`}
                sx={{ mt: 1, backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }}
              />
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                color="inherit"
                startIcon={isEditing ? <CancelIcon /> : <EditIcon />}
                onClick={handleEditToggle}
                sx={{ mr: 1 }}
              >
                {isEditing ? '取消' : '编辑资料'}
              </Button>
              {isEditing && (
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveProfile}
                >
                  保存
                </Button>
              )}
            </Grid>
          </Grid>
        </Box>

        {/* 标签页导航 */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="profile tabs">
            <Tab icon={<PersonIcon />} label="基本信息" />
            <Tab icon={<SettingsIcon />} label="偏好设置" />
            <Tab icon={<LockIcon />} label="安全设置" />
          </Tabs>
        </Box>

        {/* 基本信息面板 */}
        <TabPanel value={tabValue} index={0}>
          <Container maxWidth="md">
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="用户名"
                  value={editedUserInfo.username}
                  onChange={handleInputChange('username')}
                  disabled={!isEditing}
                  InputProps={{
                    startAdornment: <PersonIcon sx={{ mr: 1, color: 'action.active' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="邮箱"
                  type="email"
                  value={editedUserInfo.email}
                  onChange={handleInputChange('email')}
                  disabled={!isEditing}
                  InputProps={{
                    startAdornment: <EmailIcon sx={{ mr: 1, color: 'action.active' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="手机号"
                  value={editedUserInfo.phone}
                  onChange={handleInputChange('phone')}
                  disabled={!isEditing}
                  InputProps={{
                    startAdornment: <PhoneIcon sx={{ mr: 1, color: 'action.active' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="个人简介"
                  multiline
                  rows={4}
                  value={editedUserInfo.bio}
                  onChange={handleInputChange('bio')}
                  disabled={!isEditing}
                />
              </Grid>
            </Grid>
          </Container>
        </TabPanel>

        {/* 偏好设置面板 */}
        <TabPanel value={tabValue} index={1}>
          <Container maxWidth="md">
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <NotificationsIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">通知设置</Typography>
                    </Box>
                    <List>
                      <ListItem>
                        <ListItemText
                          primary="邮件通知"
                          secondary="接收重要更新和通知邮件"
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={preferences.emailNotifications}
                              onChange={handlePreferenceChange('emailNotifications')}
                            />
                          }
                          label=""
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemText
                          primary="推送通知"
                          secondary="接收浏览器推送通知"
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={preferences.pushNotifications}
                              onChange={handlePreferenceChange('pushNotifications')}
                            />
                          }
                          label=""
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <PaletteIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">界面设置</Typography>
                    </Box>
                    <List>
                      <ListItem>
                        <ListItemText
                          primary="自动保存"
                          secondary="自动保存编辑内容"
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={preferences.autoSave}
                              onChange={handlePreferenceChange('autoSave')}
                            />
                          }
                          label=""
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Container>
        </TabPanel>

        {/* 安全设置面板 */}
        <TabPanel value={tabValue} index={2}>
          <Container maxWidth="md">
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <LockIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">密码管理</Typography>
                    </Box>
                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <LockIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary="修改密码"
                          secondary="定期修改密码以保护账户安全"
                        />
                        <Button
                          variant="outlined"
                          onClick={handlePasswordDialogOpen}
                        >
                          修改密码
                        </Button>
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      账户信息
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemText
                          primary="账户 ID"
                          secondary={userInfo.id}
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemText
                          primary="注册时间"
                          secondary={userInfo.createdAt}
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Container>
        </TabPanel>
      </Paper>

      {/* 修改密码对话框 */}
      <Dialog
        open={passwordDialogOpen}
        onClose={handlePasswordDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>修改密码</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              type="password"
              label="当前密码"
              value={passwordForm.currentPassword}
              onChange={(e) =>
                setPasswordForm({ ...passwordForm, currentPassword: e.target.value })
              }
              error={!!passwordErrors.currentPassword}
              helperText={passwordErrors.currentPassword}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              type="password"
              label="新密码"
              value={passwordForm.newPassword}
              onChange={(e) =>
                setPasswordForm({ ...passwordForm, newPassword: e.target.value })
              }
              error={!!passwordErrors.newPassword}
              helperText={passwordErrors.newPassword}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              type="password"
              label="确认新密码"
              value={passwordForm.confirmPassword}
              onChange={(e) =>
                setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })
              }
              error={!!passwordErrors.confirmPassword}
              helperText={passwordErrors.confirmPassword}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handlePasswordDialogClose}>取消</Button>
          <Button onClick={handlePasswordChange} variant="contained">
            确认修改
          </Button>
        </DialogActions>
      </Dialog>

      {/* 提示消息 */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Profile;