#!/usr/bin/env python3
"""
API Documentation Generator for Statistics Data Aggregation
生成统计数据聚合 API 文档
"""

import json
from datetime import datetime
from typing import Dict, Any


class APIDocGenerator:
    """API 文档生成器"""

    def __init__(self):
        self.api_version = "v1"
        self.base_url = "/api/v1/statistics"
        self.generated_at = datetime.now().isoformat()

    def generate_docs(self) -> Dict[str, Any]:
        """生成完整的 API 文档"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Statistics Data Aggregation API",
                "description": "统计数据聚合 API 接口文档",
                "version": self.api_version,
                "generated_at": self.generated_at,
                "contact": {
                    "name": "API Support",
                    "email": "support@example.com"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:8000",
                    "description": "开发环境"
                },
                {
                    "url": "https://api.example.com",
                    "description": "生产环境"
                }
            ],
            "tags": [
                {
                    "name": "trends",
                    "description": "收支趋势相关接口"
                },
                {
                    "name": "categories",
                    "description": "分类统计相关接口"
                },
                {
                    "name": "comparison",
                    "description": "对比分析相关接口"
                },
                {
                    "name": "overview",
                    "description": "总览统计相关接口"
                },
                {
                    "name": "metrics",
                    "description": "关键指标相关接口"
                }
            ],
            "paths": self._generate_paths(),
            "components": self._generate_components()
        }

    def _generate_paths(self) -> Dict[str, Any]:
        """生成所有 API 路径定义"""
        return {
            f"{self.base_url}/trends": self._trend_api(),
            f"{self.base_url}/categories/distribution": self._category_distribution_api(),
            f"{self.base_url}/monthly-comparison": self._monthly_comparison_api(),
            f"{self.base_url}/annual-overview": self._annual_overview_api(),
            f"{self.base_url}/key-metrics": self._key_metrics_api()
        }

    def _trend_api(self) -> Dict[str, Any]:
        """收支趋势查询接口"""
        return {
            "get": {
                "tags": ["trends"],
                "summary": "查询收支趋势",
                "description": "获取指定时间范围内的收支趋势数据，支持按日、周、月维度聚合",
                "operationId": "getTrends",
                "parameters": [
                    {
                        "name": "start_date",
                        "in": "query",
                        "required": True,
                        "description": "开始日期 (YYYY-MM-DD)",
                        "schema": {
                            "type": "string",
                            "format": "date",
                            "example": "2024-01-01"
                        }
                    },
                    {
                        "name": "end_date",
                        "in": "query",
                        "required": True,
                        "description": "结束日期 (YYYY-MM-DD)",
                        "schema": {
                            "type": "string",
                            "format": "date",
                            "example": "2024-12-31"
                        }
                    },
                    {
                        "name": "dimension",
                        "in": "query",
                        "required": False,
                        "description": "聚合维度",
                        "schema": {
                            "type": "string",
                            "enum": ["day", "week", "month"],
                            "default": "month"
                        }
                    },
                    {
                        "name": "type",
                        "in": "query",
                        "required": False,
                        "description": "交易类型筛选",
                        "schema": {
                            "type": "string",
                            "enum": ["income", "expense", "all"],
                            "default": "all"
                        }
                    },
                    {
                        "name": "category_id",
                        "in": "query",
                        "required": False,
                        "description": "分类ID筛选",
                        "schema": {
                            "type": "integer",
                            "example": 1
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功返回趋势数据",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/TrendResponse"
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/BadRequest"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalError"
                    }
                },
                "security": [
                    {
                        "bearerAuth": []
                    }
                ]
            }
        }

    def _category_distribution_api(self) -> Dict[str, Any]:
        """分类占比统计接口"""
        return {
            "get": {
                "tags": ["categories"],
                "summary": "查询分类占比统计",
                "description": "获取指定时间范围内各分类的金额占比，支持分别统计收入和支出",
                "operationId": "getCategoryDistribution",
                "parameters": [
                    {
                        "name": "start_date",
                        "in": "query",
                        "required": True,
                        "description": "开始日期 (YYYY-MM-DD)",
                        "schema": {
                            "type": "string",
                            "format": "date",
                            "example": "2024-01-01"
                        }
                    },
                    {
                        "name": "end_date",
                        "in": "query",
                        "required": True,
                        "description": "结束日期 (YYYY-MM-DD)",
                        "schema": {
                            "type": "string",
                            "format": "date",
                            "example": "2024-12-31"
                        }
                    },
                    {
                        "name": "type",
                        "in": "query",
                        "required": True,
                        "description": "交易类型",
                        "schema": {
                            "type": "string",
                            "enum": ["income", "expense"]
                        }
                    },
                    {
                        "name": "top_n",
                        "in": "query",
                        "required": False,
                        "description": "返回前N个分类，其余归入'其他'",
                        "schema": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 10
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功返回分类占比数据",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CategoryDistributionResponse"
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/BadRequest"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalError"
                    }
                },
                "security": [
                    {
                        "bearerAuth": []
                    }
                ]
            }
        }

    def _monthly_comparison_api(self) -> Dict[str, Any]:
        """月度收支对比接口"""
        return {
            "get": {
                "tags": ["comparison"],
                "summary": "查询月度收支对比",
                "description": "获取指定年份各月的收支对比数据，包括收入、支出、结余",
                "operationId": "getMonthlyComparison",
                "parameters": [
                    {
                        "name": "year",
                        "in": "query",
                        "required": True,
                        "description": "年份",
                        "schema": {
                            "type": "integer",
                            "minimum": 2000,
                            "maximum": 2100,
                            "example": 2024
                        }
                    },
                    {
                        "name": "compare_with_previous",
                        "in": "query",
                        "required": False,
                        "description": "是否对比上一年同期",
                        "schema": {
                            "type": "boolean",
                            "default": False
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功返回月度对比数据",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/MonthlyComparisonResponse"
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/BadRequest"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalError"
                    }
                },
                "security": [
                    {
                        "bearerAuth": []
                    }
                ]
            }
        }

    def _annual_overview_api(self) -> Dict[str, Any]:
        """年度统计总览接口"""
        return {
            "get": {
                "tags": ["overview"],
                "summary": "查询年度统计总览",
                "description": "获取指定年份的统计总览，包括总收入、总支出、结余、月均收支等",
                "operationId": "getAnnualOverview",
                "parameters": [
                    {
                        "name": "year",
                        "in": "query",
                        "required": True,
                        "description": "年份",
                        "schema": {
                            "type": "integer",
                            "minimum": 2000,
                            "maximum": 2100,
                            "example": 2024
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功返回年度总览数据",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AnnualOverviewResponse"
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/BadRequest"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalError"
                    }
                },
                "security": [
                    {
                        "bearerAuth": []
                    }
                ]
            }
        }

    def _key_metrics_api(self) -> Dict[str, Any]:
        """关键指标查询接口"""
        return {
            "get": {
                "tags": ["metrics"],
                "summary": "查询关键指标",
                "description": "获取指定时间范围的关键财务指标，如总收入、总支出、结余等",
                "operationId": "getKeyMetrics",
                "parameters": [
                    {
                        "name": "period",
                        "in": "query",
                        "required": False,
                        "description": "时间周期",
                        "schema": {
                            "type": "string",
                            "enum": ["current_month", "last_month", "current_year", "last_year", "custom"],
                            "default": "current_month"
                        }
                    },
                    {
                        "name": "start_date",
                        "in": "query",
                        "required": False,
                        "description": "自定义开始日期 (period=custom时必填)",
                        "schema": {
                            "type": "string",
                            "format": "date",
                            "example": "2024-01-01"
                        }
                    },
                    {
                        "name": "end_date",
                        "in": "query",
                        "required": False,
                        "description": "自定义结束日期 (period=custom时必填)",
                        "schema": {
                            "type": "string",
                            "format": "date",
                            "example": "2024-12-31"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功返回关键指标数据",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/KeyMetricsResponse"
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/BadRequest"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalError"
                    }
                },
                "security": [
                    {
                        "bearerAuth": []
                    }
                ]
            }
        }

    def _generate_components(self) -> Dict[str, Any]:
        """生成组件定义"""
        return {
            "schemas": {
                "TrendResponse": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "integer",
                            "example": 200
                        },
                        "message": {
                            "type": "string",
                            "example": "success"
                        },
                        "data": {
                            "type": "object",
                            "properties": {
                                "dimension": {
                                    "type": "string",
                                    "enum": ["day", "week", "month"],
                                    "example": "month"
                                },
                                "start_date": {
                                    "type": "string",
                                    "format": "date",
                                    "example": "2024-01-01"
                                },
                                "end_date": {
                                    "type": "string",
                                    "format": "date",
                                    "example": "2024-12-31"
                                },
                                "trends": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "period": {
                                                "type": "string",
                                                "description": "时间周期标识",
                                                "example": "2024-01"
                                            },
                                            "income": {
                                                "type": "number",
                                                "format": "decimal",
                                                "description": "收入金额",
                                                "example": 15000.00
                                            },
                                            "expense": {
                                                "type": "number",
                                                "format": "decimal",
                                                "description": "支出金额",
                                                "example": 8500.00
                                            },
                                            "balance": {
                                                "type": "number",
                                                "format": "decimal",
                                                "description": "结余",
                                                "example": 6500.00
                                            },
                                            "transaction_count": {
                                                "type": "integer",
                                                "description": "交易笔数",
                                                "example": 45
                                            }
                                        }
                                    }
                                },
                                "summary": {
                                    "type": "object",
                                    "properties": {
                                        "total_income": {
                                            "type": "number",
                                            "format": "decimal",
                                            "example": 180000.00
                                        },
                                        "total_expense": {
                                            "type": "number",
                                            "format": "decimal",
                                            "example": 102000.00
                                        },
                                        "total_balance": {
                                            "type": "number",
                                            "format": "decimal",
                                            "example": 78000.00
                                        },
                                        "avg_income": {
                                            "type": "number",
                                            "format": "decimal",
                                            "example": 15000.00
                                        },
                                        "avg_expense": {
                                            "type": "number",
                                            "format": "decimal",
                                            "example": 8500.00
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "CategoryDistributionResponse": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "integer",
                            "example": 200
                        },
                        "message": {
                            "type": "string",
                            "example": "success"
                        },
                        "data": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["income", "expense"],
                                    "example": "expense"
                                },
                                "start_date": {
                                    "type": "string",
                                    "format": "date",
                                    "example": "2024-01-01"
                                },
                                "end_date": {
                                    "type": "string",
                                    "format": "date",
                                    "example": "2024-12-31"
                                },
                                "total_amount": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "总金额",
                                    "example": 102000.00
                                },
                                "categories": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "category_id": {
                                                "type": "integer",
                                                "example": 1
                                            },
                                            "category_name": {
                                                "type": "string",
                                                "example": "餐饮"
                                            },
                                            "amount": {
                                                "type": "number",
                                                "format": "decimal",
                                                "example": 25500.00
                                            },
                                            "percentage": {
                                                "type": "number",
                                                "format": "decimal",
                                                "description": "占比百分比",
                                                "example": 25.00
                                            },
                                            "transaction_count": {
                                                "type": "integer",
                                                "example": 120
                                            },
                                            "avg_amount": {
                                                "type": "number",
                                                "format": "decimal",
                                                "description": "平均金额",
                                                "example": 212.50
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "MonthlyComparisonResponse": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "integer",
                            "example": 200
                        },
                        "message": {
                            "type": "string",
                            "example": "success"
                        },
                        "data": {
                            "type": "object",
                            "properties": {
                                "year": {
                                    "type": "integer",
                                    "example": 2024
                                },
                                "months": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "month": {
                                                "type": "integer",
                                                "minimum": 1,
                                                "maximum": 12,
                                                "example": 1
                                            },
                                            "income": {
                                                "type": "number",
                                                "format": "decimal",
                                                "example": 15000.00
                                            },
                                            "expense": {
                                                "type": "number",
                                                "format": "decimal",
                                                "example": 8500.00
                                            },
                                            "balance": {
                                                "type": "number",
                                                "format": "decimal",
                                                "example": 6500.00
                                            },
                                            "income_growth": {
                                                "type": "number",
                                                "format": "decimal",
                                                "description": "收入环比增长率(%)",
                                                "example": 5.5
                                            },
                                            "expense_growth": {
                                                "type": "number",
                                                "format": "decimal",
                                                "description": "支出环比增长率(%)",
                                                "example": -2.3
                                            },
                                            "previous_year": {
                                                "type": "object",
                                                "description": "上一年同期数据(如果请求了对比)",
                                                "properties": {
                                                    "income": {
                                                        "type": "number",
                                                        "format": "decimal",
                                                        "example": 14000.00
                                                    },
                                                    "expense": {
                                                        "type": "number",
                                                        "format": "decimal",
                                                        "example": 8000.00
                                                    },
                                                    "balance": {
                                                        "type": "number",
                                                        "format": "decimal",
                                                        "example": 6000.00
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "AnnualOverviewResponse": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "integer",
                            "example": 200
                        },
                        "message": {
                            "type": "string",
                            "example": "success"
                        },
                        "data": {
                            "type": "object",
                            "properties": {
                                "year": {
                                    "type": "integer",
                                    "example": 2024
                                },
                                "total_income": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "年度总收入",
                                    "example": 180000.00
                                },
                                "total_expense": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "年度总支出",
                                    "example": 102000.00
                                },
                                "total_balance": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "年度总结余",
                                    "example": 78000.00
                                },
                                "avg_monthly_income": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "月均收入",
                                    "example": 15000.00
                                },
                                "avg_monthly_expense": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "月均支出",
                                    "example": 8500.00
                                },
                                "total_transactions": {
                                    "type": "integer",
                                    "description": "总交易笔数",
                                    "example": 540
                                },
                                "highest_income_month": {
                                    "type": "object",
                                    "properties": {
                                        "month": {
                                            "type": "integer",
                                            "example": 12
                                        },
                                        "amount": {
                                            "type": "number",
                                            "format": "decimal",
                                            "example": 25000.00
                                        }
                                    }
                                },
                                "highest_expense_month": {
                                    "type": "object",
                                    "properties": {
                                        "month": {
                                            "type": "integer",
                                            "example": 2
                                        },
                                        "amount": {
                                            "type": "number",
                                            "format": "decimal",
                                            "example": 15000.00
                                        }
                                    }
                                },
                                "top_expense_categories": {
                                    "type": "array",
                                    "description": "支出最多的前5个分类",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "category_name": {
                                                "type": "string",
                                                "example": "餐饮"
                                            },
                                            "amount": {
                                                "type": "number",
                                                "format": "decimal",
                                                "example": 25500.00
                                            },
                                            "percentage": {
                                                "type": "number",
                                                "format": "decimal",
                                                "example": 25.00
                                            }
                                        }
                                    }
                                },
                                "top_income_categories": {
                                    "type": "array",
                                    "description": "收入最多的前5个分类",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "category_name": {
                                                "type": "string",
                                                "example": "工资"
                                            },
                                            "amount": {
                                                "type": "number",
                                                "format": "decimal",
                                                "example": 150000.00
                                            },
                                            "percentage": {
                                                "type": "number",
                                                "format": "decimal",
                                                "example": 83.33
                                            }
                                        }
                                    }
                                },
                                "year_over_year": {
                                    "type": "object",
                                    "description": "同比数据",
                                    "properties": {
                                        "income_growth": {
                                            "type": "number",
                                            "format": "decimal",
                                            "description": "收入同比增长率(%)",
                                            "example": 8.5
                                        },
                                        "expense_growth": {
                                            "type": "number",
                                            "format": "decimal",
                                            "description": "支出同比增长率(%)",
                                            "example": 3.2
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "KeyMetricsResponse": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "integer",
                            "example": 200
                        },
                        "message": {
                            "type": "string",
                            "example": "success"
                        },
                        "data": {
                            "type": "object",
                            "properties": {
                                "period": {
                                    "type": "string",
                                    "example": "current_month"
                                },
                                "start_date": {
                                    "type": "string",
                                    "format": "date",
                                    "example": "2024-01-01"
                                },
                                "end_date": {
                                    "type": "string",
                                    "format": "date",
                                    "example": "2024-01-31"
                                },
                                "total_income": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "总收入",
                                    "example": 15000.00
                                },
                                "total_expense": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "总支出",
                                    "example": 8500.00
                                },
                                "balance": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "结余",
                                    "example": 6500.00
                                },
                                "income_count": {
                                    "type": "integer",
                                    "description": "收入笔数",
                                    "example": 5
                                },
                                "expense_count": {
                                    "type": "integer",
                                    "description": "支出笔数",
                                    "example": 40
                                },
                                "avg_income": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "平均收入",
                                    "example": 3000.00
                                },
                                "avg_expense": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "平均支出",
                                    "example": 212.50
                                },
                                "savings_rate": {
                                    "type": "number",
                                    "format": "decimal",
                                    "description": "储蓄率(%)",
                                    "example": 43.33
                                },
                                "daily_avg_expense": {
                                    "type