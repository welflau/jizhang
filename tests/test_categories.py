import pytest
from fastapi import status
from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.record import Record
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
def test_user(db: Session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """获取认证头"""
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def income_category(db: Session, test_user):
    """创建收入分类"""
    category = Category(
        name="工资",
        type="income",
        user_id=test_user.id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def expense_category(db: Session, test_user):
    """创建支出分类"""
    category = Category(
        name="餐饮",
        type="expense",
        user_id=test_user.id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


class TestGetCategories:
    """测试获取分类列表"""
    
    def test_get_categories_success(self, client, auth_headers, income_category, expense_category):
        """测试成功获取分类列表"""
        response = client.get("/api/categories", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "income" in data
        assert "expense" in data
        assert len(data["income"]) == 1
        assert len(data["expense"]) == 1
        assert data["income"][0]["name"] == "工资"
        assert data["expense"][0]["name"] == "餐饮"
    
    def test_get_categories_unauthorized(self, client):
        """测试未认证访问"""
        response = client.get("/api/categories")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_categories_empty(self, client, auth_headers):
        """测试空分类列表"""
        response = client.get("/api/categories", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["income"] == []
        assert data["expense"] == []
    
    def test_get_categories_multiple(self, client, auth_headers, db, test_user):
        """测试多个分类"""
        categories = [
            Category(name="工资", type="income", user_id=test_user.id),
            Category(name="奖金", type="income", user_id=test_user.id),
            Category(name="餐饮", type="expense", user_id=test_user.id),
            Category(name="交通", type="expense", user_id=test_user.id),
            Category(name="购物", type="expense", user_id=test_user.id),
        ]
        for cat in categories:
            db.add(cat)
        db.commit()
        
        response = client.get("/api/categories", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["income"]) == 2
        assert len(data["expense"]) == 3
    
    def test_get_categories_only_own(self, client, auth_headers, db, test_user):
        """测试只返回当前用户的分类"""
        # 创建其他用户的分类
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("pass123")
        )
        db.add(other_user)
        db.commit()
        
        other_category = Category(
            name="其他分类",
            type="income",
            user_id=other_user.id
        )
        db.add(other_category)
        
        own_category = Category(
            name="自己的分类",
            type="income",
            user_id=test_user.id
        )
        db.add(own_category)
        db.commit()
        
        response = client.get("/api/categories", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["income"]) == 1
        assert data["income"][0]["name"] == "自己的分类"


class TestCreateCategory:
    """测试创建分类"""
    
    def test_create_income_category_success(self, client, auth_headers):
        """测试成功创建收入分类"""
        category_data = {
            "name": "工资",
            "type": "income"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "工资"
        assert data["type"] == "income"
        assert "id" in data
        assert "user_id" in data
    
    def test_create_expense_category_success(self, client, auth_headers):
        """测试成功创建支出分类"""
        category_data = {
            "name": "餐饮",
            "type": "expense"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "餐饮"
        assert data["type"] == "expense"
    
    def test_create_category_unauthorized(self, client):
        """测试未认证创建分类"""
        category_data = {
            "name": "工资",
            "type": "income"
        }
        
        response = client.post("/api/categories", json=category_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_category_missing_name(self, client, auth_headers):
        """测试缺少名称"""
        category_data = {
            "type": "income"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_category_missing_type(self, client, auth_headers):
        """测试缺少类型"""
        category_data = {
            "name": "工资"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_category_invalid_type(self, client, auth_headers):
        """测试无效的类型"""
        category_data = {
            "name": "工资",
            "type": "invalid"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_category_empty_name(self, client, auth_headers):
        """测试空名称"""
        category_data = {
            "name": "",
            "type": "income"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_category_duplicate_name(self, client, auth_headers, income_category):
        """测试重复的分类名称"""
        category_data = {
            "name": "工资",
            "type": "income"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "已存在" in response.json()["detail"]
    
    def test_create_category_long_name(self, client, auth_headers):
        """测试过长的名称"""
        category_data = {
            "name": "a" * 51,
            "type": "income"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdateCategory:
    """测试更新分类"""
    
    def test_update_category_name_success(self, client, auth_headers, income_category):
        """测试成功更新分类名称"""
        update_data = {
            "name": "基本工资"
        }
        
        response = client.put(
            f"/api/categories/{income_category.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "基本工资"
        assert data["type"] == "income"
    
    def test_update_category_type_success(self, client, auth_headers, income_category):
        """测试成功更新分类类型"""
        update_data = {
            "type": "expense"
        }
        
        response = client.put(
            f"/api/categories/{income_category.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["type"] == "expense"
        assert data["name"] == "工资"
    
    def test_update_category_both_success(self, client, auth_headers, income_category):
        """测试同时更新名称和类型"""
        update_data = {
            "name": "餐饮",
            "type": "expense"
        }
        
        response = client.put(
            f"/api/categories/{income_category.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "餐饮"
        assert data["type"] == "expense"
    
    def test_update_category_unauthorized(self, client, income_category):
        """测试未认证更新分类"""
        update_data = {
            "name": "新名称"
        }
        
        response = client.put(
            f"/api/categories/{income_category.id}",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_category_not_found(self, client, auth_headers):
        """测试更新不存在的分类"""
        update_data = {
            "name": "新名称"
        }
        
        response = client.put(
            "/api/categories/99999",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_category_not_owner(self, client, auth_headers, db, income_category):
        """测试更新其他用户的分类"""
        # 创建另一个用户并登录
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("pass123")
        )
        db.add(other_user)
        db.commit()
        
        login_response = client.post(
            "/api/auth/login",
            data={"username": "otheruser", "password": "pass123"}
        )
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        update_data = {
            "name": "新名称"
        }
        
        response = client.put(
            f"/api/categories/{income_category.id}",
            json=update_data,
            headers=other_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_category_duplicate_name(self, client, auth_headers, db, test_user):
        """测试更新为已存在的名称"""
        category1 = Category(name="工资", type="income", user_id=test_user.id)
        category2 = Category(name="奖金", type="income", user_id=test_user.id)
        db.add(category1)
        db.add(category2)
        db.commit()
        
        update_data = {
            "name": "工资"
        }
        
        response = client.put(
            f"/api/categories/{category2.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "已存在" in response.json()["detail"]
    
    def test_update_category_invalid_type(self, client, auth_headers, income_category):
        """测试更新为无效类型"""
        update_data = {
            "type": "invalid"
        }
        
        response = client.put(
            f"/api/categories/{income_category.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_category_empty_name(self, client, auth_headers, income_category):
        """测试更新为空名称"""
        update_data = {
            "name": ""
        }
        
        response = client.put(
            f"/api/categories/{income_category.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteCategory:
    """测试删除分类"""
    
    def test_delete_category_success(self, client, auth_headers, income_category):
        """测试成功删除分类"""
        response = client.delete(
            f"/api/categories/{income_category.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # 验证分类已删除
        get_response = client.get("/api/categories", headers=auth_headers)
        data = get_response.json()
        assert len(data["income"]) == 0
    
    def test_delete_category_unauthorized(self, client, income_category):
        """测试未认证删除分类"""
        response = client.delete(f"/api/categories/{income_category.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_category_not_found(self, client, auth_headers):
        """测试删除不存在的分类"""
        response = client.delete(
            "/api/categories/99999",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_category_not_owner(self, client, auth_headers, db, income_category):
        """测试删除其他用户的分类"""
        # 创建另一个用户并登录
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("pass123")
        )
        db.add(other_user)
        db.commit()
        
        login_response = client.post(
            "/api/auth/login",
            data={"username": "otheruser", "password": "pass123"}
        )
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        response = client.delete(
            f"/api/categories/{income_category.id}",
            headers=other_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_category_with_records(self, client, auth_headers, db, income_category, test_user):
        """测试删除有关联记录的分类"""
        # 创建关联记录
        record = Record(
            amount=1000.00,
            type="income",
            category_id=income_category.id,
            user_id=test_user.id,
            description="测试记录"
        )
        db.add(record)
        db.commit()
        
        response = client.delete(
            f"/api/categories/{income_category.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "存在关联记录" in response.json()["detail"] or "cannot be deleted" in response.json()["detail"].lower()
    
    def test_delete_category_cascade_check(self, client, auth_headers, db, income_category, test_user):
        """测试删除分类时的级联检查"""
        # 创建多条关联记录
        records = [
            Record(
                amount=1000.00,
                type="income",
                category_id=income_category.id,
                user_id=test_user.id,
                description=f"记录{i}"
            )
            for i in range(3)
        ]
        for record in records:
            db.add(record)
        db.commit()
        
        response = client.delete(
            f"/api/categories/{income_category.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # 验证分类仍然存在
        get_response = client.get("/api/categories", headers=auth_headers)
        data = get_response.json()
        assert len(data["income"]) == 1


class TestCategoryValidation:
    """测试分类数据验证"""
    
    def test_category_name_whitespace(self, client, auth_headers):
        """测试名称前后空格处理"""
        category_data = {
            "name": "  工资  ",
            "type": "income"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "工资"
    
    def test_category_name_special_characters(self, client, auth_headers):
        """测试特殊字符名称"""
        category_data = {
            "name": "工资&奖金",
            "type": "income"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "工资&奖金"
    
    def test_category_name_unicode(self, client, auth_headers):
        """测试Unicode字符名称"""
        category_data = {
            "name": "工资💰",
            "type": "income"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "工资💰"
    
    def test_category_type_case_sensitive(self, client, auth_headers):
        """测试类型大小写敏感"""
        category_data = {
            "name": "工资",
            "type": "INCOME"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCategoryEdgeCases:
    """测试边界情况"""
    
    def test_create_many_categories(self, client, auth_headers, db, test_user):
        """测试创建大量分类"""
        for i in range(50):
            category_data = {
                "name": f"分类{i}",
                "type": "income" if i % 2 == 0 else "expense"
            }
            response = client.post(
                "/api/categories",
                json=category_data,
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_201_CREATED
        
        # 验证所有分类都已创建
        response = client.get("/api/categories", headers=auth_headers)
        data = response.json()
        assert len(data["income"]) == 25
        assert len(data["expense"]) == 25
    
    def test_category_name_max_length(self, client, auth_headers):
        """测试最大长度名称"""
        category_data = {
            "name": "a" * 50,
            "type": "income"
        }
        
        response = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_concurrent_category_creation(self, client, auth_headers):
        """测试并发创建相同分类"""
        category_data = {
            "name": "工资",
            "type": "income"
        }
        
        response1 = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        response2 = client.post(
            "/api/categories",
            json=category_data,
            headers=auth_headers
        )
        
        # 一个成功，一个失败
        assert (response1.status_code == status.HTTP_201_CREATED and 
                response2.status_code == status.HTTP_400_BAD_REQUEST) or \
               (response2.status_code == status.HTTP_201_CREATED and 
                response1.status_code == status.HTTP_400_BAD_REQUEST)