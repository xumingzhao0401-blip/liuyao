"""
浑天甲子纳甲、六亲推导、六神定位与伏神系统
依据《火珠林》、《增删卜易》、《卜筮正宗》
"""

from typing import List, Dict, Any, Optional
from app.core.bagua_tables import TRIGRAM_BINARY_MAP
from app.core.hexagram import HexagramResult, HexagramDetail

# 地支五行属性
BRANCH_ELEMENTS = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 八经卦内外卦纳支 (自下而上 3 个地支)
# 乾金阳顺: 内子寅辰, 外午申戌
# 坤土阴逆: 内未巳卯, 外丑亥酉
# 震木阳顺: 内子寅辰, 外午申戌
# 巽木阴逆: 内丑亥酉, 外未巳卯
# 坎水阳顺: 内寅辰午, 外申戌子
# 离火阴逆: 内卯丑亥, 外酉未巳
# 艮土阳顺: 内辰午申, 外戌子寅
# 兑金阴逆: 内巳卯丑, 外亥酉未
TRIGRAM_NAZHI = {
    "乾": {"inner": ["子", "寅", "辰"], "outer": ["午", "申", "戌"]},
    "坤": {"inner": ["未", "巳", "卯"], "outer": ["丑", "亥", "酉"]},
    "震": {"inner": ["子", "寅", "辰"], "outer": ["午", "申", "戌"]},
    "巽": {"inner": ["丑", "亥", "酉"], "outer": ["未", "巳", "卯"]},
    "坎": {"inner": ["寅", "辰", "午"], "outer": ["申", "戌", "子"]},
    "离": {"inner": ["卯", "丑", "亥"], "outer": ["酉", "未", "巳"]},
    "艮": {"inner": ["辰", "午", "申"], "outer": ["戌", "子", "寅"]},
    "兑": {"inner": ["巳", "卯", "丑"], "outer": ["亥", "酉", "未"]},
}

# 五行生克对应六亲关系: 相对 "我" 的生克
# 关系: 生我(父母), 我生(子孙), 克我(官鬼), 我克(妻财), 同我(兄弟)
ELEMENT_RELATIONS = {
    "生我": "父母",
    "我生": "子孙",
    "克我": "官鬼",
    "我克": "妻财",
    "同我": "兄弟"
}

FIVE_ELEMENTS_ORDER = ["木", "火", "土", "金", "水"]

def get_relation(me: str, target: str) -> str:
    """计算 target 五行相对 me 五行的六亲"""
    if me == target:
        return ELEMENT_RELATIONS["同我"]
    
    me_idx = FIVE_ELEMENTS_ORDER.index(me)
    target_idx = FIVE_ELEMENTS_ORDER.index(target)

    # 生我: target 生成 me (me_idx - 1) % 5 == target_idx
    if (target_idx + 1) % 5 == me_idx:
        return ELEMENT_RELATIONS["生我"]
    # 我生: me 生成 target
    if (me_idx + 1) % 5 == target_idx:
        return ELEMENT_RELATIONS["我生"]
    # 克我: target 克制 me
    if (target_idx + 2) % 5 == me_idx:
        return ELEMENT_RELATIONS["克我"]
    # 我克: me 克制 target
    if (me_idx + 2) % 5 == target_idx:
        return ELEMENT_RELATIONS["我克"]
    
    raise ValueError(f"无法确定五行生克: {me} 与 {target}")

# 日干起六神表 (自初爻至上爻)
SIX_GODS_ORDER = ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]
DAY_STEM_SIX_GOD_START = {
    "甲": 0, "乙": 0,  # 甲乙起青龙
    "丙": 1, "丁": 1,  # 丙丁起朱雀
    "戊": 2,          # 戊日起勾陈
    "己": 3,          # 己日起螣蛇
    "庚": 4, "辛": 4,  # 庚辛起白虎
    "壬": 5, "癸": 5   # 壬癸起玄武
}

def get_six_gods(day_stem: str) -> List[str]:
    """根据日干返回从初爻到上爻的 6 个六神名称"""
    if day_stem not in DAY_STEM_SIX_GOD_START:
        raise ValueError(f"未知天干: {day_stem}，必须为十天干之一。")
    start_idx = DAY_STEM_SIX_GOD_START[day_stem]
    return [SIX_GODS_ORDER[(start_idx + i) % 6] for i in range(6)]

def get_hexagram_branches(lower_trigram_name: str, upper_trigram_name: str) -> List[str]:
    """获取六爻从初至上的 6 个地支"""
    return TRIGRAM_NAZHI[lower_trigram_name]["inner"] + TRIGRAM_NAZHI[upper_trigram_name]["outer"]

class NaJiaEngine:
    def __init__(self, hex_res: HexagramResult, day_stem: str = "甲"):
        self.hex_res = hex_res
        self.day_stem = day_stem
        self.palace_element = hex_res.original_hex.element
        self.six_gods = get_six_gods(day_stem)

    def assemble_full_hexagram(self) -> Dict[str, Any]:
        """为本卦与变卦装配地支、五行、六亲、六神及伏神"""
        orig_hex = self.hex_res.original_hex
        orig_branches = get_hexagram_branches(orig_hex.lower_meta["name"], orig_hex.upper_meta["name"])

        # 1. 装配本卦六爻
        original_assembled = []
        present_relations = set()

        for i in range(6):
            branch = orig_branches[i]
            elem = BRANCH_ELEMENTS[branch]
            relation = get_relation(self.palace_element, elem)
            present_relations.add(relation)

            line_data = self.hex_res.lines[i].to_dict()
            line_data.update({
                "branch": branch,
                "element": elem,
                "six_relative": relation,
                "six_god": self.six_gods[i],
                "is_shi": (i + 1) == orig_hex.shi_pos,
                "is_ying": (i + 1) == orig_hex.ying_pos,
            })
            original_assembled.append(line_data)

        # 2. 查伏神 (取本宫纯卦)
        # 本宫纯卦上下卦同名
        pure_branches = get_hexagram_branches(orig_hex.palace, orig_hex.palace)
        all_six_rel = {"父母", "子孙", "官鬼", "妻财", "兄弟"}
        missing_relations = all_six_rel - present_relations

        fushen_map = {}
        if missing_relations:
            for i in range(6):
                p_branch = pure_branches[i]
                p_elem = BRANCH_ELEMENTS[p_branch]
                p_rel = get_relation(self.palace_element, p_elem)
                if p_rel in missing_relations and p_rel not in fushen_map:
                    fushen_map[i + 1] = {
                        "six_relative": p_rel,
                        "branch": p_branch,
                        "element": p_elem,
                        "note": f"伏于第{i + 1}爻"
                    }

        # 挂载伏神到爻数据
        for item in original_assembled:
            pos = item["position"]
            item["fushen"] = fushen_map.get(pos, None)

        # 3. 若有变卦，装配变卦动爻纳支六亲 (变卦六亲依然依本宫五行为准)
        transformed_assembled = None
        if self.hex_res.transformed_hex:
            trans_hex = self.hex_res.transformed_hex
            trans_branches = get_hexagram_branches(trans_hex.lower_meta["name"], trans_hex.upper_meta["name"])
            transformed_assembled = []
            for i in range(6):
                branch = trans_branches[i]
                elem = BRANCH_ELEMENTS[branch]
                relation = get_relation(self.palace_element, elem)
                transformed_assembled.append({
                    "position": i + 1,
                    "branch": branch,
                    "element": elem,
                    "six_relative": relation,
                    "symbol": "--" if (self.hex_res.lines[i].meta["transformed_bit"] == 0) else "—"
                })

        return {
            "day_stem": self.day_stem,
            "palace_element": self.palace_element,
            "original_name": orig_hex.name,
            "original_lines": original_assembled,
            "transformed_name": self.hex_res.transformed_hex.name if self.hex_res.transformed_hex else None,
            "transformed_lines": transformed_assembled,
            "missing_relations": list(missing_relations)
        }
