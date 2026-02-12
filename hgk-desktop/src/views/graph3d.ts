import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { api } from '../api/client';
import type { GraphNode, GraphEdge, GraphFullResponse, LinkGraphNode, LinkGraphFullResponse } from '../api/client';
// @ts-ignore — d3-force-3d has no types
import { forceSimulation, forceLink, forceManyBody, forceCenter } from 'd3-force-3d';

// ─── Constants ───────────────────────────────────────────────

const SERIES_COLORS: Record<string, string> = {
    O: '#00d4ff', S: '#10b981', H: '#ef4444',
    P: '#a855f7', K: '#f59e0b', A: '#f97316',
};

const NATURALITY_COLORS: Record<string, string> = {
    experiential: '#00d4ff', reflective: '#ffd700', structural: '#8888aa',
};

const BG_COLOR = 0x050508;

// ─── Source type colors (dimmed series colors) ───────────────

const SOURCE_TYPE_COLORS: Record<string, string> = {
    kernel: '#005570', ki: '#006688', doxa: '#772222',
    workflow: '#086640', research: '#7a5000', xseries: '#7a3a00',
    handoff: '#6a4d00', session: '#5a4000', review: '#5a2a00',
    knowledge: '#553388',
};

// ─── LOD thresholds ──────────────────────────────────────────

const LOD_FAR = 120;       // > 120: theorem only
const LOD_MEDIUM = 60;     // 60-120: theorem + bridge nodes
const LOD_CLOSE = 30;      // < 30: all knowledge nodes + labels

// ─── Series-specific Geometry ────────────────────────────────

function createNodeGeometry(series: string, isPure: boolean): THREE.BufferGeometry {
    const s = isPure ? 1.0 : 0.72;
    switch (series) {
        case 'O': return new THREE.OctahedronGeometry(2.5 * s, 0);
        case 'S': return new THREE.BoxGeometry(3.2 * s, 3.2 * s, 3.2 * s);
        case 'H': return new THREE.TetrahedronGeometry(3 * s, 0);
        case 'P': return new THREE.DodecahedronGeometry(2.5 * s, 0);
        case 'K': return new THREE.IcosahedronGeometry(2.5 * s, 0);
        case 'A': return new THREE.OctahedronGeometry(2.5 * s, 1);
        default: return new THREE.SphereGeometry(2.5 * s, 16, 16);
    }
}



// ─── Types ───────────────────────────────────────────────────

interface SimNode extends GraphNode {
    x: number; y: number; z: number;
    vx?: number; vy?: number; vz?: number;
    index?: number;
}
interface SimLink { source: SimNode | string; target: SimNode | string; edge: GraphEdge; }

// Knowledge node with computed 3D position
interface KnowledgeNode3D extends LinkGraphNode {
    x: number; y: number; z: number;
    isBridge: boolean;
}

// ─── Cleanup ─────────────────────────────────────────────────

let cleanup: (() => void) | null = null;

// ─── Main Export ─────────────────────────────────────────────

export async function renderGraph3D(): Promise<void> {
    if (cleanup) { cleanup(); cleanup = null; }

    const container = document.getElementById('view-content')!;
    container.innerHTML = `
    <div id="graph-container">
      <div id="graph-tooltip" class="node-tooltip hidden"></div>
      <div id="graph-info-panel" class="graph-info-panel hidden"></div>
      <div id="graph-layer-toggle" class="graph-layer-toggle">
        <button id="toggle-knowledge" class="btn btn-sm btn-layer" title="Toggle knowledge nodes">🧠 Knowledge</button>
      </div>
    </div>
  `;
    const graphContainer = document.getElementById('graph-container')!;

    // ─── Fetch theorem data ──────────────────────────────────

    let data: GraphFullResponse;
    try { data = await api.graphFull(); }
    catch (err) {
        container.innerHTML = `<div class="card status-error">Graph data unavailable: ${(err as Error).message}</div>`;
        return;
    }

    const edges = data.edges.filter(e => e.type !== 'identity');
    const nodes = data.nodes;

    // ─── Fetch knowledge data (non-blocking) ─────────────────

    let linkGraphData: LinkGraphFullResponse | null = null;
    let knowledgeVisible = false;
    const linkGraphPromise = api.linkGraphFull().catch(err => {
        console.warn('[LinkGraph] unavailable:', err);
        return null;
    });

    // ─── Three.js ─────────────────────────────────────────────

    const width = graphContainer.clientWidth;
    const height = graphContainer.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(BG_COLOR);

    const camera = new THREE.PerspectiveCamera(55, width / height, 1, 1500);
    camera.position.set(55, 40, 75);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    graphContainer.appendChild(renderer.domElement);

    // Bloom
    const composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));
    composer.addPass(new UnrealBloomPass(new THREE.Vector2(width, height), 0.5, 0.3, 0.5));

    // Labels
    const labelRenderer = new CSS2DRenderer();
    labelRenderer.setSize(width, height);
    labelRenderer.domElement.style.position = 'absolute';
    labelRenderer.domElement.style.top = '0';
    labelRenderer.domElement.style.left = '0';
    labelRenderer.domElement.style.pointerEvents = 'none';
    graphContainer.appendChild(labelRenderer.domElement);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.rotateSpeed = 0.5;
    controls.zoomSpeed = 0.8;
    controls.minDistance = 20;
    controls.maxDistance = 250;

    let autoOrbit = true;
    let lastInteraction = 0;
    controls.addEventListener('start', () => { autoOrbit = false; lastInteraction = performance.now(); });
    controls.addEventListener('end', () => { lastInteraction = performance.now(); });

    // Lights
    scene.add(new THREE.AmbientLight(0x303050, 0.5));
    const dl = new THREE.DirectionalLight(0xaaccff, 0.8); dl.position.set(40, 60, 50); scene.add(dl);
    const fl = new THREE.PointLight(0x8866cc, 0.5, 300); fl.position.set(-50, -30, 60); scene.add(fl);

    // Particles
    const pCount = 400;
    const pGeo = new THREE.BufferGeometry();
    const pPos = new Float32Array(pCount * 3);
    for (let i = 0; i < pCount * 3; i++) pPos[i] = (Math.random() - 0.5) * 400;
    pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
    const pMat = new THREE.PointsMaterial({ color: 0x334466, size: 0.4, transparent: true, opacity: 0.2 });
    const particles = new THREE.Points(pGeo, pMat);
    scene.add(particles);

    // ─── Force Simulation ─────────────────────────────────────

    const simNodes: SimNode[] = nodes.map(n => ({
        ...n,
        x: (Math.random() - 0.5) * 20,
        y: (Math.random() - 0.5) * 20,
        z: (Math.random() - 0.5) * 20,
    }));

    const nodeById = new Map<string, SimNode>();
    simNodes.forEach(n => nodeById.set(n.id, n));

    const simLinks: SimLink[] = edges
        .filter(e => nodeById.has(e.source) && nodeById.has(e.target))
        .map(e => ({ source: e.source, target: e.target, edge: e }));

    const simulation = forceSimulation(simNodes, 3)
        .force('link', forceLink(simLinks).id((d: SimNode) => d.id).distance(18).strength(0.5))
        .force('charge', forceManyBody().strength(-40).distanceMax(120))
        .force('center', forceCenter(0, 0, 0).strength(0.05))
        .alpha(1.0)
        .alphaDecay(0.008)
        .velocityDecay(0.3);

    // Pre-stabilize: run 300 ticks before rendering
    for (let i = 0; i < 300; i++) simulation.tick();

    // ─── Node Groups ──────────────────────────────────────────

    const nodeMeshes = new Map<string, THREE.Group>();
    // Cache raycast targets (build once, not every frame)
    const raycastTargets: THREE.Mesh[] = [];

    simNodes.forEach(node => {
        const color = new THREE.Color(SERIES_COLORS[node.series] || '#ffffff');
        const isPure = node.type === 'Pure';

        const group = new THREE.Group();
        group.position.set(node.x, node.y, node.z);
        group.userData = { nodeId: node.id };

        // Core
        const coreGeo = createNodeGeometry(node.series, isPure);
        const coreMat = new THREE.MeshPhongMaterial({
            color: color.clone().multiplyScalar(0.6),
            emissive: color,
            emissiveIntensity: 0.5,
            shininess: 100,
            transparent: true,
            opacity: 0.9,
        });
        const core = new THREE.Mesh(coreGeo, coreMat);
        group.add(core);
        raycastTargets.push(core);

        // Wireframe
        const wireGeo = createNodeGeometry(node.series, isPure);
        const wireMat = new THREE.MeshBasicMaterial({ color, wireframe: true, transparent: true, opacity: 0.2 });
        const wire = new THREE.Mesh(wireGeo, wireMat);
        wire.scale.setScalar(1.15);
        group.add(wire);

        // Ring for Pure nodes
        if (isPure) {
            const ringGeo = new THREE.TorusGeometry(3.8, 0.06, 8, 32);
            const ringMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.3 });
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.x = Math.PI / 2;
            group.add(ring);
        }

        scene.add(group);
        nodeMeshes.set(node.id, group);

        // Label
        const labelDiv = document.createElement('div');
        labelDiv.className = 'graph-label';
        labelDiv.textContent = node.id;
        labelDiv.style.color = SERIES_COLORS[node.series] || '#fff';
        const label = new CSS2DObject(labelDiv);
        label.position.set(0, isPure ? 4.5 : 3.5, 0);
        group.add(label);
    });

    // ─── Edges ────────────────────────────────────────────────

    const edgeLines: THREE.Line[] = [];
    simLinks.forEach(link => {
        const src = (typeof link.source === 'string' ? nodeById.get(link.source) : link.source)!;
        const tgt = (typeof link.target === 'string' ? nodeById.get(link.target) : link.target)!;
        if (!src || !tgt) return;
        const c = NATURALITY_COLORS[link.edge.naturality] || '#333';
        const geo = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(src.x, src.y, src.z),
            new THREE.Vector3(tgt.x, tgt.y, tgt.z)]);
        const mat = new THREE.LineBasicMaterial({ color: new THREE.Color(c), transparent: true, opacity: 0.12 });
        const line = new THREE.Line(geo, mat);
        line.userData = { edge: link.edge };
        scene.add(line);
        edgeLines.push(line);
    });

    // ═══════════════════════════════════════════════════════════
    // ─── LinkGraph Satellite Layer ────────────────────────────
    // ═══════════════════════════════════════════════════════════

    const knowledgeGroup = new THREE.Group();
    knowledgeGroup.visible = false;
    scene.add(knowledgeGroup);

    const kNodes3D: KnowledgeNode3D[] = [];
    const kEdgeLines: THREE.Line[] = [];
    let knowledgeInitialized = false;
    let bridgeNodeIds: Set<string> = new Set();

    // Initialize knowledge satellites after sim stabilizes and data arrives
    async function initKnowledgeSatellites(): Promise<void> {
        if (knowledgeInitialized) return;
        linkGraphData = await linkGraphPromise;
        if (!linkGraphData || linkGraphData.nodes.length === 0) return;
        knowledgeInitialized = true;

        // Get bridge nodes from stats
        try {
            const stats = await api.linkGraphStats();
            bridgeNodeIds = new Set(stats.bridge_nodes);
        } catch { /* ignore */ }

        // Build 3D positions for knowledge nodes
        for (const kn of linkGraphData.nodes) {
            const theorem = nodeById.get(kn.projected_theorem);
            if (!theorem) continue;

            // Satellite position = theorem position + orbit
            const x = theorem.x + kn.orbit_radius * Math.cos(kn.orbit_angle);
            const y = theorem.y + kn.orbit_radius * Math.sin(kn.orbit_angle) * 0.5;
            const z = theorem.z + kn.orbit_radius * Math.sin(kn.orbit_angle);

            kNodes3D.push({
                ...kn,
                x, y, z,
                isBridge: bridgeNodeIds.has(kn.id),
            });
        }

        // InstancedMesh per source_type for performance
        const groups = new Map<string, KnowledgeNode3D[]>();
        for (const kn of kNodes3D) {
            const g = groups.get(kn.source_type) || [];
            g.push(kn);
            groups.set(kn.source_type, g);
        }

        const sphereGeo = new THREE.SphereGeometry(0.35, 6, 6);

        for (const [srcType, knodes] of groups) {
            const color = new THREE.Color(SOURCE_TYPE_COLORS[srcType] || '#333355');
            const mat = new THREE.MeshPhongMaterial({
                color: color.clone().multiplyScalar(0.5),
                emissive: color,
                emissiveIntensity: 0.4,
                transparent: true,
                opacity: 0.5,
            });

            const mesh = new THREE.InstancedMesh(sphereGeo, mat, knodes.length);
            const dummy = new THREE.Object3D();

            knodes.forEach((kn, i) => {
                dummy.position.set(kn.x, kn.y, kn.z);
                // Bridge nodes are slightly larger
                const scale = kn.isBridge ? 1.8 : 1.0;
                dummy.scale.setScalar(scale);
                dummy.updateMatrix();
                mesh.setMatrixAt(i, dummy.matrix);

                // Per-instance color for bridges
                if (kn.isBridge) {
                    mesh.setColorAt(i, new THREE.Color('#ffffff'));
                }
            });

            mesh.instanceMatrix.needsUpdate = true;
            if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
            mesh.userData = { sourceType: srcType, knodes };
            knowledgeGroup.add(mesh);
        }

        // Knowledge edges — thin semi-transparent curves
        const kNodeMap = new Map<string, KnowledgeNode3D>();
        kNodes3D.forEach(kn => kNodeMap.set(kn.id, kn));

        for (const edge of linkGraphData.edges) {
            const src = kNodeMap.get(edge.source);
            const tgt = kNodeMap.get(edge.target);
            if (!src || !tgt) continue;

            // Quadratic bezier — midpoint lifted for curve
            const mid = new THREE.Vector3(
                (src.x + tgt.x) / 2 + (Math.random() - 0.5) * 3,
                (src.y + tgt.y) / 2 + 2,
                (src.z + tgt.z) / 2 + (Math.random() - 0.5) * 3,
            );
            const curve = new THREE.QuadraticBezierCurve3(
                new THREE.Vector3(src.x, src.y, src.z),
                mid,
                new THREE.Vector3(tgt.x, tgt.y, tgt.z),
            );
            const points = curve.getPoints(12);
            const geo = new THREE.BufferGeometry().setFromPoints(points);
            const mat = new THREE.LineBasicMaterial({
                color: 0x334466,
                transparent: true,
                opacity: 0.04,
            });
            const line = new THREE.Line(geo, mat);
            knowledgeGroup.add(line);
            kEdgeLines.push(line);
        }

        sphereGeo.dispose(); // InstancedMesh keeps its own copy

        // Enable toggle button
        const btn = document.getElementById('toggle-knowledge');
        if (btn) {
            btn.classList.add('btn-layer-ready');
            btn.textContent = `🧠 Knowledge (${kNodes3D.length})`;
        }
    }

    // Layer toggle
    const toggleBtn = document.getElementById('toggle-knowledge');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', async () => {
            if (!knowledgeInitialized) await initKnowledgeSatellites();
            knowledgeVisible = !knowledgeVisible;
            knowledgeGroup.visible = knowledgeVisible;
            toggleBtn.classList.toggle('btn-layer-active', knowledgeVisible);
        });
    }

    // ─── Raycaster (cached targets) ───────────────────────────

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let hoveredGroup: THREE.Group | null = null;
    let selectedNodeId: string | null = null;
    const tooltip = document.getElementById('graph-tooltip')!;
    const infoPanel = document.getElementById('graph-info-panel')!;

    function findParentGroup(obj: THREE.Object3D): THREE.Group | null {
        let c: THREE.Object3D | null = obj;
        while (c) { if (c instanceof THREE.Group && c.userData.nodeId) return c; c = c.parent; }
        return null;
    }

    // Throttle mousemove to max 30fps
    let lastMoveTime = 0;
    function onMouseMove(event: MouseEvent): void {
        const now = performance.now();
        if (now - lastMoveTime < 33) return; // ~30fps throttle
        lastMoveTime = now;

        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(raycastTargets, false);

        if (hoveredGroup) { hoveredGroup.scale.setScalar(1); hoveredGroup = null; }

        if (intersects.length > 0 && intersects[0]) {
            const group = findParentGroup(intersects[0].object);
            if (group) {
                const nodeId = group.userData.nodeId as string;
                const node = nodeById.get(nodeId);
                if (node) {
                    hoveredGroup = group;
                    group.scale.setScalar(1.3);
                    tooltip.innerHTML = `
            <div class="tooltip-header" style="color:${SERIES_COLORS[node.series]}">${node.id} — ${node.name}</div>
            <div class="tooltip-greek">${node.greek}</div>
            <div class="tooltip-meaning">${node.meaning}</div>
            <div class="tooltip-wf">${node.workflow}</div>`;
                    tooltip.classList.remove('hidden');
                    tooltip.style.left = `${event.clientX - rect.left + 15}px`;
                    tooltip.style.top = `${event.clientY - rect.top + 15}px`;
                }
            }
        } else {
            tooltip.classList.add('hidden');
        }
    }

    function onClick(event: MouseEvent): void {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(raycastTargets, false);
        if (intersects.length > 0 && intersects[0]) {
            const group = findParentGroup(intersects[0].object);
            if (group) { selectedNodeId = group.userData.nodeId as string; showNodeDetails(selectedNodeId); }
        } else { selectedNodeId = null; infoPanel.classList.add('hidden'); }
    }

    function showNodeDetails(nodeId: string): void {
        const node = nodeById.get(nodeId);
        if (!node) return;
        const conn = edges.filter(e => e.source === nodeId || e.target === nodeId);
        const list = conn.map(e => {
            const c = NATURALITY_COLORS[e.naturality] || '#888';
            return `<li><span style="color:${c}">●</span> <strong>${e.source}</strong> → <strong>${e.target}</strong>
        <span class="edge-meta">${e.naturality} · ${e.shared_coordinate}</span>
        <div class="edge-meaning">${e.meaning}</div></li>`;
        }).join('');

        // Count satellite knowledge nodes
        const satellites = kNodes3D.filter(kn => kn.projected_theorem === nodeId);
        const satInfo = satellites.length > 0
            ? `<h4>Satellites <span class="conn-count">${satellites.length}</span></h4>
               <ul class="satellite-list">${satellites.slice(0, 8).map(s =>
                `<li class="sat-item${s.isBridge ? ' sat-bridge' : ''}">
                    <span class="sat-type">${s.source_type}</span> ${s.title.slice(0, 50)}
                </li>`).join('')}${satellites.length > 8 ? `<li>... +${satellites.length - 8} more</li>` : ''}</ul>`
            : '';

        infoPanel.innerHTML = `
      <h3 style="color:${SERIES_COLORS[node.series]}">${node.id} — ${node.name}</h3>
      <p class="info-greek">${node.greek}</p>
      <p class="info-meaning">${node.meaning}</p>
      <p class="info-meta">${node.workflow} · ${node.type}</p>
      <h4>Connections <span class="conn-count">${conn.length}</span></h4>
      <ul>${list || '<li>None</li>'}</ul>
      ${satInfo}
      <button id="close-info" class="btn btn-sm">Close</button>`;
        infoPanel.classList.remove('hidden');
        document.getElementById('close-info')?.addEventListener('click', () => {
            infoPanel.classList.add('hidden'); selectedNodeId = null;
        });
    }

    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('click', onClick);

    // ─── Auto-init knowledge after sim stabilizes ─────────────
    // /dia+ 修正提案 #3: alpha < 0.001 後にのみ知識ノード配置開始

    let simStabilized = false;

    // ─── Animation ────────────────────────────────────────────

    let animationId: number;
    let frame = 0;
    let orbitAngle = Math.atan2(camera.position.z, camera.position.x);
    let lastSelectedNodeId: string | null = null; // Track selection changes

    function animate(): void {
        animationId = requestAnimationFrame(animate);
        frame++;
        const now = performance.now();

        if (!autoOrbit && now - lastInteraction > 3000) autoOrbit = true;
        if (autoOrbit) {
            orbitAngle += 0.0006;
            const r = Math.sqrt(camera.position.x ** 2 + camera.position.z ** 2);
            camera.position.x = Math.cos(orbitAngle) * r;
            camera.position.z = Math.sin(orbitAngle) * r;
            camera.lookAt(0, 0, 0);
        }

        const isSimulating = simulation.alpha() > 0.001;
        if (isSimulating) {
            simulation.tick();
        } else if (!simStabilized) {
            simStabilized = true;
            // Trigger knowledge satellite initialization
            initKnowledgeSatellites().catch(console.warn);
        }

        simNodes.forEach(node => {
            const group = nodeMeshes.get(node.id);
            if (!group) return;

            // ⚡ Bolt Optimization: Only update position if simulation is active
            if (isSimulating) {
                group.position.set(node.x, node.y, node.z);
            }

            const core = group.children[0] as THREE.Mesh;
            const wire = group.children[1] as THREE.Mesh;
            if (group !== hoveredGroup) {
                core.rotation.y += 0.004;
                core.rotation.x += 0.002;
                wire.rotation.y -= 0.003;
                const coreMat = core.material as THREE.MeshPhongMaterial;
                coreMat.emissiveIntensity = 0.5 + Math.sin(frame * 0.02 + (node.index || 0) * 0.6) * 0.1;
                if (group.children.length > 2) {
                    const ring = group.children[2] as THREE.Mesh;
                    ring.rotation.z += 0.006;
                }
            }
        });

        // ⚡ Bolt Optimization: Only update geometry/material if needed
        const selectionChanged = selectedNodeId !== lastSelectedNodeId;
        if (isSimulating || selectionChanged) {
            edgeLines.forEach((line, i) => {
                const link = simLinks[i];
                if (!link) return;

                if (isSimulating) {
                    const s = link.source as SimNode, t = link.target as SimNode;
                    const pos = line.geometry.attributes.position as THREE.BufferAttribute;
                    pos.setXYZ(0, s.x, s.y, s.z);
                    pos.setXYZ(1, t.x, t.y, t.z);
                    pos.needsUpdate = true;
                }

                // Only update opacity if selection changed or simulation is running (initial settlement)
                // (Checking isSimulating here ensures initial opacities are correct if selection happens during sim)
                const mat = line.material as THREE.LineBasicMaterial;
                const e = line.userData.edge as GraphEdge;
                mat.opacity = selectedNodeId
                    ? (e.source === selectedNodeId || e.target === selectedNodeId ? 0.5 : 0.02)
                    : 0.12;
            });
            lastSelectedNodeId = selectedNodeId;
        }

        // LOD for knowledge layer
        if (knowledgeVisible && knowledgeInitialized) {
            const camDist = camera.position.length();
            knowledgeGroup.children.forEach(child => {
                if (child instanceof THREE.InstancedMesh) {
                    const knodes = child.userData.knodes as KnowledgeNode3D[] | undefined;
                    if (!knodes) return;
                    // Bridge nodes always visible when layer is on
                    // Other nodes only when camera is close enough
                    if (camDist > LOD_FAR) {
                        child.visible = false;
                    } else if (camDist > LOD_MEDIUM) {
                        // Only show bridge nodes
                        child.visible = knodes.some(kn => kn.isBridge);
                    } else {
                        child.visible = true;
                    }

                    // Pulsate bridge nodes
                    if (child.visible) {
                        const mat = child.material as THREE.MeshPhongMaterial;
                        mat.emissiveIntensity = 0.4 + Math.sin(frame * 0.03) * 0.15;
                    }
                } else if (child instanceof THREE.Line) {
                    // Knowledge edges only visible when close
                    child.visible = camera.position.length() < LOD_CLOSE;
                }
            });
        }

        particles.rotation.y += 0.0001;
        controls.update();
        composer.render();
        labelRenderer.render(scene, camera);
    }

    animate();

    // ─── Resize ───────────────────────────────────────────────

    function onResize(): void {
        const w = graphContainer.clientWidth, h = graphContainer.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
        composer.setSize(w, h);
        labelRenderer.setSize(w, h);
    }
    window.addEventListener('resize', onResize);

    // ─── Cleanup ──────────────────────────────────────────────

    cleanup = () => {
        cancelAnimationFrame(animationId);
        simulation.stop();
        window.removeEventListener('resize', onResize);
        renderer.domElement.removeEventListener('mousemove', onMouseMove);
        renderer.domElement.removeEventListener('click', onClick);
        scene.traverse(obj => {
            if (obj instanceof THREE.Mesh || obj instanceof THREE.Line || obj instanceof THREE.InstancedMesh) {
                obj.geometry.dispose();
                const m = obj.material;
                if (Array.isArray(m)) m.forEach(x => x.dispose()); else (m as THREE.Material).dispose();
            }
        });
        pGeo.dispose(); pMat.dispose(); composer.dispose(); renderer.dispose(); controls.dispose();
    };
}
