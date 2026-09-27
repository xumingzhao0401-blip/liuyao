import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.core.coin import generate_six_lines
from app.core.hexagram import HexagramResult
from app.core.najia import NaJiaEngine

def run_najia_test():
    print(f"\n{'='*25} 纳甲、六亲、六神、伏神 完整验证 {'='*25}")
    # 模拟：火地晋 初爻老阴发动 (6, 8, 8, 7, 8, 7)，起卦日设定为 丁酉日 (日干: 丁)
    day_stem = "丁"
    sums = [6, 8, 8, 7, 8, 7]
    hex_res = HexagramResult(generate_six_lines(sums))

    engine = NaJiaEngine(hex_res, day_stem=day_stem)
    assembled = engine.assemble_full_hexagram()

    orig_name = assembled["original_name"]
    trans_name = assembled["transformed_name"]
    palace_elem = assembled["palace_element"]

    print(f"日干: {day_stem}日 | 本卦: {orig_name} (宫位五行: {palace_elem}) | 变卦: {trans_name}")
    if assembled["missing_relations"]:
        print(f"缺六亲: {', '.join(assembled['missing_relations'])}")
    print("-" * 75)
    print(f"{'伏神':<14} | {'六神':<4} | {'本卦爻位':<8} | {'纳支五行六亲':<14} | {'变卦动爻纳甲':<14}")
    print("-" * 75)

    orig_lines = assembled["original_lines"]
    trans_lines = assembled["transformed_lines"]

    # 从第6爻向下打印
    for i in reversed(range(6)):
        orig = orig_lines[i]
        trans = trans_lines[i] if trans_lines else None

        # 伏神展示
        if orig["fushen"]:
            fu = orig["fushen"]
            fu_str = f"伏 {fu['six_relative']}{fu['branch']}({fu['element']})"
        else:
            fu_str = " " * 12

        # 世应标识
        sy_str = "世" if orig["is_shi"] else ("应" if orig["is_ying"] else "  ")

        # 变爻展示
        if orig["is_moving"] and trans:
            trans_str = f"化 {trans['six_relative']}{trans['branch']}({trans['element']}) {trans['symbol']}"
        else:
            trans_str = ""

        print(f"{fu_str:<12} | {orig['six_god']:<4} | 第{orig['position']}爻 [{orig['line_name']}] {sy_str} {orig['symbol']} {orig['mark']} | "
              f"{orig['six_relative']}{orig['branch']}({orig['element']}){' ':4s} | {trans_str}")

if __name__ == "__main__":
    run_najia_test()
