---
title: "Song Recommender"
date: 2025-01-15
description: "AI-powered song recommendations using Gemini API"
tags: ["AI", "Music", "Recommendations", "Web App"]
categories: ["Miscellaneous"]
draft: true
---

{{< rawhtml >}}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Song Recommender</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        .song-card {
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        .song-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        /* Simple spinner animation */
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border-left-color: #0ea5e9; /* sky-500 */
            animation: spin 1s ease infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-gray-50 text-gray-800">

    <div class="container mx-auto px-4 py-8 md:py-16 min-h-screen flex flex-col items-center">
        
        <!-- Header -->
        <header class="text-center mb-8 md:mb-12">
            <h1 class="text-4xl md:text-5xl font-bold text-gray-900">Song Recommender</h1>
            <p class="mt-3 text-lg text-gray-600">Find your next favorite song.</p>
        </header>

        <!-- Input Form -->
        <div class="w-full max-w-lg mb-8">
            <div class="flex flex-col sm:flex-row gap-4">
                <input type="text" id="songInput" placeholder="Enter a song title..." class="flex-grow w-full px-4 py-3 text-lg bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition duration-200">
                <button id="getRecommendationsBtn" class="bg-sky-500 hover:bg-sky-600 text-white font-bold py-3 px-6 rounded-lg text-lg transition duration-200 shadow-md hover:shadow-lg">
                    Get Recommendations
                </button>
            </div>
        </div>

        <!-- Results Section -->
        <main id="results" class="w-full max-w-4xl">
            <!-- Loading Spinner -->
            <div id="loader" class="hidden justify-center items-center py-10">
                <div class="spinner"></div>
            </div>

            <!-- Error Message -->
            <div id="errorMessage" class="hidden text-center bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
                <p>Could not fetch recommendations. Please try again.</p>
            </div>

            <!-- Song List -->
            <div id="songList" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Recommended songs will be injected here -->
            </div>
        </main>
        
    </div>

    <script>
        const songInput = document.getElementById('songInput');
        const getRecommendationsBtn = document.getElementById('getRecommendationsBtn');
        const songList = document.getElementById('songList');
        const loader = document.getElementById('loader');
        const errorMessage = document.getElementById('errorMessage');

        getRecommendationsBtn.addEventListener('click', fetchRecommendations);
        songInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                fetchRecommendations();
            }
        });

        async function fetchRecommendations() {
            const songTitle = songInput.value.trim();
            if (!songTitle) {
                // You could show a message here if you want
                return;
            }

            // --- UI Updates: Show loader, hide previous results/errors ---
            loader.style.display = 'flex';
            errorMessage.classList.add('hidden');
            songList.innerHTML = '';

            // --- Construct the prompt for the Gemini API ---
            const prompt = `Provide a list of 10 songs that are similar to "${songTitle}". The list should not include the original song.`;
            const chatHistory = [{ role: "user", parts: [{ text: prompt }] }];

            // --- Define the desired JSON output structure ---
            const generationConfig = {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "OBJECT",
                    properties: {
                        "recommendations": {
                            type: "ARRAY",
                            items: {
                                type: "OBJECT",
                                properties: {
                                    "title": { "type": "STRING" },
                                    "artist": { "type": "STRING" }
                                },
                                required: ["title", "artist"]
                            }
                        }
                    },
                    required: ["recommendations"]
                }
            };
            
            const payload = {
                contents: chatHistory,
                generationConfig: generationConfig
            };

            // Get API key from environment variable or prompt user
            let apiKey = '';
            if (typeof process !== 'undefined' && process.env && process.env.GEMINI_API_KEY) {
                apiKey = process.env.GEMINI_API_KEY;
            } else {
                // For client-side, you'll need to set this up differently
                apiKey = prompt('Please enter your Gemini API key:');
                if (!apiKey) {
                    errorMessage.classList.remove('hidden');
                    errorMessage.innerHTML = '<p>API key is required. Please enter a valid Gemini API key.</p>';
                    loader.style.display = 'none';
                    return;
                }
            }

            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error(`API call failed with status: ${response.status}`);
                }

                const result = await response.json();
                
                if (result.candidates && result.candidates.length > 0 &&
                    result.candidates[0].content && result.candidates[0].content.parts &&
                    result.candidates[0].content.parts.length > 0) {
                    
                    const jsonText = result.candidates[0].content.parts[0].text;
                    const parsedData = JSON.parse(jsonText);
                    displaySongs(parsedData.recommendations);

                } else {
                    throw new Error("Invalid response structure from API.");
                }

            } catch (error) {
                console.error("Error fetching recommendations:", error);
                errorMessage.classList.remove('hidden');
                errorMessage.innerHTML = '<p>Could not fetch recommendations. Please check your API key and try again.</p>';
            } finally {
                // Hide loader regardless of success or failure
                loader.style.display = 'none';
            }
        }

        function displaySongs(songs) {
            songList.innerHTML = ''; // Clear previous results
            if (!songs || songs.length === 0) {
                songList.innerHTML = '<p class="text-center text-gray-500 col-span-full">No recommendations found.</p>';
                return;
            }

            songs.forEach(song => {
                const songCard = document.createElement('div');
                songCard.className = 'song-card bg-white p-6 rounded-lg shadow-md border border-gray-200';
                
                const cardContent = `
                    <div class="flex items-center space-x-4">
                        <div class="flex-shrink-0">
                            <svg class="w-8 h-8 text-sky-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2z"></path></svg>
                        </div>
                        <div>
                            <h3 class="text-xl font-semibold text-gray-800">${song.title}</h3>
                            <p class="text-md text-gray-600">${song.artist}</p>
                        </div>
                    </div>
                `;
                
                songCard.innerHTML = cardContent;
                songList.appendChild(songCard);
            });
        }
    </script>
</body>
</html>
{{< /rawhtml >}} 