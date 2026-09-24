import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.core.coin import generate_six_lines
from app.core.hexagram import HexagramResult
from app.core.najia import NaJiaEngine
from app.core.time_engine import TimeEngine

def run_time_engine_test():
    print(f"\n{'='*25} 时空干支、旬空月破与状态诊断测试 {'='*25}")

    # 构造测试时间：酉月（八月秋金当令），丁卯日（丁卯旬戌亥空，日冲酉，月建酉冲卯）
    # 2026年9月23日处于秋分前后，为酉月
    dt = datetime(2026, 9, 23, 10, 30, 0)
    time_engine = TimeEngine(dt)
    time_info = time_engine.to_dict()

    print(f"公历时间: {time_info['datetime_str']}")
    print(f"四柱八字: {time_info['year_ganzhi']}年  {time_info['month_ganzhi']}月  {time_info['day_ganzhi']}日  {time_info['time_ganzhi']}时")
    print(f"月令: {time_info['month_branch']}({time_info['month_element']}) | 日辰: {time_info['day_branch']}({time_info['day_element']})")
    print(f"日旬空: {time_info['day_kongwang']} | 月破之支: {time_info['month_po']}")
    print("-" * 75)

    # 起卦测试：火地晋 初爻动（未土化子水）、三爻动（卯木化申金，卯临月破且动化回头克）
    # 点数：初爻老阴(6)、二爻少阴(8)、三爻老阴(6)、四爻少阳(7)、五爻少阴(8)、上爻少阳(7)
    sums = [6, 8, 6, 7, 8, 7]
    hex_res = HexagramResult(generate_six_lines(sums))

    # 使用根据起卦时间推导出的日干起六神
    engine = NaJiaEngine(hex_res, day_stem=time_info["day_stem"])
    assembled = engine.assemble_full_hexagram()

    # 结合时空信息诊断各爻状态
    diagnosed_lines = time_engine.diagnose_lines(assembled)

    print(f"卦名: {assembled['original_name']} 变 {assembled['transformed_name']}")
    print("-" * 75)
    print(f"{'爻位与六神':<14} | {'纳支六亲':<12} | {'动变信息':<18} | {'旺衰破空诊断'}")
    print("-" * 75)

    for line in reversed(diagnosed_lines):
        pos = line["position"]
        tags_str = "【" + " / ".join(line["status_tags"]) + "】" if line["status_tags"] else "平稳"
        change_str = line["change_relationship"] if line["change_relationship"] else "——"
        sy_str = "世" if line["is_shi"] else ("应" if line["is_ying"] else "  ")

        print(f"第{pos}爻 [{line['line_name']}] {sy_str} {line['six_god']} | "
              f"{line['six_relative']}{line['branch']}({line['element']}){' ':3s} | "
              f"{change_str:<16} | {tags_str}")

if __name__ == "__main__":
    run_time_engine_test()
