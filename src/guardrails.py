"""
🛡️ INPUT GUARDRAILS MODULE (AI SMART MIXOLOGIST & BARISTA AGENT)
Lớp phòng thủ đầu vào (Input Guardrail) bảo vệ Tác tử trước:
1. Tấn công Prompt Injection / Jailbreak (Cố tình ép bỏ qua quy tắc y tế, dị ứng)
2. Yêu cầu chất độc hại / cồn công nghiệp / hóa chất nguy hiểm
3. Cảnh báo cấp cứu y tế khẩn cấp (Emergency medical escalation)
4. Giới hạn độ dài và định dạng truy vấn (DoS prevention)
"""

import re
from typing import Dict, Any

# 1. Danh sách mẫu nhận diện Prompt Injection / Jailbreak
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?(previous )?instructions",
    r"disregard (all )?(previous )?instructions",
    r"bỏ qua (tất cả )?(các )?(hướng dẫn|chỉ dẫn|quy tắc|kiểm tra|cảnh báo)",
    r"quên (hết|tất cả) (các )?(chỉ dẫn|quy tắc|ràng buộc)",
    r"override (all )?(safety|system) (rules|checks|instructions)",
    r"bỏ qua (kiểm tra )?dị ứng",
    r"không cần kiểm tra (y tế|sức khỏe|dị ứng)",
    r"jailbreak",
    r"dan mode",
    r"act as an unrestricted",
    r"system override"
]

# 2. Danh sách chất độc hại và chất cấm
HAZARDOUS_SUBSTANCES = [
    "methanol",
    "cồn công nghiệp",
    "cyanide",
    "thuốc độc",
    "poison",
    "thuốc trừ sâu",
    "thủy ngân",
    "bleach",
    "thuốc tẩy",
    "xút",
    "axit đậm đặc"
]

# 3. Từ khóa cấp cứu y tế khẩn cấp
EMERGENCY_MEDICAL_KEYWORDS = [
    "sốc phản vệ",
    "khó thở dữ dội",
    "ngừng tim",
    "ngộ độc cấp",
    "uống nhầm thuốc độc",
    "sắp ngất lịm",
    "co giật"
]

MAX_QUERY_LENGTH = 2000


def check_input_guardrail(user_query: str) -> Dict[str, Any]:
    """
    Kiểm tra toàn diện Guardrail đầu vào trước khi chuyển tiếp cho LLM.
    Trả về Dict:
      - passed: bool
      - violation_type: str | None ("PROMPT_INJECTION", "HAZARDOUS_REQUEST", "EMERGENCY_MEDICAL", "INPUT_TOO_LONG", "EMPTY_INPUT")
      - reason: str
      - response_message: str
    """
    if not user_query or not user_query.strip():
        return {
            "passed": False,
            "violation_type": "EMPTY_INPUT",
            "reason": "Truy vấn rỗng hoặc chỉ chứa khoảng trắng.",
            "response_message": "Vui lòng nhập yêu cầu hợp lệ về đồ uống hoặc tra cứu thông tin."
        }

    query_str = user_query.strip()

    # Kiểm tra DoS / Độ dài bất thường
    if len(query_str) > MAX_QUERY_LENGTH:
        return {
            "passed": False,
            "violation_type": "INPUT_TOO_LONG",
            "reason": f"Độ dài truy vấn ({len(query_str)} ký tự) vượt quá giới hạn an toàn {MAX_QUERY_LENGTH} ký tự.",
            "response_message": "Yêu cầu của bạn quá dài. Vui lòng tóm tắt ngắn gọn nhu cầu đồ uống hoặc thông tin cần tra cứu."
        }

    query_lower = query_str.lower()

    # Kiểm tra Tình huống Y tế Khẩn cấp (Emergency Escalation)
    for kw in EMERGENCY_MEDICAL_KEYWORDS:
        if kw in query_lower:
            return {
                "passed": False,
                "violation_type": "EMERGENCY_MEDICAL",
                "reason": f"Phát hiện tình huống cấp cứu y tế khẩn cấp liên quan đến từ khóa '{kw}'.",
                "response_message": (
                    "🚨 [CẢNH BÁO Y TẾ KHẨN CẤP]: Nếu bạn hoặc người bên cạnh đang gặp triệu chứng nguy kịch "
                    "(khó thở, sốc phản vệ, co giật hoặc ngộ độc cấp tính), vui lòng GỌI NGAY CẤP CỨU 115 "
                    "hoặc đến phòng cấp cứu bệnh viện gần nhất ngay lập tức! Hệ thống AI quầy bar không thể thay thế cấp cứu y tế."
                )
            }

    # Kiểm tra Yêu cầu Hóa chất / Chất độc hại
    for toxic in HAZARDOUS_SUBSTANCES:
        if toxic in query_lower:
            return {
                "passed": False,
                "violation_type": "HAZARDOUS_REQUEST",
                "reason": f"Yêu cầu chứa chất cấm hoặc hóa chất độc hại: '{toxic}'.",
                "response_message": (
                    f"⛔ [TỪ CHỐI AN TOÀN]: Hệ thống quầy bar tuyệt đối từ chối tiếp nhận hoặc xử lý "
                    f"nguyên liệu nguy hại '{toxic}'. Lệnh đã bị hủy để đảm bảo an toàn tính mạng."
                )
            }

    # Kiểm tra Prompt Injection / Jailbreak
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, query_lower):
            return {
                "passed": False,
                "violation_type": "PROMPT_INJECTION",
                "reason": f"Phát hiện mẫu tấn công can thiệp chỉ dẫn (Prompt Injection): '{pattern}'.",
                "response_message": (
                    "🛡️ [INPUT GUARDRAIL BLOCKED]: Hệ thống phát hiện nỗ lực can thiệp hoặc vô hiệu hóa "
                    "hàng rào an toàn y sinh của Tác tử. Tất cả quy định kiểm soát dị ứng, chống chỉ định thuốc "
                    "và nồng độ cồn BAC đều được thực thi nghiêm ngặt theo chính sách an toàn."
                )
            }

    return {
        "passed": True,
        "violation_type": None,
        "reason": "Truy vấn hợp lệ và an toàn.",
        "response_message": ""
    }

