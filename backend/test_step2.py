import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.core.coin import generate_six_lines
from app.core.hexagram import HexagramResult

def print_analysis(hex_res: HexagramResult, title: str):
    print(f"\n{'='*25} {title} {'='*25}")
    orig = hex_res.original_hex
    print(f"【本卦】: {orig.name}  | 宫位: {orig.palace}宫 ({orig.element}) | 类型: {orig.generation_type}")
    print(f"       世爻: 第{orig.shi_pos}爻 | 应爻: 第{orig.ying_pos}爻 | 结构: 上{orig.upper_meta['name']} 下{orig.lower_meta['name']}")

    if hex_res.transformed_hex:
        trans = hex_res.transformed_hex
        moving_str = "、".join([f"第{p}爻" for p in hex_res.moving_lines])
        print(f"【动爻】: {moving_str} 发动")
        print(f"【变卦】: {trans.name}  | 宫位: {trans.palace}宫 ({trans.element}) | 类型: {trans.generation_type}")
    else:
        print("【变卦】: 无动爻，纯静卦")

    print("-" * 60)
    for line in reversed(hex_res.lines):
        d = line.to_dict()
        pos = d['position']
        shi_ying = "世" if pos == orig.shi_pos else ("应" if pos == orig.ying_pos else "  ")
        wood = "[==== 整木 ====]" if d['wood_type'] == 'solid_wood' else "[==左==]  [==右==]"
        mark = f"({d['mark']})" if d['mark'].strip() else "   "
        print(f"第{pos}爻 [{d['line_name']}] {shi_ying}  {d['symbol']} {mark}  {wood:<18} 动效: {d['anim_type']}")

if __name__ == "__main__":
    # 1. 静卦：坤为地
    kun_sums = [8, 8, 8, 8, 8, 8]
    kun_res = HexagramResult(generate_six_lines(kun_sums))
    print_analysis(kun_res, "静卦验证 (坤为地)")

    # 2. 动卦测试 A：火地晋 初爻老阴动 (下坤000变震100 -> 火雷噬嗑)
    jin_sums_1 = [6, 8, 8, 7, 8, 7]
    jin_res_1 = HexagramResult(generate_six_lines(jin_sums_1))
    print_analysis(jin_res_1, "动爻变卦验证 (火地晋初爻动 -> 火雷噬嗑)")

    # 3. 动卦测试 B：火地晋 三爻老阴动 (下坤000变艮001 -> 火山旅)
    jin_sums_3 = [8, 8, 6, 7, 8, 7]
    jin_res_3 = HexagramResult(generate_six_lines(jin_sums_3))
    print_analysis(jin_res_3, "动爻变卦验证 (火地晋三爻动 -> 火山旅)")
