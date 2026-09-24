/**
 * 东方写意水墨动效引擎 - 高性能无损版 (Ink Effects Engine)
 * 1. 远山叠翠/江汀云雾背景渲染 (低频静态合成，0卡顿)
 * 2. 毫芒水墨笔刷光标拖尾 (贝塞尔曲线平滑 + 飞白晕染 + 速度自适应)
 */

(function () {
    // ================= 1. 远近山峦与水墨画背景 =================
    const bgCanvas = document.getElementById("ink-bg-canvas");
    if (!bgCanvas) return;
    const bgCtx = bgCanvas.getContext("2d");

    let width = (bgCanvas.width = window.innerWidth);
    let height = (bgCanvas.height = window.innerHeight);

    // 预计算山峦地形轮廓点（避免每帧计算）
    function generateMountainPoints(segments, baseY, amplitude, roughness) {
        const points = [];
        const step = width / segments;
        for (let i = 0; i <= segments + 2; i++) {
            const x = (i - 1) * step;
            const noise = Math.sin(i * 0.45) * Math.cos(i * 0.28) * amplitude;
            points.push({ x, y: baseY + noise });
        }
        return points;
    }

    let mountains = [];
    function initMountains() {
        mountains = [
            // 远山（墨色极淡，若隐若现）
            { color: "rgba(185, 178, 166, 0.22)", points: generateMountainPoints(24, height * 0.55, 110, 0.4), speed: 0.0003 },
            // 次远山（清墨重山）
            { color: "rgba(145, 138, 126, 0.28)", points: generateMountainPoints(20, height * 0.65, 95, 0.5), speed: 0.0005 },
            // 近景山冈（稍浓，苍秀）
            { color: "rgba(98, 90, 80, 0.20)", points: generateMountainPoints(16, height * 0.78, 80, 0.6), speed: 0.0008 }
        ];
    }

    function drawMountainLayer(m, offset) {
        bgCtx.fillStyle = m.color;
        bgCtx.beginPath();
        bgCtx.moveTo(0, height);

        const pts = m.points;
        for (let i = 0; i < pts.length - 1; i++) {
            const p0 = pts[i];
            const p1 = pts[i + 1];
            // 微妙起伏
            const wave = Math.sin(offset + i) * 8;
            const cX = (p0.x + p1.x) / 2;
            const cY = (p0.y + p1.y) / 2 + wave;
            bgCtx.quadraticCurveTo(p0.x, p0.y + wave, cX, cY);
        }
        bgCtx.lineTo(width, height);
        bgCtx.closePath();
        bgCtx.fill();
    }

    let bgTime = 0;
    function renderBackground() {
        bgCtx.clearRect(0, 0, width, height);

        // 宣纸温润底晕
        const grad = bgCtx.createRadialGradient(width * 0.5, height * 0.3, 80, width * 0.5, height * 0.5, width * 0.8);
        grad.addColorStop(0, "rgba(255, 252, 246, 0.6)");
        grad.addColorStop(1, "rgba(240, 233, 220, 0.85)");
        bgCtx.fillStyle = grad;
        bgCtx.fillRect(0, 0, width, height);

        // 渲染三层叠墨山水
        mountains.forEach((m, idx) => {
            drawMountainLayer(m, bgTime * m.speed * 1000);
        });

        bgTime += 0.01;
    }

    initMountains();
    // 背景以 20FPS 极低频绘制（烟雨淡雅），完全不争抢 CPU 资源
    setInterval(renderBackground, 50);

    // ================= 2. 高性能写意水墨毛笔拖尾 =================
    const trailCanvas = document.getElementById("ink-trail-canvas");
    if (!trailCanvas) return;
    const trailCtx = trailCanvas.getContext("2d");

    trailCanvas.width = width;
    trailCanvas.height = height;

    const points = [];
    const MAX_POINTS = 28; // 保持 28 个控制点，平滑且不卡顿
    const drops = [];      // 飞白墨粒

    let lastMouse = { x: 0, y: 0, time: Date.now() };

    window.addEventListener("pointermove", (e) => {
        const now = Date.now();
        const dt = Math.max(now - lastMouse.time, 1);
        const dist = Math.hypot(e.clientX - lastMouse.x, e.clientY - lastMouse.y);
        const speed = Math.min(dist / dt, 6); // 光标滑动速度

        lastMouse = { x: e.clientX, y: e.clientY, time: now };

        // 速度快时笔画细、速度慢时浓墨重彩
        const targetRadius = Math.max(14 - speed * 1.8, 3.5);

        points.push({
            x: e.clientX,
            y: e.clientY,
            radius: targetRadius,
            alpha: 0.75,
            age: 0
        });

        // 快速挥毫时产生轻微飞白水墨微滴
        if (speed > 2.2 && Math.random() < 0.35) {
            drops.push({
                x: e.clientX + (Math.random() - 0.5) * 12,
                y: e.clientY + (Math.random() - 0.5) * 12,
                radius: Math.random() * 2.2 + 1,
                alpha: 0.65,
                vx: (Math.random() - 0.5) * 1.5,
                vy: Math.random() * 1.2
            });
        }

        if (points.length > MAX_POINTS) {
            points.shift();
        }
    });

    function renderTrail() {
        // 轻柔淡出上一帧，产生宣纸洇墨留痕感
        trailCtx.globalCompositeOperation = "destination-out";
        trailCtx.fillStyle = "rgba(0, 0, 0, 0.12)";
        trailCtx.fillRect(0, 0, width, height);

        trailCtx.globalCompositeOperation = "source-over";

        // 绘制主干水墨曲线 (三次贝塞尔拟合毛笔手感)
        if (points.length > 2) {
            for (let i = 1; i < points.length - 1; i++) {
                const xc = (points[i].x + points[i + 1].x) / 2;
                const yc = (points[i].y + points[i + 1].y) / 2;
                const p = points[i];

                trailCtx.beginPath();
                trailCtx.moveTo(p.x, p.y);
                trailCtx.quadraticCurveTo(p.x, p.y, xc, yc);

                // 松烟墨色 (微暖玄色)
                trailCtx.strokeStyle = `rgba(32, 28, 25, ${p.alpha})`;
                trailCtx.lineWidth = p.radius;
                trailCtx.lineCap = "round";
                trailCtx.lineJoin = "round";
                trailCtx.stroke();

                p.alpha *= 0.92;
                p.radius *= 0.96;
            }
        }

        // 渲染零散飞白墨粒
        for (let i = drops.length - 1; i >= 0; i--) {
            const d = drops[i];
            trailCtx.beginPath();
            trailCtx.arc(d.x, d.y, d.radius, 0, Math.PI * 2);
            trailCtx.fillStyle = `rgba(38, 32, 28, ${d.alpha})`;
            trailCtx.fill();

            d.x += d.vx;
            d.y += d.vy;
            d.alpha *= 0.88;

            if (d.alpha < 0.05) {
                drops.splice(i, 1);
            }
        }

        // 清理老旧控制点
        while (points.length > 0 && points[0].alpha < 0.04) {
            points.shift();
        }

        requestAnimationFrame(renderTrail);
    }

    requestAnimationFrame(renderTrail);

    // 窗口尺寸自适应
    window.addEventListener("resize", () => {
        width = bgCanvas.width = trailCanvas.width = window.innerWidth;
        height = bgCanvas.height = trailCanvas.height = window.innerHeight;
        initMountains();
    });
})();
