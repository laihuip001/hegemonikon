import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js';
import { api } from '../api/client';
import type { GraphNode, GraphEdge, GraphFullResponse } from '../api/client';
// @ts-ignore — d3-force-3d has no types
import { forceSimulation, forceLink, forceManyBody, forceCenter } from 'd3-force-3d';

// ─── Constants ───────────────────────────────────────────────

const SERIES_COLORS: Record<string, string> = {
    O: '#00d4ff',
    S: '#10b981',
    H: '#ef4444',
    P: '#a855f7',
    K: '#f59e0b',
    A: '#f97316',
};

const NATURALITY_COLORS: Record<string, string> = {
    experiential: '#00d4ff',
    reflective: '#ffd700',
    structural: '#c0c0c0',
};

const BG_COLOR = 0x0a0a0f;
const PURE_RADIUS = 8;
const MIXED_RADIUS = 5;

// ─── Cleanup Management ─────────────────────────────────────

let cleanup: (() => void) | null = null;

// ─── Main Export ─────────────────────────────────────────────

export async function renderGraph3D(): Promise<void> {
    if (cleanup) {
        cleanup();
        cleanup = null;
    }

    const container = document.getElementById('view-content')!;
    container.innerHTML = `
    <div id="graph-container">
      <div id="graph-tooltip" class="node-tooltip hidden"></div>
      <div id="graph-info-panel" class="graph-info-panel hidden"></div>
    </div>
  `;

    const graphContainer = document.getElementById('graph-container')!;

    // Fetch data
    let data: GraphFullResponse;
    try {
        data = await api.graphFull();
    } catch (err) {
        container.innerHTML = `<div class="card status-error">Graph data unavailable: ${(err as Error).message}</div>`;
        return;
    }

    // Filter out identity edges
    const edges = data.edges.filter(e => e.type !== 'identity');
    const nodes = data.nodes;

    // ─── Three.js Setup ──────────────────────────────────────

    const width = graphContainer.clientWidth;
    const height = graphContainer.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(BG_COLOR);

    const camera = new THREE.PerspectiveCamera(60, width / height, 1, 2000);
    camera.position.set(80, 60, 120);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    graphContainer.appendChild(renderer.domElement);

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
    controls.dampingFactor = 0.05;
    controls.rotateSpeed = 0.8;
    controls.zoomSpeed = 1.2;
    controls.minDistance = 30;
    controls.maxDistance = 500;

    // Lights
    const ambientLight = new THREE.AmbientLight(0x404060, 0.6);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x58a6ff, 1.5, 400);
    pointLight.position.set(50, 80, 60);
    scene.add(pointLight);

    const pointLight2 = new THREE.PointLight(0xa855f7, 0.8, 300);
    pointLight2.position.set(-60, -40, 80);
    scene.add(pointLight2);

    // ─── Particle Field (background) ─────────────────────────

    const particleCount = 500;
    const particleGeom = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i++) {
        particlePositions[i] = (Math.random() - 0.5) * 600;
    }
    particleGeom.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    const particleMat = new THREE.PointsMaterial({
        color: 0x58a6ff,
        size: 0.8,
        transparent: true,
        opacity: 0.3,
    });
    const particles = new THREE.Points(particleGeom, particleMat);
    scene.add(particles);

    // ─── Force Simulation ────────────────────────────────────

    interface SimNode extends GraphNode {
        x: number; y: number; z: number;
        vx?: number; vy?: number; vz?: number;
        fx?: number | null; fy?: number | null; fz?: number | null;
        index?: number;
    }

    interface SimLink {
        source: SimNode | string;
        target: SimNode | string;
        edge: GraphEdge;
    }

    const simNodes: SimNode[] = nodes.map(n => ({
        ...n,
        x: n.position.x * 2,
        y: n.position.y * 2,
        z: n.position.z * 2,
    }));

    const nodeById = new Map<string, SimNode>();
    simNodes.forEach(n => nodeById.set(n.id, n));

    const simLinks: SimLink[] = edges
        .filter(e => nodeById.has(e.source) && nodeById.has(e.target))
        .map(e => ({
            source: e.source,
            target: e.target,
            edge: e,
        }));

    const simulation = forceSimulation(simNodes, 3)
        .force('link', forceLink(simLinks)
            .id((d: SimNode) => d.id)
            .distance(40)
            .strength(0.3))
        .force('charge', forceManyBody().strength(-80))
        .force('center', forceCenter(0, 0, 0))
        .alpha(0.8)
        .alphaDecay(0.02);

    // ─── Node Meshes ─────────────────────────────────────────

    const nodeMeshes = new Map<string, THREE.Mesh>();
    const nodeLabels = new Map<string, CSS2DObject>();

    simNodes.forEach(node => {
        const radius = node.type === 'Pure' ? PURE_RADIUS : MIXED_RADIUS;
        const color = new THREE.Color(SERIES_COLORS[node.series] || '#ffffff');

        const geometry = new THREE.SphereGeometry(radius, 32, 32);
        const material = new THREE.MeshPhongMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: 0.4,
            shininess: 80,
            transparent: true,
            opacity: 0.9,
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(node.x, node.y, node.z);
        mesh.userData = { nodeId: node.id };
        scene.add(mesh);
        nodeMeshes.set(node.id, mesh);

        // Label
        const labelDiv = document.createElement('div');
        labelDiv.className = 'graph-label';
        labelDiv.textContent = node.id;
        labelDiv.style.color = SERIES_COLORS[node.series] || '#ffffff';
        const label = new CSS2DObject(labelDiv);
        label.position.set(0, radius + 3, 0);
        mesh.add(label);
        nodeLabels.set(node.id, label);
    });

    // ─── Edge Lines ──────────────────────────────────────────

    const edgeLines: THREE.Line[] = [];

    simLinks.forEach(link => {
        const src = typeof link.source === 'string' ? nodeById.get(link.source)! : link.source;
        const tgt = typeof link.target === 'string' ? nodeById.get(link.target)! : link.target;
        if (!src || !tgt) return;

        const edgeColor = NATURALITY_COLORS[link.edge.naturality] || '#444444';
        const points = [
            new THREE.Vector3(src.x, src.y, src.z),
            new THREE.Vector3(tgt.x, tgt.y, tgt.z),
        ];

        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: new THREE.Color(edgeColor),
            transparent: true,
            opacity: 0.25,
        });

        const line = new THREE.Line(geometry, material);
        line.userData = { edge: link.edge };
        scene.add(line);
        edgeLines.push(line);
    });

    // ─── Raycaster (Hover + Click) ───────────────────────────

    const raycaster = new THREE.Raycaster();
    raycaster.params.Points = { threshold: 5 };
    const mouse = new THREE.Vector2();
    let hoveredMesh: THREE.Mesh | null = null;
    let selectedNodeId: string | null = null;

    const tooltip = document.getElementById('graph-tooltip')!;
    const infoPanel = document.getElementById('graph-info-panel')!;

    function onMouseMove(event: MouseEvent): void {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const meshArray = Array.from(nodeMeshes.values());
        const intersects = raycaster.intersectObjects(meshArray);

        if (hoveredMesh) {
            const mat = hoveredMesh.material as THREE.MeshPhongMaterial;
            mat.emissiveIntensity = 0.4;
            hoveredMesh.scale.setScalar(1);
        }

        if (intersects.length > 0) {
            const hit = intersects[0];
            if (!hit) return;
            const mesh = hit.object as THREE.Mesh;
            const nodeId = mesh.userData.nodeId as string;
            const node = nodeById.get(nodeId);
            if (node) {
                hoveredMesh = mesh;
                const mat = mesh.material as THREE.MeshPhongMaterial;
                mat.emissiveIntensity = 0.8;
                mesh.scale.setScalar(1.3);

                tooltip.innerHTML = `
          <strong>${node.id} — ${node.name}</strong><br/>
          <span style="color:${SERIES_COLORS[node.series]}">${node.greek}</span><br/>
          ${node.meaning}<br/>
          <small style="color:#8b949e">${node.workflow}</small>
        `;
                tooltip.classList.remove('hidden');
                tooltip.style.left = `${event.clientX - rect.left + 15}px`;
                tooltip.style.top = `${event.clientY - rect.top + 15}px`;
            }
        } else {
            hoveredMesh = null;
            tooltip.classList.add('hidden');
        }
    }

    function onClick(event: MouseEvent): void {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const meshArray = Array.from(nodeMeshes.values());
        const intersects = raycaster.intersectObjects(meshArray);

        if (intersects.length > 0) {
            const hit = intersects[0];
            if (!hit) return;
            const nodeId = hit.object.userData.nodeId as string;
            selectedNodeId = nodeId;
            showNodeDetails(nodeId);
        } else {
            selectedNodeId = null;
            infoPanel.classList.add('hidden');
        }
    }

    function showNodeDetails(nodeId: string): void {
        const node = nodeById.get(nodeId);
        if (!node) return;

        const connectedEdges = edges.filter(e => e.source === nodeId || e.target === nodeId);
        const edgeList = connectedEdges.map(e => {
            const otherId = e.source === nodeId ? e.target : e.source;
            const other = nodeById.get(otherId);
            const color = NATURALITY_COLORS[e.naturality] || '#888';
            return `<li>
        <span style="color:${color}">●</span>
        ${e.source} → ${e.target}
        <small style="color:#8b949e">(${e.naturality}, ${e.shared_coordinate})</small>
        ${other ? `<br/><small>${e.meaning}</small>` : ''}
      </li>`;
        }).join('');

        infoPanel.innerHTML = `
      <h3 style="color:${SERIES_COLORS[node.series]}">${node.id} — ${node.name}</h3>
      <p>${node.greek} — ${node.meaning}</p>
      <p><small>Workflow: ${node.workflow} | Type: ${node.type}</small></p>
      <h4>Connections (${connectedEdges.length})</h4>
      <ul>${edgeList || '<li>No connections</li>'}</ul>
      <button id="close-info" class="btn btn-sm" style="margin-top:0.5rem">Close</button>
    `;
        infoPanel.classList.remove('hidden');

        document.getElementById('close-info')?.addEventListener('click', () => {
            infoPanel.classList.add('hidden');
            selectedNodeId = null;
        });
    }

    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('click', onClick);

    // ─── Animation Loop ──────────────────────────────────────

    let animationId: number;
    let frame = 0;

    function animate(): void {
        animationId = requestAnimationFrame(animate);
        frame++;

        // Update simulation positions
        simulation.tick();

        simNodes.forEach(node => {
            const mesh = nodeMeshes.get(node.id);
            if (mesh) {
                mesh.position.set(node.x, node.y, node.z);

                // Pulse animation (emissive intensity oscillation)
                if (node.id !== selectedNodeId) {
                    const mat = mesh.material as THREE.MeshPhongMaterial;
                    const base = mesh === hoveredMesh ? 0.8 : 0.4;
                    mat.emissiveIntensity = base + Math.sin(frame * 0.03 + node.index! * 0.5) * 0.1;
                }
            }
        });

        // Update edge positions
        simLinks.forEach((link, i) => {
            const src = link.source as SimNode;
            const tgt = link.target as SimNode;
            const line = edgeLines[i];
            if (!line || !src || !tgt) return;

            const positions = line.geometry.attributes.position as THREE.BufferAttribute;
            positions.setXYZ(0, src.x, src.y, src.z);
            positions.setXYZ(1, tgt.x, tgt.y, tgt.z);
            positions.needsUpdate = true;
        });

        // Highlight edges for selected node
        if (selectedNodeId) {
            edgeLines.forEach(line => {
                const edge = line.userData.edge as GraphEdge;
                const mat = line.material as THREE.LineBasicMaterial;
                if (edge.source === selectedNodeId || edge.target === selectedNodeId) {
                    mat.opacity = 0.8;
                } else {
                    mat.opacity = 0.08;
                }
            });
        } else {
            edgeLines.forEach(line => {
                (line.material as THREE.LineBasicMaterial).opacity = 0.25;
            });
        }

        // Rotate particle field slowly
        particles.rotation.y += 0.0003;
        particles.rotation.x += 0.0001;

        controls.update();
        renderer.render(scene, camera);
        labelRenderer.render(scene, camera);
    }

    animate();

    // ─── Resize ──────────────────────────────────────────────

    function onResize(): void {
        const w = graphContainer.clientWidth;
        const h = graphContainer.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
        labelRenderer.setSize(w, h);
    }

    window.addEventListener('resize', onResize);

    // ─── Cleanup ─────────────────────────────────────────────

    cleanup = () => {
        cancelAnimationFrame(animationId);
        simulation.stop();
        window.removeEventListener('resize', onResize);
        renderer.domElement.removeEventListener('mousemove', onMouseMove);
        renderer.domElement.removeEventListener('click', onClick);

        // Dispose Three.js resources
        scene.traverse(obj => {
            if (obj instanceof THREE.Mesh) {
                obj.geometry.dispose();
                if (Array.isArray(obj.material)) {
                    obj.material.forEach(m => m.dispose());
                } else {
                    obj.material.dispose();
                }
            } else if (obj instanceof THREE.Line) {
                obj.geometry.dispose();
                (obj.material as THREE.Material).dispose();
            }
        });

        particleGeom.dispose();
        particleMat.dispose();
        renderer.dispose();
        controls.dispose();
    };
}
