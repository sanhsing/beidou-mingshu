"""
API 文檔規範 api_docs.py v1.0
============================
XTF任務：消-E1 | 執行星：澄書（記錄）+ 璃語（介面）
確定度：★★★★★（技術規範）

核心本質：OpenAPI = 自動生成 + 手動補充

📚 API 文檔結構：
1. 基本資訊（版本、描述）
2. 端點定義（路徑、方法）
3. 參數說明（請求、響應）
4. 錯誤碼定義
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

# API 版本
API_VERSION = "2.4"
API_TITLE = "北斗命數 API"
API_DESCRIPTION = """
北斗命數命理分析系統 API

## 功能模組
- 🔮 八字分析：四柱八字、大運流年
- ⭐ 紫微斗數：命盤排盤、大限流年、四化飛星
- 📝 姓名學：五格分析、三才配置
- 🌸 梅花易數：起卦解卦
- 💑 命盤比對：合婚、親子、合作

## 認證方式
使用 JWT Bearer Token 認證

## XTF8 確定度標註
所有分析結果都包含確定度標註：
- ★★★★★ 計算公式（可驗證）
- ★★★★☆ 規則推導（有依據）
- ★★★☆☆ 經驗統計（參考性質）
- ★★☆☆☆ 推測建議（僅供參考）
"""


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class APIParameter:
    """API 參數"""
    name: str
    type: str  # string, integer, boolean, object, array
    required: bool
    description: str
    example: Any = None
    location: str = "body"  # path, query, body, header


@dataclass
class APIResponse:
    """API 響應"""
    status_code: int
    description: str
    schema: Dict = None
    example: Dict = None


@dataclass
class APIEndpoint:
    """API 端點"""
    path: str
    method: HTTPMethod
    summary: str
    description: str
    tags: List[str]
    parameters: List[APIParameter]
    responses: List[APIResponse]
    requires_auth: bool = False


# ============================================================
# API 端點定義
# ============================================================

API_ENDPOINTS: List[APIEndpoint] = [
    # ========== 認證 ==========
    APIEndpoint(
        path="/api/auth/register",
        method=HTTPMethod.POST,
        summary="用戶註冊",
        description="註冊新用戶帳號",
        tags=["認證"],
        parameters=[
            APIParameter("username", "string", True, "用戶名（3-20字符）", "beidou"),
            APIParameter("password", "string", True, "密碼（至少6字符）", "password123"),
            APIParameter("email", "string", False, "電子郵件", "user@example.com"),
        ],
        responses=[
            APIResponse(200, "註冊成功", example={"success": True, "user_id": 1}),
            APIResponse(400, "註冊失敗", example={"success": False, "error": "用戶名已存在"}),
        ],
    ),
    APIEndpoint(
        path="/api/auth/login",
        method=HTTPMethod.POST,
        summary="用戶登入",
        description="使用用戶名和密碼登入",
        tags=["認證"],
        parameters=[
            APIParameter("username", "string", True, "用戶名", "beidou"),
            APIParameter("password", "string", True, "密碼", "password123"),
        ],
        responses=[
            APIResponse(200, "登入成功", example={
                "success": True,
                "access_token": "eyJ...",
                "refresh_token": "eyJ...",
                "token_type": "Bearer",
                "expires_in": 86400,
            }),
            APIResponse(401, "登入失敗", example={"success": False, "error": "密碼錯誤"}),
        ],
    ),
    APIEndpoint(
        path="/api/auth/refresh",
        method=HTTPMethod.POST,
        summary="刷新 Token",
        description="使用 refresh_token 取得新的 access_token",
        tags=["認證"],
        parameters=[
            APIParameter("refresh_token", "string", True, "刷新令牌", "eyJ..."),
        ],
        responses=[
            APIResponse(200, "刷新成功", example={"access_token": "eyJ..."}),
            APIResponse(401, "刷新失敗", example={"error": "Token 已過期"}),
        ],
    ),
    
    # ========== 八字分析 ==========
    APIEndpoint(
        path="/api/bazi/calculate",
        method=HTTPMethod.POST,
        summary="八字排盤",
        description="根據出生資料計算八字命盤",
        tags=["八字"],
        requires_auth=True,
        parameters=[
            APIParameter("year", "integer", True, "出生年", 1973),
            APIParameter("month", "integer", True, "出生月", 12),
            APIParameter("day", "integer", True, "出生日", 30),
            APIParameter("hour", "integer", True, "出生時（0-23）", 17),
            APIParameter("gender", "string", True, "性別（男/女）", "男"),
            APIParameter("is_lunar", "boolean", False, "是否農曆", False),
        ],
        responses=[
            APIResponse(200, "計算成功", example={
                "year": "癸丑",
                "month": "甲子",
                "day": "庚子",
                "hour": "乙酉",
                "day_master": "庚",
                "wuxing_count": {"木": 2, "火": 0, "土": 2, "金": 2, "水": 4},
            }),
        ],
    ),
    APIEndpoint(
        path="/api/bazi/dayun",
        method=HTTPMethod.POST,
        summary="八字大運",
        description="計算八字大運排列",
        tags=["八字"],
        requires_auth=True,
        parameters=[
            APIParameter("year_gan", "string", True, "年干", "癸"),
            APIParameter("month_ganzhi", "string", True, "月柱", "甲子"),
            APIParameter("gender", "string", True, "性別", "男"),
            APIParameter("birth_year", "integer", True, "出生年", 1973),
            APIParameter("birth_month", "integer", True, "出生月", 12),
            APIParameter("birth_day", "integer", True, "出生日", 30),
        ],
        responses=[
            APIResponse(200, "計算成功", example={
                "direction": "逆行",
                "qiyun_age": 7.7,
                "dayun_list": [{"order": 1, "ganzhi": "癸亥", "start_age": 7}],
            }),
        ],
    ),
    APIEndpoint(
        path="/api/bazi/liunian",
        method=HTTPMethod.POST,
        summary="八字流年",
        description="分析特定年份流年運勢",
        tags=["八字"],
        requires_auth=True,
        parameters=[
            APIParameter("day_master", "string", True, "日主天干", "庚"),
            APIParameter("pillars", "object", True, "四柱", {"year": "癸丑", "month": "甲子"}),
            APIParameter("year", "integer", True, "分析年份", 2026),
            APIParameter("is_strong", "boolean", False, "是否身強", False),
        ],
        responses=[
            APIResponse(200, "分析成功", example={
                "year": 2026,
                "ganzhi": "丙午",
                "gan_shishen": "七殺",
                "tendency": "凶",
                "advice": "壓力挑戰",
            }),
        ],
    ),
    
    # ========== 紫微斗數 ==========
    APIEndpoint(
        path="/api/ziwei/calculate",
        method=HTTPMethod.POST,
        summary="紫微排盤",
        description="根據出生資料計算紫微命盤",
        tags=["紫微"],
        requires_auth=True,
        parameters=[
            APIParameter("year", "integer", True, "出生年", 1973),
            APIParameter("month", "integer", True, "出生月", 12),
            APIParameter("day", "integer", True, "出生日", 7),
            APIParameter("hour", "integer", True, "出生時（0-23）", 17),
            APIParameter("gender", "string", True, "性別", "男"),
            APIParameter("is_lunar", "boolean", False, "是否農曆", True),
        ],
        responses=[
            APIResponse(200, "計算成功", example={
                "ju_shu": "金四局",
                "ming_gong": "午",
                "ming_stars": ["天相"],
                "gongs": [],
            }),
        ],
    ),
    APIEndpoint(
        path="/api/ziwei/daxian",
        method=HTTPMethod.POST,
        summary="紫微大限",
        description="計算紫微大限排列",
        tags=["紫微"],
        requires_auth=True,
        parameters=[
            APIParameter("year_gan", "string", True, "年干", "癸"),
            APIParameter("gender", "string", True, "性別", "男"),
            APIParameter("ju_shu", "string", True, "局數", "金四局"),
            APIParameter("ming_gong_idx", "integer", True, "命宮索引", 6),
            APIParameter("birth_year", "integer", True, "出生年", 1973),
        ],
        responses=[
            APIResponse(200, "計算成功", example={
                "direction": "逆行",
                "daxian_list": [{"order": 1, "gong_name": "命宮"}],
            }),
        ],
    ),
    APIEndpoint(
        path="/api/ziwei/liunian",
        method=HTTPMethod.POST,
        summary="紫微流年",
        description="分析紫微流年運勢",
        tags=["紫微"],
        requires_auth=True,
        parameters=[
            APIParameter("year", "integer", True, "分析年份", 2026),
            APIParameter("ming_gong_zhi", "string", True, "命宮地支", "午"),
            APIParameter("gongs", "array", False, "十二宮資料", []),
        ],
        responses=[
            APIResponse(200, "分析成功", example={
                "year": 2026,
                "taisui_gong": "遷移",
                "sihua": {"祿": "天同"},
                "overall": "整體有利",
            }),
        ],
    ),
    
    # ========== 姓名學 ==========
    APIEndpoint(
        path="/api/name/analyze",
        method=HTTPMethod.POST,
        summary="姓名分析",
        description="分析姓名五格三才",
        tags=["姓名"],
        requires_auth=True,
        parameters=[
            APIParameter("surname", "string", True, "姓氏", "楊"),
            APIParameter("given_name", "string", True, "名字", "三興"),
        ],
        responses=[
            APIResponse(200, "分析成功", example={
                "tian_ge": 14,
                "ren_ge": 16,
                "di_ge": 18,
                "wai_ge": 16,
                "zong_ge": 31,
                "sancai": "火土金",
            }),
        ],
    ),
    
    # ========== 梅花易數 ==========
    APIEndpoint(
        path="/api/meihua/divine",
        method=HTTPMethod.POST,
        summary="梅花起卦",
        description="根據數字或時間起卦",
        tags=["梅花"],
        requires_auth=True,
        parameters=[
            APIParameter("method", "string", True, "起卦方式", "number"),
            APIParameter("number1", "integer", False, "上卦數字", 3),
            APIParameter("number2", "integer", False, "下卦數字", 5),
            APIParameter("question", "string", False, "問事", "今日運勢"),
        ],
        responses=[
            APIResponse(200, "起卦成功", example={
                "ben_gua": "離",
                "bian_gua": "坤",
                "hu_gua": "兌",
                "interpretation": "...",
            }),
        ],
    ),
    
    # ========== 命盤比對 ==========
    APIEndpoint(
        path="/api/match/marriage",
        method=HTTPMethod.POST,
        summary="合婚比對",
        description="比對兩人婚姻契合度",
        tags=["比對"],
        requires_auth=True,
        parameters=[
            APIParameter("person1", "object", True, "甲方資料", {"day_master": "庚", "year_zhi": "丑"}),
            APIParameter("person2", "object", True, "乙方資料", {"day_master": "乙", "year_zhi": "未"}),
        ],
        responses=[
            APIResponse(200, "比對成功", example={
                "percentage": 72,
                "grade": "B",
                "summary": "合婚契合度高",
                "factors": [],
            }),
        ],
    ),
    APIEndpoint(
        path="/api/match/parent-child",
        method=HTTPMethod.POST,
        summary="親子比對",
        description="比對親子關係契合度",
        tags=["比對"],
        requires_auth=True,
        parameters=[
            APIParameter("parent", "object", True, "父母資料", {"day_master": "庚"}),
            APIParameter("child", "object", True, "子女資料", {"day_master": "壬"}),
        ],
        responses=[
            APIResponse(200, "比對成功", example={"percentage": 78, "grade": "B"}),
        ],
    ),
    
    # ========== 完整報告 ==========
    APIEndpoint(
        path="/api/report/full",
        method=HTTPMethod.POST,
        summary="完整報告",
        description="生成完整命理分析報告",
        tags=["報告"],
        requires_auth=True,
        parameters=[
            APIParameter("year", "integer", True, "出生年", 1973),
            APIParameter("month", "integer", True, "出生月", 12),
            APIParameter("day", "integer", True, "出生日", 30),
            APIParameter("hour", "integer", True, "出生時", 17),
            APIParameter("gender", "string", True, "性別", "男"),
            APIParameter("name", "string", False, "姓名", "楊三興"),
            APIParameter("is_lunar", "boolean", False, "是否農曆", False),
        ],
        responses=[
            APIResponse(200, "生成成功", example={
                "report_text": "...",
                "bazi": {},
                "ziwei": {},
                "name": {},
            }),
        ],
    ),
]


# ============================================================
# OpenAPI 規範生成
# ============================================================

def generate_openapi_spec() -> Dict:
    """生成 OpenAPI 3.0 規範"""
    
    paths = {}
    
    for endpoint in API_ENDPOINTS:
        path_item = paths.get(endpoint.path, {})
        
        # 參數
        parameters = []
        request_body = None
        body_properties = {}
        body_required = []
        
        for param in endpoint.parameters:
            if param.location == "body":
                body_properties[param.name] = {
                    "type": param.type,
                    "description": param.description,
                }
                if param.example is not None:
                    body_properties[param.name]["example"] = param.example
                if param.required:
                    body_required.append(param.name)
            else:
                parameters.append({
                    "name": param.name,
                    "in": param.location,
                    "required": param.required,
                    "description": param.description,
                    "schema": {"type": param.type},
                })
        
        if body_properties:
            request_body = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": body_properties,
                            "required": body_required,
                        }
                    }
                }
            }
        
        # 響應
        responses = {}
        for resp in endpoint.responses:
            responses[str(resp.status_code)] = {
                "description": resp.description,
            }
            if resp.example:
                responses[str(resp.status_code)]["content"] = {
                    "application/json": {
                        "example": resp.example
                    }
                }
        
        # 操作
        operation = {
            "summary": endpoint.summary,
            "description": endpoint.description,
            "tags": endpoint.tags,
            "responses": responses,
        }
        
        if parameters:
            operation["parameters"] = parameters
        if request_body:
            operation["requestBody"] = request_body
        if endpoint.requires_auth:
            operation["security"] = [{"bearerAuth": []}]
        
        path_item[endpoint.method.value.lower()] = operation
        paths[endpoint.path] = path_item
    
    return {
        "openapi": "3.0.0",
        "info": {
            "title": API_TITLE,
            "version": API_VERSION,
            "description": API_DESCRIPTION,
        },
        "servers": [
            {"url": "http://localhost:8000", "description": "本地開發"},
            {"url": "https://api.beidou-mingshu.com", "description": "生產環境"},
        ],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
        "tags": [
            {"name": "認證", "description": "用戶認證相關"},
            {"name": "八字", "description": "八字命理分析"},
            {"name": "紫微", "description": "紫微斗數分析"},
            {"name": "姓名", "description": "姓名學分析"},
            {"name": "梅花", "description": "梅花易數分析"},
            {"name": "比對", "description": "命盤比對分析"},
            {"name": "報告", "description": "綜合報告生成"},
        ],
    }


def generate_api_docs_markdown() -> str:
    """生成 Markdown 格式的 API 文檔"""
    
    doc = f"""# {API_TITLE} v{API_VERSION}

{API_DESCRIPTION}

---

## 端點列表

"""
    
    # 按標籤分組
    tags = {}
    for endpoint in API_ENDPOINTS:
        for tag in endpoint.tags:
            if tag not in tags:
                tags[tag] = []
            tags[tag].append(endpoint)
    
    for tag, endpoints in tags.items():
        doc += f"### {tag}\n\n"
        
        for endpoint in endpoints:
            auth_badge = "🔒" if endpoint.requires_auth else "🔓"
            doc += f"#### {auth_badge} {endpoint.method.value} `{endpoint.path}`\n\n"
            doc += f"**{endpoint.summary}**\n\n"
            doc += f"{endpoint.description}\n\n"
            
            if endpoint.parameters:
                doc += "**參數**\n\n"
                doc += "| 名稱 | 類型 | 必填 | 說明 |\n"
                doc += "|------|------|------|------|\n"
                for param in endpoint.parameters:
                    required = "是" if param.required else "否"
                    doc += f"| {param.name} | {param.type} | {required} | {param.description} |\n"
                doc += "\n"
            
            doc += "---\n\n"
    
    return doc


if __name__ == "__main__":
    import json
    
    # 生成 OpenAPI 規範
    spec = generate_openapi_spec()
    print("=== OpenAPI 規範 ===")
    print(f"端點數量：{len(API_ENDPOINTS)}")
    print(f"標籤數量：{len(spec['tags'])}")
    
    # 輸出 JSON
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    print("✅ 已生成 openapi.json")
    
    # 生成 Markdown
    md = generate_api_docs_markdown()
    with open("API_DOCS.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("✅ 已生成 API_DOCS.md")
