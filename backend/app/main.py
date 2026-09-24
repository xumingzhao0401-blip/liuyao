"""
六爻排盘与典籍引证系统 Web API 核心
包含排盘计算、时态推演、问事注入、动态Prompt构建、AI划词考据、初学者白话通俗导读与静态托管
"""

import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.core.coin import generate_six_lines
from app.core.hexagram import HexagramResult
from app.core.najia import NaJiaEngine
from app.core.time_engine import TimeEngine
from app.core.classics_kb import EvidenceEngine, CLASSICS_CATALOG



app = FastAPI(title="六爻象数营造与典籍考据系统 API", version="1.3.0")

# ================= 规范挂载静态资源目录 =================
from fastapi.staticfiles import StaticFiles
import os

frontend_dir = "/app/frontend"
if not os.path.exists(frontend_dir):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))

# 同时挂载 /static 和根目录资源，确保全部兼容
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")
if os.path.exists(os.path.join(frontend_dir, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- 数据模型 -----------------
class DivineRequest(BaseModel):
    datetime_str: Optional[str] = None
    tense: Optional[str] = "future"
    question: Optional[str] = None
    manual_sums: Optional[List[int]] = None

class ExplainRequest(BaseModel):
    query_text: str
    hexagram_context: Optional[Dict[str, Any]] = None
    custom_prompt: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model_name: Optional[str] = None

class LaymanGuideRequest(BaseModel):
    hexagram_context: Dict[str, Any]
    dynamic_prompt: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model_name: Optional[str] = None

# 初学者专有名词现代生活化通俗库
BEGINNER_GLOSSARY = {
    "卦 (Hexagram)": {
        "title": "卦 (卦象)",
        "vernacular": "事情所处的大环境与基本形态。六根木块从下往上搭建，像六层大楼，记录了事情从萌芽到最终结局的演变规律。"
    },
    "世爻 (Self)": {
        "title": "世 / 世爻",
        "vernacular": "代表【你本人】、问事的主体、己方的基本盘或身体现状。世爻旺盛说明底气足、有主动权；受克说明压力大、心有余而力不足。"
    },
    "应爻 (Target)": {
        "title": "应 / 应爻",
        "vernacular": "代表【对方】、你问的那件事、合作伙伴、客户、竞争对手或目标物。世应相生合代表彼此配合；世应相冲克代表意见不一或有阻力。"
    },
    "月建 (Monthly Governor)": {
        "title": "月建 / 月令提纲",
        "vernacular": "当月的【大气候、行业大趋势、政策背景】。月建生助你，代表站在了风口；被月建克，代表逆风前行、大环境不支持。"
    },
    "日辰 (Daily Officer)": {
        "title": "日辰 / 日令主事",
        "vernacular": "占卦当天的【直属领导、即时主事裁判、直接推动力】。能当场拍板定夺，是判定吉凶最直接的操盘力量。"
    },
    "伏神 (Hidden Deity)": {
        "title": "伏 / 伏神",
        "vernacular": "【潜伏在暗处或暂时缺席的人事物】。本卦里表面上没看到它，但它躲在某一爻底下，代表事情还在筹划、资金还在路上或未露面。"
    },
    "动爻 (Moving Line)": {
        "title": "动爻 (圈与叉)",
        "vernacular": "【突然发生的变化、事情的转折点】。老阴老阳会发生变化（变出新爻）。静止的爻代表现状稳定，动爻代表‘有动作、有变故’。"
    },
    "旬空 (Void)": {
        "title": "旬空 (空亡)",
        "vernacular": "【心里没底、暂时落空、虚晃一枪】。代表事情还在构想、资金未到位。但‘出空’（过了这个旬期）或‘冲空’时事情就会坐实落地。"
    },
    "月破 (Monthly Clash)": {
        "title": "月破",
        "vernacular": "【与大趋势逆着干、被大环境打碎】。如同逆水行舟被大浪拍碎。但交了下个月令（出月）或逢合逢值之日，尚有转机。"
    },
    "回头克 (Backlash Clash)": {
        "title": "回头克",
        "vernacular": "【搬起石头砸自己的脚】。自己主动去做一件事（动爻），变出来的结果反而克制自己本身，代表自找麻烦、好心办坏事。"
    },
    "回头生 (Supportive Trans)": {
        "title": "回头生",
        "vernacular": "【渐入佳境、越办越顺】。主动去做的一件事，变出来的结果反过来哺育支撑自己，代表后劲绵长、利好连连。"
    }
}

LAYMAN_SYSTEM_PROMPT = """
你是一位通晓六爻象数且善于用通俗现代汉语表达的“易学白话翻译官”。
请把专业 Prompt 与卦象用【初学者一听就懂的大白话】全盘解读：
1. 坚决不说玄虚黑话。世爻比喻为“你本人/己方底气”；应爻比喻为“你想办成的事/对方”；月建比喻为“行业大环境”；日辰比喻为“即时拍板人”；动爻比喻为“关键变数”。
2. 分块清晰解读：
   - 🎯【一句话定心丸/核心结论】：用一句人话概括事情成败与阻力；
   - 👥【你与事情的关系 (世应分析)】；
   - 🌪️【突发变数与隐患 (动爻与月破旬空)】；
   - ⏰【时间节律与何时转机 (应期大白话)】；
   - 💡【给当代人的务实行动建议】。
"""

def construct_dynamic_prompt(time_info: Dict[str, Any], hex_meta: Dict[str, Any], lines: List[Dict[str, Any]], evidences: List[Dict[str, Any]], question: Optional[str] = None) -> str:
    ev_summary = "\n".join([f"- 【{e['phenomenon']}】出处《{e['book_title']}·{e['chapter']}》：{e['original_text']} (解：{e['explanation']})" for e in evidences])
    
    line_desc = []
    for l in reversed(lines):
        sy = "【世爻】" if l["is_shi"] else ("【应爻】" if l["is_ying"] else "")
        chg = f" -> 变爻: {l['change_relationship']}" if l.get("change_relationship") else ""
        timing = f" [应期/时态断法: {l.get('timing_deduction')}]" if l.get("timing_deduction") else ""
        tags = "、".join(l.get("status_tags", []))
        line_desc.append(f"第{l['position']}爻 ({l['six_god']}) {l['six_relative']}{l['branch']}({l['element']}) {sy} {tags}{chg}{timing}")
    
    lines_summary = "\n".join(line_desc)

    tense_map = {"future": "推断后事发展与吉凶应期", "past": "推求前事起因与伏笔过往", "present": "决断当下处境之利弊进退"}
    tense_str = tense_map.get(time_info.get("tense", "future"), "象数义理研判")
    q_str = f"占测求问：【{question.strip()}】\n" if (question and question.strip()) else "占测求问：【全局气数象数推演】\n"

    prompt = f"""【易学考据背景设定】
{q_str}占问时空：{time_info.get('classical_date_str')}
干支提纲：月令【{time_info.get('month_branch')}月（{time_info.get('month_element')}）】提纲司令，日辰【{time_info.get('day_branch')}日（{time_info.get('day_element')}）】主事，旬空在【{time_info.get('day_kongwang')}】，月破在【{time_info.get('month_po')}】。
占问指向：{tense_str}。
卦象格局：本卦【{hex_meta.get('original_name')}】之变卦【{hex_meta.get('transformed_name')}】，属【{hex_meta.get('palace_element')}宫】。

【六爻纳甲与旺衰结构（自上而下）】
{lines_summary}

【古籍规则引证依据】
{ev_summary if ev_summary else "六爻中和，未引出特殊刑冲破害条目。"}

【学术答辩要求】
1. 严格以《增删卜易》、《黄金策》、《卜筮正宗》等正统象数法理为宗，论证必有依据。
2. 结合所占时态（{tense_str}），重点结合动变之爻、受克受生之爻、逢空逢破之爻展开论述，阐明时间节点机理。
3. 语言典雅、逻辑缜密、辩证中道。
"""
    return prompt

# ----------------- 路由接口 -----------------
@app.get("/api/classics")
async def get_classics_catalog():
    return {"status": "success", "catalog": CLASSICS_CATALOG}

@app.get("/api/glossary")
async def get_beginner_glossary():
    return {"status": "success", "glossary": BEGINNER_GLOSSARY}

@app.post("/api/divine")
async def perform_divination(req: DivineRequest):
    if req.datetime_str:
        try:
            dt = datetime.strptime(req.datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="时间格式错误，应为 'YYYY-MM-DD HH:MM:SS'")
    else:
        dt = datetime.now()

    tense = req.tense if req.tense in ["future", "past", "present"] else "future"
    time_engine = TimeEngine(dt, tense=tense)
    time_info = time_engine.to_dict()

    input_sums = req.manual_sums if req.manual_sums else []
    # 补齐不足 6 爻以支撑局部排盘
    full_sums = input_sums + [7] * (6 - len(input_sums))
    lines = generate_six_lines(full_sums[:6])
    hex_res = HexagramResult(lines)

    engine = NaJiaEngine(hex_res, day_stem=time_info["day_stem"])
    assembled = engine.assemble_full_hexagram()

    diagnosed_lines = time_engine.diagnose_lines(assembled)
    evidences = EvidenceEngine.extract_evidences(diagnosed_lines)

    hex_meta = {
        "original_name": assembled["original_name"],
        "transformed_name": assembled["transformed_name"],
        "palace_element": assembled["palace_element"],
        "missing_relations": assembled["missing_relations"],
        "shi_pos": hex_res.original_hex.shi_pos,
        "ying_pos": hex_res.original_hex.ying_pos,
        "has_changes": bool(hex_res.moving_lines)
    }

    dynamic_prompt = construct_dynamic_prompt(time_info, hex_meta, diagnosed_lines, evidences, question=req.question)

    return {
        "status": "success",
        "time_info": time_info,
        "hexagram": hex_meta,
        "lines": diagnosed_lines,
        "evidences": evidences,
        "dynamic_prompt": dynamic_prompt,
        "current_steps_count": len(input_sums)
    }

@app.post("/api/ai/layman_guide")
async def stream_layman_guide(req: LaymanGuideRequest):
    api_key = req.api_key or os.getenv("AI_API_KEY")
    api_base = req.api_base or os.getenv("AI_API_BASE", "https://api.deepseek.com/v1")
    model_name = req.model_name or os.getenv("AI_MODEL_NAME", "deepseek-chat")

    if not api_key:
        fallback_text = (
            "【离线初学白话速览】\n\n"
            "当前未配置联网模型 Key，系统已为您提供本地教学速查：\n"
            "1. 🏠【看世爻】：世爻代表你本人，找找盘面上写着【世(你)】的那一爻，旺衰生克决定了你的底气与主动权；\n"
            "2. 🎯【看应爻】：应爻代表你要问的人或事，看看【应(事)】爻与【世(你)】爻是生是克；\n"
            "3. 🌊【看环境】：上方卡片里的【月令提纲】就是行业与社会大趋势，【日辰主事】是眼下直接经办人；\n"
            "4. ⚡【看动爻】：带红色标记的木块代表事情正在发生的变故；\n"
            "5. ⏳【看应期】：留意标注旬空（暂时没有）和月破（当前受挫）的爻位，出空或逢合之日往往是转机之时。\n\n"
            "👉 请点击右上角【模型与API】填入 DeepSeek 或 Qwen 密钥，即可开启大模型全景白话深度解读！"
        )
        async def fallback_stream():
            yield fallback_text
        return StreamingResponse(fallback_stream(), media_type="text/plain; charset=utf-8")

    import openai
    client = openai.AsyncOpenAI(api_key=api_key, base_url=api_base)

    user_content = (
        f"请根据以下已经生成的专业易学排盘与 Prompt 内容，为一位易经初学者写一篇【通俗易懂、生动接地气的大白话解盘指南】。\n"
        f"必须把里面出现的专业词（世、应、月令、日辰、动爻、旬空、月破等）自然融入大白话比喻中。\n\n"
        f"【后台生成的专业 Prompt 骨架】：\n{req.dynamic_prompt}\n\n"
        f"【排盘核心数据】：\n{json.dumps(req.hexagram_context, ensure_ascii=False)}"
    )

    async def event_generator():
        try:
            stream = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": LAYMAN_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                stream=True,
                temperature=0.4
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                yield content
        except Exception as e:
            yield f"[初学导读生成异常: {str(e)}。请检查 API 配置]"

    return StreamingResponse(event_generator(), media_type="text/plain; charset=utf-8")

@app.post("/api/ai/explain")
async def explain_term(req: ExplainRequest):
    api_key = req.api_key or os.getenv("AI_API_KEY")
    api_base = req.api_base or os.getenv("AI_API_BASE", "https://api.deepseek.com/v1")
    model_name = req.model_name or os.getenv("AI_MODEL_NAME", "deepseek-chat")

    if not api_key:
        query = req.query_text.strip()
        local_ans = None
        for k, v in BEGINNER_GLOSSARY.items():
            if k.split()[0] in query:
                local_ans = f"【{v['title']}】：{v['vernacular']}"
                break
        if not local_ans:
            local_ans = (
                f"【{query}】：当前处于离线模式。此概念系六爻重要概念，"
                f"请点击右上角【模型与API】填入 DeepSeek 或 Qwen 密钥，即可实时获取动态白话解读。"
            )

        async def local_stream():
            yield local_ans

        return StreamingResponse(local_stream(), media_type="text/plain; charset=utf-8")

    import openai
    client = openai.AsyncOpenAI(api_key=api_key, base_url=api_base)

    system_prompt = req.custom_prompt or "你是一位善于用现代白话和生活案例讲解象数易理的导师。请用清晰明了、接地气的方式讲解。"
    user_content = (
        f"【待考据词句】：\n{req.query_text}\n\n"
        f"【当前卦象背景】：\n{json.dumps(req.hexagram_context, ensure_ascii=False) if req.hexagram_context else '无'}\n\n"
        f"请用【当代普通人一听就懂的大白话】进行讲解：\n"
        f"1. 这个词到底是什么意思？（用日常生活或职场打比方）\n"
        f"2. 它在当前卦局里代表了什么利好或者隐患？\n"
        f"3. 遇到它应该如何理解和应对？"
    )

    async def event_generator():
        try:
            stream = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                stream=True,
                temperature=0.3
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                yield content
        except Exception as e:
            yield f"[模型调用发生异常: {str(e)}。请检查配置]"

    return StreamingResponse(event_generator(), media_type="text/plain; charset=utf-8")

# ----------------- 静态托管 -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../frontend"))

if os.path.isdir(FRONTEND_DIR):
    css_dir = os.path.join(FRONTEND_DIR, "css")
    js_dir = os.path.join(FRONTEND_DIR, "js")
    if os.path.isdir(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.isdir(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# ---------------- 六十四卦营造图谱全量接口 ----------------
from app.core.hexagram_manual_kb import get_hexagrams_summary, get_hexagram_detail

@app.get("/api/hexagrams")
async def api_list_hexagrams():
    """获取六十四卦图谱概览列表"""
    return {"status": "success", "data": get_hexagrams_summary()}

@app.get("/api/hexagrams/{code}")
async def api_get_hexagram_detail(code: str):
    """获取单卦深度研读档案"""
    data = get_hexagram_detail(code)
    if not data:
        return {"status": "error", "message": "卦象编码未查到"}
    return {"status": "success", "data": data}
