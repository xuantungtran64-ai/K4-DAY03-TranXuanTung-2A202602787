"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND (AI SMART MIXOLOGIST & BARISTA AGENT)
Mã nguồn chứa Tool Schemas (JSON Schema) và Execution Layer quản lý an toàn sinh trắc:
- Kiểm soát dị ứng (Allergy checks)
- Tương tác thuốc (Medication contraindications: kháng sinh, thuốc an thần...)
- Quản lý hạn mức tiêu thụ Cồn (Alcohol Units/BAC) và Caffeine theo mốc thời gian
- Kiểm soát kho nguyên liệu quầy pha chế đa dạng (Cocktail, Mocktail, Cà phê, Trà thảo mộc, Nước ép)
"""

import json
from typing import Dict, Any, List

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Tra cứu hồ sơ sức khỏe, hạn mức cồn/caffeine và kho quầy bar
    {
        "name": "query_guest_health_and_bar_inventory",
        "description": "Tra cứu chi tiết hồ sơ khách hàng: tiền sử dị ứng, thuốc đang sử dụng (chống chỉ định cồn/caffeine), lượng cồn và caffeine đã nạp trong ngày, thời điểm nạp gần nhất, hạn mức an toàn còn lại và tồn kho nguyên liệu quầy bar.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Mã định danh khách hàng (ví dụ: 'USR001', 'USR002', 'USR003')"
                },
                "target_mood": {
                    "type": "string",
                    "description": "Tâm trạng hoặc nhu cầu mong muốn của khách (ví dụ: 'thư giãn', 'tỉnh táo làm việc', 'chill nhẹ sau giờ làm', 'dễ ngủ', 'tiệc tùng')"
                }
            },
            "required": ["user_id"]
        }
    },
    
    # Tool 2: Thẩm định an toàn sinh trắc & gửi lệnh điều khiển máy pha chế tự động
    {
        "name": "dispense_smart_drink",
        "description": "Thẩm định an toàn sinh trắc (dị ứng, tương tác thuốc, quá tải cồn/caffeine) và gửi lệnh pha chế tới máy pha tự động.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Mã định danh khách hàng đặt đồ uống"
                },
                "drink_name": {
                    "type": "string",
                    "description": "Tên đồ uống (ví dụ: 'Cocktail Gin Tonic', 'Virgin Mojito Mocktail', 'Trà hoa cúc mật ong', 'Cà phê yến mạch')"
                },
                "category": {
                    "type": "string",
                    "description": "Phân loại thức uống",
                    "enum": ["COCKTAIL_ALCOHOLIC", "MOCKTAIL_NON_ALCOHOLIC", "COFFEE_CAFFEINE", "HERBAL_TEA", "DETOX_JUICE"]
                },
                "contains_alcohol": {
                    "type": "boolean",
                    "description": "Đồ uống có chứa cồn hay không (True nếu có cồn, False nếu không cồn)"
                },
                "contains_caffeine": {
                    "type": "boolean",
                    "description": "Đồ uống có chứa caffeine hay không (True nếu có caffeine, False nếu không)"
                },
                "ingredients": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Danh sách các mã nguyên liệu sử dụng (ví dụ: ['gin_bombay', 'tonic_water', 'lime_juice'])"
                },
                "temperature": {
                    "type": "string",
                    "description": "Nhiệt độ phục vụ",
                    "enum": ["NÓNG", "ĐÁ", "NHIỆT_ĐỘ_PHÒNG"]
                },
                "sweetness_level": {
                    "type": "string",
                    "description": "Mức độ ngọt yêu cầu (ví dụ: '0%', '30%', '50%', '100%')"
                }
            },
            "required": ["user_id", "drink_name", "category", "contains_alcohol", "contains_caffeine", "ingredients"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU SỨC KHỎE KHÁCH HÀNG & KHO QUẦY BAR (EXECUTION LAYER)
# ==============================================================================

MOCK_GUESTS = {
    # Khách 1: Đang uống thuốc kháng sinh + lái xe -> Tuyệt đối CẤM CỒN, caffeine sắp đầy
    "USR001": {
        "full_name": "Trần Xuân Tùng",
        "current_medication": "Kháng sinh Amoxicillin & Paracetamol (Điều trị viêm họng)",
        "medical_contraindications": ["STRICT_NO_ALCOHOL (Nguy cơ ngộ độc gan cấp và sốc phản vệ)", "LIMIT_CAFFEINE (Tránh đau dạ dày)"],
        "driving_status": "Đang tự lái xe ô tô (Yêu cầu BAC = 0.00% tuyệt đối)",
        "allergies": ["dairy (dị ứng sữa bò/lactose)", "peanut (dị ứng đậu phộng)"],
        "today_consumption": {
            "caffeine_consumed_mg": 280,
            "max_daily_caffeine_mg": 300,
            "last_caffeine_time": "14:30 (Đã nạp 2 shot Espresso chiều)",
            "alcohol_units_consumed": 0.0,
            "max_daily_alcohol_units": 0.0  # Bị khóa về 0 do dùng thuốc và lái xe
        },
        "safe_allowance": {
            "remaining_caffeine_mg": 20,
            "remaining_alcohol_units": 0.0,
            "recommendation": "Chỉ được dùng đồ uống không cồn (Mocktail/Trà thảo mộc), không dùng sữa động vật (dairy), hạn chế tối đa caffeine vào buổi tối."
        }
    },
    
    # Khách 2: Hoàn toàn khỏe mạnh, chưa nạp cồn hay caffeine hôm nay
    "USR002": {
        "full_name": "Nguyễn Hoàng Nam",
        "current_medication": "Không dùng thuốc",
        "medical_contraindications": [],
        "driving_status": "Đi Grab / Taxi (Không lái xe)",
        "allergies": [],
        "today_consumption": {
            "caffeine_consumed_mg": 0,
            "max_daily_caffeine_mg": 400,
            "last_caffeine_time": "Chưa dùng",
            "alcohol_units_consumed": 0.0,
            "max_daily_alcohol_units": 2.5
        },
        "safe_allowance": {
            "remaining_caffeine_mg": 400,
            "remaining_alcohol_units": 2.5,
            "recommendation": "Có thể thưởng thức Cocktail nồng độ vừa phải hoặc Cà phê đậm vị theo sở thích."
        }
    },

    # Khách 3: Đã uống 3 ly bia (chạm ngưỡng say xỉn), dị ứng dứa (pineapple)
    "USR003": {
        "full_name": "Lê Bảo Anh",
        "current_medication": "Không dùng thuốc",
        "medical_contraindications": ["ALCOHOL_LIMIT_REACHED (Đã uống 3 ly bia lúc 18:30)"],
        "driving_status": "Đi bộ",
        "allergies": ["pineapple (dị ứng dứa/thơm)"],
        "today_consumption": {
            "caffeine_consumed_mg": 100,
            "max_daily_caffeine_mg": 400,
            "last_caffeine_time": "09:00",
            "alcohol_units_consumed": 3.0,
            "max_daily_alcohol_units": 3.0  # Đã chạm ngưỡng tối đa
        },
        "safe_allowance": {
            "remaining_caffeine_mg": 300,
            "remaining_alcohol_units": 0.0,
            "recommendation": "Đã đạt ngưỡng cồn tối đa trong ngày. Tuyệt đối KHÔNG phục vụ thêm đồ uống có cồn. Đề xuất nước ép giải rượu hoặc Trà thảo mộc."
        }
    }
}

MOCK_INVENTORY = {
    # Rượu & Đồ có cồn
    "gin_bombay": {"name": "Rượu Gin Bombay Sapphire", "stock": "SẴN SÀNG", "alcohol_units": 1.2, "allergens": []},
    "rum_bacardi": {"name": "Rượu Rum Bacardi Superior", "stock": "SẴN SÀNG", "alcohol_units": 1.2, "allergens": []},
    "craft_beer_ipa": {"name": "Bia Thủ công Heart of Darkness IPA", "stock": "SẴN SÀNG", "alcohol_units": 1.5, "allergens": ["gluten"]},
    
    # Cà phê & Trà (Caffeine & Herbal)
    "espresso_arabica": {"name": "Hạt Cà phê Arabica Cầu Đất", "stock": "SẴN SÀNG", "caffeine_mg": 120, "allergens": []},
    "matcha_uji": {"name": "Bột Trà xanh Uji Matcha Nhật Bản", "stock": "SẴN SÀNG", "caffeine_mg": 35, "allergens": []},
    "chamomile_tea": {"name": "Trà hoa cúc hữu cơ Chamomile", "stock": "SẴN SÀNG", "caffeine_mg": 0, "allergens": []},
    
    # Sữa & Phụ gia
    "cow_dairy_milk": {"name": "Sữa bò tươi nguyên kem Barista", "stock": "SẴN SÀNG", "allergens": ["dairy"]},
    "oat_milk": {"name": "Sữa yến mạch Oatside Barista", "stock": "SẴN SÀNG", "allergens": []},
    
    # Nước ép & Syrups
    "lime_mint_syrup": {"name": "Syrup Chanh Bạc Hà Tươi", "stock": "SẴN SÀNG", "allergens": []},
    "raw_forest_honey": {"name": "Mật ong rừng tự nhiên", "stock": "SẴN SÀNG", "allergens": []},
    "tonic_water": {"name": "Nước Tonic Schweppes", "stock": "SẴN SÀNG", "allergens": []},
    "pineapple_juice": {"name": "Nước ép dứa tươi nguyên chất", "stock": "SẴN SÀNG", "allergens": ["pineapple"]},
    "syrup_salted_caramel": {"name": "Syrup Caramel muối biển", "stock": "OUT_OF_STOCK (HẾT HÀNG)", "allergens": []}
}


def execute_query_guest_health_and_bar_inventory(user_id: str, target_mood: str = "") -> str:
    """Thực thi truy vấn hồ sơ sức khỏe và tồn kho quầy bar"""
    uid = user_id.strip().upper()
    guest_info = MOCK_GUESTS.get(uid)
    
    if not guest_info:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy hồ sơ khách hàng '{user_id}'. Cần đăng ký hồ sơ y tế/dị ứng trước khi pha chế.",
            "available_inventory_sample": list(MOCK_INVENTORY.keys())[:5]
        }, ensure_ascii=False)
        
    return json.dumps({
        "status": "SUCCESS",
        "user_id": uid,
        "health_profile": guest_info,
        "target_mood": target_mood or "Thư giãn & Trải nghiệm",
        "inventory": MOCK_INVENTORY
    }, ensure_ascii=False)


def execute_dispense_smart_drink(
    user_id: str,
    drink_name: str,
    category: str,
    contains_alcohol: bool,
    contains_caffeine: bool,
    ingredients: List[str],
    temperature: str = "ĐÁ",
    sweetness_level: str = "50%"
) -> str:
    """Thẩm định an toàn sinh học đa tầng và kích hoạt lệnh pha chế thông minh"""
    uid = user_id.strip().upper()
    guest = MOCK_GUESTS.get(uid)
    
    if not guest:
        return json.dumps({
            "status": "UNAUTHORIZED_GUEST",
            "message": f"Từ chối pha chế: Khách hàng '{user_id}' chưa xác thực hồ sơ sức khỏe."
        }, ensure_ascii=False)

    # 1. KIỂM TRA DỊ ỨNG (ALLERGY SAFETY CHECK)
    user_allergies = [a.lower() for a in guest.get("allergies", [])]
    detected_allergens = []
    for ing_key in ingredients:
        ing_data = MOCK_INVENTORY.get(ing_key.strip().lower())
        if ing_data:
            for item_allergen in ing_data.get("allergens", []):
                if item_allergen.lower() in user_allergies:
                    detected_allergens.append(f"{ing_data['name']} (chứa {item_allergen})")
        # Kiểm tra theo tên thành phần tự do
        if "dairy" in user_allergies and ("cow_dairy_milk" in ing_key or "sữa bò" in ing_key.lower()):
            detected_allergens.append("Sữa động vật (dairy)")
        if "pineapple" in user_allergies and ("pineapple" in ing_key or "dứa" in ing_key.lower()):
            detected_allergens.append("Dứa (pineapple)")

    if detected_allergens:
        return json.dumps({
            "status": "ALLERGY_SAFETY_ALERT",
            "message": f"NGUY HIỂM: Từ chối pha chế '{drink_name}' do khách hàng {guest['full_name']} có tiền sử dị ứng với: {', '.join(set(detected_allergens))}.",
            "suggestion": "Chuyển sang thành phần an toàn thay thế (ví dụ: dùng Sữa yến mạch hữu cơ Oatside thay cho sữa bò)."
        }, ensure_ascii=False)

    # 2. KIỂM TRA CHỐNG CHỈ ĐỊNH Y TẾ & TƯƠNG TÁC THUỐC (MEDICATION & DRIVING CHECK)
    medication = guest.get("current_medication", "")
    driving_status = guest.get("driving_status", "")
    
    if contains_alcohol:
        if "Kháng sinh" in medication or "Amoxicillin" in medication or "Paracetamol" in medication:
            return json.dumps({
                "status": "MEDICATION_CONTRAINDICATION",
                "message": f"CẢNH BÁO Y TẾ: Khách hàng đang sử dụng {medication}. Rượu/cồn tuyệt đối bị chống chỉ định do nguy cơ tổn thương gan cấp tính và ức chế thần kinh.",
                "suggestion": "Tác tử khuyến nghị chuyển sang Mocktail không cồn (Virgin Mojito hoặc Trà hoa cúc mật ong ấm)."
            }, ensure_ascii=False)
            
        is_driving = (
            ("tự lái xe" in driving_status.lower() or "lái xe" in driving_status.lower())
            and "không lái xe" not in driving_status.lower()
            and "đi grab" not in driving_status.lower()
            and "taxi" not in driving_status.lower()
            and "đi bộ" not in driving_status.lower()
        )
        if is_driving:
            return json.dumps({
                "status": "DRIVING_RESTRICTION",
                "message": "VI PHẠM NỒNG ĐỘ CỒN: Khách hàng đang tự lái xe ô tô. Luật định yêu cầu nồng độ cồn BAC = 0.00% tuyệt đối.",
                "suggestion": "Tác tử chỉ được phục vụ đồ uống Mocktail/Nước ép không cồn."
            }, ensure_ascii=False)

        # Kiểm tra hạn mức cồn trong ngày
        if guest["safe_allowance"]["remaining_alcohol_units"] <= 0:
            return json.dumps({
                "status": "ALCOHOL_LIMIT_EXCEEDED",
                "message": f"VƯỢT HẠN MỨC: Khách hàng đã nạp {guest['today_consumption']['alcohol_units_consumed']} units cồn hôm nay. Đã chạm ngưỡng an toàn tối đa.",
                "suggestion": "Phục vụ Nước ép Detox thanh nhiệt hoặc Trà hoa cúc hỗ trợ gan."
            }, ensure_ascii=False)

    # 3. KIỂM TRA HẠN MỨC CAFFEINE
    if contains_caffeine:
        if guest["safe_allowance"]["remaining_caffeine_mg"] < 50:
            return json.dumps({
                "status": "CAFFEINE_LIMIT_WARNING",
                "message": f"CẢNH BÁO CAFFEINE: Khách hàng đã nạp {guest['today_consumption']['caffeine_consumed_mg']}mg/300mg caffeine hôm nay. Uống thêm cà phê sẽ gây tim đập nhanh và mất ngủ.",
                "suggestion": "Đề xuất đổi sang Trà hoa cúc (0mg caffeine) hoặc Trà xanh Matcha nhẹ (35mg)."
            }, ensure_ascii=False)

    # 4. KIỂM TRA TỒN KHO NGUYÊN LIỆU (INVENTORY CHECK)
    out_of_stock = []
    for ing in ingredients:
        ing_key = ing.strip().lower()
        if ing_key in MOCK_INVENTORY and "OUT_OF_STOCK" in MOCK_INVENTORY[ing_key]["stock"]:
            out_of_stock.append(MOCK_INVENTORY[ing_key]["name"])
        elif "caramel" in ing_key:
            out_of_stock.append("Syrup Caramel muối biển")
            
    if out_of_stock:
        return json.dumps({
            "status": "OUT_OF_STOCK",
            "message": f"Không thể pha chế '{drink_name}' do quầy bar vừa hết: {', '.join(out_of_stock)}.",
            "suggestion": "Đổi sang Mật ong hoa rừng hoặc Syrup chanh bạc hà tươi có sẵn."
        }, ensure_ascii=False)

    # 5. TẤT CẢ TIÊU CHÍ AN TOÀN ĐẠT CHUẨN -> PHÁT LỆNH PHA CHẾ THÀNH CÔNG
    order_id = f"SMART-BAR-{uid}-88"
    return json.dumps({
        "status": "SUCCESS",
        "order_id": order_id,
        "user_id": uid,
        "guest_name": guest["full_name"],
        "drink_name": drink_name,
        "category": category,
        "safety_audit": {
            "allergy_safe": True,
            "medication_safe": True,
            "intake_limits_approved": True
        },
        "recipe_parameters": {
            "temperature": temperature,
            "sweetness": sweetness_level,
            "ingredients": ingredients
        },
        "estimated_prep_seconds": 75,
        "message": f"Thẩm định an toàn sinh trắc HOÀN TOÀN ĐẠT CHUẨN! Lệnh pha chế '{drink_name}' ({category}, {temperature}, ngọt {sweetness_level}) đã được gửi tới hệ thống quầy bar. Đồ uống sẽ sẵn sàng sau 75 giây (Mã đơn: {order_id})."
    }, ensure_ascii=False)


# Router gọi tool
TOOL_ROUTER = {
    "query_guest_health_and_bar_inventory": execute_query_guest_health_and_bar_inventory,
    "dispense_smart_drink": execute_dispense_smart_drink,
    # Fallback alias cũ để tránh gãy khi gọi từ client cũ
    "query_bar_inventory_and_intake": lambda user_id, target_mood="": execute_query_guest_health_and_bar_inventory(user_id, target_mood),
    "academic_query": lambda student_id: execute_query_guest_health_and_bar_inventory("USR001"),
    "schedule_appointment": lambda student_id, datetime_str, advisor_name="": execute_dispense_smart_drink(
        "USR001", "Trà hoa cúc mật ong ấm", "HERBAL_TEA", False, False, ["chamomile_tea", "raw_forest_honey"], "NÓNG", "50%"
    )
}


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool cho MCP Server"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
