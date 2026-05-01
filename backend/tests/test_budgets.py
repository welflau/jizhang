import pytest
from datetime import datetime
from decimal import Decimal
from flask import json
from backend.models import Budget, Transaction, Category
from backend.extensions import db


class TestBudgetCRUD:
    """测试预算 CRUD API 端点"""

    def test_create_budget_success(self, client, auth_headers, test_user, test_category):
        """测试成功创建预算"""
        data = {
            'category_id': test_category.id,
            'amount': 1000.00,
            'period': '2024-01'
        }
        response = client.post('/api/budgets', 
                              headers=auth_headers,
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 201
        result = json.loads(response.data)
        assert result['category_id'] == test_category.id
        assert float(result['amount']) == 1000.00
        assert result['period'] == '2024-01'
        assert result['user_id'] == test_user.id
        assert 'spent' in result
        assert 'percentage' in result

    def test_create_budget_invalid_amount(self, client, auth_headers, test_category):
        """测试创建预算时金额无效"""
        # 测试金额为 0
        data = {
            'category_id': test_category.id,
            'amount': 0,
            'period': '2024-01'
        }
        response = client.post('/api/budgets',
                              headers=auth_headers,
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'amount' in result['message'].lower()

        # 测试金额为负数
        data['amount'] = -100
        response = client.post('/api/budgets',
                              headers=auth_headers,
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400

    def test_create_budget_invalid_period_format(self, client, auth_headers, test_category):
        """测试创建预算时周期格式无效"""
        invalid_periods = ['2024', '202401', '2024/01', '24-01', '2024-13', '2024-00']
        
        for period in invalid_periods:
            data = {
                'category_id': test_category.id,
                'amount': 1000.00,
                'period': period
            }
            response = client.post('/api/budgets',
                                  headers=auth_headers,
                                  data=json.dumps(data),
                                  content_type='application/json')
            assert response.status_code == 400
            result = json.loads(response.data)
            assert 'period' in result['message'].lower()

    def test_create_budget_missing_fields(self, client, auth_headers):
        """测试创建预算时缺少必填字段"""
        data = {'amount': 1000.00}
        response = client.post('/api/budgets',
                              headers=auth_headers,
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400

    def test_create_budget_duplicate(self, client, auth_headers, test_user, test_category):
        """测试创建重复预算（同一用户、分类、周期）"""
        data = {
            'category_id': test_category.id,
            'amount': 1000.00,
            'period': '2024-01'
        }
        # 第一次创建
        response = client.post('/api/budgets',
                              headers=auth_headers,
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 201

        # 第二次创建相同预算
        response = client.post('/api/budgets',
                              headers=auth_headers,
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'already exists' in result['message'].lower()

    def test_create_budget_invalid_category(self, client, auth_headers):
        """测试创建预算时分类不存在"""
        data = {
            'category_id': 99999,
            'amount': 1000.00,
            'period': '2024-01'
        }
        response = client.post('/api/budgets',
                              headers=auth_headers,
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 404

    def test_create_budget_unauthorized(self, client, test_category):
        """测试未授权创建预算"""
        data = {
            'category_id': test_category.id,
            'amount': 1000.00,
            'period': '2024-01'
        }
        response = client.post('/api/budgets',
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 401

    def test_get_budgets_list(self, client, auth_headers, test_user, test_category):
        """测试获取预算列表"""
        # 创建多个预算
        budgets_data = [
            {'category_id': test_category.id, 'amount': 1000, 'period': '2024-01'},
            {'category_id': test_category.id, 'amount': 1500, 'period': '2024-02'},
            {'category_id': test_category.id, 'amount': 2000, 'period': '2024-03'}
        ]
        
        for data in budgets_data:
            budget = Budget(user_id=test_user.id, **data)
            db.session.add(budget)
        db.session.commit()

        response = client.get('/api/budgets', headers=auth_headers)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert len(result) == 3
        assert all('spent' in b and 'percentage' in b for b in result)

    def test_get_budgets_filter_by_period(self, client, auth_headers, test_user, test_category):
        """测试按周期筛选预算列表"""
        # 创建不同周期的预算
        budgets_data = [
            {'category_id': test_category.id, 'amount': 1000, 'period': '2024-01'},
            {'category_id': test_category.id, 'amount': 1500, 'period': '2024-02'}
        ]
        
        for data in budgets_data:
            budget = Budget(user_id=test_user.id, **data)
            db.session.add(budget)
        db.session.commit()

        # 筛选 2024-01
        response = client.get('/api/budgets?period=2024-01', headers=auth_headers)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert len(result) == 1
        assert result[0]['period'] == '2024-01'

    def test_get_budgets_empty_list(self, client, auth_headers):
        """测试获取空预算列表"""
        response = client.get('/api/budgets', headers=auth_headers)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result == []

    def test_get_budgets_only_own_budgets(self, client, auth_headers, test_user, test_category):
        """测试只能获取自己的预算"""
        # 创建其他用户的预算
        other_user = User(username='other', email='other@test.com')
        other_user.set_password('password')
        db.session.add(other_user)
        db.session.commit()

        other_budget = Budget(
            user_id=other_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(other_budget)
        db.session.commit()

        response = client.get('/api/budgets', headers=auth_headers)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert len(result) == 0

    def test_update_budget_success(self, client, auth_headers, test_user, test_category):
        """测试成功更新预算"""
        # 创建预算
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()

        # 更新预算
        update_data = {'amount': 1500.00}
        response = client.put(f'/api/budgets/{budget.id}',
                             headers=auth_headers,
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert float(result['amount']) == 1500.00

    def test_update_budget_invalid_amount(self, client, auth_headers, test_user, test_category):
        """测试更新预算时金额无效"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()

        update_data = {'amount': -100}
        response = client.put(f'/api/budgets/{budget.id}',
                             headers=auth_headers,
                             data=json.dumps(update_data),
                             content_type='application/json')
        assert response.status_code == 400

    def test_update_budget_not_found(self, client, auth_headers):
        """测试更新不存在的预算"""
        update_data = {'amount': 1500.00}
        response = client.put('/api/budgets/99999',
                             headers=auth_headers,
                             data=json.dumps(update_data),
                             content_type='application/json')
        assert response.status_code == 404

    def test_update_budget_permission_denied(self, client, auth_headers, test_category):
        """测试更新其他用户的预算（权限校验）"""
        from backend.models import User
        
        # 创建其他用户的预算
        other_user = User(username='other', email='other@test.com')
        other_user.set_password('password')
        db.session.add(other_user)
        db.session.commit()

        other_budget = Budget(
            user_id=other_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(other_budget)
        db.session.commit()

        # 尝试更新其他用户的预算
        update_data = {'amount': 1500.00}
        response = client.put(f'/api/budgets/{other_budget.id}',
                             headers=auth_headers,
                             data=json.dumps(update_data),
                             content_type='application/json')
        assert response.status_code == 403

    def test_delete_budget_success(self, client, auth_headers, test_user, test_category):
        """测试成功删除预算"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()
        budget_id = budget.id

        response = client.delete(f'/api/budgets/{budget_id}', headers=auth_headers)
        assert response.status_code == 204

        # 验证预算已删除
        deleted_budget = Budget.query.get(budget_id)
        assert deleted_budget is None

    def test_delete_budget_not_found(self, client, auth_headers):
        """测试删除不存在的预算"""
        response = client.delete('/api/budgets/99999', headers=auth_headers)
        assert response.status_code == 404

    def test_delete_budget_permission_denied(self, client, auth_headers, test_category):
        """测试删除其他用户的预算（权限校验）"""
        from backend.models import User
        
        other_user = User(username='other', email='other@test.com')
        other_user.set_password('password')
        db.session.add(other_user)
        db.session.commit()

        other_budget = Budget(
            user_id=other_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(other_budget)
        db.session.commit()

        response = client.delete(f'/api/budgets/{other_budget.id}', headers=auth_headers)
        assert response.status_code == 403


class TestBudgetUsageCalculation:
    """测试预算使用进度计算逻辑"""

    def test_budget_spent_calculation(self, client, auth_headers, test_user, test_category):
        """测试预算已使用金额计算"""
        # 创建预算
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()

        # 创建交易记录
        transactions = [
            Transaction(
                user_id=test_user.id,
                category_id=test_category.id,
                amount=200,
                type='expense',
                date=datetime(2024, 1, 15),
                description='Test 1'
            ),
            Transaction(
                user_id=test_user.id,
                category_id=test_category.id,
                amount=300,
                type='expense',
                date=datetime(2024, 1, 20),
                description='Test 2'
            )
        ]
        for t in transactions:
            db.session.add(t)
        db.session.commit()

        # 获取预算列表
        response = client.get('/api/budgets', headers=auth_headers)
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert len(result) == 1
        assert float(result[0]['spent']) == 500.00
        assert float(result[0]['percentage']) == 50.0

    def test_budget_percentage_calculation(self, client, auth_headers, test_user, test_category):
        """测试预算使用百分比计算"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()

        # 创建超出预算的交易
        transaction = Transaction(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1200,
            type='expense',
            date=datetime(2024, 1, 15),
            description='Over budget'
        )
        db.session.add(transaction)
        db.session.commit()

        response = client.get('/api/budgets', headers=auth_headers)
        result = json.loads(response.data)
        
        assert float(result[0]['spent']) == 1200.00
        assert float(result[0]['percentage']) == 120.0

    def test_budget_only_expense_transactions(self, client, auth_headers, test_user, test_category):
        """测试预算只计算支出类型交易"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()

        # 创建支出和收入交易
        transactions = [
            Transaction(
                user_id=test_user.id,
                category_id=test_category.id,
                amount=200,
                type='expense',
                date=datetime(2024, 1, 15),
                description='Expense'
            ),
            Transaction(
                user_id=test_user.id,
                category_id=test_category.id,
                amount=500,
                type='income',
                date=datetime(2024, 1, 20),
                description='Income'
            )
        ]
        for t in transactions:
            db.session.add(t)
        db.session.commit()

        response = client.get('/api/budgets', headers=auth_headers)
        result = json.loads(response.data)
        
        # 只计算支出
        assert float(result[0]['spent']) == 200.00

    def test_budget_period_filtering(self, client, auth_headers, test_user, test_category):
        """测试预算周期内交易筛选"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()

        # 创建不同月份的交易
        transactions = [
            Transaction(
                user_id=test_user.id,
                category_id=test_category.id,
                amount=200,
                type='expense',
                date=datetime(2024, 1, 15),
                description='January'
            ),
            Transaction(
                user_id=test_user.id,
                category_id=test_category.id,
                amount=300,
                type='expense',
                date=datetime(2024, 2, 15),
                description='February'
            )
        ]
        for t in transactions:
            db.session.add(t)
        db.session.commit()

        response = client.get('/api/budgets', headers=auth_headers)
        result = json.loads(response.data)
        
        # 只计算 2024-01 的交易
        assert float(result[0]['spent']) == 200.00

    def test_budget_zero_spent(self, client, auth_headers, test_user, test_category):
        """测试预算无支出情况"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000,
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()

        response = client.get('/api/budgets', headers=auth_headers)
        result = json.loads(response.data)
        
        assert float(result[0]['spent']) == 0.00
        assert float(result[0]['percentage']) == 0.0
