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

// Canvas Elements
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Button Elements
const dealButton = document.getElementById('deal-btn');
const hitButton = document.getElementById('hit-btn');
const standButton = document.getElementById('stand-btn');
const doubleDownButton = document.getElementById('double-down-btn');
const splitButton = document.getElementById('split-btn');

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
    }
};

// Load saved state
async function loadGameState() {
    playerMoney = await storage.loadMoney();
    highScore = await storage.loadHighScore();
    drawGame(); // Make sure to draw the game after loading state
}

// Save game state
async function saveGameState() {
    await storage.saveMoney(playerMoney);
    if (playerMoney > highScore) {
        highScore = playerMoney;
        await storage.saveHighScore(highScore);
    }
    drawGame(); // Make sure to draw the game after saving state
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
    playerMoney += currentBet * 2; // Regular win pays 1:1
    saveGameState();
    checkGameOver();
}

function blackjackWin(handIndex = 0) {
    playerMoney += currentBet * 2.5; // Blackjack pays 3:2
    saveGameState();
    checkGameOver();
}

function pushBet(handIndex = 0) {
    playerMoney += currentBet; // Push returns the bet
    saveGameState();
    checkGameOver();
}

function doubleDownBet() {
    if (playerMoney >= currentBet) {
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
        
        if (card1.rank === card2.rank) {
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

    for (const card of hand) {
        score += card.value;
        if (card.rank === 'A') {
            numAces++;
        }
    }

    while (score > 21 && numAces > 0) {
        score -= 10;
        numAces--;
    }
    return score;
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

    // Deal initial cards
    playerHands[0].push(dealCard());
    dealerHand.push(dealCard());
    playerHands[0].push(dealCard());
    dealerHand.push(dealCard());

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

    drawGame();
}

function hit() {
    if (!gameInProgress) return;

    playerHands[activeHandIndex].push(dealCard());
    playerScores[activeHandIndex] = calculateScore(playerHands[activeHandIndex]);
    canDoubleDown = false;
    canSplit = false;

    if (playerScores[activeHandIndex] > 21) {
        if (activeHandIndex < playerHands.length - 1) {
            // Move to next hand if there is one
            activeHandIndex++;
            updateButtonStates();
        } else {
            // All hands are done, dealer's turn
            dealerPlay();
        }
    }

    drawGame();
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

function doubleDown() {
    if (!gameInProgress || !canDoubleDown) return;

    if (doubleDownBet()) {
        playerHands[activeHandIndex].push(dealCard());
        playerScores[activeHandIndex] = calculateScore(playerHands[activeHandIndex]);
        canDoubleDown = false;
        canSplit = false;

        if (activeHandIndex < playerHands.length - 1) {
            activeHandIndex++;
            updateButtonStates();
        } else {
            dealerPlay();
        }
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
    dealerSecondCardRevealed = true;
    gameMessage = "Dealer's turn...";

    while (dealerScore < 17) {
        dealerHand.push(dealCard());
        dealerScore = calculateScore(dealerHand);
    }

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
            gameMessage = "Dealer wins!";
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

function endGame() {
    gameInProgress = false;
    dealerSecondCardRevealed = true;
    dealButton.disabled = false;
    hitButton.disabled = true;
    standButton.disabled = true;
    doubleDownButton.disabled = true;
    splitButton.disabled = true;
    currentBet = 0;
}

function updateButtonStates() {
    const currentHand = playerHands[activeHandIndex];
    const currentScore = playerScores[activeHandIndex];
    
    dealButton.disabled = gameInProgress;
    hitButton.disabled = !gameInProgress || currentScore >= 21;
    standButton.disabled = !gameInProgress || currentScore >= 21;
    
    // Double down only available on first two cards and when you have enough money
    doubleDownButton.disabled = !gameInProgress || !canDoubleDown || 
                               currentHand.length !== 2 || 
                               currentScore >= 21 ||
                               playerMoney < currentBet;
    
    // Split only available on first two cards of same rank and when you have enough money
    splitButton.disabled = !gameInProgress || !canSplit || 
                          currentHand.length !== 2 || 
                          currentHand[0].rank !== currentHand[1].rank ||
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
        
        // Draw rank and suit
        ctx.font = 'bold 20px Arial';
        ctx.fillText(card.rank, x + 5, y + 25);
        
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
        
        // Draw score
        ctx.fillStyle = isActiveHand ? '#FFD700' : '#fff';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(`Hand ${handIndex + 1}: ${playerScores[handIndex]}`, 20, handY - 20);
    });
    
    // Draw dealer score
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'left';
    ctx.fillText(`Dealer: ${dealerSecondCardRevealed ? dealerScore : '?'}`, 20, DEALER_HAND_Y - 20);
    
    // Draw money and high score
    ctx.textAlign = 'right';
    ctx.fillText(`Money: $${playerMoney}`, canvas.width - 20, 30);
    ctx.fillText(`High Score: $${highScore}`, canvas.width - 20, 60);
    if (currentBet > 0) {
        ctx.fillText(`Current Bet: $${currentBet}`, canvas.width - 20, 90);
    }
    
    // Draw game message
    ctx.textAlign = 'center';
    ctx.fillText(gameMessage, canvas.width/2, canvas.height/2);
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
    
    const betAmounts = [10, 25, 50, 100];
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