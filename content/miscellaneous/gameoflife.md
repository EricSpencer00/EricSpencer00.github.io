---
title: "Conway's Game of Life"
date: 2025-10-01
description: "Interactive implementation of Conway's Game of Life with preset patterns"
tags: ["Game", "Simulation"]
categories: ["Miscellaneous"]
draft: false
image: "/previews/gameoflife.png"
---

Experience Conway's Game of Life - a cellular automaton that demonstrates how complex patterns can emerge from simple rules. Click cells to toggle them, use preset patterns, and watch life evolve!

{{< rawhtml >}}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conway's Game of Life</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            overflow: hidden;
        }
        
        .game-container {
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .controls {
            background: rgba(20, 20, 20, 0.95);
            padding: 15px 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            justify-content: center;
            border-bottom: 2px solid #333;
            z-index: 10;
        }
        
        .control-group {
            display: flex;
            gap: 10px;
            align-items: center;
            padding: 5px 10px;
            background: rgba(40, 40, 40, 0.5);
            border-radius: 8px;
        }
        
        button {
            background: #2a2a2a;
            color: #ffffff;
            border: 2px solid #444;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        button:hover {
            background: #3a3a3a;
            border-color: #666;
            transform: translateY(-1px);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button.active {
            background: #4a9eff;
            border-color: #6ab0ff;
        }
        
        button.danger {
            background: #d32f2f;
            border-color: #f44336;
        }
        
        button.danger:hover {
            background: #e53935;
        }
        
        .canvas-wrapper {
            flex: 1;
            position: relative;
            overflow: hidden;
        }
        
        canvas {
            display: block;
            cursor: crosshair;
            background: #000000;
        }
        
        .info {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(20, 20, 20, 0.9);
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 13px;
            border: 1px solid #333;
        }
        
        .info-item {
            margin: 3px 0;
        }
        
        label {
            font-size: 13px;
            color: #aaa;
            margin-right: 5px;
        }
        
        select {
            background: #2a2a2a;
            color: #ffffff;
            border: 2px solid #444;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        
        select:hover {
            border-color: #666;
        }
        
        .zoom-display {
            font-size: 13px;
            color: #aaa;
            min-width: 60px;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="controls">
            <div class="control-group">
                <button id="playPauseBtn" class="active">⏸ Pause</button>
                <button id="stepBtn">⏭ Step</button>
                <button id="clearBtn" class="danger">🗑 Clear</button>
                <button id="randomBtn">🎲 Random</button>
            </div>
            
            <div class="control-group">
                <label for="patternSelect">Pattern:</label>
                <select id="patternSelect">
                    <option value="">-- Select Pattern --</option>
                    <option value="glider">Glider</option>
                    <option value="lwss">Lightweight Spaceship</option>
                    <option value="gosperGun">Gosper Glider Gun</option>
                    <option value="pulsar">Pulsar</option>
                    <option value="pentadecathlon">Pentadecathlon</option>
                    <option value="acorn">Acorn</option>
                    <option value="diehard">Diehard</option>
                    <option value="rpentomino">R-pentomino</option>
                </select>
            </div>
            
            <div class="control-group">
                <button id="zoomOutBtn">➖ Zoom Out</button>
                <span class="zoom-display" id="zoomDisplay">100%</span>
                <button id="zoomInBtn">➕ Zoom In</button>
            </div>
        </div>
        
        <div class="canvas-wrapper">
            <canvas id="gameCanvas"></canvas>
            <div class="info">
                <div class="info-item">Generation: <strong id="generation">0</strong></div>
                <div class="info-item">Living Cells: <strong id="population">0</strong></div>
                <div class="info-item">FPS: <strong id="fps">60</strong></div>
            </div>
        </div>
    </div>

    <script>
        class GameOfLife {
            constructor() {
                this.canvas = document.getElementById('gameCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.cellSize = 10;
                this.isRunning = false;
                this.generation = 0;
                this.grid = [];
                this.nextGrid = [];
                this.lastFrameTime = 0;
                this.frameDelay = 100; // milliseconds between frames
                this.isDragging = false;
                this.offsetX = 0;
                this.offsetY = 0;
                this.dragStartX = 0;
                this.dragStartY = 0;
                
                this.resizeCanvas();
                this.initGrid();
                this.setupEventListeners();
                this.draw();
                
                window.addEventListener('resize', () => this.resizeCanvas());
            }
            
            resizeCanvas() {
                const wrapper = this.canvas.parentElement;
                this.canvas.width = wrapper.clientWidth;
                this.canvas.height = wrapper.clientHeight;
                this.cols = Math.ceil(this.canvas.width / this.cellSize) + 2;
                this.rows = Math.ceil(this.canvas.height / this.cellSize) + 2;
                this.initGrid();
                this.draw();
            }
            
            initGrid() {
                this.grid = Array(this.rows).fill(null).map(() => Array(this.cols).fill(false));
                this.nextGrid = Array(this.rows).fill(null).map(() => Array(this.cols).fill(false));
            }
            
            setupEventListeners() {
                // Play/Pause
                document.getElementById('playPauseBtn').addEventListener('click', () => this.togglePlayPause());
                
                // Step
                document.getElementById('stepBtn').addEventListener('click', () => {
                    if (!this.isRunning) {
                        this.update();
                        this.draw();
                    }
                });
                
                // Clear
                document.getElementById('clearBtn').addEventListener('click', () => this.clear());
                
                // Random
                document.getElementById('randomBtn').addEventListener('click', () => this.randomize());
                
                // Pattern selection
                document.getElementById('patternSelect').addEventListener('change', (e) => {
                    if (e.target.value) {
                        this.loadPattern(e.target.value);
                        e.target.value = '';
                    }
                });
                
                // Zoom
                document.getElementById('zoomInBtn').addEventListener('click', () => this.zoom(1.2));
                document.getElementById('zoomOutBtn').addEventListener('click', () => this.zoom(0.8));
                
                // Canvas interactions
                this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
                this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
                this.canvas.addEventListener('mouseup', () => this.handleMouseUp());
                this.canvas.addEventListener('mouseleave', () => this.handleMouseUp());
                
                // Touch support
                this.canvas.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    const touch = e.touches[0];
                    this.handleMouseDown({clientX: touch.clientX, clientY: touch.clientY});
                });
                this.canvas.addEventListener('touchmove', (e) => {
                    e.preventDefault();
                    const touch = e.touches[0];
                    this.handleMouseMove({clientX: touch.clientX, clientY: touch.clientY});
                });
                this.canvas.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    this.handleMouseUp();
                });
                
                // Mouse wheel zoom
                this.canvas.addEventListener('wheel', (e) => {
                    e.preventDefault();
                    const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
                    this.zoom(zoomFactor);
                });
            }
            
            handleMouseDown(e) {
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                this.isDragging = true;
                this.dragStartX = x - this.offsetX;
                this.dragStartY = y - this.offsetY;
                
                // Toggle cell on click
                this.toggleCell(x, y);
            }
            
            handleMouseMove(e) {
                if (!this.isDragging) return;
                
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                this.offsetX = x - this.dragStartX;
                this.offsetY = y - this.dragStartY;
                
                this.draw();
            }
            
            handleMouseUp() {
                this.isDragging = false;
            }
            
            toggleCell(x, y) {
                const col = Math.floor((x - this.offsetX) / this.cellSize);
                const row = Math.floor((y - this.offsetY) / this.cellSize);
                
                if (row >= 0 && row < this.rows && col >= 0 && col < this.cols) {
                    this.grid[row][col] = !this.grid[row][col];
                    this.draw();
                }
            }
            
            togglePlayPause() {
                this.isRunning = !this.isRunning;
                const btn = document.getElementById('playPauseBtn');
                if (this.isRunning) {
                    btn.textContent = '⏸ Pause';
                    btn.classList.add('active');
                    this.animate();
                } else {
                    btn.textContent = '▶ Play';
                    btn.classList.remove('active');
                }
            }
            
            clear() {
                this.initGrid();
                this.generation = 0;
                this.offsetX = 0;
                this.offsetY = 0;
                this.draw();
            }
            
            randomize() {
                for (let row = 0; row < this.rows; row++) {
                    for (let col = 0; col < this.cols; col++) {
                        this.grid[row][col] = Math.random() > 0.7;
                    }
                }
                this.generation = 0;
                this.draw();
            }
            
            zoom(factor) {
                const newCellSize = this.cellSize * factor;
                if (newCellSize >= 4 && newCellSize <= 50) {
                    // Adjust offset to zoom toward center
                    const centerX = this.canvas.width / 2;
                    const centerY = this.canvas.height / 2;
                    
                    this.offsetX = centerX - (centerX - this.offsetX) * factor;
                    this.offsetY = centerY - (centerY - this.offsetY) * factor;
                    
                    this.cellSize = newCellSize;
                    const oldRows = this.rows;
                    const oldCols = this.cols;
                    
                    this.cols = Math.ceil(this.canvas.width / this.cellSize) + 2;
                    this.rows = Math.ceil(this.canvas.height / this.cellSize) + 2;
                    
                    // Preserve existing cells when resizing
                    const newGrid = Array(this.rows).fill(null).map(() => Array(this.cols).fill(false));
                    for (let row = 0; row < Math.min(oldRows, this.rows); row++) {
                        for (let col = 0; col < Math.min(oldCols, this.cols); col++) {
                            newGrid[row][col] = this.grid[row][col];
                        }
                    }
                    this.grid = newGrid;
                    this.nextGrid = Array(this.rows).fill(null).map(() => Array(this.cols).fill(false));
                    
                    document.getElementById('zoomDisplay').textContent = Math.round(this.cellSize * 10) + '%';
                    this.draw();
                }
            }
            
            loadPattern(patternName) {
                const centerRow = Math.floor(this.rows / 2);
                const centerCol = Math.floor(this.cols / 2);
                
                const patterns = {
                    glider: [
                        [0, 1, 0],
                        [0, 0, 1],
                        [1, 1, 1]
                    ],
                    lwss: [
                        [0, 1, 0, 0, 1],
                        [1, 0, 0, 0, 0],
                        [1, 0, 0, 0, 1],
                        [1, 1, 1, 1, 0]
                    ],
                    gosperGun: [
                        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                    ],
                    pulsar: [
                        [0,0,1,1,1,0,0,0,1,1,1,0,0],
                        [0,0,0,0,0,0,0,0,0,0,0,0,0],
                        [1,0,0,0,0,1,0,1,0,0,0,0,1],
                        [1,0,0,0,0,1,0,1,0,0,0,0,1],
                        [1,0,0,0,0,1,0,1,0,0,0,0,1],
                        [0,0,1,1,1,0,0,0,1,1,1,0,0],
                        [0,0,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,1,1,1,0,0,0,1,1,1,0,0],
                        [1,0,0,0,0,1,0,1,0,0,0,0,1],
                        [1,0,0,0,0,1,0,1,0,0,0,0,1],
                        [1,0,0,0,0,1,0,1,0,0,0,0,1],
                        [0,0,0,0,0,0,0,0,0,0,0,0,0],
                        [0,0,1,1,1,0,0,0,1,1,1,0,0]
                    ],
                    pentadecathlon: [
                        [0,0,1,0,0,0,0,1,0,0],
                        [1,1,0,1,1,1,1,0,1,1],
                        [0,0,1,0,0,0,0,1,0,0]
                    ],
                    acorn: [
                        [0,1,0,0,0,0,0],
                        [0,0,0,1,0,0,0],
                        [1,1,0,0,1,1,1]
                    ],
                    diehard: [
                        [0,0,0,0,0,0,1,0],
                        [1,1,0,0,0,0,0,0],
                        [0,1,0,0,0,1,1,1]
                    ],
                    rpentomino: [
                        [0,1,1],
                        [1,1,0],
                        [0,1,0]
                    ]
                };
                
                const pattern = patterns[patternName];
                if (pattern) {
                    const startRow = centerRow - Math.floor(pattern.length / 2);
                    const startCol = centerCol - Math.floor(pattern[0].length / 2);
                    
                    for (let row = 0; row < pattern.length; row++) {
                        for (let col = 0; col < pattern[row].length; col++) {
                            const gridRow = startRow + row;
                            const gridCol = startCol + col;
                            if (gridRow >= 0 && gridRow < this.rows && gridCol >= 0 && gridCol < this.cols) {
                                this.grid[gridRow][gridCol] = pattern[row][col] === 1;
                            }
                        }
                    }
                    this.draw();
                }
            }
            
            countNeighbors(row, col) {
                let count = 0;
                for (let i = -1; i <= 1; i++) {
                    for (let j = -1; j <= 1; j++) {
                        if (i === 0 && j === 0) continue;
                        const newRow = row + i;
                        const newCol = col + j;
                        if (newRow >= 0 && newRow < this.rows && newCol >= 0 && newCol < this.cols) {
                            if (this.grid[newRow][newCol]) count++;
                        }
                    }
                }
                return count;
            }
            
            update() {
                let population = 0;
                
                for (let row = 0; row < this.rows; row++) {
                    for (let col = 0; col < this.cols; col++) {
                        const neighbors = this.countNeighbors(row, col);
                        const cell = this.grid[row][col];
                        
                        if (cell && (neighbors === 2 || neighbors === 3)) {
                            this.nextGrid[row][col] = true;
                            population++;
                        } else if (!cell && neighbors === 3) {
                            this.nextGrid[row][col] = true;
                            population++;
                        } else {
                            this.nextGrid[row][col] = false;
                        }
                    }
                }
                
                [this.grid, this.nextGrid] = [this.nextGrid, this.grid];
                this.generation++;
                
                document.getElementById('generation').textContent = this.generation;
                document.getElementById('population').textContent = population;
            }
            
            draw() {
                this.ctx.fillStyle = '#000000';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Draw grid lines
                this.ctx.strokeStyle = '#111111';
                this.ctx.lineWidth = 1;
                
                const startCol = Math.max(0, Math.floor(-this.offsetX / this.cellSize));
                const endCol = Math.min(this.cols, Math.ceil((this.canvas.width - this.offsetX) / this.cellSize));
                const startRow = Math.max(0, Math.floor(-this.offsetY / this.cellSize));
                const endRow = Math.min(this.rows, Math.ceil((this.canvas.height - this.offsetY) / this.cellSize));
                
                // Draw living cells
                this.ctx.fillStyle = '#00ff00';
                let population = 0;
                
                for (let row = startRow; row < endRow; row++) {
                    for (let col = startCol; col < endCol; col++) {
                        if (this.grid[row][col]) {
                            const x = col * this.cellSize + this.offsetX;
                            const y = row * this.cellSize + this.offsetY;
                            this.ctx.fillRect(x + 1, y + 1, this.cellSize - 2, this.cellSize - 2);
                            population++;
                        }
                    }
                }
                
                // Draw grid lines (optional, only if cell size is large enough)
                if (this.cellSize > 8) {
                    this.ctx.strokeStyle = '#1a1a1a';
                    for (let col = startCol; col <= endCol; col++) {
                        const x = col * this.cellSize + this.offsetX;
                        this.ctx.beginPath();
                        this.ctx.moveTo(x, 0);
                        this.ctx.lineTo(x, this.canvas.height);
                        this.ctx.stroke();
                    }
                    for (let row = startRow; row <= endRow; row++) {
                        const y = row * this.cellSize + this.offsetY;
                        this.ctx.beginPath();
                        this.ctx.moveTo(0, y);
                        this.ctx.lineTo(this.canvas.width, y);
                        this.ctx.stroke();
                    }
                }
                
                if (!this.isRunning) {
                    document.getElementById('population').textContent = population;
                }
            }
            
            animate(timestamp = 0) {
                if (!this.isRunning) return;
                
                if (timestamp - this.lastFrameTime >= this.frameDelay) {
                    this.update();
                    this.draw();
                    this.lastFrameTime = timestamp;
                    
                    const fps = Math.round(1000 / this.frameDelay);
                    document.getElementById('fps').textContent = fps;
                }
                
                requestAnimationFrame((t) => this.animate(t));
            }
        }
        
        // Initialize the game
        window.addEventListener('load', () => {
            new GameOfLife();
        });
    </script>
</body>
</html>
{{< /rawhtml >}}
