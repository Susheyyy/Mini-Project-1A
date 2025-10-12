// compare.js - Logic for the algorithm comparison page
document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const generateInputsBtn = document.getElementById('generate-inputs-btn');
    const compareBtn = document.getElementById('compare-btn');
    const algo1Select = document.getElementById('algo1-select');
    const algo2Select = document.getElementById('algo2-select');
    const startNodeGroup = document.getElementById('start-node-group');

    // --- State & Mappings ---
    let graphData = { nodes: [], edges: [] };
    let nodeLetterToId = {};
    let nodeIdToLetter = {};
    
    // Algorithm 1 state
    let viz1 = {
        steps: [],
        currentStep: 0,
        svg: document.getElementById('graph-svg-1'),
        messageBox: document.getElementById('message-box-1'),
        timeline: document.getElementById('timeline-slider-1'),
        stepCounter: document.getElementById('step-counter-1'),
        prevBtn: document.getElementById('prev-step-btn-1'),
        nextBtn: document.getElementById('next-step-btn-1'),
        timeDisplay: document.getElementById('algo1-time'),
        titleDisplay: document.getElementById('algo1-title'),
    };
    // Algorithm 2 state
    let viz2 = {
        steps: [],
        currentStep: 0,
        svg: document.getElementById('graph-svg-2'),
        messageBox: document.getElementById('message-box-2'),
        timeline: document.getElementById('timeline-slider-2'),
        stepCounter: document.getElementById('step-counter-2'),
        prevBtn: document.getElementById('prev-step-btn-2'),
        nextBtn: document.getElementById('next-step-btn-2'),
        timeDisplay: document.getElementById('algo2-time'),
        titleDisplay: document.getElementById('algo2-title'),
    };

    // --- Event Listeners ---
    generateInputsBtn.addEventListener('click', generateEdgeInputs);
    compareBtn.addEventListener('click', runComparison);
    
    [algo1Select, algo2Select].forEach(select => {
        select.addEventListener('change', checkStartNodeVisibility);
    });

    // Timeline controls for both visualizers
    viz1.prevBtn.addEventListener('click', () => updateVisualization(viz1, viz1.currentStep - 1));
    viz1.nextBtn.addEventListener('click', () => updateVisualization(viz1, viz1.currentStep + 1));
    viz1.timeline.addEventListener('input', (e) => updateVisualization(viz1, parseInt(e.target.value)));
    
    viz2.prevBtn.addEventListener('click', () => updateVisualization(viz2, viz2.currentStep - 1));
    viz2.nextBtn.addEventListener('click', () => updateVisualization(viz2, viz2.currentStep + 1));
    viz2.timeline.addEventListener('input', (e) => updateVisualization(viz2, parseInt(e.target.value)));

    // --- Core Functions ---
    function setupNodeMappings(numVertices) {
        nodeLetterToId = {};
        nodeIdToLetter = {};
        for (let i = 0; i < numVertices; i++) {
            const letter = String.fromCharCode(65 + i);
            nodeLetterToId[letter] = i;
            nodeIdToLetter[i] = letter;
        }
    }

    function generateEdgeInputs() {
        const numVertices = parseInt(document.getElementById('vertices').value);
        if (numVertices < 2 || numVertices > 26) return;
        setupNodeMappings(numVertices);

        const numEdges = parseInt(document.getElementById('edges').value);
        const container = document.getElementById('edge-inputs-container');
        container.innerHTML = '';

        for (let i = 0; i < numEdges; i++) {
            const row = document.createElement('div');
            row.className = 'edge-input-row';
            row.innerHTML = `
                <span>E${i + 1}:</span>
                <input type="text" placeholder="From" class="edge-from" maxlength="1" style="text-transform:uppercase">
                <input type="text" placeholder="To" class="edge-to" maxlength="1" style="text-transform:uppercase">
                <input type="number" placeholder="Weight" class="edge-weight" min="1">`;
            container.appendChild(row);
        }
    }

    function checkStartNodeVisibility() {
        const algo1 = algo1Select.value;
        const algo2 = algo2Select.value;
        const needsStartNode = ['dijkstra', 'bellman-ford'].includes(algo1) || ['dijkstra', 'bellman-ford'].includes(algo2);
        startNodeGroup.style.display = needsStartNode ? 'flex' : 'none';
    }

    function drawInitialGraphs() {
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
            viz1.messageBox.textContent = "Error: Invalid graph data.";
            viz2.messageBox.textContent = "Error: Invalid graph data.";
            return false;
        }

        renderGraphToSVG(viz1.svg, graphData);
        renderGraphToSVG(viz2.svg, graphData);
        return true;
    }

    function renderGraphToSVG(svgElement, data) {
        svgElement.innerHTML = '';
        const { width, height } = svgElement.getBoundingClientRect();
        const radius = Math.min(width, height) * 0.35;
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
            const edgeId = `${svgElement.id}-edge-${Math.min(u,v)}-${Math.max(u,v)}`;
            edgeGroup.innerHTML += `<line x1="${n1.x}" y1="${n1.y}" x2="${n2.x}" y2="${n2.y}" id="${edgeId}" class="edge"/><text x="${(n1.x + n2.x) / 2}" y="${(n1.y + n2.y) / 2 - 8}" class="edge-weight">${w}</text>`;
        });
        svgElement.appendChild(edgeGroup);
        
        const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        data.nodes.forEach(node => {
            const nodeId = `${svgElement.id}-node-${node.id}`;
            const infoTextId = `${svgElement.id}-info-text-${node.id}`;
            nodeGroup.innerHTML += `<g class="node" id="${nodeId}"><circle cx="${node.x}" cy="${node.y}" r="20" /><text x="${node.x}" y="${node.y}" dy=".3em">${nodeIdToLetter[node.id]}</text><text x="${node.x}" y="${node.y - 28}" class="node-info-text" id="${infoTextId}"></text></g>`;
        });
        svgElement.appendChild(nodeGroup);
    }
    
    async function runComparison() {
        if (!drawInitialGraphs()) return;

        const algo1 = algo1Select.value;
        const algo2 = algo2Select.value;
        const startNodeLetter = document.getElementById('start-node').value.toUpperCase();
        const startNodeId = nodeLetterToId[startNodeLetter];

        const payload = {
            algo1: algo1,
            algo2: algo2,
            graph: {
                nodes: graphData.nodes.map(n => n.id),
                edges: graphData.edges,
                startNode: startNodeId
            }
        };

        compareBtn.disabled = true;
        compareBtn.textContent = 'Comparing...';
        viz1.messageBox.textContent = `Running ${algo1}...`;
        viz2.messageBox.textContent = `Running ${algo2}...`;

        try {
            const response = await fetch('/api/compare_algorithms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`Server Error: ${response.statusText}`);

            const results = await response.json();
            
            // Process results for Algo 1
            viz1.steps = results.algo1_result.steps;
            viz1.timeDisplay.textContent = `${results.algo1_result.execution_time} ms`;
            viz1.titleDisplay.textContent = algo1Select.options[algo1Select.selectedIndex].text;
            setupVisualization(viz1);

            // Process results for Algo 2
            viz2.steps = results.algo2_result.steps;
            viz2.timeDisplay.textContent = `${results.algo2_result.execution_time} ms`;
            viz2.titleDisplay.textContent = algo2Select.options[algo2Select.selectedIndex].text;
            setupVisualization(viz2);

        } catch (error) {
            viz1.messageBox.textContent = `Error: ${error.message}`;
            viz2.messageBox.textContent = `Error: ${error.message}`;
        } finally {
            compareBtn.disabled = false;
            compareBtn.textContent = 'Compare Algorithms';
        }
    }
    
    function setupVisualization(viz) {
        if (viz.steps.length > 0) {
            viz.currentStep = 0;
            viz.timeline.max = viz.steps.length - 1;
            viz.timeline.disabled = false;
            viz.prevBtn.disabled = true;
            viz.nextBtn.disabled = false;
            updateVisualization(viz, 0);
        } else {
             viz.messageBox.textContent = "No steps generated.";
        }
    }

    function updateVisualization(viz, stepIndex) {
        if (stepIndex < 0 || stepIndex >= viz.steps.length) return;
        viz.currentStep = stepIndex;
        const stepData = viz.steps[viz.currentStep];

        Object.entries(stepData.nodes).forEach(([nodeId, state]) => {
            const nodeG = viz.svg.querySelector(`#${viz.svg.id}-node-${nodeId}`);
            if (nodeG) {
                nodeG.querySelector('circle').style.fill = state.color;
                nodeG.querySelector('.node-info-text').textContent = state.text;
            }
        });
        
        Object.entries(stepData.edges).forEach(([edgeId, state]) => {
            const edgeLine = viz.svg.querySelector(`#${viz.svg.id}-edge-${edgeId}`);
            if (edgeLine) {
                edgeLine.style.stroke = state.color;
                edgeLine.style.strokeWidth = state.width + 'px';
            }
        });
        
        viz.messageBox.textContent = stepData.message;
        viz.timeline.value = viz.currentStep;
        viz.stepCounter.textContent = `${viz.currentStep}/${viz.steps.length - 1}`;
        viz.prevBtn.disabled = viz.currentStep === 0;
        viz.nextBtn.disabled = viz.currentStep === viz.steps.length - 1;
    }
    
    // Initial call
    checkStartNodeVisibility();
    generateEdgeInputs();
});
