import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.core.coin import generate_six_lines
from app.core.hexagram import HexagramResult
from app.core.najia import NaJiaEngine
from app.core.time_engine import TimeEngine
from app.core.classics_kb import EvidenceEngine, CLASSICS_CATALOG

def run_evidence_test():
    print(f"\n{'='*25} 经典典籍引证与有理有据断卦验证 {'='*25}")

    # 1. 模拟起卦时间
    dt = datetime(2026, 9, 23, 10, 30, 0)
    time_engine = TimeEngine(dt)
    time_info = time_engine.to_dict()

    # 2. 火地晋 初爻老阴动(6)、三爻老阴动(6)
    sums = [6, 8, 6, 7, 8, 7]
    hex_res = HexagramResult(generate_six_lines(sums))

    # 3. 纳甲与六神
    engine = NaJiaEngine(hex_res, day_stem=time_info["day_stem"])
    assembled = engine.assemble_full_hexagram()

    # 4. 诊断状态
    diagnosed_lines = time_engine.diagnose_lines(assembled)

    # 5. 自动检索典籍依据
    evidences = EvidenceEngine.extract_evidences(diagnosed_lines)

    print(f"卦象: {assembled['original_name']} 变 {assembled['transformed_name']}")
    print(f"四柱: {time_info['year_ganzhi']}年 {time_info['month_ganzhi']}月 {time_info['day_ganzhi']}日 {time_info['time_ganzhi']}时")
    print(f"匹配出处条目数: {len(evidences)} 条")
    print("=" * 75)

    for idx, item in enumerate(evidences, 1):
        print(f"【依据 {idx}】针对目标: {item['target']}")
        print(f"▶ 触发象数特征: 【{item['phenomenon']}】")
        print(f"▶ 典籍出处: {item['book_title']} · {item['chapter']}")
        print(f"▶ 原文依据: “{item['original_text']}”")
        print(f"▶ 学理解析: {item['explanation']}")
        print("-" * 75)

if __name__ == "__main__":
    run_evidence_test()
