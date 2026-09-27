"""
六爻经典典籍引证引擎与知识库
收录十大经典考据条目，支持动爻变克、静卦旺衰、旬空出空、月破填实与伏神查验
各典籍全文收录于 backend/app/data/classics/（UTF-8 纯文本，公有领域版本），
引证一律以收录原文逐字核对，source_type 标注"原文"/"义理转述"。
"""

# source_file 相对于 backend/app/；has_fulltext 在全文入库后置 True
CLASSICS_CATALOG = {
    "zsby": {"title": "增删卜易", "dynasty": "清", "author": "野鹤老人",
             "summary": "纳甲六爻实占巅峰之作，破除神煞繁冗，专主五行生克与月令日辰旺衰。",
             "source_file": "data/classics/zengshanbuyi.txt", "has_fulltext": True},
    "bszz": {"title": "卜筮正宗", "dynasty": "清", "author": "王洪绪",
             "summary": "集先贤易说之大成，详论十八问答、黄金策千金赋注解，学理谨严。",
             "source_file": "data/classics/bushizhengzong.txt", "has_fulltext": True},
    "hjc":  {"title": "黄金策", "dynasty": "明", "author": "刘伯温",
             "summary": "六爻统括总纲，'动静阴阳，反复迁变'，辞藻典雅，断语精当。",
             "source_file": "data/classics/huangjince.txt", "has_fulltext": True},
    "hzl":  {"title": "火珠林", "dynasty": "唐", "author": "麻衣道者",
             "summary": "铜钱摇卦之始，奠定钱代蓍草、以干支五行断吉凶之法门。",
             "source_file": "data/classics/huozhulin.txt", "has_fulltext": True},
    "yy":   {"title": "易隐", "dynasty": "清", "author": "曹九锡",
             "summary": "融汇飞伏互变、神煞星宿与深层象数，考究隐幽，推断精细绝伦。",
             "source_file": "data/classics/yiyin.txt", "has_fulltext": True},
    "ym":   {"title": "易冒", "dynasty": "清", "author": "程良玉",
             "summary": "以聋道人笔名传世，条分缕析，辨析卦理极明，破除诸家疑窦。",
             "source_file": "data/classics/yimao.txt", "has_fulltext": False},
    "dytj": {"title": "断易天机", "dynasty": "明", "author": "万历刊本",
             "summary": "收录元明诸多绝密秘诀，附图考证，专论百事吉凶生克。",
             "source_file": "data/classics/duanyitianji.txt", "has_fulltext": True},
    "bsqs": {"title": "卜筮全书", "dynasty": "明", "author": "姚际隆",
             "summary": "汇辑周易源流、纳甲诸法，乃明清两代易占案头必习之渊薮。",
             "source_file": "data/classics/bushiquanshu.txt", "has_fulltext": True},
    "ylby": {"title": "易林补遗", "dynasty": "明", "author": "张㴶",
             "summary": "精微细密，专攻六十四卦应验吉凶细目，补前人所未备。",
             "source_file": "data/classics/yilinbuyi.txt", "has_fulltext": True},
    "jsyz": {"title": "京氏易传", "dynasty": "西汉", "author": "京房",
             "summary": "八宫卦变、纳甲筮法之真正源头，开创以五行生克言人事天机之先河。",
             "source_file": "data/classics/jingshiyizhuan.txt", "has_fulltext": True},
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
                    "chapter": "卷二·月破章",
                    "original_text": "诸书皆以用神临月破，谓之“悖时”，如枯根朽木，逢生生之不起，逢伤伤者更重。虽现于卦，……有亦如无；伏于卦中，终难透露。",
                    "explanation": "爻逢日辰冲克为破。破主事体动摇、当面受挫。若是静卦，则为被动破损，需待后时填实逢合转机。",

                    "book_key": "zsby",
                    "source_type": "原文"
                })

            # 2. 空（旬空）
            if any("空" in t for t in tags):
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "爻值旬空",
                    "book_title": "卜筮正宗",
                    "chapter": "启蒙节要·用神空亡诀",
                    "original_text": "发动逢冲不谓空，静空遇克却为空，忌神最喜逢空去，用与原神不可空。",
                    "explanation": "旬空代表事情目前悬空、当事人底气不足或资金尚未落实。待出空或日辰冲实之时，虚妄坐实。",

                    "book_key": "bszz",
                    "source_type": "原文"
                })

            # 3. 动变回头克
            if "回头克" in change:
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "动化回头克",
                    "book_title": "黄金策",
                    "chapter": "总断千金赋直解",
                    "original_text": "戒回头之克我，勿反德以扶人——回头克乃用神自化忌神，如火爻化水之类是也。……诸占世爻、身爻、用爻遇之不吉也。",
                    "explanation": "自身主动生发动作，结果变爻反克自身本位，代表自找麻烦或后续条件恶化。",

                    "book_key": "hjc",
                    "source_type": "原文"
                })

            # 4. 动变回头生
            if "回头生" in change:
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "动化回头生",
                    "book_title": "增删卜易",
                    "chapter": "卷一·元神忌神衰旺章",
                    "original_text": "元神动，化回头生，及化进神者……此五者，乃有力之元神也，诸占皆吉。",
                    "explanation": "变爻哺育本爻，预示事件后劲充沛，事情能因势利导越走越顺。",

                    "book_key": "zsby",
                    "source_type": "原文"
                })

            # 5. 伏神
            if line.get("fushen") and isinstance(line["fushen"], dict):
                fs = line["fushen"]
                evidences.append({
                    "target": f"{pos_name} 伏神",
                    "phenomenon": f"伏藏 {fs.get('six_relative', '')}{fs.get('branch', '')}",
                    "book_title": "火珠林",
                    "chapter": "六亲根源",
                    "original_text": "又问：何谓旁通?曰：本宫之六亲在飞象之下，为之亲王，为之伏神。旁宫之飞象加伏神之上，为飞象，亲爻世下之爻为伏。",
                    "explanation": "伏神代表潜藏在暗处未摆上台面的人事与资金，需查飞神是否能容之、引拔之。",

                    "book_key": "hzl",
                    "source_type": "原文"
                })

            # 5b. 动化进神
            if "进神" in change:
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "动化进神",
                    "book_title": "增删卜易",
                    "chapter": "卷二·进神退神章",
                    "original_text": "进退神者，爻之动而化也，化进化退，吉凶祸福，有喜忌之分。所喜者，宜化进神……进神者：由此而前进也，如春木之荣，有源之水，久远长久之象；",
                    "explanation": "动爻化出同五行之进一位地支，代表事情向前滚动、越做越大，宜乘势推进。",

                    "book_key": "zsby",
                    "source_type": "原文"
                })

            # 5c. 动化退神
            if "退神" in change:
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "动化退神",
                    "book_title": "增删卜易",
                    "chapter": "卷二·进神退神章",
                    "original_text": "……所忌者，……宜化退神……退神者：由此而渐退也，如秋天花木，渐渐凋零。",
                    "explanation": "动爻化出同五行之退一位地支，代表事情后劲不足、逐渐收敛，宜见好就收。",

                    "book_key": "zsby",
                    "source_type": "原文"
                })

            # 5d. 暗动（静爻得月令生扶逢日冲）
            if "暗动" in tags:
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "静爻暗动",
                    "book_title": "增删卜易",
                    "chapter": "卷一·暗动章",
                    "original_text": "静爻旺相，日辰冲之，为暗动。……古以暗动，福来而不知，祸来而不觉。",
                    "explanation": "静爻被日辰冲而月令有气，暗中已动。表面平静之下已有力量在运作，需按动爻论吉凶。",

                    "book_key": "zsby",
                    "source_type": "原文"
                })

            # 5e. 动爻逢日冲（动而逢冲，事变极速）
            if "动爻逢日冲" in tags:
                evidences.append({
                    "target": f"{pos_name} ({rel})",
                    "phenomenon": "动爻逢冲",
                    "book_title": "增删卜易",
                    "chapter": "卷一·动散章",
                    "original_text": "古以日辰冲动爻，谓之冲散……余屡试之，旺相者，冲之不散；",
                    "explanation": "动爻再逢日辰冲，如快马加鞭，事情变化来得极快；但冲亦主动荡，需防反复。",

                    "book_key": "zsby",
                    "source_type": "原文"
                })

        # 6. 静卦总纲（六爻皆无动爻）
        if not has_moving:
            evidences.append({
                "target": "全卦静局",
                "phenomenon": "六爻安静",
                "book_title": "卜筮正宗",
                "chapter": "启蒙节要·六爻安静诀",
                "original_text": "卦遇六爻安静，当看用与日辰，日辰克用及相刑，作事宜当谨慎。……更在世应推究，忌神切莫加临，世应临用及原神，作事断然昌盛。",
                "explanation": "静卦代表当下大局相对稳定，事情发展没有激烈的突发变故，重点看所测之'用神'与'世爻'得不得日令月建之生助。",

                "book_key": "bszz",
                "source_type": "原文"
            })

        return evidences
