import pytest
import json
import io
from datetime import datetime
from flask import Flask
from app import app, db, Visit


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def sample_visits(client):
    """创建示例访问记录"""
    with app.app_context():
        visits = [
            Visit(
                ip_address='192.168.1.1',
                user_agent='Mozilla/5.0 Test Browser 1',
                timestamp=datetime(2024, 1, 1, 10, 0, 0)
            ),
            Visit(
                ip_address='192.168.1.2',
                user_agent='Mozilla/5.0 Test Browser 2',
                timestamp=datetime(2024, 1, 2, 11, 0, 0)
            ),
            Visit(
                ip_address='192.168.1.3',
                user_agent='Mozilla/5.0 Test Browser 3',
                timestamp=datetime(2024, 1, 3, 12, 0, 0)
            )
        ]
        for visit in visits:
            db.session.add(visit)
        db.session.commit()
        return visits


class TestDataExport:
    """测试数据导出功能"""
    
    def test_export_empty_database(self, client):
        """测试导出空数据库"""
        response = client.get('/api/export')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert 'visits' in data
        assert len(data['visits']) == 0
        assert 'export_time' in data
        assert 'total_count' in data
        assert data['total_count'] == 0
    
    def test_export_with_data(self, client, sample_visits):
        """测试导出包含数据的数据库"""
        response = client.get('/api/export')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total_count'] == 3
        assert len(data['visits']) == 3
        
        # 验证导出的数据结构
        for visit_data in data['visits']:
            assert 'ip_address' in visit_data
            assert 'user_agent' in visit_data
            assert 'timestamp' in visit_data
    
    def test_export_filename_format(self, client, sample_visits):
        """测试导出文件名格式"""
        response = client.get('/api/export')
        content_disposition = response.headers.get('Content-Disposition')
        
        assert content_disposition is not None
        assert 'attachment' in content_disposition
        assert 'visits_backup_' in content_disposition
        assert '.json' in content_disposition


class TestDataImport:
    """测试数据导入功能"""
    
    def test_import_valid_data(self, client):
        """测试导入有效数据"""
        import_data = {
            'visits': [
                {
                    'ip_address': '10.0.0.1',
                    'user_agent': 'Test Agent 1',
                    'timestamp': '2024-01-01T10:00:00'
                },
                {
                    'ip_address': '10.0.0.2',
                    'user_agent': 'Test Agent 2',
                    'timestamp': '2024-01-02T11:00:00'
                }
            ]
        }
        
        data = io.BytesIO(json.dumps(import_data).encode('utf-8'))
        response = client.post(
            '/api/import',
            data={'file': (data, 'backup.json')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] == 2
        assert result['failed'] == 0
        
        # 验证数据已导入
        with app.app_context():
            visits = Visit.query.all()
            assert len(visits) == 2
    
    def test_import_no_file(self, client):
        """测试未上传文件"""
        response = client.post('/api/import')
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_import_invalid_json(self, client):
        """测试导入无效的JSON文件"""
        data = io.BytesIO(b'invalid json content')
        response = client.post(
            '/api/import',
            data={'file': (data, 'invalid.json')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_import_missing_visits_key(self, client):
        """测试导入缺少visits键的数据"""
        import_data = {'other_key': []}
        data = io.BytesIO(json.dumps(import_data).encode('utf-8'))
        
        response = client.post(
            '/api/import',
            data={'file': (data, 'backup.json')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_import_partial_success(self, client):
        """测试部分数据导入成功"""
        import_data = {
            'visits': [
                {
                    'ip_address': '10.0.0.1',
                    'user_agent': 'Valid Agent',
                    'timestamp': '2024-01-01T10:00:00'
                },
                {
                    'ip_address': '10.0.0.2',
                    # 缺少必需字段
                    'timestamp': '2024-01-02T11:00:00'
                }
            ]
        }
        
        data = io.BytesIO(json.dumps(import_data).encode('utf-8'))
        response = client.post(
            '/api/import',
            data={'file': (data, 'backup.json')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] >= 0
        assert result['failed'] >= 0
        assert result['success'] + result['failed'] == 2


class TestDataClear:
    """测试数据清空功能"""
    
    def test_clear_empty_database(self, client):
        """测试清空空数据库"""
        response = client.post('/api/clear')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['deleted_count'] == 0
    
    def test_clear_with_data(self, client, sample_visits):
        """测试清空包含数据的数据库"""
        response = client.post('/api/clear')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['deleted_count'] == 3
        
        # 验证数据已清空
        with app.app_context():
            visits = Visit.query.all()
            assert len(visits) == 0
    
    def test_clear_method_not_allowed(self, client):
        """测试不允许的HTTP方法"""
        response = client.get('/api/clear')
        assert response.status_code == 405


class TestDataManagementFlow:
    """测试完整的数据管理流程"""
    
    def test_export_import_restore_flow(self, client, sample_visits):
        """测试导出-导入-恢复流程"""
        # 1. 导出数据
        export_response = client.get('/api/export')
        assert export_response.status_code == 200
        exported_data = json.loads(export_response.data)
        assert exported_data['total_count'] == 3
        
        # 2. 清空数据
        clear_response = client.post('/api/clear')
        assert clear_response.status_code == 200
        
        with app.app_context():
            assert Visit.query.count() == 0
        
        # 3. 导入数据
        data = io.BytesIO(json.dumps(exported_data).encode('utf-8'))
        import_response = client.post(
            '/api/import',
            data={'file': (data, 'backup.json')},
            content_type='multipart/form-data'
        )
        assert import_response.status_code == 200
        
        # 4. 验证恢复的数据
        with app.app_context():
            restored_visits = Visit.query.all()
            assert len(restored_visits) == 3
    
    def test_multiple_import_accumulation(self, client):
        """测试多次导入数据累积"""
        import_data = {
            'visits': [
                {
                    'ip_address': '10.0.0.1',
                    'user_agent': 'Agent 1',
                    'timestamp': '2024-01-01T10:00:00'
                }
            ]
        }
        
        # 第一次导入
        data1 = io.BytesIO(json.dumps(import_data).encode('utf-8'))
        client.post(
            '/api/import',
            data={'file': (data1, 'backup1.json')},
            content_type='multipart/form-data'
        )
        
        # 第二次导入
        data2 = io.BytesIO(json.dumps(import_data).encode('utf-8'))
        client.post(
            '/api/import',
            data={'file': (data2, 'backup2.json')},
            content_type='multipart/form-data'
        )
        
        # 验证数据累积
        with app.app_context():
            visits = Visit.query.all()
            assert len(visits) == 2
    
    def test_clear_and_verify_empty(self, client, sample_visits):
        """测试清空后验证数据库为空"""
        # 清空数据
        client.post('/api/clear')
        
        # 导出验证
        export_response = client.get('/api/export')
        exported_data = json.loads(export_response.data)
        assert exported_data['total_count'] == 0
        assert len(exported_data['visits']) == 0


class TestUIIntegration:
    """测试UI集成相关功能"""
    
    def test_export_button_functionality(self, client, sample_visits):
        """测试导出按钮功能"""
        response = client.get('/api/export')
        
        # 验证响应头适合浏览器下载
        assert response.headers.get('Content-Type') == 'application/json'
        assert 'attachment' in response.headers.get('Content-Disposition', '')
    
    def test_import_result_format(self, client):
        """测试导入结果格式（用于UI显示）"""
        import_data = {
            'visits': [
                {
                    'ip_address': '10.0.0.1',
                    'user_agent': 'Test Agent',
                    'timestamp': '2024-01-01T10:00:00'
                }
            ]
        }
        
        data = io.BytesIO(json.dumps(import_data).encode('utf-8'))
        response = client.post(
            '/api/import',
            data={'file': (data, 'backup.json')},
            content_type='multipart/form-data'
        )
        
        result = json.loads(response.data)
        # 验证返回格式适合UI显示
        assert 'success' in result
        assert 'failed' in result
        assert isinstance(result['success'], int)
        assert isinstance(result['failed'], int)
    
    def test_clear_confirmation_required(self, client, sample_visits):
        """测试清空操作（UI应显示确认对话框）"""
        # 这个测试验证API端点存在且工作正常
        # 实际的确认对话框由前端JavaScript处理
        response = client.post('/api/clear')
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert 'deleted_count' in result
        assert result['deleted_count'] == 3
