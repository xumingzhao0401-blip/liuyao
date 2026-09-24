import sys
import os

# 确保 Python 能正确导入 backend 目录下的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.core.coin import generate_six_lines

def print_hexagram(lines, title):
    print(f"\n{'='*20} {title} {'='*20}")
    # 传统卦象展示习惯：从上爻（第6爻，索引5）向下展示到初爻（第1爻，索引0）
    for line in reversed(lines):
        d = line.to_dict()
        wood_display = "[==== 整木 ====]" if d['wood_type'] == 'solid_wood' else "[==左==]  [==右==]"
        mark_display = f"({d['mark']})" if d['mark'].strip() else "   "
        print(f"第{d['position']}爻 [{d['line_name']}]  {d['symbol']:2s} {mark_display}  "
              f"{wood_display:<20} 动效:{d['anim_type']:<11} 点数:{d['coin_sum']} ({d['nature_name']})")

if __name__ == "__main__":
    # 1. 测试随机摇卦
    random_lines = generate_six_lines()
    print_hexagram(random_lines, "随机起卦测试")

    # 2. 测试固定点数（初九动、九五动：9, 7, 7, 7, 9, 7）
    fixed_sums = [9, 7, 7, 7, 9, 7]
    fixed_lines = generate_six_lines(fixed_sums)
    print_hexagram(fixed_lines, "固定动爻测试 (初九、九五动)")
