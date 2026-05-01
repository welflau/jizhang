import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from categories.models import Category
from records.models import Record
from decimal import Decimal

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='testpass123'
    )


@pytest.fixture
def income_category(user):
    return Category.objects.create(
        user=user,
        name='工资',
        type='income',
        icon='salary',
        color='#4CAF50'
    )


@pytest.fixture
def expense_category(user):
    return Category.objects.create(
        user=user,
        name='餐饮',
        type='expense',
        icon='food',
        color='#FF5722'
    )


@pytest.fixture
def other_user_category(other_user):
    return Category.objects.create(
        user=other_user,
        name='其他用户分类',
        type='expense',
        icon='other',
        color='#9E9E9E'
    )


@pytest.mark.django_db
class TestCategoryList:
    """测试获取分类列表"""

    def test_list_categories_unauthenticated(self, api_client):
        """未认证用户无法获取分类列表"""
        url = reverse('category-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_categories_authenticated(self, api_client, user, income_category, expense_category):
        """认证用户可以获取自己的分类列表"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        # 验证返回的分类属于当前用户
        category_ids = [cat['id'] for cat in response.data]
        assert income_category.id in category_ids
        assert expense_category.id in category_ids

    def test_list_categories_only_own(self, api_client, user, income_category, other_user_category):
        """用户只能看到自己的分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == income_category.id

    def test_list_categories_filter_by_type(self, api_client, user, income_category, expense_category):
        """按类型筛选分类"""
        api_client.force_authenticate(user=user)
        
        # 筛选收入分类
        url = reverse('category-list') + '?type=income'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['type'] == 'income'
        
        # 筛选支出分类
        url = reverse('category-list') + '?type=expense'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['type'] == 'expense'

    def test_list_categories_grouped(self, api_client, user, income_category, expense_category):
        """按收入/支出分组返回分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list') + '?grouped=true'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'income' in response.data
        assert 'expense' in response.data
        assert len(response.data['income']) == 1
        assert len(response.data['expense']) == 1


@pytest.mark.django_db
class TestCategoryCreate:
    """测试创建分类"""

    def test_create_category_unauthenticated(self, api_client):
        """未认证用户无法创建分类"""
        url = reverse('category-list')
        data = {
            'name': '新分类',
            'type': 'expense',
            'icon': 'shopping',
            'color': '#2196F3'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_category_success(self, api_client, user):
        """成功创建分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        data = {
            'name': '购物',
            'type': 'expense',
            'icon': 'shopping',
            'color': '#2196F3'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == '购物'
        assert response.data['type'] == 'expense'
        assert response.data['icon'] == 'shopping'
        assert response.data['color'] == '#2196F3'
        
        # 验证数据库中已创建
        category = Category.objects.get(id=response.data['id'])
        assert category.user == user
        assert category.name == '购物'

    def test_create_category_missing_required_fields(self, api_client, user):
        """缺少必填字段"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        data = {
            'name': '新分类'
            # 缺少 type
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'type' in response.data

    def test_create_category_invalid_type(self, api_client, user):
        """无效的分类类型"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        data = {
            'name': '新分类',
            'type': 'invalid_type',
            'icon': 'icon',
            'color': '#000000'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_duplicate_name(self, api_client, user, income_category):
        """同一用户不能创建同名分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        data = {
            'name': income_category.name,
            'type': 'income',
            'icon': 'icon',
            'color': '#000000'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_invalid_color(self, api_client, user):
        """无效的颜色格式"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        data = {
            'name': '新分类',
            'type': 'expense',
            'icon': 'icon',
            'color': 'invalid_color'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCategoryRetrieve:
    """测试获取单个分类详情"""

    def test_retrieve_category_unauthenticated(self, api_client, income_category):
        """未认证用户无法获取分类详情"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_category_success(self, api_client, user, income_category):
        """成功获取分类详情"""
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == income_category.id
        assert response.data['name'] == income_category.name
        assert response.data['type'] == income_category.type

    def test_retrieve_other_user_category(self, api_client, user, other_user_category):
        """无法获取其他用户的分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': other_user_category.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_nonexistent_category(self, api_client, user):
        """获取不存在的分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': 99999})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCategoryUpdate:
    """测试更新分类"""

    def test_update_category_unauthenticated(self, api_client, income_category):
        """未认证用户无法更新分类"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'name': '更新后的名称'}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_category_success(self, api_client, user, income_category):
        """成功更新分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {
            'name': '更新后的工资',
            'icon': 'new_icon',
            'color': '#FF0000'
        }
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == '更新后的工资'
        assert response.data['icon'] == 'new_icon'
        assert response.data['color'] == '#FF0000'
        
        # 验证数据库已更新
        income_category.refresh_from_db()
        assert income_category.name == '更新后的工资'

    def test_update_category_type_not_allowed(self, api_client, user, income_category):
        """不允许修改分类类型"""
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'type': 'expense'}
        response = api_client.patch(url, data)
        
        # 根据实际实现，可能返回400或忽略type字段
        income_category.refresh_from_db()
        assert income_category.type == 'income'

    def test_update_other_user_category(self, api_client, user, other_user_category):
        """无法更新其他用户的分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': other_user_category.id})
        data = {'name': '尝试更新'}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_category_duplicate_name(self, api_client, user, income_category, expense_category):
        """更新为已存在的名称"""
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'name': expense_category.name}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCategoryDelete:
    """测试删除分类"""

    def test_delete_category_unauthenticated(self, api_client, income_category):
        """未认证用户无法删除分类"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_category_success(self, api_client, user, income_category):
        """成功删除分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=income_category.id).exists()

    def test_delete_category_with_records(self, api_client, user, expense_category):
        """删除有关联记录的分类应该失败"""
        # 创建关联记录
        Record.objects.create(
            user=user,
            category=expense_category,
            amount=Decimal('100.00'),
            type='expense',
            date='2024-01-01',
            description='测试记录'
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': expense_category.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.filter(id=expense_category.id).exists()
        assert 'records' in str(response.data).lower() or 'associated' in str(response.data).lower()

    def test_delete_other_user_category(self, api_client, user, other_user_category):
        """无法删除其他用户的分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': other_user_category.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_category(self, api_client, user):
        """删除不存在的分类"""
        api_client.force_authenticate(user=user)
        url = reverse('category-detail', kwargs={'pk': 99999})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCategoryPermissions:
    """测试分类权限控制"""

    def test_user_can_only_access_own_categories(self, api_client, user, other_user, income_category, other_user_category):
        """用户只能访问自己的分类"""
        api_client.force_authenticate(user=user)
        
        # 可以访问自己的分类
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # 无法访问其他用户的分类
        url = reverse('category-detail', kwargs={'pk': other_user_category.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_category_auto_assign_user(self, api_client, user):
        """创建分类时自动关联当前用户"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        data = {
            'name': '自动关联用户',
            'type': 'expense',
            'icon': 'icon',
            'color': '#000000'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        category = Category.objects.get(id=response.data['id'])
        assert category.user == user


@pytest.mark.django_db
class TestCategoryValidation:
    """测试分类数据校验"""

    def test_category_name_max_length(self, api_client, user):
        """分类名称长度限制"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        data = {
            'name': 'A' * 101,  # 超过最大长度
            'type': 'expense',
            'icon': 'icon',
            'color': '#000000'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_category_name_required(self, api_client, user):
        """分类名称必填"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        data = {
            'type': 'expense',
            'icon': 'icon',
            'color': '#000000'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_category_type_choices(self, api_client, user):
        """分类类型只能是income或expense"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        
        # 测试有效类型
        for valid_type in ['income', 'expense']:
            data = {
                'name': f'测试{valid_type}',
                'type': valid_type,
                'icon': 'icon',
                'color': '#000000'
            }
            response = api_client.post(url, data)
            assert response.status_code == status.HTTP_201_CREATED

    def test_category_color_format(self, api_client, user):
        """颜色格式验证"""
        api_client.force_authenticate(user=user)
        url = reverse('category-list')
        
        # 有效的颜色格式
        valid_colors = ['#FF0000', '#00ff00', '#0000FF']
        for color in valid_colors:
            data = {
                'name': f'测试{color}',
                'type': 'expense',
                'icon': 'icon',
                'color': color
            }
            response = api_client.post(url, data)
            assert response.status_code == status.HTTP_201_CREATED