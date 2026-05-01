import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from backend.models import Category, Transaction

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
        password='otherpass123'
    )


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def income_category(user):
    return Category.objects.create(
        name='Salary',
        type='income',
        user=user
    )


@pytest.fixture
def expense_category(user):
    return Category.objects.create(
        name='Food',
        type='expense',
        user=user
    )


@pytest.mark.django_db
class TestCategoryListAPI:
    def test_list_categories_unauthenticated(self, api_client):
        """测试未认证用户无法获取分类列表"""
        url = reverse('category-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_categories_authenticated(self, auth_client, income_category, expense_category):
        """测试认证用户可以获取自己的分类列表"""
        url = reverse('category-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_categories_only_own(self, auth_client, income_category, other_user):
        """测试用户只能看到自己的分类"""
        Category.objects.create(name='Other Category', type='income', user=other_user)
        url = reverse('category-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Salary'

    def test_list_categories_grouped_by_type(self, auth_client, income_category, expense_category):
        """测试分类按类型分组"""
        url = reverse('category-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        income_categories = [cat for cat in response.data if cat['type'] == 'income']
        expense_categories = [cat for cat in response.data if cat['type'] == 'expense']
        
        assert len(income_categories) == 1
        assert len(expense_categories) == 1
        assert income_categories[0]['name'] == 'Salary'
        assert expense_categories[0]['name'] == 'Food'

    def test_filter_categories_by_type(self, auth_client, income_category, expense_category):
        """测试按类型过滤分类"""
        url = reverse('category-list')
        response = auth_client.get(url, {'type': 'income'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['type'] == 'income'

    def test_list_categories_empty(self, auth_client):
        """测试空分类列表"""
        url = reverse('category-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestCategoryCreateAPI:
    def test_create_category_unauthenticated(self, api_client):
        """测试未认证用户无法创建分类"""
        url = reverse('category-list')
        data = {'name': 'New Category', 'type': 'income'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_income_category(self, auth_client, user):
        """测试创建收入分类"""
        url = reverse('category-list')
        data = {'name': 'Bonus', 'type': 'income'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Bonus'
        assert response.data['type'] == 'income'
        assert Category.objects.filter(user=user, name='Bonus').exists()

    def test_create_expense_category(self, auth_client, user):
        """测试创建支出分类"""
        url = reverse('category-list')
        data = {'name': 'Transport', 'type': 'expense'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Transport'
        assert response.data['type'] == 'expense'

    def test_create_category_missing_name(self, auth_client):
        """测试创建分类缺少名称"""
        url = reverse('category-list')
        data = {'type': 'income'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_create_category_missing_type(self, auth_client):
        """测试创建分类缺少类型"""
        url = reverse('category-list')
        data = {'name': 'New Category'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'type' in response.data

    def test_create_category_invalid_type(self, auth_client):
        """测试创建分类使用无效类型"""
        url = reverse('category-list')
        data = {'name': 'New Category', 'type': 'invalid'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_empty_name(self, auth_client):
        """测试创建分类名称为空"""
        url = reverse('category-list')
        data = {'name': '', 'type': 'income'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_duplicate_name_same_user(self, auth_client, income_category):
        """测试同一用户创建重复名称的分类"""
        url = reverse('category-list')
        data = {'name': 'Salary', 'type': 'income'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_duplicate_name_different_user(self, auth_client, other_user):
        """测试不同用户可以创建相同名称的分类"""
        Category.objects.create(name='Salary', type='income', user=other_user)
        url = reverse('category-list')
        data = {'name': 'Salary', 'type': 'income'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_category_with_icon(self, auth_client):
        """测试创建带图标的分类"""
        url = reverse('category-list')
        data = {'name': 'Shopping', 'type': 'expense', 'icon': '🛒'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['icon'] == '🛒'

    def test_create_category_with_color(self, auth_client):
        """测试创建带颜色的分类"""
        url = reverse('category-list')
        data = {'name': 'Shopping', 'type': 'expense', 'color': '#FF5733'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['color'] == '#FF5733'


@pytest.mark.django_db
class TestCategoryUpdateAPI:
    def test_update_category_unauthenticated(self, api_client, income_category):
        """测试未认证用户无法更新分类"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'name': 'Updated Salary'}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_category_name(self, auth_client, income_category):
        """测试更新分类名称"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'name': 'Updated Salary'}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Salary'
        income_category.refresh_from_db()
        assert income_category.name == 'Updated Salary'

    def test_update_category_type(self, auth_client, income_category):
        """测试更新分类类型"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'type': 'expense'}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['type'] == 'expense'

    def test_update_category_icon(self, auth_client, income_category):
        """测试更新分类图标"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'icon': '💰'}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['icon'] == '💰'

    def test_update_category_color(self, auth_client, income_category):
        """测试更新分类颜色"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'color': '#00FF00'}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['color'] == '#00FF00'

    def test_update_category_not_owner(self, auth_client, other_user):
        """测试用户无法更新其他用户的分类"""
        other_category = Category.objects.create(
            name='Other Category',
            type='income',
            user=other_user
        )
        url = reverse('category-detail', kwargs={'pk': other_category.id})
        data = {'name': 'Hacked'}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_category_invalid_type(self, auth_client, income_category):
        """测试更新分类为无效类型"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'type': 'invalid'}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_category_empty_name(self, auth_client, income_category):
        """测试更新分类名称为空"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'name': ''}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_category_duplicate_name(self, auth_client, income_category, expense_category):
        """测试更新分类为已存在的名称"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {'name': 'Food'}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_category_full_update(self, auth_client, income_category):
        """测试完整更新分类"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        data = {
            'name': 'New Salary',
            'type': 'income',
            'icon': '💵',
            'color': '#0000FF'
        }
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'New Salary'
        assert response.data['icon'] == '💵'
        assert response.data['color'] == '#0000FF'


@pytest.mark.django_db
class TestCategoryDeleteAPI:
    def test_delete_category_unauthenticated(self, api_client, income_category):
        """测试未认证用户无法删除分类"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_category_without_transactions(self, auth_client, income_category):
        """测试删除没有关联交易的分类"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=income_category.id).exists()

    def test_delete_category_with_transactions(self, auth_client, income_category, user):
        """测试删除有关联交易的分类应该失败"""
        Transaction.objects.create(
            user=user,
            category=income_category,
            amount=1000,
            type='income',
            description='Test transaction'
        )
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.filter(id=income_category.id).exists()

    def test_delete_category_not_owner(self, auth_client, other_user):
        """测试用户无法删除其他用户的分类"""
        other_category = Category.objects.create(
            name='Other Category',
            type='income',
            user=other_user
        )
        url = reverse('category-detail', kwargs={'pk': other_category.id})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Category.objects.filter(id=other_category.id).exists()

    def test_delete_category_nonexistent(self, auth_client):
        """测试删除不存在的分类"""
        url = reverse('category-detail', kwargs={'pk': 99999})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_category_cascade_check(self, auth_client, income_category, user):
        """测试删除分类时检查关联交易数量"""
        for i in range(3):
            Transaction.objects.create(
                user=user,
                category=income_category,
                amount=1000 + i,
                type='income',
                description=f'Test transaction {i}'
            )
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'transactions' in str(response.data).lower() or 'related' in str(response.data).lower()


@pytest.mark.django_db
class TestCategoryRetrieveAPI:
    def test_retrieve_category_unauthenticated(self, api_client, income_category):
        """测试未认证用户无法获取分类详情"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_category_authenticated(self, auth_client, income_category):
        """测试认证用户可以获取自己的分类详情"""
        url = reverse('category-detail', kwargs={'pk': income_category.id})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Salary'
        assert response.data['type'] == 'income'

    def test_retrieve_category_not_owner(self, auth_client, other_user):
        """测试用户无法获取其他用户的分类详情"""
        other_category = Category.objects.create(
            name='Other Category',
            type='income',
            user=other_user
        )
        url = reverse('category-detail', kwargs={'pk': other_category.id})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_category_nonexistent(self, auth_client):
        """测试获取不存在的分类"""
        url = reverse('category-detail', kwargs={'pk': 99999})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_category_with_all_fields(self, auth_client, user):
        """测试获取包含所有字段的分类详情"""
        category = Category.objects.create(
            name='Complete Category',
            type='expense',
            icon='🎯',
            color='#FF0000',
            user=user
        )
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Complete Category'
        assert response.data['type'] == 'expense'
        assert response.data['icon'] == '🎯'
        assert response.data['color'] == '#FF0000'