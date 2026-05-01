from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Transaction, Category, User
from sqlalchemy import and_, or_

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/api/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    """创建收支记录"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # 参数验证
        required_fields = ['amount', 'type', 'category_id', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        # 验证金额
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': '金额必须大于0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': '金额格式不正确'}), 400

        # 验证类型
        if data['type'] not in ['income', 'expense']:
            return jsonify({'error': '类型必须是 income 或 expense'}), 400

        # 验证分类是否存在且属于当前用户
        category = Category.query.filter_by(
            id=data['category_id'],
            user_id=current_user_id
        ).first()
        if not category:
            return jsonify({'error': '分类不存在或无权访问'}), 404

        # 验证分类类型与交易类型是否匹配
        if category.type != data['type']:
            return jsonify({'error': '分类类型与交易类型不匹配'}), 400

        # 验证日期格式
        try:
            transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式不正确，应为 YYYY-MM-DD'}), 400

        # 创建交易记录
        transaction = Transaction(
            user_id=current_user_id,
            amount=amount,
            type=data['type'],
            category_id=data['category_id'],
            date=transaction_date,
            description=data.get('description', '').strip()
        )

        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'message': '记录创建成功',
            'transaction': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'type': transaction.type,
                'category_id': transaction.category_id,
                'category_name': category.name,
                'date': transaction.date.strftime('%Y-%m-%d'),
                'description': transaction.description,
                'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建记录失败: {str(e)}'}), 500


@transactions_bp.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """获取收支记录列表（支持分页和筛选）"""
    try:
        current_user_id = get_jwt_identity()

        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        transaction_type = request.args.get('type', None)
        category_id = request.args.get('category_id', None, type=int)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        search = request.args.get('search', None)

        # 参数验证
        if page < 1:
            return jsonify({'error': '页码必须大于0'}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({'error': '每页数量必须在1-100之间'}), 400

        # 构建查询
        query = Transaction.query.filter_by(user_id=current_user_id)

        # 类型筛选
        if transaction_type:
            if transaction_type not in ['income', 'expense']:
                return jsonify({'error': '类型参数无效'}), 400
            query = query.filter_by(type=transaction_type)

        # 分类筛选
        if category_id:
            # 验证分类是否属于当前用户
            category = Category.query.filter_by(
                id=category_id,
                user_id=current_user_id
            ).first()
            if not category:
                return jsonify({'error': '分类不存在或无权访问'}), 404
            query = query.filter_by(category_id=category_id)

        # 日期范围筛选
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Transaction.date >= start)
            except ValueError:
                return jsonify({'error': '开始日期格式不正确'}), 400

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Transaction.date <= end)
            except ValueError:
                return jsonify({'error': '结束日期格式不正确'}), 400

        # 关键词搜索（描述）
        if search:
            search_term = f'%{search.strip()}%'
            query = query.filter(Transaction.description.like(search_term))

        # 按日期降序排序
        query = query.order_by(Transaction.date.desc(), Transaction.created_at.desc())

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # 构建返回数据
        transactions = []
        for transaction in pagination.items:
            category = Category.query.get(transaction.category_id)
            transactions.append({
                'id': transaction.id,
                'amount': float(transaction.amount),
                'type': transaction.type,
                'category_id': transaction.category_id,
                'category_name': category.name if category else '未知分类',
                'date': transaction.date.strftime('%Y-%m-%d'),
                'description': transaction.description,
                'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify({
            'transactions': transactions,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'获取记录失败: {str(e)}'}), 500


@transactions_bp.route('/api/transactions/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    """获取单条记录详情"""
    try:
        current_user_id = get_jwt_identity()

        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=current_user_id
        ).first()

        if not transaction:
            return jsonify({'error': '记录不存在或无权访问'}), 404

        category = Category.query.get(transaction.category_id)

        return jsonify({
            'transaction': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'type': transaction.type,
                'category_id': transaction.category_id,
                'category_name': category.name if category else '未知分类',
                'date': transaction.date.strftime('%Y-%m-%d'),
                'description': transaction.description,
                'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': transaction.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'获取记录失败: {str(e)}'}), 500


@transactions_bp.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    """更新收支记录"""
    try:
        current_user_id = get_jwt_identity()

        # 查询记录并验证权限
        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=current_user_id
        ).first()

        if not transaction:
            return jsonify({'error': '记录不存在或无权访问'}), 404

        data = request.get_json()

        # 更新金额
        if 'amount' in data:
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    return jsonify({'error': '金额必须大于0'}), 400
                transaction.amount = amount
            except (ValueError, TypeError):
                return jsonify({'error': '金额格式不正确'}), 400

        # 更新类型
        if 'type' in data:
            if data['type'] not in ['income', 'expense']:
                return jsonify({'error': '类型必须是 income 或 expense'}), 400
            transaction.type = data['type']

        # 更新分类
        if 'category_id' in data:
            category = Category.query.filter_by(
                id=data['category_id'],
                user_id=current_user_id
            ).first()
            if not category:
                return jsonify({'error': '分类不存在或无权访问'}), 404

            # 验证分类类型与交易类型是否匹配
            transaction_type = data.get('type', transaction.type)
            if category.type != transaction_type:
                return jsonify({'error': '分类类型与交易类型不匹配'}), 400

            transaction.category_id = data['category_id']

        # 更新日期
        if 'date' in data:
            try:
                transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '日期格式不正确，应为 YYYY-MM-DD'}), 400

        # 更新描述
        if 'description' in data:
            transaction.description = data['description'].strip()

        transaction.updated_at = datetime.utcnow()
        db.session.commit()

        category = Category.query.get(transaction.category_id)

        return jsonify({
            'message': '记录更新成功',
            'transaction': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'type': transaction.type,
                'category_id': transaction.category_id,
                'category_name': category.name if category else '未知分类',
                'date': transaction.date.strftime('%Y-%m-%d'),
                'description': transaction.description,
                'updated_at': transaction.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新记录失败: {str(e)}'}), 500


@transactions_bp.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    """删除收支记录"""
    try:
        current_user_id = get_jwt_identity()

        # 查询记录并验证权限
        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=current_user_id
        ).first()

        if not transaction:
            return jsonify({'error': '记录不存在或无权访问'}), 404

        db.session.delete(transaction)
        db.session.commit()

        return jsonify({'message': '记录删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除记录失败: {str(e)}'}), 500


@transactions_bp.route('/api/transactions/batch', methods=['DELETE'])
@jwt_required()
def batch_delete_transactions():
    """批量删除收支记录"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if 'ids' not in data or not isinstance(data['ids'], list):
            return jsonify({'error': '请提供要删除的记录ID列表'}), 400

        if not data['ids']:
            return jsonify({'error': '删除列表不能为空'}), 400

        # 查询并验证所有记录
        transactions = Transaction.query.filter(
            and_(
                Transaction.id.in_(data['ids']),
                Transaction.user_id == current_user_id
            )
        ).all()

        if len(transactions) != len(data['ids']):
            return jsonify({'error': '部分记录不存在或无权访问'}), 404

        # 批量删除
        for transaction in transactions:
            db.session.delete(transaction)

        db.session.commit()

        return jsonify({
            'message': f'成功删除 {len(transactions)} 条记录'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'批量删除失败: {str(e)}'}), 500
