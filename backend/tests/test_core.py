"""pytest 断言式回归测试：六爻核心算法"""
import sys
import os
import pytest
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.constants import COIN_SUM_MAP
from app.core.coin import YaoResult, generate_six_lines, toss_three_coins
from app.core.bagua_tables import HEXAGRAM_PALACE_MAP, TRIGRAM_BINARY_MAP
from app.core.hexagram import HexagramDetail, HexagramResult
from app.core.najia import (
    BRANCH_ELEMENTS, TRIGRAM_NAZHI, get_relation, get_six_gods,
    get_hexagram_branches, NaJiaEngine,
)
from app.core.time_engine import (
    BRANCH_CLASH_MAP, TimeEngine, is_support_by_month, get_change_relationship,
)
from app.core.classics_kb import EvidenceEngine


# ================= 铜钱映射 =================
class TestCoinMapping:
    @pytest.mark.parametrize("sums,nature,moving,obit,tbit", [
        (6, "old_yin", True, 0, 1),    # 老阴
        (7, "young_yang", False, 1, 1),  # 少阳
        (8, "young_yin", False, 0, 0),   # 少阴
        (9, "old_yang", True, 1, 0),    # 老阳
    ])
    def test_sum_mapping(self, sums, nature, moving, obit, tbit):
        y = YaoResult(0, sums)
        assert y.meta["nature"] == nature
        assert y.meta["is_moving"] is moving
        assert y.meta["original_bit"] == obit
        assert y.meta["transformed_bit"] == tbit

    def test_invalid_sum_raises(self):
        with pytest.raises(ValueError):
            YaoResult(0, 5)

    def test_line_names(self):
        assert YaoResult(0, 9).line_name == "初九"   # 阳
        assert YaoResult(1, 8).line_name == "六二"   # 阴
        assert YaoResult(5, 7).line_name == "上九"
        assert YaoResult(5, 6).line_name == "上六"

    def test_generate_manual(self):
        lines = generate_six_lines([7, 8, 7, 8, 9, 8])
        assert len(lines) == 6
        assert [l.position for l in lines] == list(range(6))
        assert lines[4].meta["is_moving"] is True  # 第5爻老阳动

    def test_generate_manual_bad_length(self):
        with pytest.raises(ValueError):
            generate_six_lines([7, 8, 7])

    def test_random_toss_range(self):
        for _ in range(50):
            assert toss_three_coins() in (6, 7, 8, 9)


# ================= 六十四卦 =================
class TestHexagramTable:
    def test_64_hexagrams_unique_names(self):
        assert len(HEXAGRAM_PALACE_MAP) == 64
        names = [v[0] for v in HEXAGRAM_PALACE_MAP.values()]
        assert len(set(names)) == 64

    def test_shi_ying_positions(self):
        for key, val in HEXAGRAM_PALACE_MAP.items():
            shi = val[4]
            assert 1 <= shi <= 6, key
            if "游魂" in val[3]:
                assert shi == 4, key
            if "归魂" in val[3]:
                assert shi == 3, key

    def _detail(self, upper, lower):
        return HexagramDetail(upper, lower)

    def test_spot_check_known_hexagrams(self):
        # (上卦, 下卦, 卦名, 宫, 世爻, 应爻)
        cases = [
            ((1, 1, 1), (1, 1, 1), "乾为天", "乾", 6, 3),
            ((1, 1, 1), (0, 1, 1), "天风姤", "乾", 1, 4),
            ((1, 0, 1), (0, 0, 0), "火地晋", "乾", 4, 1),  # 游魂
            ((1, 0, 1), (1, 1, 1), "火天大有", "乾", 3, 6),  # 归魂
            ((0, 0, 0), (0, 0, 0), "坤为地", "坤", 6, 3),
            ((0, 1, 0), (1, 1, 0), "水泽节", "坎", 1, 4),
            ((0, 1, 0), (1, 0, 1), "水火既济", "坎", 3, 6),
            ((0, 0, 0), (1, 1, 1), "地天泰", "坤", 3, 6),
            ((1, 1, 0), (0, 1, 0), "泽水困", "兑", 1, 4),
        ]
        for up, low, name, palace, shi, ying in cases:
            h = self._detail(up, low)
            assert (h.name, h.palace, h.shi_pos, h.ying_pos) == (name, palace, shi, ying)

    def test_transformed_hexagram(self):
        # 水火既济第五爻(老阳9)动 -> 地火明夷
        h = HexagramResult(generate_six_lines([7, 8, 7, 8, 9, 8]))
        assert h.original_hex.name == "水火既济"
        assert h.moving_lines == [5]
        assert h.transformed_hex.name == "地火明夷"
        # 乾为天初爻、五爻动 -> 火风鼎
        h2 = HexagramResult(generate_six_lines([9, 7, 7, 7, 9, 7]))
        assert h2.original_hex.name == "乾为天"
        assert h2.moving_lines == [1, 5]
        assert h2.transformed_hex.name == "火风鼎"

    def test_static_hexagram_no_transform(self):
        h = HexagramResult(generate_six_lines([7, 8, 7, 8, 7, 8]))
        assert h.moving_lines == []
        assert h.transformed_hex is None


# ================= 纳甲 =================
class TestNajia:
    def test_trigram_nazhi_spot(self):
        assert TRIGRAM_NAZHI["乾"]["inner"] == ["子", "寅", "辰"]
        assert TRIGRAM_NAZHI["乾"]["outer"] == ["午", "申", "戌"]
        assert TRIGRAM_NAZHI["坤"]["inner"] == ["未", "巳", "卯"]
        assert TRIGRAM_NAZHI["坤"]["outer"] == ["丑", "亥", "酉"]
        assert TRIGRAM_NAZHI["坎"]["inner"] == ["寅", "辰", "午"]
        assert TRIGRAM_NAZHI["坎"]["outer"] == ["申", "戌", "子"]
        assert TRIGRAM_NAZHI["离"]["inner"] == ["卯", "丑", "亥"]
        assert TRIGRAM_NAZHI["离"]["outer"] == ["酉", "未", "巳"]

    def test_get_relation_all_combos(self):
        elems = ["木", "火", "土", "金", "水"]
        for me in elems:
            for target in elems:
                rel = get_relation(me, target)
                assert rel in ("父母", "子孙", "官鬼", "妻财", "兄弟")

    def test_get_relation_spot(self):
        assert get_relation("金", "金") == "兄弟"   # 同我
        assert get_relation("金", "土") == "父母"   # 土生金，生我
        assert get_relation("金", "水") == "子孙"   # 金生水，我生
        assert get_relation("金", "火") == "官鬼"   # 火克金，克我
        assert get_relation("金", "木") == "妻财"   # 金克木，我克
        assert get_relation("火", "木") == "父母"   # 木生火

    def test_six_gods_by_stem(self):
        assert get_six_gods("甲")[0] == "青龙"
        assert get_six_gods("乙")[0] == "青龙"
        assert get_six_gods("丙")[0] == "朱雀"
        assert get_six_gods("戊")[0] == "勾陈"
        assert get_six_gods("己")[0] == "螣蛇"
        assert get_six_gods("庚")[0] == "白虎"
        assert get_six_gods("壬")[0] == "玄武"
        assert get_six_gods("癸")[0] == "玄武"
        assert len(get_six_gods("甲")) == 6
        with pytest.raises(ValueError):
            get_six_gods("子")

    def test_assemble_qian(self):
        # 乾为天：地支 子寅辰午申戌，宫五行金
        h = HexagramResult(generate_six_lines([7, 7, 7, 7, 7, 7]))
        asm = NaJiaEngine(h, day_stem="甲").assemble_full_hexagram()
        branches = [l["branch"] for l in asm["original_lines"]]
        assert branches == ["子", "寅", "辰", "午", "申", "戌"]
        assert asm["palace_element"] == "金"
        rels = {l["branch"]: l["six_relative"] for l in asm["original_lines"]}
        assert rels["子"] == "子孙" and rels["午"] == "官鬼" and rels["申"] == "兄弟"
        # 世在上爻，应在三爻
        assert asm["original_lines"][5]["is_shi"] is True
        assert asm["original_lines"][2]["is_ying"] is True
        # 六亲俱全，无伏神
        assert all(l["fushen"] is None for l in asm["original_lines"])

    def test_fushen_missing_guan_gui(self):
        # 天水讼（上乾下坎，离宫火）：本卦缺官鬼，伏神应为亥水官鬼伏于第三爻下
        h = HexagramResult(generate_six_lines([8, 7, 8, 7, 7, 7]))
        assert h.original_hex.name == "天水讼"
        asm = NaJiaEngine(h, day_stem="甲").assemble_full_hexagram()
        assert "官鬼" in asm["missing_relations"]
        fushen_holders = [l for l in asm["original_lines"] if l["fushen"]]
        assert len(fushen_holders) == 1
        fs = fushen_holders[0]["fushen"]
        assert fs["six_relative"] == "官鬼" and fs["branch"] == "亥"

    def test_branch_elements_complete(self):
        assert len(BRANCH_ELEMENTS) == 12


# ================= 时空 =================
class TestTimeEngine:
    def test_fixed_date_regression(self):
        # 回归锚点：2026-09-27 14:00（秋分后酉月，甲辰日）
        # 年月干支已用五虎遁/干支纪年交叉核对；甲辰旬空寅卯为内在一致性校验
        te = TimeEngine(datetime(2026, 9, 27, 14, 0, 0))
        d = te.to_dict()
        assert d["year_ganzhi"] == "丙午"
        assert d["month_ganzhi"] == "丁酉"
        assert d["day_ganzhi"] == "甲辰"
        assert d["time_ganzhi"] == "辛未"
        assert d["day_kongwang"] == "寅卯"   # 甲辰旬空寅卯
        assert d["month_branch"] == "酉"
        assert d["month_po"] == "卯"        # 酉冲卯
        assert d["day_stem"] == "甲"
        assert "岁在丙午" in d["classical_date_str"]

    def test_kongwang_clash_consistency(self):
        te = TimeEngine(datetime(2026, 9, 27, 14, 0, 0))
        assert te.month_po == BRANCH_CLASH_MAP[te.month_branch]

    def test_is_support_by_month(self):
        assert is_support_by_month("火", "木") is True    # 木生火
        assert is_support_by_month("土", "土") is True    # 同气
        assert is_support_by_month("金", "火") is False   # 火克金
        assert is_support_by_month("水", "土") is False   # 土克水

    def test_change_relationship(self):
        assert get_change_relationship("寅", "木", "卯", "木") == "动化进神"
        assert get_change_relationship("卯", "木", "寅", "木") == "动化退神"
        assert get_change_relationship("午", "火", "寅", "木") == "动化回头生"  # 木生火
        assert get_change_relationship("申", "金", "午", "火") == "动化回头克"  # 火克金
        assert get_change_relationship("子", "水", "子", "水") is None
        assert get_change_relationship("子", "水", None, None) is None

    def test_diagnose_month_po_tag(self):
        # 2026-09-27 酉月，月破在卯；泽火革（上兑下离）初爻临卯支
        te = TimeEngine(datetime(2026, 9, 27, 14, 0, 0))
        h = HexagramResult(generate_six_lines([7, 8, 7, 7, 7, 8]))
        assert h.original_hex.name == "泽火革"
        asm = NaJiaEngine(h, day_stem=te.day_stem).assemble_full_hexagram()
        diagnosed = te.diagnose_lines(asm)
        mao_lines = [l for l in diagnosed if l["branch"] == "卯"]
        assert mao_lines and all("月破" in l["status_tags"] for l in mao_lines)


# ================= 典籍引证 =================
class TestEvidenceEngine:
    def _line(self, **kw):
        base = {"position": 1, "six_relative": "父母", "is_moving": False,
                "status_tags": [], "change_relationship": "", "fushen": None}
        base.update(kw)
        return base

    def test_month_po_evidence(self):
        evs = EvidenceEngine.extract_evidences([self._line(status_tags=["月破"])])
        assert any(e["phenomenon"] == "爻临月破/日破" and e["book_title"] == "增删卜易" for e in evs)

    def test_kongwang_evidence(self):
        evs = EvidenceEngine.extract_evidences([self._line(status_tags=["旬空"])])
        assert any(e["phenomenon"] == "爻值旬空" and e["book_title"] == "卜筮正宗" for e in evs)

    def test_huitou_ke_evidence(self):
        evs = EvidenceEngine.extract_evidences([self._line(change_relationship="动化回头克")])
        assert any(e["phenomenon"] == "动化回头克" and e["book_title"] == "黄金策" for e in evs)

    def test_huitou_sheng_evidence(self):
        evs = EvidenceEngine.extract_evidences([self._line(change_relationship="动化回头生")])
        assert any(e["phenomenon"] == "动化回头生" for e in evs)

    def test_fushen_evidence(self):
        evs = EvidenceEngine.extract_evidences(
            [self._line(fushen={"six_relative": "官鬼", "branch": "亥"})])
        assert any(e["book_title"] == "火珠林" for e in evs)

    def test_static_hexagram_summary(self):
        evs = EvidenceEngine.extract_evidences([self._line(), self._line(position=2)])
        assert any(e["phenomenon"] == "六爻安静" for e in evs)

    def test_empty_input(self):
        assert EvidenceEngine.extract_evidences([]) == []
        assert EvidenceEngine.extract_evidences(None) == []

    def test_jinshen_tuishen_evidence(self):
        evs = EvidenceEngine.extract_evidences([self._line(change_relationship="动化进神")])
        assert any(e["phenomenon"] == "动化进神" and e["book_title"] == "增删卜易" for e in evs)
        evs = EvidenceEngine.extract_evidences([self._line(change_relationship="动化退神")])
        assert any(e["phenomenon"] == "动化退神" for e in evs)

    def test_andong_evidence(self):
        evs = EvidenceEngine.extract_evidences([self._line(status_tags=["暗动"])])
        assert any(e["phenomenon"] == "静爻暗动" for e in evs)

    def test_moving_line_clashed_evidence(self):
        evs = EvidenceEngine.extract_evidences([self._line(status_tags=["动爻逢日冲"])])
        assert any(e["phenomenon"] == "动爻逢冲" for e in evs)

    def test_all_evidences_have_source_type(self):
        # 端到端：天雷无妄二爻动 -> 天泽履（寅化卯，进神）
        h = HexagramResult(generate_six_lines([7, 6, 8, 7, 7, 7]))
        assert h.original_hex.name == "天雷无妄"
        assert h.transformed_hex.name == "天泽履"
        te = TimeEngine(datetime(2026, 9, 27, 14, 0, 0))
        asm = NaJiaEngine(h, day_stem=te.day_stem).assemble_full_hexagram()
        evs = EvidenceEngine.extract_evidences(te.diagnose_lines(asm))
        assert any(e["phenomenon"] == "动化进神" for e in evs)
        assert evs and all(e.get("source_type") in ("原文", "义理转述") for e in evs)
