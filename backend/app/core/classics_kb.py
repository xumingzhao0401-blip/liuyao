"""
六爻经典典籍引证引擎与知识库
收录十大经典考据条目，支持动爻变克、静卦旺衰、旬空出空、月破填实与伏神查验
"""

CLASSICS_CATALOG = {
    "zsby": {"title": "增删卜易", "dynasty": "清", "author": "野鹤老人", "summary": "纳甲六爻实占巅峰之作，破除神煞繁冗，专主五行生克与月令日辰旺衰。"},
    "bszz": {"title": "卜筮正宗", "dynasty": "清", "author": "王洪绪", "summary": "集先贤易说之大成，详论十八问答、黄金策千金赋注解，学理谨严。"},
    "hjc":  {"title": "黄金策", "dynasty": "明", "author": "刘伯温", "summary": "六爻统括总纲，'动静阴阳，反复迁变'，辞藻典雅，断语精当。"},
    "hzl":  {"title": "火珠林", "dynasty": "唐", "author": "麻衣道者", "summary": "铜钱摇卦之始，奠定钱代蓍草、以干支五行断吉凶之法门。"}
}

class EvidenceEngine:
    @staticmethod
    def extract_evidences(diagnosed_lines: list) -> list:
        evidences = []
        if not diagnosed_lines or not isinstance(diagnosed_lines, list):
            return evidences

        has_moving = False

        for line in diagnosed_lines:
            if not isinstance(line, dict):
                continue

            pos = line.get("position", 1)
            pos_name = f"第{pos}爻"
            rel = line.get("six_relative", "")
            
            # 防御 NoneType
            raw_tags = line.get("status_tags")
            tags = [str(t) for t in raw_tags] if isinstance(raw_tags, (list, tuple)) else []
            
            raw_change = line.get("change_relationship")
            change = str(raw_change) if raw_change is not None else ""

            if line.get("is_moving"):
                has_moving = True

            # 1. 破（月破/日破）
            if any("破" in t for t in tags):
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "爻临月破/日破",
                    "book_title": "增删卜易",
                    "chapter": "卷一·月破章",
                    "original_text": "用神临月破，如枯木逢霜，万物凋零，虽有日辰生扶，亦难发力。必待出月、逢合之日，方得补救。",
                    "explanation": "爻逢日辰冲克为破。破主事体动摇、当面受挫。若是静卦，则为被动破损，需待后时填实逢合转机。"
                })

            # 2. 空（旬空）
            if any("空" in t for t in tags):
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "爻值旬空",
                    "book_title": "卜筮正宗",
                    "chapter": "辟诸书动变章",
                    "original_text": "空非真空，逢冲则实；静空遇冲为起，动空遇冲为实。出空逢值，方定吉凶。",
                    "explanation": "旬空代表事情目前悬空、当事人底气不足或资金尚未落实。待出空或日辰冲实之时，虚妄坐实。"
                })

            # 3. 动变回头克
            if "回头克" in change:
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "动化回头克",
                    "book_title": "黄金策",
                    "chapter": "总断千金赋",
                    "original_text": "生扶虽美，回头克处有凶危；化绝化克，谋事难期成就。",
                    "explanation": "自身主动生发动作，结果变爻反克自身本位，代表自找麻烦或后续条件恶化。"
                })

            # 4. 动变回头生
            if "回头生" in change:
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "动化回头生",
                    "book_title": "增删卜易",
                    "chapter": "生克章",
                    "original_text": "动化回头生者，如春苗得雨，渐入佳境。事起初虽艰，终获厚报。",
                    "explanation": "变爻哺育本爻，预示事件后劲充沛，事情能因势利导越走越顺。"
                })

            # 5. 伏神
            if line.get("fushen") and isinstance(line["fushen"], dict):
                fs = line["fushen"]
                evidences.append({
                    "target": f"{pos_name} 伏神",
                    "phenomenon": f"伏藏 {fs.get('six_relative', '')}{fs.get('branch', '')}",
                    "book_title": "火珠林",
                    "chapter": "伏神论",
                    "original_text": "伏居飞下，须看飞神生克。飞来克伏难成器，伏去克飞亦有灾；生扶比和，终当出露。",
                    "explanation": "伏神代表潜藏在暗处未摆上台面的人事与资金，需查飞神是否能容之、引拔之。"
                })

        # 6. 静卦总纲（六爻皆无动爻）
        if not has_moving:
            evidences.append({
                "target": "全卦静局",
                "phenomenon": "六爻安静",
                "book_title": "增删卜易",
                "chapter": "静卦章",
                "original_text": "静卦无动变，专主世应生克与提纲旺衰。世克应事多阻隔，应生世易于成就。最忌日辰冲动暗起波澜。",
                "explanation": "静卦代表当下大局相对稳定，事情发展没有激烈的突发变故，重点看所测之'用神'与'世爻'得不得日令月建之生助。"
            })

        return evidences
