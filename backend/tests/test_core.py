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

    def test_all_original_quotes_verbatim_in_source_texts(self):
        """防伪造回归：每条 source_type=原文 的引证，其每个……分隔片段
        必须在对应典籍 txt 中逐字存在；book_key 必须能对应到 catalog。"""
        import os
        from app.core.classics_kb import CLASSICS_CATALOG

        classics_dir = os.path.join(os.path.dirname(__file__), "..", "app", "data", "classics")
        lines = [
            self._line(status_tags=["月破"], is_moving=True),
            self._line(status_tags=["旬空"], is_moving=True),
            self._line(status_tags=["暗动"], change_relationship="动化回头克", is_moving=True),
            self._line(change_relationship="动化回头生", is_moving=True),
            self._line(change_relationship="动化进神", is_moving=True),
            self._line(status_tags=["动爻逢日冲"], change_relationship="动化退神", is_moving=True),
            self._line(fushen={"six_relative": "官鬼", "branch": "亥"}, is_moving=True),
        ]
        evs = EvidenceEngine.extract_evidences(lines)
        evs += EvidenceEngine.extract_evidences([self._line(), self._line(position=2)])
        assert len(evs) == 10, [e["phenomenon"] for e in evs]

        texts = {}
        for e in evs:
            assert e["source_type"] == "原文", e["phenomenon"]
            bk = e.get("book_key")
            assert bk in CLASSICS_CATALOG, (e["phenomenon"], bk)
            entry = CLASSICS_CATALOG[bk]
            assert e["book_title"] == entry["title"], (e["phenomenon"], e["book_title"])
            assert entry.get("has_fulltext") is True, bk
            fname = entry["source_file"].split("/")[-1]
            if bk not in texts:
                p = os.path.join(classics_dir, fname)
                assert os.path.isfile(p), p
                with open(p, encoding="utf-8") as f:
                    texts[bk] = f.read()
            for seg in (s.strip("…") for s in e["original_text"].split("……")):
                if len(seg) < 4:  # 省略号占位片段跳过
                    continue
                assert seg in texts[bk], (e["phenomenon"], e["chapter"], seg[:40])

# ================= 典籍档案（十大典籍单一可信源） =================
class TestClassicsCatalog:
    EXPECTED_TITLES = ["增删卜易", "卜筮正宗", "黄金策", "火珠林", "易隐",
                       "易冒", "断易天机", "卜筮全书", "易林补遗", "京氏易传"]

    def test_catalog_has_ten_classics(self):
        from app.core.classics_kb import CLASSICS_CATALOG
        assert len(CLASSICS_CATALOG) == 10
        titles = [v["title"] for v in CLASSICS_CATALOG.values()]
        assert titles == self.EXPECTED_TITLES

    def test_catalog_entries_have_source_fields(self):
        from app.core.classics_kb import CLASSICS_CATALOG
        for key, v in CLASSICS_CATALOG.items():
            assert v.get("source_file", "").endswith(".txt"), key
            assert isinstance(v.get("has_fulltext"), bool), key
            for f in ("title", "dynasty", "author", "summary"):
                assert v.get(f), (key, f)


# ================= 词典接口契约（防“undefined/空分类”回归） =================
class TestGlossaryContract:
    def test_glossary_items_shape(self):
        from app.core.glossary_kb import GLOSSARY_ITEMS
        assert len(GLOSSARY_ITEMS) == 31
        for i, item in enumerate(GLOSSARY_ITEMS):
            for f in ("term", "pinyin", "definition", "classic", "example",
                      "category", "category_name"):
                assert item.get(f), (i, f)

    def test_glossary_categories_match_frontend_filters(self):
        from app.core.glossary_kb import GLOSSARY_ITEMS
        cats = {i["category"] for i in GLOSSARY_ITEMS}
        assert cats == {"core", "timing", "mutation", "pattern"}
        for c in cats:
            assert sum(1 for i in GLOSSARY_ITEMS if i["category"] == c) >= 1

    def test_frontend_single_glossary_impl(self):
        js = open(os.path.join(os.path.dirname(__file__), "..", "..",
                               "frontend", "js", "app.js"), encoding="utf-8").read()
        assert js.count("function openGlossaryModal") == 1
        assert "res.data" in js  # 与后端 {"status","data"} 契约一致


# ================= 典籍全文阅读 =================
class TestClassicsReader:
    def test_all_books_split_into_chapters(self):
        from app.core.classics_kb import CLASSICS_CATALOG
        from app.core.classics_reader import load_book_text
        for key, meta in CLASSICS_CATALOG.items():
            r = load_book_text(key, meta["source_file"])
            assert r["chapter_count"] >= 1, key
            assert r["char_count"] > 10000, key
            for c in r["chapters"]:
                assert c["title"].strip(), key
            # 分章不丢正文（仅允许剥离空行带来的微小差异）
            joined = sum(len(c["text"]) for c in r["chapters"])
            assert joined >= r["char_count"] * 0.95, key

    def test_chapter_spot_checks(self):
        from app.core.classics_reader import load_book_text as load
        zsby = load("zsby", "data/classics/zengshanbuyi.txt")
        assert any(c["title"] == "八卦章" for c in zsby["chapters"])
        ym = load("ym", "data/classics/yimao.txt")
        assert any(c["title"] == "甲子章第一" for c in ym["chapters"])
        assert ym["chapter_count"] >= 90  # 90 章 + 卷首
        assert ym["note"] and "占诫章第九十一" in ym["note"]
        jsyz = load("jsyz", "data/classics/jingshiyizhuan.txt")
        assert any(c["title"] == "乾上乾下" for c in jsyz["chapters"])

    def test_reader_frontend_wired(self):
        base = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
        js = open(os.path.join(base, "js", "app.js"), encoding="utf-8").read()
        html = open(os.path.join(base, "index.html"), encoding="utf-8").read()
        assert "window.openClassicsReader" in js
        assert "/api/classics/${bookKey}/text" in js
        assert 'id="classics-reader"' in html
        assert 'id="reader-chapter-select"' in html


# ================= 版本号 =================
class TestVersion:
    def test_version_module(self):
        from app.version import VERSION, BUILD_DATE
        assert VERSION == "1.5.1"
        assert BUILD_DATE == "2026-09-27"

    def test_version_footer_in_index(self):
        html = open(os.path.join(os.path.dirname(__file__), "..", "..",
                                 "frontend", "index.html"), encoding="utf-8").read()
        assert 'id="app-version"' in html
        assert "/api/version" in html
        assert "v1.5.1" in html


# ================= 典籍收录诚实标注 =================
class TestCatalogHonesty:
    def test_text_status_schema(self):
        from app.core.classics_kb import CLASSICS_CATALOG
        assert len(CLASSICS_CATALOG) == 10
        for key, b in CLASSICS_CATALOG.items():
            assert b["text_status"] in ("full", "partial", "ocr_gaps"), key
            if b["text_status"] == "partial":
                assert b["has_fulltext"] is False, key
                assert b.get("source_note"), key  # 残本必须有说明

    def test_duanyitianji_partial(self):
        from app.core.classics_kb import CLASSICS_CATALOG
        b = CLASSICS_CATALOG["dytj"]
        assert b["text_status"] == "partial"
        assert "4、5、6、7、8、19、24、28" in b["source_note"]

    def test_yiyin_ocr_gaps(self):
        from app.core.classics_kb import CLASSICS_CATALOG
        b = CLASSICS_CATALOG["yy"]
        assert b["text_status"] == "ocr_gaps"
        assert "98" in b["source_note"]

    def test_yimao_partial(self):
        from app.core.classics_kb import CLASSICS_CATALOG
        assert CLASSICS_CATALOG["ym"]["text_status"] == "partial"

    def test_reader_notes_surface(self):
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from app.core.classics_reader import load_book_text
        from app.core.classics_kb import CLASSICS_CATALOG
        for key in ("dytj", "yy", "ym"):
            info = load_book_text(key, CLASSICS_CATALOG[key]["source_file"])
            assert info["note"], key
            assert "残本" in info["note"] or "校勘" in info["note"], key


# ================= 服务器时间接口 =================
class TestServerTime:
    def test_api_time(self):
        import time
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from fastapi.testclient import TestClient
        from app.main import app
        r = TestClient(app).get("/api/time").json()
        assert r["status"] == "success"
        assert abs(r["timestamp"] - time.time()) < 5
        assert "timezone" in r and r["timezone"]

    def test_clock_element_in_index(self):
        html = open(os.path.join(os.path.dirname(__file__), "..", "..",
                                 "frontend", "index.html"), encoding="utf-8").read()
        assert 'id="server-clock"' in html
        js = open(os.path.join(os.path.dirname(__file__), "..", "..",
                               "frontend", "js", "app.js"), encoding="utf-8").read()
        assert "/api/time" in js
        assert "initServerClock" in js
        assert "classicsStatusBadge" in js


# ================= 起卦时空输入框动态 placeholder =================
class TestDatetimePlaceholder:
    def test_placeholder_logic_present(self):
        js = open(os.path.join(os.path.dirname(__file__), "..", "..",
                               "frontend", "js", "app.js"), encoding="utf-8").read()
        assert "formatServerDateTime" in js
        assert 'getElementById("input-datetime")' in js
        html = open(os.path.join(os.path.dirname(__file__), "..", "..",
                                 "frontend", "index.html"), encoding="utf-8").read()
        assert 'id="input-datetime"' in html
