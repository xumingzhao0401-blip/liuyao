/**
 * 六爻象数营造与典籍引证系统 - 前端总调度
 * 深度联动 2D 木块排盘与 3D 太极八卦天圆地方营造视界
 */

const API_BASE = window.location.origin;

let manualSteps = [];
let currentDivinationData = null;
let selectedTextContext = "";
let scene3dInstance = null;
let currentViewMode = "2d"; // "2d" 或 "3d"

document.addEventListener("DOMContentLoaded", () => {
    initEvents();
    initSettingsForm();
    init3DView();
});

function initEvents() {
    document.getElementById("btn-toss-single").addEventListener("click", tossSingleYao);
    document.getElementById("btn-toss-all").addEventListener("click", tossAllRemaining);
    document.getElementById("btn-undo-single").addEventListener("click", undoLastYao);
    document.getElementById("btn-reset-divine").addEventListener("click", resetAll);

    document.getElementById("select-tense").addEventListener("change", () => {
        if (manualSteps.length === 6) sendDivinationRequest(manualSteps);
    });

    const inputQ = document.getElementById("input-question");
    if (inputQ) {
        inputQ.addEventListener("change", () => {
            if (manualSteps.length === 6) sendDivinationRequest(manualSteps);
        });
    }

    // 白话导读与名词词典
    document.getElementById("btn-open-layman").addEventListener("click", openLaymanGuideModal);
    document.getElementById("layman-modal-close").addEventListener("click", () => closeModal("layman-modal"));
    document.getElementById("btn-show-glossary").addEventListener("click", openGlossaryModal);
    document.getElementById("glossary-modal-close").addEventListener("click", () => closeModal("glossary-modal"));

    // 模型 API 设置
    document.getElementById("btn-open-settings").addEventListener("click", openSettingsModal);
    document.getElementById("settings-modal-close").addEventListener("click", () => closeModal("settings-modal"));
    document.getElementById("btn-save-settings").addEventListener("click", saveSettings);
    document.getElementById("preset-deepseek").addEventListener("click", () => applyPreset("deepseek"));
    document.getElementById("preset-qwen").addEventListener("click", () => applyPreset("qwen"));
    document.getElementById("preset-local").addEventListener("click", () => applyPreset("local"));

    // 动态 Prompt 弹窗
    document.getElementById("btn-show-prompt").addEventListener("click", openPromptModal);
    document.getElementById("prompt-modal-close").addEventListener("click", () => closeModal("prompt-modal"));
    document.getElementById("btn-copy-prompt").addEventListener("click", copyPromptText);

    const btnSubmitCustom = document.getElementById("btn-submit-custom-prompt");
    if (btnSubmitCustom) {
        btnSubmitCustom.addEventListener("click", submitEditedPromptForExplain);
    }

    // 典籍档案
    document.getElementById("btn-show-classics").addEventListener("click", openClassicsModal);
    document.getElementById("classics-modal-close").addEventListener("click", () => closeModal("classics-modal"));
    document.getElementById("modal-close").addEventListener("click", () => closeModal("explain-modal"));

    // 划词气泡
    document.addEventListener("mouseup", handleTextSelection);
    document.getElementById("btn-bubble-explain").addEventListener("click", () => triggerExplain(selectedTextContext));

    // 右键自定义菜单
    document.addEventListener("contextmenu", handleContextMenu);
    document.addEventListener("click", () => hideContextMenu());
    document.getElementById("menu-item-explain").addEventListener("click", () => triggerExplain(selectedTextContext));
    document.getElementById("menu-item-copy").addEventListener("click", () => {
        navigator.clipboard.writeText(selectedTextContext);
        hideContextMenu();
    });
}

// ----------------- 3D 视图切换与自适应 -----------------
function init3DView() {
    const btnToggle = document.getElementById("btn-toggle-view");
    const btnResetCam = document.getElementById("btn-reset-camera");

    if (btnToggle) {
        btnToggle.addEventListener("click", () => {
            const vp3d = document.getElementById("viewport-3d");
            const vp2d = document.getElementById("hexagram-board");

            if (currentViewMode === "2d") {
                currentViewMode = "3d";
                btnToggle.innerText = "📜 切换 平面排盘";
                btnToggle.style.background = "#5c4033";
                vp2d.style.display = "none";
                vp3d.style.display = "block";

                requestAnimationFrame(() => {
                    if (!scene3dInstance) {
                        scene3dInstance = new LiuYaoScene3D("viewport-3d");
                    } else {
                        scene3dInstance.onWindowResize();
                    }
                    if (currentDivinationData) {
                        scene3dInstance.renderHexagram(currentDivinationData.lines, manualSteps.length);
                    }
                });
            } else {
                currentViewMode = "2d";
                btnToggle.innerText = "🏛️ 切换 3D 营造视界";
                btnToggle.style.background = "#8b4513";
                vp3d.style.display = "none";
                vp2d.style.display = "flex";
            }
        });
    }

    if (btnResetCam) {
        btnResetCam.addEventListener("click", () => {
            if (scene3dInstance) scene3dInstance.resetCamera();
        });
    }
}

// ----------------- 摇卦控制 -----------------
async function tossSingleYao() {
    if (manualSteps.length >= 6) {
        alert("六爻已卦成！如需重新起卦，请点击“重置”。");
        return;
    }

    const info = document.getElementById("stage-info");
    const resultText = document.getElementById("toss-result-text");
    const coins = [document.getElementById("coin-a"), document.getElementById("coin-b"), document.getElementById("coin-c")];

    info.innerText = `第 ${manualSteps.length + 1} 爻掷币中...`;
    coins.forEach(c => c.classList.add("rolling"));

    const tossOne = () => (Math.random() < 0.5 ? { face: "字", val: 2 } : { face: "背", val: 3 });
    const res = [tossOne(), tossOne(), tossOne()];
    const sum = res.reduce((acc, cur) => acc + cur.val, 0);

    // 联动 3D 铜钱翻掷动画
    if (scene3dInstance) {
        scene3dInstance.tossCoinsAnimation(sum);
    }

    await sleep(450);

    coins.forEach((c, idx) => {
        c.classList.remove("rolling");
        if (res[idx].face === "字") {
            c.className = "coin coin-front";
            c.innerHTML = `
                <span class="coin-text-top">乾</span>
                <span class="coin-text-bottom">隆</span>
                <span class="coin-text-right">通</span>
                <span class="coin-text-left">寶</span>
            `;
        } else {
            c.className = "coin coin-back";
            c.innerHTML = `
                <span class="coin-text-left" style="font-family: serif; font-size: 11px;">ᠪᠣᠣ</span>
                <span class="coin-text-right" style="font-family: serif; font-size: 11px;">ᠴᡳᠣᠠᠨ</span>
            `;
        }
    });

    const nameMap = { 6: "老阴 (6点·动化阳)", 7: "少阳 (7点·静)", 8: "少阴 (8点·静)", 9: "老阳 (9点·动化阴)" };
    resultText.innerText = `点数和：${sum}【${nameMap[sum]}】`;
    manualSteps.push(sum);

    updateStepDots();
    await sendDivinationRequest(manualSteps);
}

async function tossAllRemaining() {
    while (manualSteps.length < 6) {
        await tossSingleYao();
        await sleep(220);
    }
}

function undoLastYao() {
    if (manualSteps.length > 0) {
        manualSteps.pop();
        updateStepDots();
        if (manualSteps.length === 0) {
            resetAll();
        } else {
            sendDivinationRequest(manualSteps);
        }
    }
}

function resetAll() {
    manualSteps = [];
    currentDivinationData = null;
    updateStepDots();
    document.getElementById("hex-names").innerText = "虚席以待 · 请摇卦";
    document.getElementById("hexagram-board").innerHTML = `<div class="empty-tip">请点击左侧“掷下一爻”或“一键摇完”，体验木块自底向上生长营造之象</div>`;
    document.getElementById("evidence-section").style.display = "none";
    document.getElementById("bazi-board").style.display = "none";
    document.getElementById("layman-quick-bar").style.display = "none";
    document.getElementById("stage-info").innerText = "铜钱就绪，点击上方按钮掷爻";
    document.getElementById("toss-result-text").innerText = "点数：--";

    if (scene3dInstance) {
        scene3dInstance.renderHexagram([], 0);
    }
}

function updateStepDots() {
    const dots = document.querySelectorAll(".step-dots .dot");
    const countText = document.getElementById("step-count-text");
    const step = manualSteps.length;

    const names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"];
    countText.innerText = step < 6 ? `第 ${step + 1} 爻 (${names[step]})` : "六爻卦成 (圆满)";

    dots.forEach((d, idx) => {
        d.classList.remove("active", "filled");
        if (idx < step) d.classList.add("filled");
        else if (idx === step) d.classList.add("active");
    });
}

// ----------------- 发起排盘请求 -----------------
async function sendDivinationRequest(steps) {
    const dtInput = document.getElementById("input-datetime").value.trim();
    const tense = document.getElementById("select-tense").value;
    const inputQ = document.getElementById("input-question");
    const question = inputQ ? inputQ.value.trim() : "";

    const payload = { manual_sums: steps, tense: tense, question: question };
    if (dtInput) payload.datetime_str = dtInput;

    try {
        const resp = await fetch(`${API_BASE}/api/divine`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) {
            console.error("排盘接口报错:", await resp.text());
            return;
        }

        const data = await resp.json();
        currentDivinationData = data;
        renderAll(data, steps.length);

        // 同步通知 3D 引擎更新木块排盘
        if (scene3dInstance) {
            scene3dInstance.renderHexagram(data.lines, steps.length);
        }
    } catch (e) {
        console.error("请求失败:", e);
    }
}

// ----------------- 2D 排盘渲染 -----------------
function renderAll(data, currentCount) {
    renderTimeBoard(data.time_info);
    renderHexagramBoard(data.hexagram, data.lines, currentCount);

    if (currentCount === 6) {
        renderEvidenceBoard(data.evidences);
        const qbar = document.getElementById("layman-quick-bar");
        if (qbar) qbar.style.display = "block";
    } else {
        document.getElementById("evidence-section").style.display = "none";
        const qbar = document.getElementById("layman-quick-bar");
        if (qbar) qbar.style.display = "none";
    }
}

function renderTimeBoard(time) {
    document.getElementById("bazi-board").style.display = "block";
    document.getElementById("classical-date-text").innerText = time.classical_date_str;
    document.getElementById("bz-year").innerText = time.year_ganzhi;
    document.getElementById("bz-month").innerText = time.month_ganzhi;
    document.getElementById("bz-day").innerText = time.day_ganzhi;
    document.getElementById("bz-time").innerText = time.time_ganzhi;
    document.getElementById("bz-kong").innerText = time.day_kongwang;
    document.getElementById("bz-po").innerText = `${time.month_po} (冲破)`;
}

function renderHexagramBoard(hexMeta, lines, currentCount) {
    const titleEl = document.getElementById("hex-names");
    if (currentCount < 6) {
        titleEl.innerText = `【起卦中... 已成 ${currentCount}/6 爻】`;
    } else {
        const transText = hexMeta.transformed_name ? ` 之 ${hexMeta.transformed_name}` : " (静卦)";
        titleEl.innerText = `【${hexMeta.original_name}】${transText} · ${hexMeta.palace_element}宫`;
    }

    const board = document.getElementById("hexagram-board");
    board.innerHTML = "";

    for (let i = lines.length - 1; i >= 0; i--) {
        const line = lines[i];
        const isRendered = (line.position <= currentCount);
        const row = document.createElement("div");
        row.className = "yao-row";
        if (!isRendered) {
            row.style.opacity = "0.22";
        }

        const fushenText = (isRendered && line.fushen) ? `伏 ${line.fushen.six_relative}${line.fushen.branch}` : "";
        const fushenCol = `<div class="col-fushen">${fushenText}</div>`;
        const sixgodCol = `<div class="col-sixgod">${isRendered ? line.six_god : "--"}</div>`;

        let syHtml = `<span class="badge" style="visibility:hidden">平</span>`;
        if (isRendered && currentCount === 6) {
            if (line.is_shi) syHtml = `<span class="mark-shi">世(你)</span>`;
            else if (line.is_ying) syHtml = `<span class="mark-ying">应(事)</span>`;
        }
        const shiyingCol = `<div class="col-shiying">${syHtml}</div>`;

        let woodHtml = "";
        let animClass = "";
        if (isRendered) {
            if (line.anim_type === "wood_split") animClass = "anim-split";
            if (line.anim_type === "wood_merge") animClass = "anim-merge";

            if (line.wood_type === "solid_wood") {
                woodHtml = `<div class="wood-block wood-solid ${animClass}"></div>`;
            } else {
                woodHtml = `
                    <div class="wood-split-wrap ${animClass}">
                        <div class="wood-block wood-part"></div>
                        <div class="wood-block wood-part"></div>
                    </div>
                `;
            }
        } else {
            woodHtml = `<div style="border-bottom: 2px dashed #d5ccbe; width: 140px; height: 12px;"></div>`;
        }
        const woodCol = `<div class="col-wood">${woodHtml}</div>`;
        const markCol = `<div class="col-mark">${(isRendered && line.mark) ? line.mark : ""}</div>`;

        let tagsHtml = "";
        if (isRendered && line.status_tags && line.status_tags.length > 0) {
            tagsHtml = line.status_tags.map(t => `<span class="tag-status">${t}</span>`).join(" ");
        }
        let changeHtml = "";
        if (isRendered && line.change_relationship) {
            changeHtml = `<span class="tag-change">${line.change_relationship}</span>`;
        }
        let timingHtml = "";
        if (isRendered && currentCount === 6 && line.timing_deduction) {
            timingHtml = `<span class="tag-timing">应期: ${line.timing_deduction}</span>`;
        }

        const detailCol = `
            <div class="col-detail">
                <strong>第${line.position}爻 [${isRendered ? line.line_name : "待摇"}]</strong>
                <span>${isRendered ? (line.six_relative + line.branch + '(' + line.element + ')') : "--"}</span>
                ${changeHtml}
                ${tagsHtml}
                ${timingHtml}
            </div>
        `;

        row.innerHTML = fushenCol + sixgodCol + shiyingCol + woodCol + markCol + detailCol;
        board.appendChild(row);
    }
}

function renderEvidenceBoard(evidences) {
    const sec = document.getElementById("evidence-section");
    const grid = document.getElementById("evidence-grid");
    const countEl = document.getElementById("evidence-count");

    sec.style.display = "block";
    grid.innerHTML = "";

    if (!evidences || evidences.length === 0) {
        countEl.innerText = "0 条依据";
        grid.innerHTML = `<div style="color: #6e675f; padding: 10px;">盘面六爻和顺中正，暂未触发旬空、月破或自刑相冲等特殊破败条目。</div>`;
        return;
    }

    countEl.innerText = `${evidences.length} 条依据`;
    evidences.forEach((ev, idx) => {
        const card = document.createElement("div");
        card.className = "evidence-card";
        card.innerHTML = `
            <div class="evidence-header">
                <span>【依据 ${idx + 1}】${ev.phenomenon} · ${ev.target}</span>
                <span>${ev.book_title}</span>
            </div>
            <div style="font-size: 11px; color: #8b3a2b; margin-bottom: 6px;">篇章：${ev.chapter}</div>
            <div class="evidence-quote">“${ev.original_text}”</div>
            <div class="evidence-desc">${ev.explanation}</div>
        `;
        grid.appendChild(card);
    });
}

// ----------------- 白话通俗导读 -----------------
async function openLaymanGuideModal() {
    if (!currentDivinationData || manualSteps.length < 6) {
        alert("请先完成六次摇卦生成完整卦象，系统方可根据全卦为您进行大白话解读！");
        return;
    }

    const modal = document.getElementById("layman-modal");
    const content = document.getElementById("layman-content");
    const badge = document.getElementById("layman-model-badge");

    const cfg = getStoredSettings();
    badge.innerText = cfg.apiKey ? `解读引擎: ${cfg.modelName} (${cfg.apiBase})` : "解读引擎: 本地离线速查 (可在右上角配置 Key 体验大模型全景白话分析)";

    content.innerText = "正在调动易学白话翻译官，将干支生克、动爻变数与应期转化为当代生活大白话...";
    modal.style.display = "flex";

    const payload = {
        hexagram_context: currentDivinationData.hexagram,
        dynamic_prompt: currentDivinationData.dynamic_prompt,
        api_key: cfg.apiKey,
        api_base: cfg.apiBase,
        model_name: cfg.modelName
    };

    try {
        const resp = await fetch(`${API_BASE}/api/ai/layman_guide`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) {
            content.innerText = "白话导读接口响应异常。";
            return;
        }

        const reader = resp.body.getReader();
        const decoder = new TextDecoder("utf-8");
        content.innerText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            content.innerText += chunk;
        }
    } catch (e) {
        content.innerText = `导读生成出错: ${e.message}`;
    }
}

// ----------------- 专有名词大白话词典 -----------------
async function openGlossaryModal() {
    const modal = document.getElementById("glossary-modal");
    const grid = document.getElementById("glossary-grid");
    modal.style.display = "flex";
    grid.innerHTML = "正在载入专有名词通俗库...";

    try {
        const resp = await fetch(`${API_BASE}/api/glossary`);
        const data = await resp.json();
        grid.innerHTML = "";

        Object.values(data.glossary).forEach(item => {
            const card = document.createElement("div");
            card.className = "glossary-card";
            card.innerHTML = `
                <div class="glossary-title">📌 ${item.title}</div>
                <div class="glossary-vernacular">${item.vernacular}</div>
            `;
            grid.appendChild(card);
        });
    } catch (e) {
        grid.innerText = `加载失败: ${e.message}`;
    }
}

// ----------------- 划词与右键菜单 -----------------
function handleTextSelection(e) {
    const bubble = document.getElementById("selection-bubble");
    if (e.target.closest("#selection-bubble") || e.target.closest(".modal") || e.target.closest("#context-menu")) return;

    const selection = window.getSelection();
    const text = selection.toString().trim();

    if (text.length > 0 && text.length <= 60) {
        selectedTextContext = text;
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        bubble.style.left = `${rect.left + rect.width / 2 + window.scrollX}px`;
        bubble.style.top = `${rect.top + window.scrollY}px`;
        bubble.style.display = "block";
    } else {
        bubble.style.display = "none";
    }
}

function handleContextMenu(e) {
    const selection = window.getSelection();
    const text = selection.toString().trim();

    if (text.length > 0) {
        e.preventDefault();
        selectedTextContext = text;
        const menu = document.getElementById("context-menu");
        menu.style.left = `${e.pageX}px`;
        menu.style.top = `${e.pageY}px`;
        menu.style.display = "block";
        document.getElementById("selection-bubble").style.display = "none";
    } else {
        hideContextMenu();
    }
}

function hideContextMenu() {
    const menu = document.getElementById("context-menu");
    if (menu) menu.style.display = "none";
}

// ----------------- 词句考据 -----------------
async function triggerExplain(queryText) {
    hideContextMenu();
    document.getElementById("selection-bubble").style.display = "none";

    const modal = document.getElementById("explain-modal");
    const title = document.getElementById("modal-term-title");
    const content = document.getElementById("modal-explanation");
    const badge = document.getElementById("modal-model-badge");

    const cfg = getStoredSettings();
    badge.innerText = cfg.apiKey ? `解读引擎: ${cfg.modelName} (${cfg.apiBase})` : "解读引擎: 本地离线词典";

    title.innerText = `大白话考据：“${queryText}”`;
    content.innerText = "调阅古籍提纲与卦境上下文推演中...";
    modal.style.display = "flex";

    const payload = {
        query_text: queryText,
        hexagram_context: currentDivinationData ? currentDivinationData.hexagram : null,
        custom_prompt: currentDivinationData ? currentDivinationData.dynamic_prompt : null,
        api_key: cfg.apiKey,
        api_base: cfg.apiBase,
        model_name: cfg.modelName
    };

    try {
        const resp = await fetch(`${API_BASE}/api/ai/explain`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) {
            content.innerText = "服务响应异常。";
            return;
        }

        const reader = resp.body.getReader();
        const decoder = new TextDecoder("utf-8");
        content.innerText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            content.innerText += chunk;
        }
    } catch (err) {
        content.innerText = `推演异常: ${err.message}`;
    }
}

// ----------------- 动态 Prompt 预览与复制 -----------------
function openPromptModal() {
    const modal = document.getElementById("prompt-modal");
    const textarea = document.getElementById("prompt-content-text");
    modal.style.display = "flex";
    if (currentDivinationData && currentDivinationData.dynamic_prompt) {
        textarea.value = currentDivinationData.dynamic_prompt;
    } else {
        textarea.value = "尚未生成完整卦象。请先完成六次摇卦。";
    }
}

function copyPromptText() {
    const textarea = document.getElementById("prompt-content-text");
    if (!textarea || !textarea.value.trim()) {
        alert("暂无 Prompt 内容可复制！");
        return;
    }
    const text = textarea.value;

    try {
        textarea.focus();
        textarea.select();
        textarea.setSelectionRange(0, 99999);
        const successful = document.execCommand("copy");
        if (successful) {
            alert("Prompt 已成功复制到剪贴板！");
            return;
        }
    } catch (e) {}

    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            alert("Prompt 已成功复制到剪贴板！");
        }).catch(() => {
            alert("已自动选中文本，请按 Ctrl+C / Cmd+C 复制。");
        });
    } else {
        alert("已自动选中文本，请直接按 Ctrl+C / Cmd+C 复制！");
    }
}

async function submitEditedPromptForExplain() {
    const customPrompt = document.getElementById("prompt-content-text").value.trim();
    if (!customPrompt) {
        alert("Prompt 内容不能为空！");
        return;
    }
    closeModal("prompt-modal");

    const modal = document.getElementById("explain-modal");
    const title = document.getElementById("modal-term-title");
    const content = document.getElementById("modal-explanation");
    const badge = document.getElementById("modal-model-badge");

    const cfg = getStoredSettings();
    badge.innerText = cfg.apiKey ? `解读引擎: ${cfg.modelName} (${cfg.apiBase})` : "解读引擎: 本地离线词典 (请配置 Key)";

    title.innerText = "自定义 Prompt 深度全景推演";
    content.innerText = "正在将您编辑完善的卦境 Prompt 提交给 AI 模型深入研读...";
    modal.style.display = "flex";

    const payload = {
        query_text: "请根据上述完整的卦象背景与用户求占具体事由，展开深度全景推演分析与务实行动建议。",
        hexagram_context: currentDivinationData ? currentDivinationData.hexagram : null,
        custom_prompt: customPrompt,
        api_key: cfg.apiKey,
        api_base: cfg.apiBase,
        model_name: cfg.modelName
    };

    try {
        const resp = await fetch(`${API_BASE}/api/ai/explain`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) {
            content.innerText = "服务响应异常。";
            return;
        }

        const reader = resp.body.getReader();
        const decoder = new TextDecoder("utf-8");
        content.innerText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            content.innerText += chunk;
        }
    } catch (err) {
        content.innerText = `推演异常: ${err.message}`;
    }
}

// ----------------- API 设置管理 -----------------
function getStoredSettings() {
    return {
        apiBase: localStorage.getItem("ly_api_base") || "",
        apiKey: localStorage.getItem("ly_api_key") || "",
        modelName: (localStorage.getItem("ly_model_name") || "deepseek-chat").replace(/\s+/g, "-")
    };
}

function initSettingsForm() {
    const cfg = getStoredSettings();
    document.getElementById("cfg-api-base").value = cfg.apiBase;
    document.getElementById("cfg-api-key").value = cfg.apiKey;
    document.getElementById("cfg-model-name").value = cfg.modelName;
}

function openSettingsModal() {
    initSettingsForm();
    document.getElementById("settings-modal").style.display = "flex";
}

function saveSettings() {
    const base = document.getElementById("cfg-api-base").value.trim();
    const key = document.getElementById("cfg-api-key").value.trim();
    const model = document.getElementById("cfg-model-name").value.trim().replace(/\s+/g, "-") || "deepseek-chat";

    localStorage.setItem("ly_api_base", base);
    localStorage.setItem("ly_api_key", key);
    localStorage.setItem("ly_model_name", model);

    alert("模型配置已保存！");
    closeModal("settings-modal");
}

function applyPreset(type) {
    if (type === "deepseek") {
        document.getElementById("cfg-api-base").value = "https://api.deepseek.com/v1";
        document.getElementById("cfg-model-name").value = "deepseek-chat";
    } else if (type === "qwen") {
        document.getElementById("cfg-api-base").value = "https://dashscope.aliyuncs.com/compatible-mode/v1";
        document.getElementById("cfg-model-name").value = "qwen-plus";
    } else if (type === "local") {
        document.getElementById("cfg-api-base").value = "";
        document.getElementById("cfg-api-key").value = "";
        document.getElementById("cfg-model-name").value = "local-dict";
    }
}

// ----------------- 典籍档案 -----------------
async function openClassicsModal() {
    const modal = document.getElementById("classics-modal");
    const list = document.getElementById("classics-list");
    modal.style.display = "flex";
    list.innerHTML = "载入中...";

    try {
        const resp = await fetch(`${API_BASE}/api/classics`);
        const data = await resp.json();
        list.innerHTML = "";
        Object.values(data.catalog).forEach(b => {
            const item = document.createElement("div");
            item.className = "classics-item";
            item.innerHTML = `
                <h4>《${b.title}》 <small>(${b.dynasty} · ${b.author})</small></h4>
                <p>${b.summary}</p>
            `;
            list.appendChild(item);
        });
    } catch (e) {
        list.innerText = `加载失败: ${e.message}`;
    }
}

function closeModal(id) {
    document.getElementById(id).style.display = "none";
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ================== 3D 构件点击二级研读抽屉调度 ==================
let currentSelectedLineData = null;

window.openYaoDetailDrawer = function(line) {
    if (!line) return;
    currentSelectedLineData = line;

    const drawer = document.getElementById("drawer-3d-detail");
    const posEl = document.getElementById("dr-yao-pos");
    const titleEl = document.getElementById("dr-yao-title");
    const tagsEl = document.getElementById("dr-tags");
    const descEl = document.getElementById("dr-desc");
    const timingBox = document.getElementById("dr-timing-box");

    drawer.style.display = "flex";

    const posNames = ["初爻 (地基发端)", "二爻 (厅堂根基)", "三爻 (门坎转折)", "四爻 (枢纽阶梯)", "五爻 (尊位君位)", "上爻 (宗庙巅峰)"];
    posEl.innerText = `第 ${line.position} 爻 · ${posNames[line.position - 1] || ""}`;

    const nature = line.nature === "yang" ? "阳爻 (奇数天数)" : "阴爻 (偶数地数)";
    const movingStr = line.is_moving ? "【动爻 · 局中有变】" : "【静爻 · 安稳如初】";
    titleEl.innerText = `${line.six_god} · ${line.six_relative} ${line.branch}(${line.element}) ${movingStr}`;

    // 标签
    let tagsHtml = `<span class="badge badge-info">${nature}</span>`;
    if (line.is_shi) tagsHtml += `<span class="badge badge-warn" style="background:#b37400;color:#fff;">【世爻】代表求测者己方基本盘</span>`;
    if (line.is_ying) tagsHtml += `<span class="badge badge-info" style="background:#1565c0;color:#fff;">【应爻】代表所谋之事/对方/环境</span>`;
    if (line.status_tags && line.status_tags.length > 0) {
        line.status_tags.forEach(t => { tagsHtml += `<span class="badge badge-warn">${t}</span>`; });
    }
    if (line.change_relationship) {
        tagsHtml += `<span class="badge badge-danger">${line.change_relationship}</span>`;
    }
    tagsEl.innerHTML = tagsHtml;

    // 白话角色隐喻分析
    let roleText = "";
    if (line.is_shi) {
        roleText = `🏠【你本人（世爻）】：这一爻是你在全卦里的“化身”。它是整件事情的承载主体。它的五行旺衰直接反映了你当下的精神底气、掌控力和资源厚度。`;
    } else if (line.is_ying) {
        roleText = `🎯【所问之事/对方（应爻）】：这一爻代表你要办的那件事、面试官、投资标的或合伙人。世爻生应爻代表你主动付出，应爻生世爻代表事情顺理成章找上门。`;
    } else {
        const relMap = {
            "父母": "代表证件、文书、房屋、合同、方案、长辈庇护或辛苦劳碌。",
            "官鬼": "代表工作职务、主管领导、官方政策、考核压力或潜在风险。",
            "兄弟": "代表合伙人、竞争对手、同行分摊、求财路上分流利益的变数。",
            "妻财": "代表资金链、收入利润、实际物质回报与可落地的利益。",
            "子孙": "代表福星、解忧策略、技术方案、产品创新与化解危机的喜神。"
        };
        roleText = `🧩【事态关联角色】：作为【${line.six_relative}】，${relMap[line.six_relative] || "在局中发挥特定的生克平衡作用。"}`;
    }

    if (line.is_moving) {
        roleText += `<br><br>⚡【突变玄机】：此爻发动，说明事情正在此处发生转机或震荡！变出的结果（${line.change_relationship || "动化"}）直接预示了下一步的演化走向。`;
    }
    descEl.innerHTML = roleText;

    // 时空应期推演
    let timingText = `<strong>时令旺衰：</strong>本爻临地支【${line.branch}】，五行属【${line.element}】。`;
    if (line.timing_deduction) {
        timingText += `<br><strong>应期节点：</strong>${line.timing_deduction}`;
    } else {
        timingText += `<br><strong>局势节律：</strong>此爻为静爻，局势平稳受时令滋润，以月令提纲与日辰主事之生克为准。`;
    }
    timingBox.innerHTML = timingText;
};

// 抽屉关闭事件
document.addEventListener("DOMContentLoaded", () => {
    const btnCloseDrawer = document.getElementById("dr-close-btn");
    if (btnCloseDrawer) {
        btnCloseDrawer.addEventListener("click", () => {
            document.getElementById("drawer-3d-detail").style.display = "none";
        });
    }

    const btnAskAi = document.getElementById("dr-ai-ask-btn");
    if (btnAskAi) {
        btnAskAi.addEventListener("click", () => {
            if (!currentSelectedLineData) return;
            document.getElementById("drawer-3d-detail").style.display = "none";
            const query = `请针对本卦第 ${currentSelectedLineData.position} 爻【${currentSelectedLineData.six_god} ${currentSelectedLineData.six_relative}${currentSelectedLineData.branch}(${currentSelectedLineData.element})】进行深入大白话全盘剖析，结合世应关系与动变说明现实应对策略。`;
            triggerExplain(query);
        });
    }
});

window.openYaoDetailDrawer = openYaoDetailDrawer;
