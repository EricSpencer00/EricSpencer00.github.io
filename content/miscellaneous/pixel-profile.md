---
title: "GitHub pfp Generator"
date: 2025-06-04
description: "Generate a default GitHub profile picture"
tags: ["web development", "javascript", "canvas"]
categories: ["Miscellaneous"]
draft: false
---

{{< rawhtml >}}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generate a Default GitHub Profile Picture</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom font for better aesthetics */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        canvas {
            border: 2px solid #e5e7eb; /* Light border for the canvas */
            background-color: #ffffff; /* White background for pixels */
            image-rendering: pixelated; /* Ensures crisp pixel rendering */
            image-rendering: -moz-crisp-edges;
            image-rendering: crisp-edges;
            border-radius: 0.75rem; /* Rounded corners for the canvas */
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); /* Subtle shadow */
        }
    </style>
</head>
<body>
    <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-2xl mx-auto text-center">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">Generate a Default GitHub Profile Picture</h1>

        <!-- Canvas for drawing the pixel art -->
        <canvas id="pixelCanvas" class="w-64 h-64 mx-auto mb-6"></canvas>

        <div class="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <!-- Generate New Button -->
            <button id="generateBtn" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75">
                Generate New
            </button>

            <!-- Download Button -->
            <button id="downloadBtn" class="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-75">
                Download Image
            </button>
        </div>
    </div>

    <script>
        // Get references to the canvas and buttons
        const canvas = document.getElementById('pixelCanvas');
        const ctx = canvas.getContext('2d');
        const generateBtn = document.getElementById('generateBtn');
        const downloadBtn = document.getElementById('downloadBtn');

        // Configuration for the pixel art
        const PIXEL_GRID_SIZE = 7;
        const TARGET_CANVAS_DIMENSION = 280;
        const PIXEL_BLOCK_SIZE = TARGET_CANVAS_DIMENSION / PIXEL_GRID_SIZE;

        // Set canvas dimensions
        canvas.width = TARGET_CANVAS_DIMENSION;
        canvas.height = TARGET_CANVAS_DIMENSION;

        // Global variable to store the density map
        let densityMap;

        function getRandomColor() {
            const letters = '0123456789ABCDEF';
            let color = '#';
            for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        }

        function createDensityMap() {
            const map = Array(PIXEL_GRID_SIZE).fill(0).map(() => Array(PIXEL_GRID_SIZE).fill(0));
            const centerX = (PIXEL_GRID_SIZE - 1) / 2;
            const centerY = (PIXEL_GRID_SIZE - 1) / 2;
            const maxDistance = Math.sqrt(Math.pow(0 - centerX, 2) + Math.pow(0 - centerY, 2));
            const halfGridSize = Math.ceil(PIXEL_GRID_SIZE / 2);

            for (let y = 0; y < PIXEL_GRID_SIZE; y++) {
                for (let x = 0; x < halfGridSize; x++) {
                    const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
                    const normalizedDistance = distance / maxDistance;
                    let probability = 1 - Math.pow(normalizedDistance, 1.5);
                    probability = Math.max(0, Math.min(1, probability));
                    map[y][x] = probability;
                    const mirroredX = PIXEL_GRID_SIZE - 1 - x;
                    map[y][mirroredX] = probability;
                }
            }
            return map;
        }

        function generatePixelArt() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const halfGridSize = Math.ceil(PIXEL_GRID_SIZE / 2);
            const mainColor = getRandomColor();
            const pixelData = Array(PIXEL_GRID_SIZE).fill(0).map(() => Array(PIXEL_GRID_SIZE).fill('#FFFFFF')); // Initialize all pixels as white

            for (let y = 0; y < PIXEL_GRID_SIZE; y++) {
                for (let x = 0; x < halfGridSize; x++) {
                    if (Math.random() < densityMap[y][x]) {
                        pixelData[y][x] = mainColor;
                        const mirroredX = PIXEL_GRID_SIZE - 1 - x;
                        pixelData[y][mirroredX] = mainColor;
                    }
                }
            }

            for (let y = 0; y < PIXEL_GRID_SIZE; y++) {
                for (let x = 0; x < PIXEL_GRID_SIZE; x++) {
                    ctx.fillStyle = pixelData[y][x];
                    ctx.fillRect(x * PIXEL_BLOCK_SIZE, y * PIXEL_BLOCK_SIZE, PIXEL_BLOCK_SIZE, PIXEL_BLOCK_SIZE);
                }
            }
        }

        function downloadImage() {
            const image = canvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.href = image;
            link.download = 'pixel-profile.png';
            link.click();
        }

        // Initialize
        densityMap = createDensityMap();
        generateBtn.addEventListener('click', generatePixelArt);
        downloadBtn.addEventListener('click', downloadImage);
        window.onload = generatePixelArt;
    </script>
</body>
</html>
{{< /rawhtml >}} 