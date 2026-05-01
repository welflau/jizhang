from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
import io
from datetime import datetime

from app.api import deps
from app.models.visit import Visit
from app.schemas.visit import VisitCreate

router = APIRouter()


@router.get("/export")
def export_data(db: Session = deps.Depends(deps.get_db)):
    """
    导出所有访问记录为 JSON 文件
    """
    try:
        visits = db.query(Visit).all()
        
        data = []
        for visit in visits:
            data.append({
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
            })
        
        # 生成文件名
        filename = f"visits_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 创建 JSON 内容
        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        
        # 创建流式响应
        return StreamingResponse(
            io.BytesIO(json_content.encode('utf-8')),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    db: Session = deps.Depends(deps.get_db)
):
    """
    从 JSON 文件导入访问记录
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="只支持 JSON 文件格式")
    
    try:
        # 读取文件内容
        content = await file.read()
        data = json.loads(content.decode('utf-8'))
        
        if not isinstance(data, list):
            raise HTTPException(status_code=400, detail="JSON 文件格式错误，应为数组格式")
        
        success_count = 0
        fail_count = 0
        errors = []
        
        for item in data:
            try:
                # 检查必填字段
                if not item.get('visitor_name'):
                    fail_count += 1
                    errors.append(f"记录缺少访客姓名: {item}")
                    continue
                
                # 检查是否已存在（根据 ID 或关键信息）
                existing = None
                if item.get('id'):
                    existing = db.query(Visit).filter(Visit.id == item['id']).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in item.items():
                        if key not in ['id', 'created_at', 'updated_at'] and hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # 创建新记录
                    visit_data = {
                        "visitor_name": item.get('visitor_name'),
                        "company": item.get('company'),
                        "phone": item.get('phone'),
                        "visit_purpose": item.get('visit_purpose'),
                        "host_name": item.get('host_name'),
                        "check_in_time": item.get('check_in_time'),
                        "check_out_time": item.get('check_out_time'),
                        "status": item.get('status', 'pending'),
                        "notes": item.get('notes')
                    }
                    new_visit = Visit(**visit_data)
                    db.add(new_visit)
                
                success_count += 1
            except Exception as e:
                fail_count += 1
                errors.append(f"导入记录失败: {str(e)}")
        
        db.commit()
        
        return {
            "success": True,
            "message": f"导入完成",
            "success_count": success_count,
            "fail_count": fail_count,
            "errors": errors[:10]  # 只返回前10条错误信息
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON 文件格式错误")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.delete("/clear")
def clear_all_data(db: Session = deps.Depends(deps.get_db)):
    """
    清空所有访问记录
    """
    try:
        count = db.query(Visit).count()
        db.query(Visit).delete()
        db.commit()
        
        return {
            "success": True,
            "message": f"已清空所有数据",
            "deleted_count": count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"清空数据失败: {str(e)}")