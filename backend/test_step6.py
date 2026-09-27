import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_classics_endpoint():
    print("=== 测试 1: 获取十大经典典籍档案接口 ===")
    response = client.get("/api/classics")
    assert response.status_code == 200
    data = response.json()
    catalog = data["catalog"]
    print(f"成功获取典籍数目: {len(catalog)} 部")
    for k, v in list(catalog.items())[:3]:
        print(f"  * 《{v['title']}》 - {v['dynasty']} · {v['author']}")
    print("-" * 60)

def test_divine_endpoint():
    print("=== 测试 2: 完整起卦排盘接口 (火地晋初爻、三爻动) ===")
    payload = {
        "datetime_str": "2026-09-23 10:30:00",
        "manual_sums": [6, 8, 6, 7, 8, 7] # 0位初六(动), 2位六三(动)
    }
    response = client.post("/api/divine", json=payload)
    assert response.status_code == 200
    res = response.json()

    print(f"干支四柱: {res['time_info']['year_ganzhi']}年 {res['time_info']['month_ganzhi']}月 {res['time_info']['day_ganzhi']}日 {res['time_info']['time_ganzhi']}时")
    print(f"本卦变卦: {res['hexagram']['original_name']} 变 {res['hexagram']['transformed_name']}")
    print(f"提取证据条数: {len(res['evidences'])} 条")

    # 验证木块元数据存在
    first_line = res['lines'][0]
    print(f"初爻木块形态: {first_line['wood_type']}, 动效: {first_line['anim_type']}, 六神: {first_line['six_god']}")
    print("-" * 60)

def test_ai_explain_endpoint():
    print("=== 测试 3: 划词释义与典籍助读接口 ===")
    term_payload = {
        "query_text": "回头克",
        "book_source": "《黄金策·千金赋》"
    }
    response = client.post("/api/ai/explain", json=term_payload)
    assert response.status_code == 200
    print("释义返回内容:")
    print(response.text)
    print("=" * 60)

if __name__ == "__main__":
    # 若环境未装 httpx，用 try-except 提示安装
    try:
        test_classics_endpoint()
        test_divine_endpoint()
        test_ai_explain_endpoint()
        print(">>> 所有 API 端点测试全部通过！ <<<")
    except ModuleNotFoundError as e:
        if "httpx" in str(e):
            print("正在安装 httpx 测试依赖...")
            os.system("pip install httpx --break-system-packages 2>/dev/null || pip install httpx")
            test_classics_endpoint()
            test_divine_endpoint()
            test_ai_explain_endpoint()
            print(">>> 所有 API 端点测试全部通过！ <<<")
        else:
            raise e
