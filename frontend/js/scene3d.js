/**
 * 六爻 3D 象数营造引擎 - 终极纯净稳定版
 * 特性：
 * 1. 实体不透明玄黑舞台 (alpha: false，彻底阻绝底图穿透)
 * 2. 完整金镶玉月梁、浑天立体罗盘台、法线阳文铜钱
 * 3. 完整射线拾取 (Raycaster)，点击木梁/白玉直出二级抽屉
 */

class LiuYaoScene3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.labelsContainer = document.getElementById("labels-3d-container");
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;

        this.hexGroup = new THREE.Group();
        this.plinthGroup = new THREE.Group();
        this.particleGroup = new THREE.Group();
        this.coins = [];
        this.materials = {};
        
        this.trackedBeams = [];
        this.animatingBeams = [];
        this.clickableMeshes = [];
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.pointerDownPos = { x: 0, y: 0 };
        this.isInitialized = false;

        this.init();
    }

    init() {
        if (!this.container || typeof THREE === "undefined") return;

        let width = this.container.clientWidth || 860;
        let height = this.container.clientHeight || 640;
        if (height < 300) height = 640;

        // 1. 纯净幽邃夜空背景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0e0c0a);
        this.scene.fog = new THREE.FogExp2(0x0e0c0a, 0.02);

        // 2. 相机
        this.camera = new THREE.PerspectiveCamera(34, width / height, 0.1, 100);
        this.resetCamera();

        // 3. 渲染器：alpha: false 彻底阻断透明透底
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true, 
            alpha: false, 
            powerPreference: "high-performance" 
        });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.setClearColor(0x0e0c0a, 1.0);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.3;

        const oldCanvas = this.container.querySelector("canvas");
        if (oldCanvas) oldCanvas.remove();
        this.container.appendChild(this.renderer.domElement);

        // 4. 控制器
        if (typeof THREE.OrbitControls !== "undefined") {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
            this.controls.rotateSpeed = 0.7;
            this.controls.zoomSpeed = 1.0;
            this.controls.maxPolarAngle = Math.PI / 2 - 0.04;
            this.controls.minDistance = 5;
            this.controls.maxDistance = 22;
        }

        // 5. 生成展厅反射贴图
        this.generateEnvironmentMap();

        // 6. 光照
        this.setupLighting();

        // 7. 材质
        this.initMaterials();

        // 8. 建造下沉式浑天立体罗盘台
        this.buildSculptedPlinth();

        // 9. 建造乾隆通宝
        this.buildAuthenticCoins();

        // 10. 星尘微粒
        this.buildAtmosphereParticles();

        this.scene.add(this.plinthGroup);
        this.scene.add(this.hexGroup);
        this.scene.add(this.particleGroup);

        // 11. 绑定交互事件
        window.addEventListener("resize", () => this.onWindowResize());
        
        const dom = this.renderer.domElement;
        dom.addEventListener("pointerdown", (e) => {
            this.pointerDownPos = { x: e.clientX, y: e.clientY };
        });
        dom.addEventListener("pointerup", (e) => {
            const dist = Math.hypot(e.clientX - this.pointerDownPos.x, e.clientY - this.pointerDownPos.y);
            if (dist < 6) {
                this.onCanvasClick(e);
            }
        });

        this.animate();
        this.isInitialized = true;
    }

    resetCamera() {
        if (!this.camera) return;
        this.camera.position.set(0, 5.6, 14.5);
        this.camera.lookAt(0, 2.6, 0);
        if (this.controls) {
            this.controls.target.set(0, 2.6, 0);
            this.controls.update();
        }
    }

    generateEnvironmentMap() {
        const pmremGenerator = new THREE.PMREMGenerator(this.renderer);
        pmremGenerator.compileEquirectangularShader();

        const canvas = document.createElement("canvas");
        canvas.width = 512;
        canvas.height = 256;
        const ctx = canvas.getContext("2d");

        const grad = ctx.createLinearGradient(0, 0, 0, 256);
        grad.addColorStop(0, "#2c2621");
        grad.addColorStop(0.4, "#191512");
        grad.addColorStop(1, "#080706");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 512, 256);

        ctx.fillStyle = "#ffecd1";
        ctx.beginPath();
        ctx.arc(256, 60, 40, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#8ab8db";
        ctx.beginPath();
        ctx.arc(100, 160, 25, 0, Math.PI * 2);
        ctx.fill();

        const tex = new THREE.CanvasTexture(canvas);
        tex.mapping = THREE.EquirectangularReflectionMapping;
        this.envMap = pmremGenerator.fromEquirectangular(tex).texture;
        this.scene.environment = this.envMap;
        pmremGenerator.dispose();
    }

    setupLighting() {
        const hemi = new THREE.HemisphereLight(0xfffaed, 0x14110e, 1.4);
        this.scene.add(hemi);

        const sun = new THREE.DirectionalLight(0xffeedb, 3.2);
        sun.position.set(4, 15, 10);
        sun.castShadow = true;
        sun.shadow.mapSize.width = 2048;
        sun.shadow.mapSize.height = 2048;
        sun.shadow.bias = -0.0001;
        this.scene.add(sun);

        const cyanRim = new THREE.DirectionalLight(0x73a8cc, 1.8);
        cyanRim.position.set(-8, 8, -6);
        this.scene.add(cyanRim);

        const bottomLight = new THREE.DirectionalLight(0xb89255, 0.6);
        bottomLight.position.set(0, -6, 4);
        this.scene.add(bottomLight);

        this.zhushaLight = new THREE.PointLight(0xff3311, 0, 9);
        this.zhushaLight.position.set(0, 2.8, 1.8);
        this.scene.add(this.zhushaLight);
    }

    initMaterials() {
        this.materials.ebonyWood = new THREE.MeshStandardMaterial({
            color: 0x2b211a,
            roughness: 0.38,
            metalness: 0.12,
            envMap: this.envMap
        });

        this.materials.whiteJade = new THREE.MeshPhysicalMaterial({
            color: 0xf8f4ea,
            emissive: 0xdfd4bc,
            emissiveIntensity: 0.18,
            roughness: 0.18,
            metalness: 0.05,
            transmission: 0.35,
            transparent: true,
            opacity: 0.95,
            ior: 1.5,
            envMap: this.envMap
        });

        this.materials.movingJade = new THREE.MeshPhysicalMaterial({
            color: 0xba2b1a,
            emissive: 0x821508,
            emissiveIntensity: 0.65,
            roughness: 0.2,
            metalness: 0.08,
            transmission: 0.3,
            transparent: true,
            opacity: 0.96,
            envMap: this.envMap
        });

        this.materials.goldChased = new THREE.MeshStandardMaterial({
            color: 0xd9b360,
            roughness: 0.25,
            metalness: 0.88,
            envMap: this.envMap
        });

        this.materials.daisBase = new THREE.MeshStandardMaterial({
            color: 0x181513,
            roughness: 0.45,
            metalness: 0.25,
            envMap: this.envMap
        });

        this.materials.daisGoldPool = new THREE.MeshStandardMaterial({
            color: 0x8a6a34,
            roughness: 0.25,
            metalness: 0.75,
            envMap: this.envMap
        });

        this.materials.coinFace = this.createReliefCoinMaterial(true);
        this.materials.coinBack = this.createReliefCoinMaterial(false);
        this.materials.coinEdge = new THREE.MeshStandardMaterial({ 
            color: 0x875f28, 
            roughness: 0.45, 
            metalness: 0.85, 
            envMap: this.envMap 
        });
    }

    createReliefCoinMaterial(isFront) {
        const size = 1024;
        const canvas = document.createElement("canvas");
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext("2d");

        ctx.fillStyle = "#9c7336";
        ctx.fillRect(0, 0, size, size);

        for (let i = 0; i < 4000; i++) {
            ctx.fillStyle = (Math.random() < 0.2) ? "rgba(40, 85, 60, 0.3)" : "rgba(220, 180, 100, 0.15)";
            ctx.fillRect(Math.random() * size, Math.random() * size, 3, 3);
        }

        ctx.lineWidth = 42;
        ctx.strokeStyle = "#cbb269";
        ctx.beginPath();
        ctx.arc(size / 2, size / 2, size / 2 - 28, 0, Math.PI * 2);
        ctx.stroke();

        const holeW = 230;
        const holeX = (size - holeW) / 2;
        ctx.fillStyle = "#1e160e";
        ctx.fillRect(holeX, holeX, holeW, holeW);

        ctx.lineWidth = 26;
        ctx.strokeStyle = "#cbb269";
        ctx.strokeRect(holeX, holeX, holeW, holeW);

        ctx.font = "Bold 140px 'STKaiti', 'KaiTi', 'SimSun', serif";
        ctx.fillStyle = "#fae5a0";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        if (isFront) {
            ctx.fillText("乾", 512, 210);
            ctx.fillText("隆", 512, 810);
            ctx.fillText("通", 800, 512);
            ctx.fillText("寶", 224, 512);
        } else {
            ctx.font = "Bold 125px serif";
            ctx.fillText("ᠪᠣᠣ", 224, 512);
            ctx.fillText("ᠴᡳᠣᠠᠨ", 800, 512);
        }

        const diffuseTex = new THREE.CanvasTexture(canvas);

        const normalCanvas = document.createElement("canvas");
        normalCanvas.width = 512;
        normalCanvas.height = 512;
        const nCtx = normalCanvas.getContext("2d");
        const imgData = ctx.getImageData(0, 0, size, size);
        const normData = nCtx.createImageData(512, 512);

        for (let y = 0; y < 512; y++) {
            for (let x = 0; x < 512; x++) {
                const sx = Math.floor(x * 2);
                const sy = Math.floor(y * 2);
                const left = (sy * size + Math.max(0, sx - 2)) * 4;
                const right = (sy * size + Math.min(size - 1, sx + 2)) * 4;
                const top = (Math.max(0, sy - 2) * size + sx) * 4;
                const down = (Math.min(size - 1, sy + 2) * size + sx) * 4;

                const dx = (imgData.data[right] - imgData.data[left]) / 255;
                const dy = (imgData.data[down] - imgData.data[top]) / 255;

                const nIdx = (y * 512 + x) * 4;
                normData.data[nIdx] = Math.floor((dx * 0.5 + 0.5) * 255);
                normData.data[nIdx + 1] = Math.floor((-dy * 0.5 + 0.5) * 255);
                normData.data[nIdx + 2] = 255;
                normData.data[nIdx + 3] = 255;
            }
        }
        nCtx.putImageData(normData, 0, 0);
        const normalTex = new THREE.CanvasTexture(normalCanvas);

        return new THREE.MeshStandardMaterial({
            map: diffuseTex,
            normalMap: normalTex,
            normalScale: new THREE.Vector2(2.2, 2.2),
            roughness: 0.3,
            metalness: 0.85,
            envMap: this.envMap
        });
    }

    buildSculptedPlinth() {
        this.plinthGroup.clear();

        const baseGeo = new THREE.CylinderGeometry(5.2, 5.6, 0.22, 48);
        const baseMesh = new THREE.Mesh(baseGeo, this.materials.daisBase);
        baseMesh.position.y = -0.11;
        baseMesh.receiveShadow = true;
        this.plinthGroup.add(baseMesh);

        const topGeo = new THREE.CylinderGeometry(4.6, 4.9, 0.18, 48);
        const topMesh = new THREE.Mesh(topGeo, this.materials.daisBase);
        topMesh.position.y = 0.08;
        topMesh.receiveShadow = true;
        this.plinthGroup.add(topMesh);

        const poolGeo = new THREE.CylinderGeometry(3.6, 3.6, 0.04, 48);
        const poolMesh = new THREE.Mesh(poolGeo, this.materials.daisGoldPool);
        poolMesh.position.y = 0.18;
        this.plinthGroup.add(poolMesh);

        const createTubularRing = (radius, tubeR, yPos) => {
            const geo = new THREE.TorusGeometry(radius, tubeR, 16, 64);
            const mesh = new THREE.Mesh(geo, this.materials.goldChased);
            mesh.rotation.x = Math.PI / 2;
            mesh.position.y = yPos;
            mesh.castShadow = true;
            return mesh;
        };

        this.ringOuter = createTubularRing(3.85, 0.035, 0.22);
        this.ringMid = createTubularRing(2.95, 0.025, 0.23);
        this.ringInner = createTubularRing(1.95, 0.02, 0.24);

        this.plinthGroup.add(this.ringOuter);
        this.plinthGroup.add(this.ringMid);
        this.plinthGroup.add(this.ringInner);

        const haloCanvas = document.createElement("canvas");
        haloCanvas.width = 512;
        haloCanvas.height = 512;
        const hCtx = haloCanvas.getContext("2d");
        const grad = hCtx.createRadialGradient(256, 256, 120, 256, 256, 256);
        grad.addColorStop(0, "rgba(224, 180, 90, 0.35)");
        grad.addColorStop(0.6, "rgba(140, 95, 30, 0.12)");
        grad.addColorStop(1, "rgba(10, 9, 8, 0)");
        hCtx.fillStyle = grad;
        hCtx.fillRect(0, 0, 512, 512);

        const haloTex = new THREE.CanvasTexture(haloCanvas);
        const haloGeo = new THREE.PlaneGeometry(16, 16);
        const haloMat = new THREE.MeshBasicMaterial({ map: haloTex, transparent: true, depthWrite: false });
        const haloMesh = new THREE.Mesh(haloGeo, haloMat);
        haloMesh.rotation.x = -Math.PI / 2;
        haloMesh.position.y = -0.21;
        this.plinthGroup.add(haloMesh);
    }

    buildAuthenticCoins() {
        this.coins = [];
        const coinGeo = new THREE.CylinderGeometry(0.55, 0.55, 0.09, 48);

        for (let i = 0; i < 3; i++) {
            const coinMaterials = [this.materials.coinEdge, this.materials.coinFace, this.materials.coinBack];
            const coinMesh = new THREE.Mesh(coinGeo, coinMaterials);
            coinMesh.castShadow = true;
            coinMesh.receiveShadow = true;

            coinMesh.position.set((i - 1) * 1.5, 0.24, 3.2);
            this.scene.add(coinMesh);
            this.coins.push(coinMesh);
        }
    }

    buildAtmosphereParticles() {
        const count = 300;
        const geo = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);

        for (let i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 16;
            positions[i * 3 + 1] = Math.random() * 8.5;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 16;
        }

        geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        const mat = new THREE.PointsMaterial({
            color: 0xdfb158,
            size: 0.055,
            transparent: true,
            opacity: 0.65,
            blending: THREE.AdditiveBlending
        });

        this.particleCloud = new THREE.Points(geo, mat);
        this.particleGroup.add(this.particleCloud);
    }

    tossCoinsAnimation(sumsValue) {
        if (!this.coins || this.coins.length < 3) return;
        const startTime = Date.now();
        const duration = 600;

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            this.coins.forEach((coin, idx) => {
                const arcY = Math.sin(progress * Math.PI) * 2.2;
                coin.position.y = 0.24 + arcY;
                coin.rotation.x += 0.42 + idx * 0.08;
                coin.rotation.z += 0.32 + idx * 0.06;
            });

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                this.coins.forEach((coin, idx) => {
                    coin.position.y = 0.24;
                    const isBack = (idx === 0 && sumsValue % 2 === 0);
                    coin.rotation.set(isBack ? Math.PI : 0, (idx - 1) * 0.32, 0);
                });
            }
        };
        animate();
    }

    createGoldJadeBeam(width, height, depth, isMoving) {
        const group = new THREE.Group();
        const woodMat = this.materials.ebonyWood;
        const jadeMat = isMoving ? this.materials.movingJade : this.materials.whiteJade;
        const goldMat = this.materials.goldChased;
        const t = 0.05;

        // 1. 温润羊脂白玉 / 朱砂血玉心
        const jadeW = width - 0.12;
        const jadeH = height - 0.08;
        const jadeD = depth - 0.08;
        const jadeGeo = new THREE.BoxGeometry(jadeW, jadeH, jadeD);
        const jadeMesh = new THREE.Mesh(jadeGeo, jadeMat);
        jadeMesh.castShadow = true;
        group.add(jadeMesh);

        // 2. 黑檀外包构架
        const topFrameGeo = new THREE.BoxGeometry(width, t, depth);
        const topFrame = new THREE.Mesh(topFrameGeo, woodMat);
        topFrame.position.y = (height - t) / 2;
        topFrame.castShadow = true;
        group.add(topFrame);

        const bottomFrameGeo = new THREE.BoxGeometry(width, t, depth);
        const bottomFrame = new THREE.Mesh(bottomFrameGeo, woodMat);
        bottomFrame.position.y = -(height - t) / 2;
        bottomFrame.castShadow = true;
        group.add(bottomFrame);

        const postGeo = new THREE.BoxGeometry(t, height, depth);
        const leftPost = new THREE.Mesh(postGeo, woodMat);
        leftPost.position.x = -(width - t) / 2;
        group.add(leftPost);

        const rightPost = new THREE.Mesh(postGeo, woodMat);
        rightPost.position.x = (width - t) / 2;
        group.add(rightPost);

        // 3. 铜抱角
        const cornerGeo = new THREE.BoxGeometry(0.08, height + 0.01, depth + 0.01);
        const leftGold = new THREE.Mesh(cornerGeo, goldMat);
        leftGold.position.x = -(width / 2 - 0.04);
        group.add(leftGold);

        const rightGold = new THREE.Mesh(cornerGeo, goldMat);
        rightGold.position.x = (width / 2 - 0.04);
        group.add(rightGold);

        // 4. 光芯
        const lightCoreGeo = new THREE.CylinderGeometry(0.012, 0.012, jadeW * 0.95, 16);
        const lightCoreMat = new THREE.MeshBasicMaterial({
            color: isMoving ? 0xff4d33 : 0xfffaed,
            transparent: true,
            opacity: 0.95
        });
        const lightCore = new THREE.Mesh(lightCoreGeo, lightCoreMat);
        lightCore.rotation.z = Math.PI / 2;
        group.add(lightCore);

        return group;
    }

    renderHexagram(lines, currentCount) {
        this.hexGroup.clear();
        this.trackedBeams = [];
        this.animatingBeams = [];
        this.clickableMeshes = [];
        if (this.labelsContainer) this.labelsContainer.innerHTML = "";
        if (!lines || lines.length === 0) return;

        const totalWidth = 5.0;
        const gap = 0.55;
        const beamHeight = 0.32;
        const beamDepth = 0.48;
        const baseY = 0.90;
        const floorHeight = 0.76;

        let hasMoving = false;

        for (let i = 0; i < 6; i++) {
            const line = lines[i];
            const isRendered = (line.position <= currentCount);
            if (!isRendered) continue;

            const yPos = baseY + i * floorHeight;
            const isMoving = line.is_moving;
            if (isMoving) hasMoving = true;

            const yaoNode = new THREE.Group();
            yaoNode.position.set(0, yPos, 0);

            if (line.wood_type === "solid_wood") {
                const solidBeam = this.createGoldJadeBeam(totalWidth, beamHeight, beamDepth, isMoving);
                yaoNode.add(solidBeam);

                if (isMoving) {
                    this.animatingBeams.push({
                        type: "yang_split",
                        node: solidBeam,
                        timeOffset: i * 0.5
                    });
                }
            } else {
                const partWidth = (totalWidth - gap) / 2;
                const leftBeam = this.createGoldJadeBeam(partWidth, beamHeight, beamDepth, isMoving);
                leftBeam.position.x = -(totalWidth / 4 + gap / 4);
                yaoNode.add(leftBeam);

                const rightBeam = this.createGoldJadeBeam(partWidth, beamHeight, beamDepth, isMoving);
                rightBeam.position.x = (totalWidth / 4 + gap / 4);
                yaoNode.add(rightBeam);

                const tenonGeo = new THREE.BoxGeometry(0.08, beamHeight * 0.6, beamDepth * 0.6);
                const tenonLeft = new THREE.Mesh(tenonGeo, this.materials.goldChased);
                tenonLeft.position.x = -(gap / 2 - 0.04);
                yaoNode.add(tenonLeft);

                const tenonRight = new THREE.Mesh(tenonGeo, this.materials.goldChased);
                tenonRight.position.x = (gap / 2 - 0.04);
                yaoNode.add(tenonRight);

                if (isMoving) {
                    this.animatingBeams.push({
                        type: "yin_merge",
                        leftNode: leftBeam,
                        rightNode: rightBeam,
                        baseLeftX: leftBeam.position.x,
                        baseRightX: rightBeam.position.x,
                        timeOffset: i * 0.5
                    });
                }
            }

            if (i > 0) {
                const colGeo = new THREE.CylinderGeometry(0.02, 0.02, floorHeight - beamHeight, 16);
                const colLeft = new THREE.Mesh(colGeo, this.materials.goldChased);
                colLeft.position.set(-totalWidth / 2 + 0.25, -(floorHeight / 2), 0);
                yaoNode.add(colLeft);

                const colRight = new THREE.Mesh(colGeo, this.materials.goldChased);
                colRight.position.set(totalWidth / 2 - 0.25, -(floorHeight / 2), 0);
                yaoNode.add(colRight);
            }

            this.hexGroup.add(yaoNode);

            // 递归打标签，支持点击射线拾取
            yaoNode.traverse((child) => {
                if (child.isMesh) {
                    child.userData = { lineData: line, yaoNode: yaoNode };
                    this.clickableMeshes.push(child);
                }
            });

            // 悬浮 HTML DOM 字牌
            if (this.labelsContainer) {
                const leftEl = document.createElement("div");
                leftEl.className = "yao-label-tag yao-label-left";
                leftEl.innerText = `${line.six_god} · ${line.six_relative}${line.branch}(${line.element})`;
                leftEl.addEventListener("click", () => {
                    if (typeof window.openYaoDetailDrawer === "function") window.openYaoDetailDrawer(line);
                });
                this.labelsContainer.appendChild(leftEl);

                let rightText = "";
                let rightClass = "yao-label-tag yao-label-right";
                if (line.is_shi) {
                    rightText = "【世】求测者";
                    rightClass += " yao-label-shi";
                } else if (line.is_ying) {
                    rightText = "【应】事体目标";
                    rightClass += " yao-label-ying";
                }
                if (line.change_relationship) {
                    rightText += ` ${line.change_relationship}`;
                }

                let rightEl = null;
                if (rightText.trim()) {
                    rightEl = document.createElement("div");
                    rightEl.className = rightClass;
                    rightEl.innerText = rightText;
                    rightEl.addEventListener("click", () => {
                        if (typeof window.openYaoDetailDrawer === "function") window.openYaoDetailDrawer(line);
                    });
                    this.labelsContainer.appendChild(rightEl);
                }

                this.trackedBeams.push({
                    yPos: yPos,
                    leftEl: leftEl,
                    rightEl: rightEl,
                    nodeGroup: yaoNode
                });
            }
        }

        if (this.zhushaLight) {
            this.zhushaLight.intensity = hasMoving ? 2.5 : 0;
        }

        this.updateLabelsPosition();
    }

    onCanvasClick(event) {
        if (!this.container || !this.camera || this.clickableMeshes.length === 0) return;

        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.clickableMeshes, false);

        if (intersects.length > 0) {
            const hit = intersects[0];
            if (hit.object && hit.object.userData && hit.object.userData.lineData) {
                const line = hit.object.userData.lineData;
                if (typeof window.openYaoDetailDrawer === "function") {
                    window.openYaoDetailDrawer(line);
                }
            }
        }
    }

    updateLabelsPosition() {
        if (!this.container || !this.camera || this.trackedBeams.length === 0) return;

        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        const widthHalf = width / 2;
        const heightHalf = height / 2;
        const tempVec = new THREE.Vector3();

        this.trackedBeams.forEach(item => {
            if (item.leftEl) {
                tempVec.set(-3.6, item.yPos, 0);
                tempVec.project(this.camera);
                const x = (tempVec.x * widthHalf) + widthHalf;
                const y = -(tempVec.y * heightHalf) + heightHalf;
                item.leftEl.style.left = `${x}px`;
                item.leftEl.style.top = `${y}px`;
                item.leftEl.style.display = tempVec.z < 1 ? "block" : "none";
            }

            if (item.rightEl) {
                tempVec.set(3.6, item.yPos, 0);
                tempVec.project(this.camera);
                const x = (tempVec.x * widthHalf) + widthHalf;
                const y = -(tempVec.y * heightHalf) + heightHalf;
                item.rightEl.style.left = `${x}px`;
                item.rightEl.style.top = `${y}px`;
                item.rightEl.style.display = tempVec.z < 1 ? "block" : "none";
            }
        });
    }

    onWindowResize() {
        if (!this.container || !this.renderer || !this.camera) return;
        const width = this.container.clientWidth;
        let height = this.container.clientHeight;
        if (width <= 0 || height <= 100) height = 640;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
        this.updateLabelsPosition();
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        if (this.controls) this.controls.update();

        if (this.ringOuter) this.ringOuter.rotation.z += 0.0006;
        if (this.ringMid) this.ringMid.rotation.z -= 0.0009;
        if (this.ringInner) this.ringInner.rotation.z += 0.0012;

        const time = Date.now() * 0.003;
        if (this.animatingBeams.length > 0) {
            this.animatingBeams.forEach(anim => {
                const wave = Math.sin(time + anim.timeOffset) * 0.06;
                if (anim.type === "yin_merge") {
                    anim.leftNode.position.x = anim.baseLeftX + wave;
                    anim.rightNode.position.x = anim.baseRightX - wave;
                } else if (anim.type === "yang_split") {
                    anim.node.scale.x = 1.0 + Math.abs(wave) * 0.03;
                }
            });
        }

        if (this.particleCloud) {
            this.particleCloud.rotation.y += 0.0004;
        }

        if (this.zhushaLight && this.zhushaLight.intensity > 0) {
            this.zhushaLight.intensity = 2.0 + Math.sin(Date.now() * 0.006) * 0.5;
        }

        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }

        this.updateLabelsPosition();
    }
}

window.LiuYaoScene3D = LiuYaoScene3D;
