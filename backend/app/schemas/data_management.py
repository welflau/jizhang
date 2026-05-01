from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class VisitRecordExport(BaseModel):
    """导出的访问记录模型"""
    id: int
    visitor_name: str
    company: Optional[str] = None
    phone: str
    id_card: Optional[str] = None
    visit_purpose: str
    host_name: str
    host_department: Optional[str] = None
    visit_time: datetime
    leave_time: Optional[datetime] = None
    status: str
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExportData(BaseModel):
    """导出数据结构"""
    export_time: datetime = Field(default_factory=datetime.now, description="导出时间")
    total_records: int = Field(description="总记录数")
    records: List[VisitRecordExport] = Field(description="访问记录列表")


class ImportResult(BaseModel):
    """导入结果"""
    success: bool = Field(description="是否成功")
    total_records: int = Field(description="总记录数")
    success_count: int = Field(description="成功导入数")
    failed_count: int = Field(description="失败数")
    error_messages: List[str] = Field(default_factory=list, description="错误信息列表")


class ClearDataResult(BaseModel):
    """清空数据结果"""
    success: bool = Field(description="是否成功")
    deleted_count: int = Field(description="删除的记录数")
    message: str = Field(description="结果消息")