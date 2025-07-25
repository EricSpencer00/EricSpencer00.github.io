// Game State Variables
let deck = [];
let playerHands = [[]]; // Array of hands for splitting
let dealerHand = [];
let playerScores = [0];
let dealerScore = 0;
let gameInProgress = false;
let dealerSecondCardRevealed = false;
let playerMoney = 1000; // Starting money
let currentBet = 0;
let highScore = 0;
let activeHandIndex = 0; // Track which hand is currently being played
let canDoubleDown = true; // Track if double down is available
let canSplit = true; // Track if split is available
let allTimeHighScore = 0;

// Animation variables
let animationInProgress = false;
const ANIMATION_DURATION = 300; // milliseconds
let animationStartTime = 0;
let animationCards = [];
let animationTargets = [];
let dealerAnimationStep = 0;
let isFlippingCard = false;
let flipCardIndex = -1;
let dealerCardsToDeal = 0;
let pendingCardReveals = [];

// Money animation variables
let moneyAnimations = [];
const MONEY_ANIMATION_DURATION = 1000; // milliseconds

// Canvas Elements
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Button Elements
const dealButton = document.getElementById('deal-btn');
const hitButton = document.getElementById('hit-btn');
const standButton = document.getElementById('stand-btn');
const doubleDownButton = document.getElementById('double-down-btn');
const splitButton = document.getElementById('split-btn');

// Add hash-based verification key generation function
function generateVerificationKey(score) {
    // Simple hash function - you could make this more complex
    const data = `blackjack-score-${score}-${Date.now()}`;
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
        const char = data.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32-bit integer
    }
    
    const hashPart = Math.abs(hash).toString(16).padStart(16, '0');
    const timestampPart = Date.now().toString(16).padStart(16, '0');
    const scorePart = score.toString(16).padStart(16, '0');
    const paddingPart = '0000000000000000'.substring(0, 16);
    
    return hashPart + timestampPart + scorePart + paddingPart;
}

// Create and show the high score modal
function showHighScoreModal(score, verificationKey) {
    // Capture parameters to prevent any race conditions
    const capturedScore = score;
    const capturedKey = verificationKey;
    
    // Remove existing modal if present
    const existing = document.getElementById('highscore-modal');
    if (existing) existing.remove();

    // Create modal elements
    const modal = document.createElement('div');
    modal.id = 'highscore-modal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.background = 'rgba(0,0,0,0.7)';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = '9999';

    const box = document.createElement('div');
    box.style.background = '#fff';
    box.style.padding = '2rem';
    box.style.borderRadius = '12px';
    box.style.boxShadow = '0 4px 32px rgba(0,0,0,0.2)';
    box.style.maxWidth = '400px';
    box.style.width = '100%';
    box.style.textAlign = 'center';

    const title = document.createElement('h2');
    title.textContent = '🎉 New All-Time High Score!';
    title.style.marginBottom = '1rem';
    box.appendChild(title);

    const scoreText = document.createElement('div');
    scoreText.textContent = `Score: $${capturedScore}`;
    scoreText.style.fontWeight = 'bold';
    scoreText.style.marginBottom = '1rem';
    box.appendChild(scoreText);

    const label = document.createElement('label');
    label.textContent = 'Enter your username (3-16 letters, numbers, or _):';
    label.style.display = 'block';
    label.style.marginBottom = '0.5rem';
    label.style.textAlign = 'left';
    box.appendChild(label);

    const input = document.createElement('input');
    input.type = 'text';
    input.maxLength = 16;
    input.style.width = '100%';
    input.style.padding = '0.5rem';
    input.style.marginBottom = '1rem';
    input.style.border = '1px solid #ccc';
    input.style.borderRadius = '6px';
    input.placeholder = 'Your username';
    box.appendChild(input);

    const keyLabel = document.createElement('div');
    keyLabel.textContent = 'Verification Key:';
    keyLabel.style.fontWeight = 'bold';
    keyLabel.style.marginBottom = '0.25rem';
    keyLabel.style.textAlign = 'left';
    box.appendChild(keyLabel);

    const keyBox = document.createElement('div');
    keyBox.textContent = capturedKey;
    keyBox.style.fontFamily = 'monospace';
    keyBox.style.background = '#f4f4f4';
    keyBox.style.padding = '0.5rem';
    keyBox.style.borderRadius = '6px';
    keyBox.style.marginBottom = '1rem';
    keyBox.style.wordBreak = 'break-all';
    box.appendChild(keyBox);

    const errorMsg = document.createElement('div');
    errorMsg.style.color = 'red';
    errorMsg.style.marginBottom = '1rem';
    errorMsg.style.display = 'none';
    box.appendChild(errorMsg);

    const submitBtn = document.createElement('button');
    submitBtn.textContent = 'Submit High Score';
    submitBtn.style.background = '#2563eb';
    submitBtn.style.color = '#fff';
    submitBtn.style.padding = '0.75rem 1.5rem';
    submitBtn.style.border = 'none';
    submitBtn.style.borderRadius = '6px';
    submitBtn.style.fontWeight = 'bold';
    submitBtn.style.cursor = 'pointer';
    submitBtn.style.fontSize = '1rem';
    submitBtn.style.marginBottom = '0.5rem';
    box.appendChild(submitBtn);

    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.style.background = '#eee';
    cancelBtn.style.color = '#333';
    cancelBtn.style.padding = '0.5rem 1rem';
    cancelBtn.style.border = 'none';
    cancelBtn.style.borderRadius = '6px';
    cancelBtn.style.marginLeft = '1rem';
    cancelBtn.style.cursor = 'pointer';
    box.appendChild(cancelBtn);

    modal.appendChild(box);
    document.body.appendChild(modal);

    cancelBtn.onclick = () => {
        modal.remove();
    };

    submitBtn.onclick = () => {
        const username = input.value.replace(/[^a-zA-Z0-9_]/g, '').substring(0, 16);
        if (username.length < 3) {
            errorMsg.textContent = 'Username must be at least 3 characters and contain only letters, numbers, and underscores.';
            errorMsg.style.display = 'block';
            return;
        }
        errorMsg.style.display = 'none';
        
        // Prefill GitHub issue
        const issueTitle = encodeURIComponent('New Blackjack High Score Submission');
        const issueBody = encodeURIComponent(
            `## New Blackjack High Score\n\n` +
            `**Username:** ${username}\n` +
            `**Score:** $${capturedScore}\n` +
            `**Verification Key:** ${capturedKey}\n\n` +
            `---\n` +
            `This issue will be automatically processed and merged if the verification key is valid.`
        );
        
        const issueUrl = `https://github.com/EricSpencer00/EricSpencer00.github.io/issues/new?title=${issueTitle}&body=${issueBody}`;
        window.open(issueUrl, '_blank');
        modal.remove();
        alert('High score submission page opened! Please submit the issue to complete your high score submission.');
    };
}

// Storage interface
const storage = {
    async loadHighScore() {
        const savedHighScore = localStorage.getItem('blackjackHighScore');
        return savedHighScore ? parseInt(savedHighScore) : 0;
    },

    async saveHighScore(score) {
        localStorage.setItem('blackjackHighScore', score.toString());
    },

    async loadMoney() {
        const savedMoney = localStorage.getItem('blackjackMoney');
        return savedMoney ? parseInt(savedMoney) : 1000;
    },

    async saveMoney(amount) {
        localStorage.setItem('blackjackMoney', amount.toString());
    },

    async loadAllTimeHighScore() {
        try {
            const response = await fetch('https://raw.githubusercontent.com/EricSpencer00/EricSpencer00.github.io/main/static/data/blackjack_highscore.json');
            const data = await response.json();
            return data.score || 0; // Updated to use new structure
        } catch (error) {
            console.error('Error loading all-time high score:', error);
            return 0; // Default to 0 if there's an error
        }
    },

    async notifyAllTimeHighScore(score) {
        // Capture the score immediately to prevent any race conditions
        const capturedScore = score;
        
        // Generate verification key
        const verificationKey = generateVerificationKey(capturedScore);
        showHighScoreModal(capturedScore, verificationKey);
    }
};

// Load saved state
async function loadGameState() {
    playerMoney = await storage.loadMoney();
    highScore = await storage.loadHighScore();
    allTimeHighScore = await storage.loadAllTimeHighScore();
    drawGame(); // Make sure to draw the game after loading state
}

// Save game state
async function saveGameState() {
    await storage.saveMoney(playerMoney);
    if (playerMoney > highScore) {
        highScore = playerMoney;
        await storage.saveHighScore(highScore);
        
        // Ensure allTimeHighScore is up to date before checking
        const currentAllTimeHighScore = await storage.loadAllTimeHighScore();
        
        // Check for all-time high score
        if (playerMoney > currentAllTimeHighScore) {
            allTimeHighScore = playerMoney;
            await storage.notifyAllTimeHighScore(playerMoney);
        }
    }
    drawGame();
}

// Card Data
const suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades'];
const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];

// Card Dimensions and Layout
const CARD_WIDTH = 80;
const CARD_HEIGHT = 110;
const CARD_SPACING = 20;
const PLAYER_HAND_Y = canvas.height * 0.65;
const DEALER_HAND_Y = canvas.height * 0.15;
const HAND_SPACING = 150; // Space between split hands

// Text display
let gameMessage = 'Click "Deal New Hand" to start!';

// Betting functions
function placeBet(amount) {
    if (!gameInProgress && amount <= playerMoney) {
        addMoneyAnimation(
            amount,
            canvas.width - 20,
            30,
            canvas.width/2,
            canvas.height/2,
            '#ff0000'
        );
        currentBet = amount;
        playerMoney -= amount;
        saveGameState();
        return true;
    }
    return false;
}

function checkGameOver() {
    if (playerMoney <= 0) {
        gameMessage = "Game Over! Starting new game with $1000";
        playerMoney = 1000;
        currentBet = 0;
        saveGameState();
        return true;
    }
    return false;
}

function winBet(handIndex = 0) {
    const winAmount = currentBet * 2;
    const handY = PLAYER_HAND_Y + (handIndex * HAND_SPACING);
    addMoneyAnimation(
        winAmount,
        canvas.width/2,
        canvas.height/2,
        canvas.width - 20,
        30,
        '#00ff00'
    );
    playerMoney += winAmount;
    saveGameState();
    checkGameOver();
}

function blackjackWin(handIndex = 0) {
    const winAmount = currentBet * 2.5;
    const handY = PLAYER_HAND_Y + (handIndex * HAND_SPACING);
    addMoneyAnimation(
        winAmount,
        canvas.width/2,
        canvas.height/2,
        canvas.width - 20,
        30,
        '#00ff00'
    );
    playerMoney += winAmount;
    saveGameState();
    checkGameOver();
}

function pushBet(handIndex = 0) {
    addMoneyAnimation(
        currentBet,
        canvas.width/2,
        canvas.height/2,
        canvas.width - 20,
        30,
        '#ffff00'
    );
    playerMoney += currentBet;
    saveGameState();
    checkGameOver();
}

function doubleDown() {
    if (!gameInProgress || !canDoubleDown) return;

    if (doubleDownBet()) {
        const targetX = canvas.width/2 - (playerHands[activeHandIndex].length * (CARD_WIDTH + CARD_SPACING))/2 + 
                       playerHands[activeHandIndex].length * (CARD_WIDTH + CARD_SPACING);
        const targetY = PLAYER_HAND_Y + (activeHandIndex * HAND_SPACING);
        
        // Deal new card with animation
        const newCard = dealCardWithAnimation(targetX, targetY);
        playerHands[activeHandIndex].push(newCard);
        playerScores[activeHandIndex] = calculateScore(playerHands[activeHandIndex]);
        canDoubleDown = false;
        canSplit = false;

        // Update UI immediately
        drawGame();

        // Wait for animation to complete before moving to next hand or dealer
        setTimeout(() => {
            if (activeHandIndex < playerHands.length - 1) {
                activeHandIndex++;
                updateButtonStates();
            } else {
                dealerPlay();
            }
            drawGame();
        }, ANIMATION_DURATION + 100);
    }
}

function doubleDownBet() {
    if (playerMoney >= currentBet) {
        addMoneyAnimation(
            currentBet,
            canvas.width - 20,
            30,
            canvas.width/2,
            canvas.height/2,
            '#ff0000'
        );
        playerMoney -= currentBet;
        currentBet *= 2;
        saveGameState();
        return true;
    }
    return false;
}

function splitHand() {
    if (playerMoney >= currentBet && playerHands[activeHandIndex].length === 2) {
        const card1 = playerHands[activeHandIndex][0];
        const card2 = playerHands[activeHandIndex][1];
        
        // Check if cards have the same value (allowing 10, J, Q, K to be split)
        if (card1.value === card2.value) {
            playerMoney -= currentBet;
            playerHands[activeHandIndex] = [card1];
            playerHands.push([card2]);
            playerScores.push(0);
            
            // Deal one card to each split hand
            playerHands[activeHandIndex].push(dealCard());
            playerHands[playerHands.length - 1].push(dealCard());
            
            // Update scores
            playerScores[activeHandIndex] = calculateScore(playerHands[activeHandIndex]);
            playerScores[playerHands.length - 1] = calculateScore(playerHands[playerHands.length - 1]);
            
            saveGameState();
            return true;
        }
    }
    return false;
}

function createDeck() {
    deck = [];
    for (const suit of suits) {
        for (const rank of ranks) {
            let value;
            if (['J', 'Q', 'K'].includes(rank)) {
                value = 10;
            } else if (rank === 'A') {
                value = 11;
            } else {
                value = parseInt(rank);
            }
            deck.push({ suit, rank, value });
        }
    }
}

function shuffleDeck() {
    for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
    }
}

function dealCard() {
    return deck.pop();
}

function calculateScore(hand) {
    let score = 0;
    let numAces = 0;

    // First pass: count aces and add up non-ace cards
    for (const card of hand) {
        if (card.rank === 'A') {
            numAces++;
        } else {
            score += card.value;
        }
    }

    // Second pass: add aces, trying to maximize score without busting
    for (let i = 0; i < numAces; i++) {
        // If adding 11 would keep us under 21, do it
        if (score + 11 <= 21) {
            score += 11;
        } else {
            // Otherwise add 1
            score += 1;
        }
    }

    return score;
}

function animateCards(timestamp) {
    if (!animationStartTime) animationStartTime = timestamp;
    const progress = Math.min((timestamp - animationStartTime) / ANIMATION_DURATION, 1);
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw dealer's hand
    dealerHand.forEach((card, index) => {
        const x = canvas.width/2 - (dealerHand.length * (CARD_WIDTH + CARD_SPACING))/2 + index * (CARD_WIDTH + CARD_SPACING);
        if (isFlippingCard && index === flipCardIndex) {
            // Draw flipping card
            const centerX = x + CARD_WIDTH / 2;
            const scale = Math.abs(Math.cos(progress * Math.PI));
            ctx.save();
            ctx.translate(centerX, DEALER_HAND_Y);
            ctx.scale(scale, 1);
            ctx.translate(-centerX, -DEALER_HAND_Y);
            drawCard(card, x, DEALER_HAND_Y, progress > 0.5);
            ctx.restore();
        } else {
            // Only show first dealer card face up, second card stays face down until revealed
            const isCardVisible = index === 0 || dealerSecondCardRevealed;
            drawCard(card, x, DEALER_HAND_Y, isCardVisible);
        }
    });
    
    // Draw all player hands
    playerHands.forEach((hand, handIndex) => {
        const handY = PLAYER_HAND_Y + (handIndex * HAND_SPACING);
        const isActiveHand = handIndex === activeHandIndex;
        
        hand.forEach((card, index) => {
            const x = canvas.width/2 - (hand.length * (CARD_WIDTH + CARD_SPACING))/2 + index * (CARD_WIDTH + CARD_SPACING);
            // Player cards are always face up after being dealt
            drawCard(card, x, handY, true);
        });
        
        // Draw score
        ctx.fillStyle = isActiveHand ? '#FFD700' : '#fff';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(`Hand ${handIndex + 1}: ${playerScores[handIndex]}`, 20, handY - 20);
    });
    
    // Draw animated cards (always face down during movement)
    animationCards.forEach((card, index) => {
        const startX = canvas.width / 2;
        const startY = canvas.height / 2;
        const target = animationTargets[index];
        
        const currentX = startX + (target.x - startX) * progress;
        const currentY = startY + (target.y - startY) * progress;
        
        // Always show card back during movement
        drawCard(card, currentX, currentY, false);
    });
    
    // Draw UI elements
    drawUI();
    
    if (progress < 1) {
        requestAnimationFrame(animateCards);
    } else {
        animationInProgress = false;
        animationStartTime = 0;
        animationCards = [];
        animationTargets = [];
        
        if (isFlippingCard) {
            isFlippingCard = false;
            flipCardIndex = -1;
            dealerSecondCardRevealed = true;
            setTimeout(() => processNextDealerAction(), 500);
        } else if (pendingCardReveals.length > 0) {
            // Process any pending card reveals
            const reveal = pendingCardReveals.shift();
            if (reveal.type === 'dealer') {
                isFlippingCard = true;
                flipCardIndex = reveal.cardIndex;
                animationStartTime = 0;
                requestAnimationFrame(animateCards);
            }
        } else {
            drawGame();
        }
    }
}

function flipDealerCard() {
    isFlippingCard = true;
    flipCardIndex = 1; // Index of the hidden card
    animationStartTime = 0;
    requestAnimationFrame(animateCards);
}

function processNextDealerAction() {
    if (dealerAnimationStep === 0) {
        // Start card flip animation
        flipDealerCard();
        dealerAnimationStep++;
    } else if (dealerAnimationStep === 1) {
        // Deal new cards if needed
        if (dealerScore < 17) {
            const targetX = canvas.width/2 - (dealerHand.length * (CARD_WIDTH + CARD_SPACING))/2 + 
                          dealerHand.length * (CARD_WIDTH + CARD_SPACING);
            const newCard = dealCardWithAnimation(targetX, DEALER_HAND_Y, true, dealerHand.length);
            dealerHand.push(newCard);
            dealerScore = calculateScore(dealerHand);
            dealerCardsToDeal--;
            drawGame();
            
            // If dealer still needs cards, continue the sequence
            if (dealerScore < 17) {
                setTimeout(() => processNextDealerAction(), 1000);
            } else {
                setTimeout(() => evaluateHands(), 1000);
            }
        } else {
            // No more cards needed, evaluate hands
            evaluateHands();
        }
    }
}

function dealCardWithAnimation(targetX, targetY, isDealerCard = false, cardIndex = -1) {
    const card = dealCard();
    
    // Only add to animation if we're not in the middle of a game
    if (!gameInProgress || animationCards.length > 0) {
        animationCards.push(card);
        animationTargets.push({ x: targetX, y: targetY });
        
        if (!animationInProgress) {
            animationInProgress = true;
            requestAnimationFrame(animateCards);
        }
    } else {
        // If we're in the middle of a game, just place the card directly
        drawCard(card, targetX, targetY, !isDealerCard || cardIndex === 0);
    }
    
    // If this is a dealer card, add it to pending reveals
    if (isDealerCard && cardIndex >= 0) {
        pendingCardReveals.push({
            type: 'dealer',
            cardIndex: cardIndex
        });
    }
    
    return card;
}

function newGame() {
    if (currentBet === 0) {
        gameMessage = "Please place a bet first!";
        drawGame();
        return;
    }

    createDeck();
    shuffleDeck();
    playerHands = [[]];
    dealerHand = [];
    playerScores = [0];
    dealerScore = 0;
    gameInProgress = true;
    dealerSecondCardRevealed = false;
    activeHandIndex = 0;
    canDoubleDown = true;
    canSplit = true;
    gameMessage = 'Dealing cards...';

    // Deal initial cards with animation
    // First card to player
    const playerCard1 = dealCardWithAnimation(
        canvas.width/2 - CARD_WIDTH - CARD_SPACING/2,
        PLAYER_HAND_Y
    );
    
    // First card to dealer
    const dealerCard1 = dealCardWithAnimation(
        canvas.width/2 - CARD_WIDTH - CARD_SPACING/2,
        DEALER_HAND_Y
    );
    
    // Second card to player
    const playerCard2 = dealCardWithAnimation(
        canvas.width/2 + CARD_SPACING/2,
        PLAYER_HAND_Y
    );
    
    // Second card to dealer (face down)
    const dealerCard2 = dealCardWithAnimation(
        canvas.width/2 + CARD_SPACING/2,
        DEALER_HAND_Y,
        true,
        1
    );

    playerHands[0] = [playerCard1, playerCard2];
    dealerHand = [dealerCard1, dealerCard2];

    playerScores[0] = calculateScore(playerHands[0]);
    dealerScore = calculateScore(dealerHand);

    // Update button states
    updateButtonStates();

    // Check for blackjack
    if (playerScores[0] === 21) {
        if (dealerScore === 21) {
            gameMessage = "Push! Both players have Blackjack!";
            pushBet();
        } else {
            gameMessage = "Blackjack! You win!";
            blackjackWin();
        }
        endGame();
    }
}

function hit() {
    if (!gameInProgress) return;

    const targetX = canvas.width/2 - (playerHands[activeHandIndex].length * (CARD_WIDTH + CARD_SPACING))/2 + 
                   playerHands[activeHandIndex].length * (CARD_WIDTH + CARD_SPACING);
    const targetY = PLAYER_HAND_Y + (activeHandIndex * HAND_SPACING);
    
    // Deal new card face down, then flip it
    const newCard = dealCardWithAnimation(targetX, targetY);
    playerHands[activeHandIndex].push(newCard);
    playerScores[activeHandIndex] = calculateScore(playerHands[activeHandIndex]);
    canDoubleDown = false;
    canSplit = false;

    // Update UI immediately after hit
    drawGame();

    if (playerScores[activeHandIndex] > 21) {
        if (activeHandIndex < playerHands.length - 1) {
            // Move to next hand if there is one
            activeHandIndex++;
            updateButtonStates();
        } else {
            // All hands are done, dealer's turn
            dealerPlay();
        }
    } else if (playerScores[activeHandIndex] === 21) {
        // Auto-stand on 21
        stand();
    }
}

function stand() {
    if (!gameInProgress) return;

    if (activeHandIndex < playerHands.length - 1) {
        // Move to next hand
        activeHandIndex++;
        updateButtonStates();
    } else {
        // All hands are done, dealer's turn
        dealerPlay();
    }

    drawGame();
}

function split() {
    if (!gameInProgress || !canSplit) return;

    if (splitHand()) {
        canSplit = false;
        updateButtonStates();
    }

    drawGame();
}

function dealerPlay() {
    dealerAnimationStep = 0;
    gameMessage = "Dealer's turn...";

    // Calculate how many cards the dealer needs to take
    dealerCardsToDeal = 0;
    let tempScore = dealerScore;
    while (tempScore < 17) {
        const newCard = dealCard();
        tempScore += newCard.value > 11 ? 1 : newCard.value;
        dealerCardsToDeal++;
    }
    
    // Start the dealer animation sequence
    processNextDealerAction();
}

function endGame() {
    gameInProgress = false;
    dealerSecondCardRevealed = true;
    hitButton.disabled = true;
    standButton.disabled = true;
    doubleDownButton.disabled = true;
    splitButton.disabled = true;
    currentBet = 0;
}

function updateButtonStates() {
    const currentHand = playerHands[activeHandIndex];
    const currentScore = playerScores[activeHandIndex];
    
    hitButton.disabled = !gameInProgress || currentScore >= 21;
    standButton.disabled = !gameInProgress || currentScore >= 21;
    
    // Double down only available on first two cards and when you have enough money
    doubleDownButton.disabled = !gameInProgress || !canDoubleDown || 
                               currentHand.length !== 2 || 
                               currentScore >= 21 ||
                               playerMoney < currentBet;
    
    // Split available on first two cards of equal value and when you have enough money
    splitButton.disabled = !gameInProgress || !canSplit || 
                          currentHand.length !== 2 || 
                          currentHand[0].value !== currentHand[1].value ||
                          playerMoney < currentBet;
}

function drawCard(card, x, y, faceUp = true) {
    ctx.save();
    
    // Draw card background
    ctx.fillStyle = '#fff';
    ctx.fillRect(x, y, CARD_WIDTH, CARD_HEIGHT);
    
    if (faceUp) {
        // Draw card border
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, CARD_WIDTH, CARD_HEIGHT);
        
        // Set text color based on suit
        ctx.fillStyle = ['Hearts', 'Diamonds'].includes(card.suit) ? '#f00' : '#000';
        
        // Draw rank and suit with adjusted position
        ctx.font = 'bold 20px Arial';
        ctx.fillText(card.rank, x + 9, y + 25); // Added 4px to x position
        
        // Draw suit symbol
        const suitSymbol = {
            'Hearts': '♥',
            'Diamonds': '♦',
            'Clubs': '♣',
            'Spades': '♠'
        }[card.suit];
        
        ctx.font = 'bold 30px Arial';
        ctx.fillText(suitSymbol, x + CARD_WIDTH/2 - 10, y + CARD_HEIGHT/2 + 10);
    } else {
        // Draw card back pattern
        ctx.fillStyle = '#0066cc';
        ctx.fillRect(x + 5, y + 5, CARD_WIDTH - 10, CARD_HEIGHT - 10);
        
        // Draw pattern
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1;
        for (let i = 0; i < 5; i++) {
            ctx.beginPath();
            ctx.moveTo(x + 10, y + 10 + i * 20);
            ctx.lineTo(x + CARD_WIDTH - 10, y + 10 + i * 20);
            ctx.stroke();
        }
    }
    
    ctx.restore();
}

function drawUI() {
    // Draw dealer score
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'left';
    const visibleDealerScore = dealerSecondCardRevealed ? dealerScore : '?';
    ctx.fillText(`Dealer: ${visibleDealerScore}`, 20, DEALER_HAND_Y - 20);
    
    // Draw money and high scores
    ctx.textAlign = 'right';
    ctx.fillText(`Money: $${playerMoney}`, canvas.width - 20, 30);
    ctx.fillText(`Session High: $${highScore}`, canvas.width - 20, 60);
    ctx.fillText(`All-Time High: $${allTimeHighScore}`, canvas.width - 20, 90);
    if (currentBet > 0) {
        ctx.fillText(`Current Bet: $${currentBet}`, canvas.width - 20, 120);
    }
    
    // Draw game message
    ctx.textAlign = 'center';
    ctx.fillText(gameMessage, canvas.width/2, canvas.height/2);
}

function drawGame() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw dealer's hand
    dealerHand.forEach((card, index) => {
        const x = canvas.width/2 - (dealerHand.length * (CARD_WIDTH + CARD_SPACING))/2 + index * (CARD_WIDTH + CARD_SPACING);
        drawCard(card, x, DEALER_HAND_Y, index === 0 || dealerSecondCardRevealed);
    });
    
    // Draw all player hands
    playerHands.forEach((hand, handIndex) => {
        const handY = PLAYER_HAND_Y + (handIndex * HAND_SPACING);
        const isActiveHand = handIndex === activeHandIndex;
        
        // Draw cards
        hand.forEach((card, index) => {
            const x = canvas.width/2 - (hand.length * (CARD_WIDTH + CARD_SPACING))/2 + index * (CARD_WIDTH + CARD_SPACING);
            drawCard(card, x, handY, true);
        });
        
        // Draw score with updated position
        ctx.fillStyle = isActiveHand ? '#FFD700' : '#fff';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'left';
        const scoreText = `Hand ${handIndex + 1}: ${playerScores[handIndex]}`;
        ctx.fillText(scoreText, 20, handY - 20);
    });
    
    // Draw UI elements
    drawUI();
}

function evaluateHands() {
    // Check each player hand against dealer
    for (let i = 0; i < playerHands.length; i++) {
        if (playerScores[i] > 21) {
            // Hand already busted
            continue;
        }

        if (dealerScore > 21) {
            gameMessage = "Dealer busts! You win!";
            winBet(i);
        } else if (dealerScore > playerScores[i]) {
            gameMessage = "You lose!";
        } else if (dealerScore < playerScores[i]) {
            gameMessage = "You win!";
            winBet(i);
        } else {
            gameMessage = "Push! It's a tie!";
            pushBet(i);
        }
    }

    endGame();
    drawGame();
}

// Event Listeners
dealButton.addEventListener('click', newGame);
hitButton.addEventListener('click', hit);
standButton.addEventListener('click', stand);
doubleDownButton.addEventListener('click', doubleDown);
splitButton.addEventListener('click', split);

// Add betting buttons to the controls
function createBettingButtons() {
    const controls = document.querySelector('.controls');
    const betContainer = document.createElement('div');
    betContainer.className = 'bet-controls';
    
    // Add reset button
    const resetButton = document.createElement('button');
    resetButton.textContent = 'Reset Game';
    resetButton.className = 'reset-btn';
    resetButton.onclick = resetGame;
    betContainer.appendChild(resetButton);
    
    const betAmounts = [100, 500, 1000];
    betAmounts.forEach(amount => {
        const button = document.createElement('button');
        button.textContent = `Bet $${amount}`;
        button.className = 'bet-btn';
        button.onclick = () => {
            if (placeBet(amount)) {
                newGame();
            } else {
                gameMessage = "Cannot place bet!";
                drawGame();
            }
        };
        betContainer.appendChild(button);
    });
    
    controls.insertBefore(betContainer, controls.firstChild);
}

// Initialize game
loadGameState().then(() => {
    createBettingButtons();
    drawGame();
});

function resetGame() {
    // Only reset money, preserve high scores
    localStorage.removeItem('blackjackMoney');
    
    // Reset game state
    playerMoney = 1000;
    currentBet = 0;
    gameInProgress = false;
    gameMessage = "Game Reset! Place your bet to start!";
    
    // Update UI
    drawGame();
}

function animateMoney(timestamp) {
    if (!animationStartTime) animationStartTime = timestamp;
    const progress = Math.min((timestamp - animationStartTime) / MONEY_ANIMATION_DURATION, 1);
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw the game state
    drawGame();
    
    // Draw money animations
    moneyAnimations.forEach((anim, index) => {
        const currentX = anim.startX + (anim.endX - anim.startX) * progress;
        const currentY = anim.startY + (anim.endY - anim.startY) * progress;
        
        // Draw money denomination
        ctx.save();
        ctx.fillStyle = anim.color;
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(anim.amount, currentX, currentY);
        ctx.restore();
    });
    
    if (progress < 1) {
        requestAnimationFrame(animateMoney);
    } else {
        animationStartTime = 0;
        moneyAnimations = [];
        drawGame();
    }
}

function addMoneyAnimation(amount, startX, startY, endX, endY, color = '#00ff00') {
    moneyAnimations.push({
        amount: `$${amount}`,
        startX,
        startY,
        endX,
        endY,
        color
    });
    
    if (!animationInProgress) {
        animationInProgress = true;
        animationStartTime = 0;
        requestAnimationFrame(animateMoney);
    }
}

// Remove deal button event listener and references
dealButton.removeEventListener('click', newGame);
dealButton.style.display = 'none'; // Hide the button

// Update button states function to remove deal button references
function updateButtonStates() {
    const currentHand = playerHands[activeHandIndex];
    const currentScore = playerScores[activeHandIndex];
    
    hitButton.disabled = !gameInProgress || currentScore >= 21;
    standButton.disabled = !gameInProgress || currentScore >= 21;
    
    // Double down only available on first two cards and when you have enough money
    doubleDownButton.disabled = !gameInProgress || !canDoubleDown || 
                               currentHand.length !== 2 || 
                               currentScore >= 21 ||
                               playerMoney < currentBet;
    
    // Split available on first two cards of equal value and when you have enough money
    splitButton.disabled = !gameInProgress || !canSplit || 
                          currentHand.length !== 2 || 
                          currentHand[0].value !== currentHand[1].value ||
                          playerMoney < currentBet;
}

function endGame() {
    gameInProgress = false;
    dealerSecondCardRevealed = true;
    hitButton.disabled = true;
    standButton.disabled = true;
    doubleDownButton.disabled = true;
    splitButton.disabled = true;
    currentBet = 0;
} 