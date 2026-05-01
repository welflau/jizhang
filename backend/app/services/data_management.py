import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.visit import Visit

logger = logging.getLogger(__name__)


class DataManagementService:
    """数据管理服务：负责数据的导出、导入和清空操作"""

    @staticmethod
    def export_data(db: Session) -> Dict[str, Any]:
        """
        导出所有访问记录数据
        
        Args:
            db: 数据库会话
            
        Returns:
            包含所有访问记录的字典
        """
        try:
            visits = db.query(Visit).all()
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "total_count": len(visits),
                "visits": [
                    {
                        "id": visit.id,
                        "visitor_name": visit.visitor_name,
                        "company": visit.company,
                        "phone": visit.phone,
                        "visit_purpose": visit.visit_purpose,
                        "host_name": visit.host_name,
                        "check_in_time": visit.check_in_time.isoformat() if visit.check_in_time else None,
                        "check_out_time": visit.check_out_time.isoformat() if visit.check_out_time else None,
                        "status": visit.status,
                        "notes": visit.notes,
                        "created_at": visit.created_at.isoformat() if visit.created_at else None,
                        "updated_at": visit.updated_at.isoformat() if visit.updated_at else None
                    }
                    for visit in visits
                ]
            }
            
            logger.info(f"成功导出 {len(visits)} 条访问记录")
            return export_data
            
        except Exception as e:
            logger.error(f"导出数据失败: {str(e)}")
            raise

    @staticmethod
    def import_data(db: Session, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        导入访问记录数据
        
        Args:
            db: 数据库会话
            data: 要导入的数据字典
            
        Returns:
            导入结果统计
        """
        success_count = 0
        fail_count = 0
        errors = []

        try:
            visits_data = data.get("visits", [])
            
            for visit_data in visits_data:
                try:
                    # 检查是否已存在相同ID的记录
                    existing_visit = db.query(Visit).filter(Visit.id == visit_data.get("id")).first()
                    
                    if existing_visit:
                        # 更新现有记录
                        for key, value in visit_data.items():
                            if key not in ["id", "created_at", "updated_at"]:
                                # 处理日期时间字段
                                if key in ["check_in_time", "check_out_time"] and value:
                                    value = datetime.fromisoformat(value)
                                setattr(existing_visit, key, value)
                        existing_visit.updated_at = datetime.now()
                    else:
                        # 创建新记录
                        visit = Visit(
                            visitor_name=visit_data.get("visitor_name"),
                            company=visit_data.get("company"),
                            phone=visit_data.get("phone"),
                            visit_purpose=visit_data.get("visit_purpose"),
                            host_name=visit_data.get("host_name"),
                            check_in_time=datetime.fromisoformat(visit_data["check_in_time"]) if visit_data.get("check_in_time") else None,
                            check_out_time=datetime.fromisoformat(visit_data["check_out_time"]) if visit_data.get("check_out_time") else None,
                            status=visit_data.get("status", "checked_in"),
                            notes=visit_data.get("notes")
                        )
                        db.add(visit)
                    
                    success_count += 1
                    
                except Exception as e:
                    fail_count += 1
                    error_msg = f"记录 {visit_data.get('visitor_name', 'Unknown')} 导入失败: {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
            
            db.commit()
            
            result = {
                "success_count": success_count,
                "fail_count": fail_count,
                "total_count": len(visits_data),
                "errors": errors[:10]  # 只返回前10个错误
            }
            
            logger.info(f"数据导入完成: 成功 {success_count} 条, 失败 {fail_count} 条")
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"导入数据失败: {str(e)}")
            raise

    @staticmethod
    def clear_all_data(db: Session) -> Dict[str, Any]:
        """
        清空所有访问记录数据
        
        Args:
            db: 数据库会话
            
        Returns:
            清空操作结果
        """
        try:
            # 获取删除前的记录数
            count = db.query(Visit).count()
            
            # 删除所有记录
            db.query(Visit).delete()
            db.commit()
            
            result = {
                "deleted_count": count,
                "message": f"成功清空 {count} 条访问记录"
            }
            
            logger.info(f"成功清空所有数据，共删除 {count} 条记录")
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"清空数据失败: {str(e)}")
            raise

    @staticmethod
    def validate_import_data(data: Dict[str, Any]) -> bool:
        """
        验证导入数据的格式是否正确
        
        Args:
            data: 要验证的数据字典
            
        Returns:
            验证是否通过
        """
        try:
            # 检查必需的顶层字段
            if "visits" not in data:
                logger.error("导入数据缺少 'visits' 字段")
                return False
            
            if not isinstance(data["visits"], list):
                logger.error("'visits' 字段必须是列表类型")
                return False
            
            # 检查每条记录的必需字段
            required_fields = ["visitor_name", "phone", "visit_purpose", "host_name"]
            
            for visit in data["visits"]:
                if not isinstance(visit, dict):
                    logger.error("访问记录必须是字典类型")
                    return False
                
                for field in required_fields:
                    if field not in visit:
                        logger.error(f"访问记录缺少必需字段: {field}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证导入数据时出错: {str(e)}")
            return False