"""
时空四柱计算、古籍时令称谓、旬空月破、应期推算与时态演化
严格依据《增删卜易·应期章》、《卜筮正宗·十八问答》
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from lunar_python import Solar, Lunar
from app.core.najia import BRANCH_ELEMENTS, FIVE_ELEMENTS_ORDER

BRANCH_CLASH_MAP = {
    "子": "午", "午": "子",
    "丑": "未", "未": "丑",
    "寅": "申", "申": "寅",
    "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰",
    "巳": "亥", "亥": "巳"
}

BRANCH_HARMONY_MAP = {
    "子": "丑", "丑": "子",
    "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯",
    "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳",
    "午": "未", "未": "午"
}

JIN_SHEN = {"寅": "卯", "巳": "午", "申": "酉", "亥": "子", "丑": "辰", "辰": "未", "未": "戌"}
TUI_SHEN = {"卯": "寅", "午": "巳", "酉": "申", "子": "亥", "辰": "丑", "未": "辰", "戌": "未"}

# 古籍季候称谓
MONTH_SEASON_NAMES = {
    "寅": "孟春", "卯": "仲春", "辰": "季春",
    "巳": "孟夏", "午": "仲夏", "未": "季夏",
    "申": "孟秋", "酉": "仲秋", "戌": "季秋",
    "亥": "孟冬", "子": "仲冬", "丑": "季冬"
}

def is_support_by_month(line_elem: str, month_elem: str) -> bool:
    if line_elem == month_elem:
        return True
    line_idx = FIVE_ELEMENTS_ORDER.index(line_elem)
    month_idx = FIVE_ELEMENTS_ORDER.index(month_elem)
    return (month_idx + 1) % 5 == line_idx

def get_change_relationship(orig_branch: str, orig_elem: str, trans_branch: str, trans_elem: str) -> Optional[str]:
    if not trans_branch:
        return None
    if JIN_SHEN.get(orig_branch) == trans_branch:
        return "动化进神"
    if TUI_SHEN.get(orig_branch) == trans_branch:
        return "动化退神"

    orig_idx = FIVE_ELEMENTS_ORDER.index(orig_elem)
    trans_idx = FIVE_ELEMENTS_ORDER.index(trans_elem)
    if (trans_idx + 1) % 5 == orig_idx:
        return "动化回头生"
    if (trans_idx + 2) % 5 == orig_idx:
        return "动化回头克"
    return None

class TimeEngine:
    def __init__(self, dt: Optional[datetime] = None, tense: str = "future"):
        """
        tense: "future" (问后事·定应期), "past" (占往事·溯因由), "present" (决当下·断进退)
        """
        self.dt = dt if dt else datetime.now()
        self.tense = tense

        solar = Solar.fromYmdHms(
            self.dt.year, self.dt.month, self.dt.day,
            self.dt.hour, self.dt.minute, self.dt.second
        )
        self.lunar = solar.getLunar()

        bazi = self.lunar.getBaZi()
        self.year_ganzhi = bazi[0]
        self.month_ganzhi = bazi[1]
        self.day_ganzhi = bazi[2]
        self.time_ganzhi = bazi[3]

        self.year_stem, self.year_branch = self.year_ganzhi[0], self.year_ganzhi[1]
        self.month_stem, self.month_branch = self.month_ganzhi[0], self.month_ganzhi[1]
        self.day_stem, self.day_branch = self.day_ganzhi[0], self.day_ganzhi[1]
        self.time_stem, self.time_branch = self.time_ganzhi[0], self.time_ganzhi[1]

        self.day_kongwang = self.lunar.getDayXunKong()
        self.month_po = BRANCH_CLASH_MAP[self.month_branch]

        # 节气与古典时令表述
        prev_jie = self.lunar.getPrevJieQi().getName()
        season_name = MONTH_SEASON_NAMES.get(self.month_branch, "")
        self.classical_date_str = (
            f"岁在{self.year_ganzhi}，时维{season_name}{self.month_ganzhi}月令（{prev_jie}后），"
            f"值{self.day_ganzhi}日，{self.time_ganzhi}时建占。"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "datetime_str": self.dt.strftime("%Y-%m-%d %H:%M:%S"),
            "classical_date_str": self.classical_date_str,
            "tense": self.tense,
            "year_ganzhi": self.year_ganzhi,
            "month_ganzhi": self.month_ganzhi,
            "day_ganzhi": self.day_ganzhi,
            "time_ganzhi": self.time_ganzhi,
            "day_stem": self.day_stem,
            "month_branch": self.month_branch,
            "month_element": BRANCH_ELEMENTS[self.month_branch],
            "day_branch": self.day_branch,
            "day_element": BRANCH_ELEMENTS[self.day_branch],
            "day_kongwang": self.day_kongwang,
            "month_po": self.month_po
        }

    def diagnose_lines(self, assembled_hex: Dict[str, Any]) -> List[Dict[str, Any]]:
        month_branch = self.month_branch
        month_elem = BRANCH_ELEMENTS[month_branch]
        day_branch = self.day_branch
        day_kongwang = self.day_kongwang

        orig_lines = assembled_hex["original_lines"]
        trans_lines = assembled_hex["transformed_lines"]

        diagnosed = []
        for i in range(6):
            line = dict(orig_lines[i])
            branch = line["branch"]
            elem = line["element"]
            is_moving = line["is_moving"]

            status_tags = []
            timing_deductions = []

            # 1. 旬空与应期
            is_kong = branch in day_kongwang
            if is_kong:
                status_tags.append("旬空")
                if self.tense == "future":
                    timing_deductions.append(f"出空（出旬逢{branch}日）或冲空（逢{BRANCH_CLASH_MAP[branch]}日）应验")
                elif self.tense == "past":
                    timing_deductions.append(f"事在虚境，昔日曾谋而未实")

            # 2. 月破与应期
            is_po = (branch == self.month_po)
            if is_po:
                status_tags.append("月破")
                if self.tense == "future":
                    timing_deductions.append(f"出月交令、逢合（{BRANCH_HARMONY_MAP[branch]}日）或填实（{branch}值日）有解")
                elif self.tense == "past":
                    timing_deductions.append(f"旧疾/前嫌破败于前，因由深种")

            # 3. 日冲 (暗动 / 日破)
            is_day_clashed = (BRANCH_CLASH_MAP[day_branch] == branch)
            if is_day_clashed:
                if is_moving:
                    status_tags.append("动爻逢日冲")
                    timing_deductions.append("事变极速，立竿见影")
                else:
                    if is_support_by_month(elem, month_elem):
                        status_tags.append("暗动")
                        timing_deductions.append("暗潮涌动，隐情待发")
                    else:
                        status_tags.append("日破")
                        timing_deductions.append("冲散无依，难以收拾")

            # 4. 动化关系
            change_note = None
            if is_moving and trans_lines:
                t_branch = trans_lines[i]["branch"]
                t_elem = trans_lines[i]["element"]
                change_rel = get_change_relationship(branch, elem, t_branch, t_elem)
                
                notes = []
                if change_rel:
                    notes.append(change_rel)
                    if change_rel == "动化回头生":
                        timing_deductions.append(f"逢变爻{t_branch}当旺之时吉庆显发")
                    elif change_rel == "动化回头克":
                        timing_deductions.append(f"逢变爻{t_branch}值日生旺之期防灾咎")
                    elif change_rel == "动化退神":
                        timing_deductions.append("后劲减退，往后日趋渐歇")
                    elif change_rel == "动化进神":
                        timing_deductions.append("如日方升，事态层层拓展")

                if t_branch in day_kongwang:
                    notes.append("动化空")
                    timing_deductions.append("化入空亡，虎头蛇尾终归虚")
                if t_branch == self.month_po:
                    notes.append("动化破")
                    timing_deductions.append("变爻逢破，转化无力")

                # 经典动而逢值逢合应期
                if not timing_deductions and self.tense == "future":
                    timing_deductions.append(f"逢本爻值日（{branch}日）或逢合（{BRANCH_HARMONY_MAP[branch]}日）应事")

                change_note = "、".join(notes) if notes else "动变"

            line["status_tags"] = status_tags
            line["change_relationship"] = change_note
            line["timing_deduction"] = "；".join(timing_deductions) if timing_deductions else "遵中和气数"
            diagnosed.append(line)

        return diagnosed
