"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return (
            f"[Mock Chatbot Response]: Xin chào! Tôi là Trợ lý pha chế ảo. "
            f"Về câu hỏi '{prompt}', trong pha chế, việc kết hợp đồ uống cần chú ý đến sức khỏe và tương tác sinh học. "
            f"Lưu ý tôi không có công cụ kết nối dữ liệu y tế cá nhân hay điều khiển máy pha tự động."
        )

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        
        # Nhận diện intent gọi món cụ thể / lệnh pha chế
        if "pha" in prompt_lower or "dispense" in prompt_lower or "order" in prompt_lower or "đặt" in prompt_lower:
            if "caramel" in prompt_lower:
                return {
                    "type": "tool_call",
                    "tool_name": "dispense_smart_drink",
                    "arguments": {
                        "user_id": "USR001",
                        "drink_name": "Cà phê Caramel Muối Sữa Bò Tươi",
                        "category": "COFFEE_CAFFEINE",
                        "contains_alcohol": False,
                        "contains_caffeine": True,
                        "ingredients": ["espresso_arabica", "syrup_salted_caramel", "cow_dairy_milk"],
                        "temperature": "ĐÁ",
                        "sweetness_level": "50%"
                    },
                    "thought": "Khách hàng USR001 yêu cầu pha Cà phê Caramel Muối với sữa bò tươi. Tôi sẽ chuyển tiếp lệnh tới dispense_smart_drink để kiểm định dị ứng và tồn kho."
                }
            elif "gin" in prompt_lower or "cocktail" in prompt_lower or "rượu" in prompt_lower:
                uid = "USR001" if "usr001" in prompt_lower else ("USR003" if "usr003" in prompt_lower else "USR002")
                return {
                    "type": "tool_call",
                    "tool_name": "dispense_smart_drink",
                    "arguments": {
                        "user_id": uid,
                        "drink_name": "Cocktail Gin Tonic",
                        "category": "COCKTAIL_ALCOHOLIC",
                        "contains_alcohol": True,
                        "contains_caffeine": False,
                        "ingredients": ["gin_bombay", "tonic_water"],
                        "temperature": "ĐÁ",
                        "sweetness_level": "30%"
                    },
                    "thought": f"Khách hàng {uid} yêu cầu Cocktail có cồn. Tôi sẽ gọi dispense_smart_drink để thẩm định an toàn y tế và nồng độ cồn."
                }
            else:
                return {
                    "type": "tool_call",
                    "tool_name": "dispense_smart_drink",
                    "arguments": {
                        "user_id": "USR001",
                        "drink_name": "Trà hoa cúc mật ong ấm",
                        "category": "HERBAL_TEA",
                        "contains_alcohol": False,
                        "contains_caffeine": False,
                        "ingredients": ["chamomile_tea", "raw_forest_honey"],
                        "temperature": "NÓNG",
                        "sweetness_level": "30%"
                    },
                    "thought": "Khách hàng cần đồ uống nhẹ nhàng, thư giãn. Tôi đề xuất và phát lệnh pha Trà hoa cúc mật ong ấm an toàn tuyệt đối."
                }

        # Nhận diện intent tra cứu hồ sơ sức khỏe & quầy bar
        elif "tra cứu" in prompt_lower or "kiểm tra" in prompt_lower or "usr" in prompt_lower or "caffeine" in prompt_lower or "cồn" in prompt_lower:
            uid = "USR001" if "usr001" in prompt_lower else ("USR003" if "usr003" in prompt_lower else "USR002")
            return {
                "type": "tool_call",
                "tool_name": "query_guest_health_and_bar_inventory",
                "arguments": {"user_id": uid, "target_mood": "Thư giãn sau giờ làm"},
                "thought": f"Khách hàng yêu cầu kiểm tra dữ liệu y tế/hạn mức. Tôi sẽ gọi query_guest_health_and_bar_inventory cho mã '{uid}'."
            }

        # Câu hỏi kiến thức chung
        else:
            return {
                "type": "text",
                "content": "[Mock Agent Response]: Theo khuyến cáo y khoa, tuyệt đối KHÔNG sử dụng đồ uống có cồn khi đang dùng kháng sinh (như Amoxicillin) hoặc thuốc hạ sốt (Paracetamol) vì sẽ gây độc gan cấp tính. Người tự lái xe cũng cần tuân thủ nồng độ cồn bằng 0.00%. Quầy bar thông minh luôn sẵn sàng các dòng Mocktail và Trà hoa cúc thanh lọc tốt cho sức khỏe!",
                "thought": "Câu hỏi tư vấn kiến thức an toàn đồ uống và y tế, trả lời trực tiếp không cần gọi Tool."
            }


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.0-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []
            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                temperature=0.2
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }

        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
