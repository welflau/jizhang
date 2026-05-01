import pytest
from datetime import datetime
from decimal import Decimal
from flask import json
from backend.models import Budget, Transaction, Category
from backend.extensions import db


class TestBudgetCRUD:
    """测试预算 CRUD 操作"""

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
        json_data = response.get_json()
        assert json_data['category_id'] == test_category.id
        assert json_data['amount'] == '1000.00'
        assert json_data['period'] == '2024-01'
        assert json_data['spent'] == '0.00'
        assert json_data['percentage'] == 0.0
        
        # 验证数据库中已创建
        budget = Budget.query.filter_by(user_id=test_user.id, period='2024-01').first()
        assert budget is not None
        assert budget.amount == Decimal('1000.00')

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
        assert 'amount' in response.get_json()['message'].lower()
        
        # 测试负数金额
        data['amount'] = -100
        response = client.post('/api/budgets',
                              headers=auth_headers,
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400

    def test_create_budget_invalid_period(self, client, auth_headers, test_category):
        """测试创建预算时周期格式无效"""
        invalid_periods = ['2024', '202401', '2024-1', '2024-13', 'invalid']
        
        for period in invalid_periods:
            data = {
                'category_id': test_category.id,
                'amount': 1000,
                'period': period
            }
            response = client.post('/api/budgets',
                                  headers=auth_headers,
                                  data=json.dumps(data),
                                  content_type='application/json')
            assert response.status_code == 400
            assert 'period' in response.get_json()['message'].lower()

    def test_create_budget_missing_fields(self, client, auth_headers):
        """测试创建预算时缺少必填字段"""
        data = {'amount': 1000}
        response = client.post('/api/budgets',
                              headers=auth_headers,
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400

    def test_create_budget_duplicate(self, client, auth_headers, test_user, test_category):
        """测试创建重复预算（同一用户、分类、周期）"""
        # 创建第一个预算
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()
        
        # 尝试创建重复预算
        data = {
            'category_id': test_category.id,
            'amount': 2000,
            'period': '2024-01'
        }
        response = client.post('/api/budgets',
                              headers=auth_headers,
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['message'].lower()

    def test_create_budget_unauthorized(self, client, test_category):
        """测试未授权创建预算"""
        data = {
            'category_id': test_category.id,
            'amount': 1000,
            'period': '2024-01'
        }
        response = client.post('/api/budgets',
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 401


class TestGetBudgets:
    """测试获取预算列表"""

    def test_get_budgets_empty(self, client, auth_headers):
        """测试获取空预算列表"""
        response = client.get('/api/budgets', headers=auth_headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data == []

    def test_get_budgets_list(self, client, auth_headers, test_user, test_category):
        """测试获取预算列表"""
        # 创建多个预算
        budgets_data = [
            {'period': '2024-01', 'amount': Decimal('1000.00')},
            {'period': '2024-02', 'amount': Decimal('1500.00')},
            {'period': '2024-03', 'amount': Decimal('2000.00')}
        ]
        
        for budget_data in budgets_data:
            budget = Budget(
                user_id=test_user.id,
                category_id=test_category.id,
                **budget_data
            )
            db.session.add(budget)
        db.session.commit()
        
        response = client.get('/api/budgets', headers=auth_headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 3

    def test_get_budgets_filter_by_period(self, client, auth_headers, test_user, test_category):
        """测试按周期筛选预算"""
        # 创建不同周期的预算
        budgets_data = [
            {'period': '2024-01', 'amount': Decimal('1000.00')},
            {'period': '2024-02', 'amount': Decimal('1500.00')},
            {'period': '2024-03', 'amount': Decimal('2000.00')}
        ]
        
        for budget_data in budgets_data:
            budget = Budget(
                user_id=test_user.id,
                category_id=test_category.id,
                **budget_data
            )
            db.session.add(budget)
        db.session.commit()
        
        # 筛选特定周期
        response = client.get('/api/budgets?period=2024-02', headers=auth_headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 1
        assert json_data[0]['period'] == '2024-02'

    def test_get_budgets_with_spent_calculation(self, client, auth_headers, test_user, test_category):
        """测试预算使用进度计算"""
        # 创建预算
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()
        
        # 创建交易记录
        transactions_data = [
            {'amount': Decimal('300.00'), 'date': datetime(2024, 1, 5)},
            {'amount': Decimal('200.00'), 'date': datetime(2024, 1, 15)},
            {'amount': Decimal('150.00'), 'date': datetime(2024, 1, 25)}
        ]
        
        for trans_data in transactions_data:
            transaction = Transaction(
                user_id=test_user.id,
                category_id=test_category.id,
                type='expense',
                description='Test expense',
                **trans_data
            )
            db.session.add(transaction)
        db.session.commit()
        
        response = client.get('/api/budgets?period=2024-01', headers=auth_headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 1
        assert json_data[0]['spent'] == '650.00'
        assert json_data[0]['percentage'] == 65.0
        assert json_data[0]['remaining'] == '350.00'

    def test_get_budgets_only_own_budgets(self, client, auth_headers, test_user, test_category):
        """测试只能获取自己的预算"""
        from backend.models import User
        
        # 创建另一个用户和预算
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        other_budget = Budget(
            user_id=other_user.id,
            category_id=test_category.id,
            amount=Decimal('5000.00'),
            period='2024-01'
        )
        db.session.add(other_budget)
        
        # 创建当前用户的预算
        my_budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(my_budget)
        db.session.commit()
        
        response = client.get('/api/budgets', headers=auth_headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 1
        assert json_data[0]['amount'] == '1000.00'

    def test_get_budgets_unauthorized(self, client):
        """测试未授权获取预算列表"""
        response = client.get('/api/budgets')
        assert response.status_code == 401


class TestUpdateBudget:
    """测试更新预算"""

    def test_update_budget_success(self, client, auth_headers, test_user, test_category):
        """测试成功更新预算"""
        # 创建预算
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()
        
        # 更新预算
        data = {'amount': 1500.00}
        response = client.put(f'/api/budgets/{budget.id}',
                             headers=auth_headers,
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['amount'] == '1500.00'
        
        # 验证数据库已更新
        db.session.refresh(budget)
        assert budget.amount == Decimal('1500.00')

    def test_update_budget_invalid_amount(self, client, auth_headers, test_user, test_category):
        """测试更新预算时金额无效"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()
        
        # 测试金额为 0
        data = {'amount': 0}
        response = client.put(f'/api/budgets/{budget.id}',
                             headers=auth_headers,
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 400

    def test_update_budget_not_found(self, client, auth_headers):
        """测试更新不存在的预算"""
        data = {'amount': 1500}
        response = client.put('/api/budgets/99999',
                             headers=auth_headers,
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 404

    def test_update_budget_permission_denied(self, client, auth_headers, test_category):
        """测试更新其他用户的预算"""
        from backend.models import User
        
        # 创建另一个用户和预算
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        other_budget = Budget(
            user_id=other_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(other_budget)
        db.session.commit()
        
        # 尝试更新其他用户的预算
        data = {'amount': 2000}
        response = client.put(f'/api/budgets/{other_budget.id}',
                             headers=auth_headers,
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 403

    def test_update_budget_unauthorized(self, client, test_user, test_category):
        """测试未授权更新预算"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()
        
        data = {'amount': 1500}
        response = client.put(f'/api/budgets/{budget.id}',
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code == 401


class TestDeleteBudget:
    """测试删除预算"""

    def test_delete_budget_success(self, client, auth_headers, test_user, test_category):
        """测试成功删除预算"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()
        budget_id = budget.id
        
        response = client.delete(f'/api/budgets/{budget_id}', headers=auth_headers)
        assert response.status_code == 200
        
        # 验证数据库中已删除
        deleted_budget = Budget.query.get(budget_id)
        assert deleted_budget is None

    def test_delete_budget_not_found(self, client, auth_headers):
        """测试删除不存在的预算"""
        response = client.delete('/api/budgets/99999', headers=auth_headers)
        assert response.status_code == 404

    def test_delete_budget_permission_denied(self, client, auth_headers, test_category):
        """测试删除其他用户的预算"""
        from backend.models import User
        
        # 创建另一个用户和预算
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        other_budget = Budget(
            user_id=other_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(other_budget)
        db.session.commit()
        
        # 尝试删除其他用户的预算
        response = client.delete(f'/api/budgets/{other_budget.id}', headers=auth_headers)
        assert response.status_code == 403

    def test_delete_budget_unauthorized(self, client, test_user, test_category):
        """测试未授权删除预算"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()
        
        response = client.delete(f'/api/budgets/{budget.id}')
        assert response.status_code == 401


class TestBudgetProgress:
    """测试预算进度计算"""

    def test_budget_progress_no_transactions(self, client, auth_headers, test_user, test_category):
        """测试无交易时的预算进度"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        db.session.commit()
        
        response = client.get('/api/budgets?period=2024-01', headers=auth_headers)
        json_data = response.get_json()
        assert json_data[0]['spent'] == '0.00'
        assert json_data[0]['percentage'] == 0.0
        assert json_data[0]['remaining'] == '1000.00'

    def test_budget_progress_with_transactions(self, client, auth_headers, test_user, test_category):
        """测试有交易时的预算进度"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        
        # 添加支出交易
        transaction = Transaction(
            user_id=test_user.id,
            category_id=test_category.id,
            type='expense',
            amount=Decimal('750.00'),
            date=datetime(2024, 1, 15),
            description='Test expense'
        )
        db.session.add(transaction)
        db.session.commit()
        
        response = client.get('/api/budgets?period=2024-01', headers=auth_headers)
        json_data = response.get_json()
        assert json_data[0]['spent'] == '750.00'
        assert json_data[0]['percentage'] == 75.0
        assert json_data[0]['remaining'] == '250.00'

    def test_budget_progress_over_budget(self, client, auth_headers, test_user, test_category):
        """测试超出预算的情况"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        
        # 添加超出预算的支出
        transaction = Transaction(
            user_id=test_user.id,
            category_id=test_category.id,
            type='expense',
            amount=Decimal('1200.00'),
            date=datetime(2024, 1, 15),
            description='Test expense'
        )
        db.session.add(transaction)
        db.session.commit()
        
        response = client.get('/api/budgets?period=2024-01', headers=auth_headers)
        json_data = response.get_json()
        assert json_data[0]['spent'] == '1200.00'
        assert json_data[0]['percentage'] == 120.0
        assert json_data[0]['remaining'] == '-200.00'

    def test_budget_progress_only_period_transactions(self, client, auth_headers, test_user, test_category):
        """测试只计算当前周期的交易"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=Decimal('1000.00'),
            period='2024-01'
        )
        db.session.add(budget)
        
        # 添加当前周期的交易
        transaction1 = Transaction(
            user_id=test_user.id,
            category_id=test_category.id,
            type='expense',
            amount=Decimal('300.00'),
            date=datetime(2024, 1, 15),
            description='January expense'
        )
        db.session.add(transaction1)
        
        # 添加其他周期的交易（不应计入）
        transaction2 = Transaction(
            user_id=test_user.id,
            category_id=test_category.id,
            type='expense',
            amount=Decimal('500.00'),
            date=datetime(2024, 2, 15),
            description='February expense'
        )
        db.session.add(transaction2)
        db.session.commit()
        
        response = client.get('/api/budgets?period=2024-01', headers=auth_headers)
        json_data = response.get_json()
        assert json_data[0]['spent'] == '300.00'
        assert json_data[0]['percentage'] == 30.0
