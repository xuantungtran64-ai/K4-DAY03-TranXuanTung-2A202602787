# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Trần Xuân Tùng  
> **Mã Sinh Viên / Mã Học viên:** 2A202602787  
> **Chủ đề Lựa chọn:** Trợ lý Tác tử AI Smart Mixologist & Barista — Quầy Pha Chế Thông Minh Kiểm Soát Dị Ứng, Y Tế & Nồng Độ Cồn/Caffeine (MCP Enhanced)  
> **Khung kiến trúc:** ReAct Agent (Level 3) + Model Context Protocol (MCP JSON-RPC 2.0)  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

### 📌 Mô tả Bối cảnh Bài toán (Problem Statement & Context)
Hệ thống quầy pha chế tự động phục vụ đa dạng danh mục thức uống: **Cocktail có cồn, Mocktail giải nhiệt, Cà phê đậm vị, Trà thảo mộc thư giãn và Nước ép thanh lọc**.  
Thay vì chỉ nhận order và pha chế thụ động như máy bán hàng thông thường, tác tử **AI Smart Mixologist** đóng vai trò là một chuyên gia sinh trắc học và pha chế:
1. **Kiểm soát Dị ứng Thực phẩm:** Tự động đối chiếu thành phần nguyên liệu với tiền sử dị ứng của khách hàng (`dairy` - sữa bò, `peanut` - đậu phộng, `pineapple` - dứa).
2. **Kiểm soát Chống chỉ định Y tế & Thuốc:** Khách đang uống thuốc kháng sinh (`Amoxicillin`) hoặc hạ sốt (`Paracetamol`) tuyệt đối bị **CẤM CỒN** do nguy cơ hoại tử gan cấp và sốc phản vệ.
3. **Tuân thủ Luật An toàn Giao thông:** Khách tự lái xe ô tô bắt buộc nồng độ cồn $\text{BAC} = 0.00\%$.
4. **Theo dõi Hạn mức Tiêu thụ theo Thời gian:** Kiểm soát lượng cồn (Alcohol Units) và caffeine ($mg$) đã nạp trong ngày, mốc thời gian uống gần nhất để tránh quá tải tim mạch hoặc mất ngủ.

---

### 📊 Ma trận Đánh giá 4 Tiêu chí Agentic Fit

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | **5 / 5** | **Chuỗi suy luận phức tạp gồm 5 bước logic nối tiếp nhau:**<br>1. *Tiếp nhận nhu cầu:* Phân tích tâm trạng, thời điểm yêu cầu (sáng/tối) và món khách muốn gọi.<br>2. *Truy xuất hồ sơ y tế:* Tra cứu tiền sử bệnh án, thuốc đang dùng, tình trạng lái xe và dị ứng.<br>3. *Tính toán hạn mức sinh học:* Đánh giá lượng cồn/caffeine đã nạp so với ngưỡng tối đa cho phép trong ngày.<br>4. *Kiểm định tồn kho thực tế:* Rà soát các nguyên liệu pha chế có sẵn hoặc hết hàng.<br>5. *Ra quyết định tối ưu:* Phát lệnh pha chế tự động HOẶC từ chối khéo léo kèm giải thích y khoa và chủ động đề xuất + kích hoạt pha món thay thế an toàn. |
| **2. Tool Interaction** | **5 / 5** | **Bắt buộc tương tác 2 chiều qua giao thức MCP Server độc lập:**<br>• `query_guest_health_and_bar_inventory`: Truy xuất cơ sở dữ liệu hồ sơ y tế cá nhân và tồn kho nguyên liệu thời gian thực.<br>• `dispense_smart_drink`: Gửi gói tin lệnh điều khiển phần cứng máy pha IoT tự động.<br>*Nếu chỉ dùng LLM Chatbot thuần túy (Level 2), mô hình sẽ bị ảo giác (hallucination) nghiêm trọng về tiền sử bệnh của khách và tình trạng kho hàng, gây nguy cơ ngộ độc/dị ứng chết người.* |
| **3. Dynamic Decision** | **5 / 5** | **Hành động tiếp theo phụ thuộc 100% vào kết quả quan sát (Observation):**<br>• *Nếu phát hiện dùng kháng sinh hoặc lái xe:* Lập tức CHẶN đồ uống có cồn, tự động rẽ nhánh sang dòng Mocktail hoặc Trà thảo mộc ấm.<br>• *Nếu phát hiện dị ứng sữa bò (`dairy`):* Tự động thay thế bằng Sữa yến mạch hữu cơ Oatside.<br>• *Nếu caffeine đã nạp $\ge 280\text{mg}$:* Cảnh báo không dùng cà phê đậm, hướng sang Trà hoa cúc La Mã $0\text{mg}$ caffeine.<br>• *Nếu nguyên liệu hết hàng (`OUT_OF_STOCK`):* Linh hoạt đề xuất hương vị tương đương. |
| **4. Long Horizon Goal** | **5 / 5** | **Duy trì mục tiêu kép xuyên suốt toàn bộ phiên làm việc:**<br>• Mục tiêu 1: Bảo vệ an toàn sinh học và sức khỏe tính mạng của khách hàng.<br>• Mục tiêu 2: Đảm bảo trải nghiệm thưởng thức đồ uống hài lòng và hoàn tất chu trình pha chế vật lý.<br>Tác tử lưu giữ định danh khách hàng, trạng thái sinh trắc và thông số đơn hàng cho đến khi hệ thống quầy bar xuất mã đơn thành công. |
| **TỔNG ĐIỂM AGENTIC FIT** | **20 / 20** | **ĐẠT ĐIỂM TUYỆT ĐỐI (20/20):** Bài toán chứng minh rõ rệt sự vượt trội và tính tất yếu của ReAct Agent (Level 3) so với Chatbot thông thường. |

---

### 🛠️ Danh mục Công cụ Ngoại vi Triển khai qua MCP Server
1. 🔍 **`query_guest_health_and_bar_inventory`**: Tra cứu hồ sơ dị ứng, đơn thuốc đang dùng, tình trạng lái xe, lượng cồn & caffeine đã nạp trong ngày, và tồn kho nguyên liệu quầy bar.
2. 🍸 **`dispense_smart_drink`**: Thẩm định an toàn sinh học đa tầng và phát lệnh pha chế tự động với các tham số nhiệt độ, độ ngọt, và công thức thành phần.

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Hãy kiểm tra hồ sơ y tế, tiền sử dị ứng và lượng cồn/caffeine đã nạp hôm nay của khách hàng USR001.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "query_guest_health_and_bar_inventory",
    "arguments": {
      "user_id": "USR001",
      "target_mood": "Thư giãn sau giờ làm"
    },
    "observation": {
      "status": "SUCCESS",
      "user_id": "USR001",
      "health_profile": {
        "full_name": "Trần Xuân Tùng",
        "current_medication": "Kháng sinh Amoxicillin & Paracetamol (Điều trị viêm họng)",
        "medical_contraindications": [
          "STRICT_NO_ALCOHOL (Nguy cơ ngộ độc gan cấp và sốc phản vệ)",
          "LIMIT_CAFFEINE (Tránh đau dạ dày)"
        ],
        "driving_status": "Đang tự lái xe ô tô (Yêu cầu BAC = 0.00% tuyệt đối)",
        "allergies": [
          "dairy (dị ứng sữa bò/lactose)",
          "peanut (dị ứng đậu phộng)"
        ],
        "today_consumption": {
          "caffeine_consumed_mg": 280,
          "max_daily_caffeine_mg": 300,
          "last_caffeine_time": "14:30 (Đã nạp 2 shot Espresso chiều)",
          "alcohol_units_consumed": 0.0,
          "max_daily_alcohol_units": 0.0
        },
        "safe_allowance": {
          "remaining_caffeine_mg": 20,
          "remaining_alcohol_units": 0.0,
          "recommendation": "Chỉ được dùng đồ uống không cồn (Mocktail/Trà thảo mộc), không dùng sữa động vật (dairy), hạn chế tối đa caffeine vào buổi tối."
        }
      }
    },
    "latency_ms": 115.4
  },
  {
    "step": 1,
    "query": "Hãy pha cho khách hàng USR002 một ly Cocktail Gin Tonic nồng độ vừa phải, phục vụ đá với độ ngọt 30%.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "dispense_smart_drink",
    "arguments": {
      "user_id": "USR002",
      "drink_name": "Cocktail Gin Tonic",
      "category": "COCKTAIL_ALCOHOLIC",
      "contains_alcohol": true,
      "contains_caffeine": false,
      "ingredients": [
        "gin_bombay",
        "tonic_water"
      ],
      "temperature": "ĐÁ",
      "sweetness_level": "30%"
    },
    "observation": {
      "status": "SUCCESS",
      "order_id": "SMART-BAR-USR002-88",
      "user_id": "USR002",
      "guest_name": "Nguyễn Hoàng Nam",
      "drink_name": "Cocktail Gin Tonic",
      "category": "COCKTAIL_ALCOHOLIC",
      "safety_audit": {
        "allergy_safe": true,
        "medication_safe": true,
        "intake_limits_approved": true
      },
      "estimated_prep_seconds": 75,
      "message": "Thẩm định an toàn sinh trắc HOÀN TOÀN ĐẠT CHUẨN! Lệnh pha chế 'Cocktail Gin Tonic' (COCKTAIL_ALCOHOLIC, ĐÁ, ngọt 30%) đã được gửi tới hệ thống quầy bar. Đồ uống sẽ sẵn sàng sau 75 giây (Mã đơn: SMART-BAR-USR002-88)."
    },
    "latency_ms": 98.2
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã thiết lập môi trường và cấu trúc Native Tool Calling qua giao thức Model Context Protocol (MCP JSON-RPC 2.0).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 4 / 4 lượt yêu cầu Tool (TC02, TC03, TC04, TC05; riêng TC01 trả lời trực tiếp không cần Tool).
- **Trạng thái xuất log vết (Observability):** Đã ghi thành công toàn bộ chuỗi Thought $\rightarrow$ Action $\rightarrow$ Observation $\rightarrow$ Final Answer ra tệp `docs/trace_waterfall.json`.
- **Kết quả đẩy Repo nộp bài:** [x] Đã sẵn sàng Commit và Push toàn bộ mã nguồn lên GitHub cá nhân `K4-DAY03-TranXuanTung-2A202602787`.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
