# -*- coding: utf-8 -*-
"""
六十四卦营造全谱图典知识库
包含八宫归属、世应爻位、卦象组成、白话场景通俗释义与卦辞
"""

# 八宫卦序基本结构 (京氏易传八宫卦变)
PALACE_ORDER = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]

# 64 卦全量通俗辞典与象数底表
HEXAGRAMS_CATALOG = {
    # 乾宫八卦 (金)
    "111111": {"name": "乾为天", "palace": "乾", "element": "金", "order": 1, "upper": "乾天", "lower": "乾天", "type": "本宫六冲", "shi": 6, "ying": 3,
               "summary": "天行健，纯阳至健，刚强开拓之象。", "layman": "大局开阔，适合把握主动权并以刚毅持重前行，但须戒骄戒躁，谨防亢龙有悔。"},
    "111110": {"name": "天风姤", "palace": "乾", "element": "金", "order": 44, "upper": "乾天", "lower": "巽风", "type": "一世卦", "shi": 1, "ying": 4,
               "summary": "天下有风，不期而遇，柔道渐长之象。", "layman": "主邂逅与意外相逢。凡事易有不可控的外力介入，宜冷静防范、审慎抉择。"},
    "111100": {"name": "天山遁", "palace": "乾", "element": "金", "order": 33, "upper": "乾天", "lower": "艮山", "type": "二世卦", "shi": 2, "ying": 5,
               "summary": "天下有山，退避隐匿，守正待时之象。", "layman": "退一步海阔天空。当前外部阻力显现，不可强行推进，退守与韬光养晦方为上策。"},
    "111000": {"name": "天地否", "palace": "乾", "element": "金", "order": 12, "upper": "乾天", "lower": "坤地", "type": "三世六合", "shi": 3, "ying": 6,
               "summary": "天地不交，闭塞不通，暗晦停滞之象。", "layman": "交流阻滞，彼此难以达成共识。此时不宜冒进签约或扩大投资，应静候阴霾消散。"},
    "110000": {"name": "风地观", "palace": "乾", "element": "金", "order": 20, "upper": "巽风", "lower": "坤地", "type": "四世卦", "shi": 4, "ying": 1,
               "summary": "风行地上，观瞻考察，内省自知之象。", "layman": "适合实地调研、复盘审视，而不宜急于拍板落地。多看、多听、少冲动。"},
    "100000": {"name": "山地剥", "palace": "乾", "element": "金", "order": 23, "upper": "艮山", "lower": "坤地", "type": "五世卦", "shi": 5, "ying": 2,
               "summary": "高山附地，根基受损，静守止损之象。", "layman": "旧结构动荡、资源消耗严重。切忌硬撑与盲目投入，首要任务是防范风险与断舍离。"},
    "101000": {"name": "火地晋", "palace": "乾", "element": "金", "order": 35, "upper": "离火", "lower": "坤地", "type": "游魂卦", "shi": 4, "ying": 1,
               "summary": "日出地上，光明渐显，顺势攀升之象。", "layman": "才华与价值开始被外界看见。适合积极展示能力、推进合作，前途光明可期。"},
    "101111": {"name": "火天大有", "palace": "乾", "element": "金", "order": 14, "upper": "离火", "lower": "乾天", "type": "归魂卦", "shi": 3, "ying": 6,
               "summary": "火在天上，普照万物，盛大丰收之象。", "layman": "资源充沛、时机成熟。顺天应人，但财富或成果聚集时更应居安思危、分润于人。"},

    # 兑宫八卦 (金)
    "011011": {"name": "兑为泽", "palace": "兑", "element": "金", "order": 58, "upper": "兑泽", "lower": "兑泽", "type": "本宫六冲", "shi": 6, "ying": 3,
               "summary": "两泽相丽，和悦交流，言辞愉洽之象。", "layman": "利于商务洽谈、沟通讲演和人际公关，但需防言多必失或流于表面空谈。"},
    "011010": {"name": "泽水困", "palace": "兑", "element": "金", "order": 47, "upper": "兑泽", "lower": "坎水", "type": "一世卦", "shi": 1, "ying": 4,
               "summary": "水漏泽底，处境逼仄，困境磨砺之象。", "layman": "资金或人手捉襟见肘，当前处于受制阶段。不可妄动强辩，唯有坚定心志以待转机。"},
    "011000": {"name": "泽地萃", "palace": "兑", "element": "金", "order": 45, "upper": "兑泽", "lower": "坤地", "type": "二世卦", "shi": 2, "ying": 5,
               "summary": "泽上于地，精英聚集，聚沙成塔之象。", "layman": "适合团队招募、资本聚合、联合办大事。聚人聚气之机，需有严明规约方能持久。"},
    "011100": {"name": "泽山咸", "palace": "兑", "element": "金", "order": 31, "upper": "兑泽", "lower": "艮山", "type": "三世卦", "shi": 3, "ying": 6,
               "summary": "山泽通气，心有灵犀，感应相投之象。", "layman": "感情合作大吉。双方默契度极高，真诚沟通能迅速达成共识，推进十分顺利。"},
    "010100": {"name": "水山蹇", "palace": "兑", "element": "金", "order": 39, "upper": "坎水", "lower": "艮山", "type": "四世卦", "shi": 4, "ying": 1,
               "summary": "山上有水，进退维谷，前途险阻之象。", "layman": "前方道路遇阻，不可强行往前闯。宜寻求长辈、贵人相助，迂回解围。"},
    "000100": {"name": "地山谦", "palace": "兑", "element": "金", "order": 15, "upper": "坤地", "lower": "艮山", "type": "五世卦", "shi": 5, "ying": 2,
               "summary": "地中有山，高而不危，谦受益盈之象。", "layman": "谦逊得福的大吉之卦。低调行事，凡事主动退让分毫，反而能收获全盘支持。"},
    "001100": {"name": "雷山小过", "palace": "兑", "element": "金", "order": 62, "upper": "震雷", "lower": "艮山", "type": "游魂卦", "shi": 4, "ying": 1,
               "summary": "山上有雷，微有出格，宜小不宜大之象。", "layman": "适合处理细枝末节、过渡性质的事务，切忌进行大规模定案、巨额签约或越俎代庖。"},
    "001011": {"name": "雷泽归妹", "palace": "兑", "element": "金", "order": 54, "upper": "震雷", "lower": "兑泽", "type": "归魂卦", "shi": 3, "ying": 6,
               "summary": "泽上有雷，缘分错置，急就失控之象。", "layman": "行事基础尚不牢固，切忌急于求成或贪图一时捷径，否则后患无穷。"},

    # 离宫八卦 (火)
    "101101": {"name": "离为火", "palace": "离", "element": "火", "order": 30, "upper": "离火", "lower": "离火", "type": "本宫六冲", "shi": 6, "ying": 3,
               "summary": "重明丽天，光彩夺目，附丽共生之象。", "layman": "才华光耀，利文书、协议、声名显露；需依附稳固的平台或依托可靠团队才能持久。"},
    "101100": {"name": "火山旅", "palace": "离", "element": "火", "order": 56, "upper": "离火", "lower": "艮山", "type": "一世卦", "shi": 1, "ying": 4,
               "summary": "山上有火，羁旅漂泊，身在客途之象。", "layman": "主出差、异地求职、奔波不定。身处异地或新环境宜低调谦和，客随主便。"},
    "101000": {"name": "火风鼎", "palace": "离", "element": "火", "order": 50, "upper": "离火", "lower": "巽风", "type": "二世卦", "shi": 2, "ying": 5,
               "summary": "木上有火，革故鼎新，稳重安邦之象。", "layman": "事业格局重组、制度确立的大成之象。适合承接重担、推陈出新、确立新模式。"},
    "101110": {"name": "火水未济", "palace": "离", "element": "火", "order": 64, "upper": "离火", "lower": "坎水", "type": "三世卦", "shi": 3, "ying": 6,
               "summary": "火在水上，蓄势待发，生生不息之象。", "layman": "事情虽未最终定论，但蕴含无尽转机与发展空间。认真走好收尾每一步即可破局。"},
    "100110": {"name": "山水蒙", "palace": "离", "element": "火", "order": 4, "upper": "艮山", "lower": "坎水", "type": "四世卦", "shi": 4, "ying": 1,
               "summary": "山下出泉，童蒙待启，求师开窍之象。", "layman": "当前认知尚未透彻，切莫盲目拍板。主动向行家前辈请教学习，方能拨云见日。"},
    "000110": {"name": "风水涣", "palace": "离", "element": "火", "order": 59, "upper": "巽风", "lower": "坎水", "type": "五世卦", "shi": 5, "ying": 2,
               "summary": "风行水上，波澜化解，人心离散亦逢机之象。", "layman": "坚冰解冻、郁结消解。也主人员流动与分散，利于破除旧有僵局重新组队。"},
    "010110": {"name": "天水讼", "palace": "离", "element": "火", "order": 6, "upper": "乾天", "lower": "坎水", "type": "游魂卦", "shi": 4, "ying": 1,
               "summary": "天水背行，争执不和，口舌诉讼之象。", "layman": "意见相左，易生法务、合约或利益纷争。宜尽早寻求调解，退步免祸，不宜硬碰硬。"},
    "010101": {"name": "天火同人", "palace": "离", "element": "火", "order": 13, "upper": "乾天", "lower": "离火", "type": "归魂卦", "shi": 3, "ying": 6,
               "summary": "天与火同，求同存异，同心合力之象。", "layman": "适宜跨部门协作、聚合同道中人。大家目标一致，开诚布公即可成大事。"},

    # 震宫八卦 (木)
    "001001": {"name": "震为雷", "palace": "震", "element": "木", "order": 51, "upper": "震雷", "lower": "震雷", "type": "本宫六冲", "shi": 6, "ying": 3,
               "summary": "震惊百里，声势浩大，破旧立新之象。", "layman": "忽如其来的变动或消息令人震惊，但临危不乱、镇定自若便能转危为机。"},
    "001000": {"name": "雷地豫", "palace": "震", "element": "木", "order": 16, "upper": "震雷", "lower": "坤地", "type": "一世卦", "shi": 1, "ying": 4,
               "summary": "雷出地上，欣欣向荣，欢愉振奋之象。", "layman": "心情舒畅、活动顺利。但享受欢乐之时不可沉溺放纵，需提前做好后续防备。"},
    "001100": {"name": "雷水解", "palace": "震", "element": "木", "order": 40, "upper": "震雷", "lower": "坎水", "type": "二世卦", "shi": 2, "ying": 5,
               "summary": "雷雨交作，困难化解，春回大地之象。", "layman": "长期困扰的难关终于迎来转机。适合抓紧时间解决遗留问题，轻装上阵。"},
    "001110": {"name": "雷风恒", "palace": "震", "element": "木", "order": 32, "upper": "震雷", "lower": "巽风", "type": "三世卦", "shi": 3, "ying": 6,
               "summary": "雷风相与，恒久坚持，始终如一之象。", "layman": "持之以恒即见胜利。不可轻易更换赛道或频繁变更初衷，按部就班最吉。"},
    "000110": {"name": "地风升", "palace": "震", "element": "木", "order": 46, "upper": "坤地", "lower": "巽风", "type": "四世卦", "shi": 4, "ying": 1,
               "summary": "木生地上，积微成著，节节高升之象。", "layman": "事业稳健爬坡期。利于晋升、拓展、考学，循序渐进必有大收获。"},
    "010110": {"name": "水风井", "palace": "震", "element": "木", "order": 48, "upper": "坎水", "lower": "巽风", "type": "五世卦", "shi": 5, "ying": 2,
               "summary": "水汲于井，源远流长，滋养互惠之象。", "layman": "注重内功修炼与长期赋能。不可半途而废（繘敝未至），坚持到底方能汲得清泉。"},
    "011110": {"name": "泽风大过", "palace": "震", "element": "木", "order": 28, "upper": "兑泽", "lower": "巽风", "type": "游魂卦", "shi": 4, "ying": 1,
               "summary": "泽灭木顶，栋桡负重，事涉非常之象。", "layman": "承担压力已接近承载极限，非常时刻当用非常之法，果断化解危机。"},
    "011001": {"name": "泽雷随", "palace": "震", "element": "木", "order": 17, "upper": "兑泽", "lower": "震雷", "type": "归魂卦", "shi": 3, "ying": 6,
               "summary": "泽中有雷，随顺机宜，择善而从之象。", "layman": "顺从大势与规律。不宜逆势独行，跟对人、跟对团队和趋势即可水到渠成。"},

    # 巽宫八卦 (木)
    "110110": {"name": "巽为风", "palace": "巽", "element": "木", "order": 57, "upper": "巽风", "lower": "巽风", "type": "本宫六冲", "shi": 6, "ying": 3,
               "summary": "随风深入，柔顺渗透，无孔不入之象。", "layman": "宜以柔克刚、潜移默化地推进事务。凡事讲究方式方法，不可蛮干。"},
    "110111": {"name": "风天小畜", "palace": "巽", "element": "木", "order": 9, "upper": "巽风", "lower": "乾天", "type": "一世卦", "shi": 1, "ying": 4,
               "summary": "风行天上，蓄力未充，密云不雨之象。", "layman": "时机尚未完全熟透，力量仍有不足。不可急于决战，适度储备积蓄最为稳妥。"},
    "110101": {"name": "风火家人", "palace": "巽", "element": "木", "order": 37, "upper": "巽风", "lower": "离火", "type": "二世卦", "shi": 2, "ying": 5,
               "summary": "火自风出，齐家有道，各安其位之象。", "layman": "注重内部建设与后防稳定。团队或家庭内部理顺关系、分工明确，外部自然顺遂。"},
    "110001": {"name": "风雷益", "palace": "巽", "element": "木", "order": 42, "upper": "巽风", "lower": "震雷", "type": "三世卦", "shi": 3, "ying": 6,
               "summary": "风雷激荡，利益分享，乘风破浪之象。", "layman": "大吉之卦，利于开拓进取、投资与自我增值。勇于开拓，大有作为。"},
    "111001": {"name": "天雷无妄", "palace": "巽", "element": "木", "order": 25, "upper": "乾天", "lower": "震雷", "type": "四世卦", "shi": 4, "ying": 1,
               "summary": "天下一雷，真实自然，不可妄为之象。", "layman": "务必脚踏实地、诚实守信。切不可投机取巧或存侥幸心理，否则恐遭无妄之灾。"},
    "101001": {"name": "火雷噬嗑", "palace": "巽", "element": "木", "order": 21, "upper": "离火", "lower": "震雷", "type": "五世卦", "shi": 5, "ying": 2,
               "summary": "雷电交施，咬碎梗阻，法度严明之象。", "layman": "遇事有障碍阻隔，必须拿出铁腕魄力去解决骨头问题，严明纪律方通。"},
    "100001": {"name": "山雷颐", "palace": "巽", "element": "木", "order": 27, "upper": "艮山", "lower": "震雷", "type": "游魂卦", "shi": 4, "ying": 1,
               "summary": "山下有雷，颐养天年，谨言慎食之象。", "layman": "注重身心休养与自我提升。言语不可轻率，饮食开销宜有节制。"},
    "100110": {"name": "山风蛊", "palace": "巽", "element": "木", "order": 18, "upper": "艮山", "lower": "巽风", "type": "归魂卦", "shi": 3, "ying": 6,
               "summary": "山下积风，积弊已久，拨乱反正之象。", "layman": "历史遗留问题爆发。需鼓足勇气大刀阔斧改革治理，方能起死回生。"},

    # 坎宫八卦 (水)
    "010010": {"name": "坎为水", "palace": "坎", "element": "水", "order": 29, "upper": "坎水", "lower": "坎水", "type": "本宫六冲", "shi": 6, "ying": 3,
               "summary": "重重险阻，水流不息，守正不失之象。", "layman": "处境险要，需如流水般沉着坚韧，心怀诚敬守正，切勿铤而走险。"},
    "010011": {"name": "水泽节", "palace": "坎", "element": "水", "order": 60, "upper": "坎水", "lower": "兑泽", "type": "一世卦", "shi": 1, "ying": 4,
               "summary": "泽上有水，节度自持，张弛有度之象。", "layman": "凡事皆需有节制。控制预算、管理预期，不过分克扣也不铺张浪费。"},
    "010001": {"name": "水雷屯", "palace": "坎", "element": "水", "order": 3, "upper": "坎水", "lower": "震雷", "type": "二世卦", "shi": 2, "ying": 5,
               "summary": "云雷初动，万事起头，艰难萌发之象。", "layman": "草创初期的艰难阶段。不可妄动强攻，宜广结善缘、招兵买马稳步筑基。"},
    "010101": {"name": "水火既济", "palace": "坎", "element": "水", "order": 63, "upper": "坎水", "lower": "离火", "type": "三世卦", "shi": 3, "ying": 6,
               "summary": "水火交融，功成名就，初吉终乱之象。", "layman": "目标已圆满达成，处于顶点。但盛极必衰，此时防守维护比继续扩张更重要。"},
    "011101": {"name": "泽火革", "palace": "坎", "element": "水", "order": 49, "upper": "兑泽", "lower": "离火", "type": "四世卦", "shi": 4, "ying": 1,
               "summary": "泽中有火，破旧立新，彻底变革之象。", "layman": "变革大潮已至，旧框架不可维系。顺应时势主动求变，必将重获新生。"},
    "001101": {"name": "雷火丰", "palace": "坎", "element": "水", "order": 55, "upper": "震雷", "lower": "离火", "type": "五世卦", "shi": 5, "ying": 2,
               "summary": "雷电俱至，盛大光明，如日中天之象。", "layman": "成果极其显著丰厚。但日中则昃，务必保持清醒头脑，做好防波堤与防守预案。"},
    "000101": {"name": "地火明夷", "palace": "坎", "element": "水", "order": 36, "upper": "坤地", "lower": "离火", "type": "游魂卦", "shi": 4, "ying": 1,
               "summary": "日入地中，光芒受损，韬光养晦之象。", "layman": "遭遇不公或打压，自身才华被埋没。切莫锋芒毕露，学会藏拙自保方能渡过至暗。"},
    "000010": {"name": "地水师", "palace": "坎", "element": "水", "order": 7, "upper": "坤地", "lower": "坎水", "type": "归魂卦", "shi": 3, "ying": 6,
               "summary": "地中有水，严正统众，行险用师之象。", "layman": "需统帅团队打硬仗。名正言顺、军纪严明、调兵遣将方能立于不败之地。"},

    # 艮宫八卦 (土)
    "100100": {"name": "艮为山", "palace": "艮", "element": "土", "order": 52, "upper": "艮山", "lower": "艮山", "type": "本宫六冲", "shi": 6, "ying": 3,
               "summary": "崇山峻岭，安止不移，止其所当止之象。", "layman": "当止则止，及时刹车。该停下脚步审视现状，不可心浮气躁勉强前行。"},
    "100101": {"name": "山火贲", "palace": "艮", "element": "土", "order": 22, "upper": "艮山", "lower": "离火", "type": "一世卦", "shi": 1, "ying": 4,
               "summary": "山下有火，华饰文明，返璞归真之象。", "layman": "利于包装形象、宣传公关；但形式不可大过实质，终究需以过硬品质为本。"},
    "100111": {"name": "山天大畜", "palace": "艮", "element": "土", "order": 26, "upper": "艮山", "lower": "乾天", "type": "二世卦", "shi": 2, "ying": 5,
               "summary": "山容巨天，大有储备，厚积薄发之象。", "layman": "积蓄深厚，实力坚强。适合蓄养贤才、钻研硬核本领，未来大有所为。"},
    "100011": {"name": "山泽损", "palace": "艮", "element": "土", "order": 41, "upper": "艮山", "lower": "兑泽", "type": "三世卦", "shi": 3, "ying": 6,
               "summary": "山下有泽，损己益人，舍小求大之象。", "layman": "适度牺牲眼前短期利益或让利于人，反而能换取长远持久的核心信任。"},
    "101011": {"name": "火泽睽", "palace": "艮", "element": "土", "order": 38, "upper": "离火", "lower": "兑泽", "type": "四世卦", "shi": 4, "ying": 1,
               "summary": "火动泽静，异趣背离，求同存异之象。", "layman": "彼此立场观点差异大，易生口角龃龉。当前不可强求思想统一步调，各行其是即可。"},
    "111011": {"name": "天泽履", "palace": "艮", "element": "土", "order": 10, "upper": "乾天", "lower": "兑泽", "type": "五世卦", "shi": 5, "ying": 2,
               "summary": "履虎之尾，如履薄冰，严守规矩之象。", "layman": "伴君如伴虎，处境敏感。只要谦逊慎行、恪守职分规范，虽险无妨。"},
    "110011": {"name": "风泽中孚", "palace": "艮", "element": "土", "order": 61, "upper": "巽风", "lower": "兑泽", "type": "游魂卦", "shi": 4, "ying": 1,
               "summary": "泽上有风，诚信内涵，感通万物之象。", "layman": "以最高等级的信誉待人，能打动最严苛的合作方。利签约立盟。"},
    "110100": {"name": "风山渐", "palace": "艮", "element": "土", "order": 53, "upper": "巽风", "lower": "艮山", "type": "归魂卦", "shi": 3, "ying": 6,
               "summary": "山上生木，循序渐进，积厚成高之象。", "layman": "像大树在山崖成长一样稳扎稳打。不可图快，每一步走扎实自然水到渠成。"},

    # 坤宫八卦 (土)
    "000000": {"name": "坤为地", "palace": "坤", "element": "土", "order": 2, "upper": "坤地", "lower": "坤地", "type": "本宫六冲", "shi": 6, "ying": 3,
               "summary": "厚德载物，顺天应时，包容承载之象。", "layman": "宜守不宜攻，宜顺不宜逆。保持从属与配合姿态，以宽厚包容化解一切波折。"},
    "000001": {"name": "地雷复", "palace": "坤", "element": "土", "order": 24, "upper": "坤地", "lower": "震雷", "type": "一世卦", "shi": 1, "ying": 4,
               "summary": "地下一阳，春意萌发，重见生机之象。", "layman": "谷底反弹的第一道微光。适合重整旗鼓、找回初心，小步试水开展新探索。"},
    "000011": {"name": "地泽临", "palace": "坤", "element": "土", "order": 19, "upper": "坤地", "lower": "兑泽", "type": "二世卦", "shi": 2, "ying": 5,
               "summary": "居高临下，视察关照，督导推进之象。", "layman": "大好局势正在逼近，自身影响力增强。宜趁热打铁狠抓落实，但八月有凶需防衰竭。"},
    "000111": {"name": "地天泰", "palace": "坤", "element": "土", "order": 11, "upper": "坤地", "lower": "乾天", "type": "三世六合", "shi": 3, "ying": 6,
               "summary": "天地交泰，小往大来，通达顺遂之象。", "layman": "上下同心、诸事顺畅的大吉之卦。合作共赢，趁此黄金期全力拓宽疆域。"},
    "001111": {"name": "雷天大壮", "palace": "坤", "element": "土", "order": 34, "upper": "震雷", "lower": "乾天", "type": "四世卦", "shi": 4, "ying": 1,
               "summary": "雷在天上，声势刚强，不可用壮之象。", "layman": "势头极猛、气势如虹。但切记不可依仗声势飞扬跋扈，否则触藩羝羊进退两难。"},
    "011111": {"name": "泽天夬", "palace": "坤", "element": "土", "order": 43, "upper": "兑泽", "lower": "乾天", "type": "五世卦", "shi": 5, "ying": 2,
               "summary": "泽上于天，决断是非，去腐生新之象。", "layman": "到了最后拍板决断的关头。对待弊端不可姑息，但处置需讲究方式方法，防反扑。"},
    "010111": {"name": "水天需", "palace": "坤", "element": "土", "order": 5, "upper": "坎水", "lower": "乾天", "type": "游魂卦", "shi": 4, "ying": 1,
               "summary": "水在天上，待时而动，饮食宴乐之象。", "layman": "前路有险，但自身实力尚在。保持从容心境，耐心等待天时转机，不急不躁。"},
    "010000": {"name": "水地比", "palace": "坤", "element": "土", "order": 8, "upper": "坎水", "lower": "坤地", "type": "归魂卦", "shi": 3, "ying": 6,
               "summary": "水附于地，亲密相依，抱团取暖之象。", "layman": "寻找靠谱的盟友或社群归属。彼此相亲相爱互相借力，后夫迟到者凶。"}
}

def get_hexagrams_summary():
    """返回用于前端卡片平铺的总览轻量字典"""
    items = []
    for code, info in HEXAGRAMS_CATALOG.items():
        items.append({
            "code": code,
            "name": info["name"],
            "palace": info["palace"],
            "element": info["element"],
            "order": info["order"],
            "upper": info["upper"],
            "lower": info["lower"],
            "type": info["type"],
            "shi": info["shi"],
            "ying": info["ying"],
            "summary": info["summary"]
        })
    # 按周易序排列
    items.sort(key=lambda x: x["order"])
    return items

def get_hexagram_detail(code: str):
    """根据 6 位二进制码返回单卦详尽卡片档案"""
    return HEXAGRAMS_CATALOG.get(code)
