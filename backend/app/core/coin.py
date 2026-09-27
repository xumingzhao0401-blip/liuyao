import random
from typing import List, Dict, Any, Optional
from app.core.constants import COIN_SUM_MAP, YIN_YANG_NAMES

class YaoResult:
    def __init__(self, position: int, coin_sum: int):
        """
        position: 爻位索引，从 0（初爻）到 5（上爻）
        coin_sum: 三枚铜钱点数和 (6, 7, 8, 9)
        """
        if coin_sum not in COIN_SUM_MAP:
            raise ValueError(f"无效的铜钱和: {coin_sum}，必须为 6, 7, 8 或 9。")
        
        self.position = position
        self.coin_sum = coin_sum
        self.meta = COIN_SUM_MAP[coin_sum]
        
        # 根据本卦阴阳确定爻名（阳为九，阴为六）
        nature_type = "yang" if self.meta["original_bit"] == 1 else "yin"
        self.line_name = YIN_YANG_NAMES[nature_type][position]

    def to_dict(self) -> Dict[str, Any]:
        """输出给前端渲染的数据结构（包含木块形态与动效元数据）"""
        return {
            "position": self.position + 1,          # 1 至 6 位 (从下到上)
            "line_name": self.line_name,             # 初九 / 六二 等
            "coin_sum": self.coin_sum,
            "nature_name": self.meta["name"],        # 少阳 / 老阳 等
            "symbol": self.meta["symbol_original"],  # — 或 --
            "mark": self.meta["symbol_mark"],        # ○ 或 × 或 空格
            "is_moving": self.meta["is_moving"],
            "original_bit": self.meta["original_bit"],
            "transformed_bit": self.meta["transformed_bit"],
            "wood_type": self.meta["wood_type"],     # solid_wood / split_wood
            "anim_type": self.meta["anim_type"],     # wood_split / wood_merge / none
            "mark_color": self.meta["mark_color"]
        }

def toss_single_coin() -> int:
    """模拟一枚铜钱落地：字(正面)=2，背(背面)=3"""
    return random.choice([2, 3])

def toss_three_coins() -> int:
    """模拟一次掷三枚铜钱的总和 (范围 6~9)"""
    return sum(toss_single_coin() for _ in range(3))

def generate_six_lines(manual_sums: Optional[List[int]] = None) -> List[YaoResult]:
    """
    生成从初爻至上爻（从下至上）的 6 个爻对象
    支持传入指定点数数组（供测试或手动录入）或完全随机摇卦
    """
    if manual_sums:
        if len(manual_sums) != 6:
            raise ValueError("必须提供完整的 6 个爻点数。")
        sums = manual_sums
    else:
        sums = [toss_three_coins() for _ in range(6)]

    # 严格按照从底到顶（初爻 -> 上爻）的次序构建
    return [YaoResult(pos, val) for pos, val in enumerate(sums)]
