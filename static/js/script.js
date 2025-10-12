// script.js for visualizer.html
document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const algoInfoBox = document.getElementById('algo-info-box');
    const generateInputsBtn = document.getElementById('generate-inputs-btn');
    const drawGraphBtn = document.getElementById('draw-graph-btn');
    const runAlgoBtn = document.getElementById('run-algo-btn');
    const prevStepBtn = document.getElementById('prev-step-btn');
    const nextStepBtn = document.getElementById('next-step-btn');
    const resetBtn = document.getElementById('reset-btn');
    const timelineSlider = document.getElementById('timeline-slider');
    const algorithmSelect = document.getElementById('algorithm-select');
    const startNodeGroup = document.getElementById('start-node-group');
    const svg = document.getElementById('graph-svg');
    const messageBox = document.getElementById('message-box');
    const stepCounter = document.getElementById('step-counter');

    // --- State & Mappings ---
    let graphData = { nodes: [], edges: [] };
    let visualizationSteps = [];
    let currentStep = 0;
    let nodeLetterToId = {};
    let nodeIdToLetter = {};
    
    // --- Constants ---
    const API_URL = '/api/run_algorithm';
    const ALGO_DESCRIPTIONS = {
        'dijkstra': { name: "Dijkstra's Algorithm", desc: "Finds the shortest path from a start node to all other nodes in a weighted graph.", complexity: "O(E log V)" },
        'bellman-ford': { name: "Bellman-Ford Algorithm", desc: "Finds shortest paths from a single source. Slower than Dijkstra's but handles negative weights.", complexity: "O(V * E)" },
        'kruskal': { name: "Kruskal's Algorithm", desc: "Finds a Minimum Spanning Tree (MST) by sorting all edges and adding them if they don't form a cycle.", complexity: "O(E log E)" },
        'prim': { name: "Prim's Algorithm", desc: "Finds an MST by growing a tree from an arbitrary starting node.", complexity: "O(E log V)" }
    };

    // --- Event Listeners ---
    algorithmSelect.addEventListener('change', updateAlgorithmInfo);
    generateInputsBtn.addEventListener('click', generateEdgeInputs);
    drawGraphBtn.addEventListener('click', drawGraph);
    runAlgoBtn.addEventListener('click', runAlgorithm);
    prevStepBtn.addEventListener('click', () => updateVisualization(currentStep - 1));
    nextStepBtn.addEventListener('click', () => updateVisualization(currentStep + 1));
    resetBtn.addEventListener('click', () => {
        if (graphData.nodes.length > 0) {
            drawGraph();
            setVisualizationControls(false);
            visualizationSteps = [];
            currentStep = 0;
            messageBox.textContent = "Visualization reset.";
        }
    });
    timelineSlider.addEventListener('input', (e) => updateVisualization(parseInt(e.target.value)));

    // --- Core Functions ---
    function setupNodeMappings(numVertices) {
        nodeLetterToId = {};
        nodeIdToLetter = {};
        for (let i = 0; i < numVertices; i++) {
            const letter = String.fromCharCode(65 + i); // A, B, C...
            nodeLetterToId[letter] = i;
            nodeIdToLetter[i] = letter;
        }
    }

    function updateAlgorithmInfo() {
        const selectedAlgo = algorithmSelect.value;
        const info = ALGO_DESCRIPTIONS[selectedAlgo];
        const needsStartNode = ['dijkstra', 'bellman-ford'].includes(selectedAlgo);
        
        startNodeGroup.style.display = needsStartNode ? 'flex' : 'none';
        algoInfoBox.innerHTML = `<h3>${info.name}</h3><p>${info.desc}</p><code>${info.complexity}</code>`;
    }

    function generateEdgeInputs() {
        const numVertices = parseInt(document.getElementById('vertices').value);
        if (numVertices < 2 || numVertices > 26) {
            messageBox.textContent = "Error: Please enter between 2 and 26 nodes.";
            return;
        }
        setupNodeMappings(numVertices);

        const numEdges = parseInt(document.getElementById('edges').value);
        const container = document.getElementById('edge-inputs-container');
        container.innerHTML = '';

        for (let i = 0; i < numEdges; i++) {
            const row = document.createElement('div');
            row.className = 'edge-input-row';
            row.innerHTML = `
                <span>E${i + 1}:</span>
                <input type="text" placeholder="From" class="edge-from" maxlength="1">
                <input type="text" placeholder="To" class="edge-to" maxlength="1">
                <input type="number" placeholder="Weight" class="edge-weight" min="1">`;
            container.appendChild(row);
        }
        drawGraphBtn.disabled = false;
        messageBox.textContent = "Fill in node letters (A, B, C...) and weights.";
    }

    function drawGraph() {
        const numVertices = parseInt(document.getElementById('vertices').value);
        setupNodeMappings(numVertices);
        const edgeInputRows = document.querySelectorAll('.edge-input-row');

        graphData.nodes = Array.from({ length: numVertices }, (_, i) => ({ id: i }));
        graphData.edges = [];
        
        let isValid = true;
        edgeInputRows.forEach(row => {
            const from = row.querySelector('.edge-from').value.trim().toUpperCase();
            const to = row.querySelector('.edge-to').value.trim().toUpperCase();
            const weight = parseInt(row.querySelector('.edge-weight').value);
            const fromId = nodeLetterToId[from];
            const toId = nodeLetterToId[to];

            if (fromId === undefined || toId === undefined || isNaN(weight)) {
                isValid = false;
            } else {
                graphData.edges.push([fromId, toId, weight]);
            }
        });
        
        if (!isValid) {
            messageBox.textContent = "Error: Invalid or empty edge data.";
            runAlgoBtn.disabled = true;
            return;
        }

        renderGraphToSVG(svg, graphData);
        runAlgoBtn.disabled = false;
        messageBox.textContent = `Graph generated successfully!`;
    }

    function renderGraphToSVG(svgElement, data) {
        svgElement.innerHTML = '';
        const { width, height } = svgElement.getBoundingClientRect();
        const radius = Math.min(width, height) * 0.38;
        const centerX = width / 2;
        const centerY = height / 2;

        data.nodes.forEach((node, i) => {
            const angle = (i / data.nodes.length) * 2 * Math.PI - Math.PI / 2;
            node.x = centerX + radius * Math.cos(angle);
            node.y = centerY + radius * Math.sin(angle);
        });

        const edgeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        data.edges.forEach(([u, v, w]) => {
            const n1 = data.nodes[u];
            const n2 = data.nodes[v];
            const edgeId = `edge-${Math.min(u,v)}-${Math.max(u,v)}`;
            edgeGroup.innerHTML += `
                <line x1="${n1.x}" y1="${n1.y}" x2="${n2.x}" y2="${n2.y}" id="${edgeId}" class="edge"/>
                <text x="${(n1.x + n2.x) / 2}" y="${(n1.y + n2.y) / 2 - 8}" class="edge-weight">${w}</text>`;
        });
        svgElement.appendChild(edgeGroup);
        
        const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        data.nodes.forEach(node => {
            nodeGroup.innerHTML += `
                <g class="node" id="node-${node.id}">
                    <circle cx="${node.x}" cy="${node.y}" r="24" />
                    <text x="${node.x}" y="${node.y}" dy=".3em">${nodeIdToLetter[node.id]}</text>
                    <text x="${node.x}" y="${node.y - 32}" class="node-info-text" id="info-text-${node.id}"></text>
                </g>`;
        });
        svgElement.appendChild(nodeGroup);
    }

    async function runAlgorithm() {
        const algorithm = algorithmSelect.value;
        const startNodeLetter = document.getElementById('start-node').value.toUpperCase();
        const startNodeId = nodeLetterToId[startNodeLetter];

        if (startNodeId === undefined && ['dijkstra', 'bellman-ford'].includes(algorithm)) {
            messageBox.textContent = `Error: Please enter a valid start node.`;
            return;
        }
        
        const payload = {
            algorithm: algorithm,
            graph: {
                nodes: graphData.nodes.map(n => n.id),
                edges: graphData.edges,
                startNode: startNodeId
            }
        };

        try {
            messageBox.textContent = `Running ${ALGO_DESCRIPTIONS[algorithm].name}...`;
            runAlgoBtn.disabled = true;
            
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) throw new Error(`Server error: ${response.statusText}`);
            
            visualizationSteps = await response.json();
            if (visualizationSteps.length > 0) {
                currentStep = 0;
                setVisualizationControls(true);
                timelineSlider.max = visualizationSteps.length - 1;
                updateVisualization(0);
            }

        } catch (error) {
            messageBox.textContent = `Error: ${error.message}.`;
        } finally {
            runAlgoBtn.disabled = false;
        }
    }

    function updateVisualization(stepIndex) {
        if (stepIndex < 0 || stepIndex >= visualizationSteps.length) return;
        currentStep = stepIndex;
        const stepData = visualizationSteps[currentStep];

        Object.entries(stepData.nodes).forEach(([nodeId, state]) => {
            const nodeG = svg.querySelector(`#node-${nodeId}`);
            if (nodeG) {
                nodeG.querySelector('circle').style.fill = state.color;
                nodeG.querySelector('.node-info-text').textContent = state.text;
            }
        });
        
        Object.entries(stepData.edges).forEach(([edgeId, state]) => {
            const edgeLine = svg.querySelector(`#edge-${edgeId}`);
            if (edgeLine) {
                edgeLine.style.stroke = state.color;
                edgeLine.style.strokeWidth = state.width + 'px';
            }
        });
        
        messageBox.textContent = stepData.message;
        timelineSlider.value = currentStep;
        stepCounter.textContent = `${currentStep}/${visualizationSteps.length - 1}`;
        prevStepBtn.disabled = currentStep === 0;
        nextStepBtn.disabled = currentStep === visualizationSteps.length - 1;
    }
    
    function setVisualizationControls(isEnabled) {
        prevStepBtn.disabled = !isEnabled;
        nextStepBtn.disabled = !isEnabled;
        resetBtn.disabled = !isEnabled;
        timelineSlider.disabled = !isEnabled;
        
        if (isEnabled) prevStepBtn.disabled = true;
        else {
            timelineSlider.value = 0;
            stepCounter.textContent = '0/0';
        }
    }

    // --- Initial Page Load ---
    updateAlgorithmInfo();
    messageBox.textContent = "Welcome! Set up your graph to begin.";
});
