from typing import List, Dict, Any, Optional
from app.core.constants import COIN_SUM_MAP
from app.core.bagua_tables import TRIGRAM_BINARY_MAP, HEXAGRAM_PALACE_MAP
from app.core.coin import YaoResult

class HexagramDetail:
    def __init__(self, upper_tri: tuple, lower_tri: tuple):
        """
        upper_tri: 上卦三爻二进制元组 (4爻, 5爻, 6爻)
        lower_tri: 下卦三爻二进制元组 (1爻, 2爻, 3爻)
        """
        self.upper_meta = TRIGRAM_BINARY_MAP[upper_tri]
        self.lower_meta = TRIGRAM_BINARY_MAP[lower_tri]

        # 纯卦与复合卦命名规则
        if self.upper_meta["name"] == self.lower_meta["name"]:
            up_name = self.upper_meta["name"]
            low_name = self.lower_meta["name"]
        else:
            up_name = self.upper_meta["nature"]
            low_name = self.lower_meta["nature"]

        palace_info = HEXAGRAM_PALACE_MAP.get((up_name, low_name))
        if not palace_info:
            raise ValueError(f"未找到六十四卦定义: 上卦 {up_name}, 下卦 {low_name}")

        self.name, self.palace, self.element, self.generation_type, self.shi_pos = palace_info
        # 应爻与世爻相隔 3 位 (1-based)
        self.ying_pos = (self.shi_pos + 2) % 6 + 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "palace": self.palace,
            "element": self.element,
            "generation_type": self.generation_type,
            "shi_position": self.shi_pos,
            "ying_position": self.ying_pos,
            "upper_trigram": self.upper_meta["name"],
            "lower_trigram": self.lower_meta["name"]
        }

class HexagramResult:
    def __init__(self, lines: List[YaoResult]):
        if len(lines) != 6:
            raise ValueError("构建卦象必须包含完整的 6 个爻。")
        self.lines = lines

        # 提取本卦二进制元组 (lines[0..2] 下卦, lines[3..5] 上卦)
        orig_lower = tuple(line.meta["original_bit"] for line in lines[0:3])
        orig_upper = tuple(line.meta["original_bit"] for line in lines[3:6])
        self.original_hex = HexagramDetail(orig_upper, orig_lower)

        # 动爻位置统一使用 1-based (第 1 爻至第 6 爻)
        self.moving_lines = [line.position + 1 for line in lines if line.meta["is_moving"]]

        # 若存在动爻，推导变卦
        if self.moving_lines:
            trans_lower = tuple(line.meta["transformed_bit"] for line in lines[0:3])
            trans_upper = tuple(line.meta["transformed_bit"] for line in lines[3:6])
            self.transformed_hex: Optional[HexagramDetail] = HexagramDetail(trans_upper, trans_lower)
        else:
            self.transformed_hex = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_hexagram": self.original_hex.to_dict(),
            "has_changes": bool(self.moving_lines),
            "moving_lines": self.moving_lines,
            "transformed_hexagram": self.transformed_hex.to_dict() if self.transformed_hex else None,
            "lines": [line.to_dict() for line in self.lines]
        }
