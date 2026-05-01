import pytest
import json
from datetime import datetime
from app import app, db, Visit

@pytest.fixture
def client():
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
    """创建测试数据"""
    with app.app_context():
        visits = [
            Visit(
                ip='192.168.1.1',
                user_agent='Mozilla/5.0',
                referer='https://google.com',
                timestamp=datetime(2024, 1, 1, 10, 0, 0)
            ),
            Visit(
                ip='192.168.1.2',
                user_agent='Chrome/90.0',
                referer='https://bing.com',
                timestamp=datetime(2024, 1, 2, 11, 0, 0)
            ),
            Visit(
                ip='192.168.1.3',
                user_agent='Safari/14.0',
                referer=None,
                timestamp=datetime(2024, 1, 3, 12, 0, 0)
            )
        ]
        for visit in visits:
            db.session.add(visit)
        db.session.commit()
        return visits

class TestExportAPI:
    """测试导出功能"""
    
    def test_export_empty_database(self, client):
        """测试导出空数据库"""
        response = client.get('/api/export')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert 'export_time' in data
        assert 'total_count' in data
        assert data['total_count'] == 0
        assert data['visits'] == []
    
    def test_export_with_data(self, client, sample_visits):
        """测试导出包含数据的数据库"""
        response = client.get('/api/export')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total_count'] == 3
        assert len(data['visits']) == 3
        
        # 验证数据结构
        visit = data['visits'][0]
        assert 'ip' in visit
        assert 'user_agent' in visit
        assert 'referer' in visit
        assert 'timestamp' in visit
    
    def test_export_response_headers(self, client, sample_visits):
        """测试导出响应头"""
        response = client.get('/api/export')
        assert response.headers['Content-Type'] == 'application/json'
        assert 'Content-Disposition' in response.headers
        assert 'visits_backup_' in response.headers['Content-Disposition']
        assert '.json' in response.headers['Content-Disposition']

class TestImportAPI:
    """测试导入功能"""
    
    def test_import_valid_data(self, client):
        """测试导入有效数据"""
        import_data = {
            'visits': [
                {
                    'ip': '10.0.0.1',
                    'user_agent': 'TestAgent',
                    'referer': 'https://test.com',
                    'timestamp': '2024-01-01T10:00:00'
                },
                {
                    'ip': '10.0.0.2',
                    'user_agent': 'TestAgent2',
                    'referer': None,
                    'timestamp': '2024-01-02T11:00:00'
                }
            ]
        }
        
        response = client.post('/api/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] == 2
        assert result['failed'] == 0
        assert result['total'] == 2
        
        # 验证数据已导入
        with app.app_context():
            count = Visit.query.count()
            assert count == 2
    
    def test_import_empty_data(self, client):
        """测试导入空数据"""
        import_data = {'visits': []}
        
        response = client.post('/api/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] == 0
        assert result['total'] == 0
    
    def test_import_invalid_json(self, client):
        """测试导入无效JSON"""
        response = client.post('/api/import',
                              data='invalid json',
                              content_type='application/json')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_import_missing_visits_key(self, client):
        """测试缺少visits键"""
        import_data = {'data': []}
        
        response = client.post('/api/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_import_partial_failure(self, client):
        """测试部分数据导入失败"""
        import_data = {
            'visits': [
                {
                    'ip': '10.0.0.1',
                    'user_agent': 'TestAgent',
                    'referer': 'https://test.com',
                    'timestamp': '2024-01-01T10:00:00'
                },
                {
                    'ip': '10.0.0.2',
                    # 缺少必需字段
                    'timestamp': 'invalid-date'
                }
            ]
        }
        
        response = client.post('/api/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['total'] == 2
        assert result['success'] >= 0
        assert result['failed'] >= 0
    
    def test_import_duplicate_data(self, client, sample_visits):
        """测试导入重复数据"""
        # 导出现有数据
        export_response = client.get('/api/export')
        export_data = json.loads(export_response.data)
        
        # 重新导入相同数据
        import_data = {'visits': export_data['visits']}
        response = client.post('/api/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # 验证数据已导入（允许重复）
        with app.app_context():
            count = Visit.query.count()
            assert count == 6  # 原有3条 + 新导入3条

class TestClearAPI:
    """测试清空功能"""
    
    def test_clear_empty_database(self, client):
        """测试清空空数据库"""
        response = client.post('/api/clear')
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['deleted'] == 0
        assert result['message'] == 'All data cleared successfully'
    
    def test_clear_with_data(self, client, sample_visits):
        """测试清空包含数据的数据库"""
        # 确认数据存在
        with app.app_context():
            count_before = Visit.query.count()
            assert count_before == 3
        
        response = client.post('/api/clear')
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['deleted'] == 3
        
        # 确认数据已清空
        with app.app_context():
            count_after = Visit.query.count()
            assert count_after == 0
    
    def test_clear_idempotent(self, client, sample_visits):
        """测试清空操作的幂等性"""
        # 第一次清空
        response1 = client.post('/api/clear')
        assert response1.status_code == 200
        result1 = json.loads(response1.data)
        assert result1['deleted'] == 3
        
        # 第二次清空
        response2 = client.post('/api/clear')
        assert response2.status_code == 200
        result2 = json.loads(response2.data)
        assert result2['deleted'] == 0

class TestDataManagementWorkflow:
    """测试完整的数据管理工作流"""
    
    def test_export_import_workflow(self, client, sample_visits):
        """测试导出-导入工作流"""
        # 1. 导出数据
        export_response = client.get('/api/export')
        export_data = json.loads(export_response.data)
        assert export_data['total_count'] == 3
        
        # 2. 清空数据
        clear_response = client.post('/api/clear')
        assert json.loads(clear_response.data)['deleted'] == 3
        
        # 3. 导入数据
        import_data = {'visits': export_data['visits']}
        import_response = client.post('/api/import',
                                     data=json.dumps(import_data),
                                     content_type='application/json')
        import_result = json.loads(import_response.data)
        assert import_result['success'] == 3
        
        # 4. 验证数据恢复
        with app.app_context():
            count = Visit.query.count()
            assert count == 3
    
    def test_backup_restore_data_integrity(self, client, sample_visits):
        """测试备份恢复的数据完整性"""
        # 导出数据
        export_response = client.get('/api/export')
        export_data = json.loads(export_response.data)
        
        # 清空并重新导入
        client.post('/api/clear')
        import_data = {'visits': export_data['visits']}
        client.post('/api/import',
                   data=json.dumps(import_data),
                   content_type='application/json')
        
        # 验证数据一致性
        with app.app_context():
            visits = Visit.query.order_by(Visit.timestamp).all()
            assert len(visits) == 3
            assert visits[0].ip == '192.168.1.1'
            assert visits[1].ip == '192.168.1.2'
            assert visits[2].ip == '192.168.1.3'

class TestUIIntegration:
    """测试UI集成相关功能"""
    
    def test_export_filename_format(self, client):
        """测试导出文件名格式"""
        response = client.get('/api/export')
        content_disposition = response.headers.get('Content-Disposition')
        
        assert 'attachment' in content_disposition
        assert 'visits_backup_' in content_disposition
        assert '.json' in content_disposition
        
        # 验证时间戳格式 (YYYYMMDD_HHMMSS)
        import re
        pattern = r'visits_backup_\d{8}_\d{6}\.json'
        assert re.search(pattern, content_disposition)
    
    def test_import_result_format(self, client):
        """测试导入结果格式（用于UI显示）"""
        import_data = {
            'visits': [
                {
                    'ip': '10.0.0.1',
                    'user_agent': 'Test',
                    'referer': None,
                    'timestamp': '2024-01-01T10:00:00'
                }
            ]
        }
        
        response = client.post('/api/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        
        result = json.loads(response.data)
        
        # 验证返回格式适合UI显示
        assert 'success' in result
        assert 'failed' in result
        assert 'total' in result
        assert isinstance(result['success'], int)
        assert isinstance(result['failed'], int)
        assert isinstance(result['total'], int)
