const fs = require('fs');
const path = require('path');

const [,, usernameRaw, scoreRaw] = process.argv;

// Sanitize username: only allow alphanumeric and underscores, 3-16 chars
const username = (usernameRaw || '').replace(/[^a-zA-Z0-9_]/g, '').substring(0, 16);
if (username.length < 3) {
  console.error('Invalid username');
  process.exit(1);
}

// Validate score
const score = parseInt(scoreRaw, 10);
if (isNaN(score) || score < 0 || score > 1000000) {
  console.error('Invalid score');
  process.exit(1);
}

const filePath = path.join(__dirname, '../static/data/blackjack_highscore.json');
let data = { username: '', score: 0, lastUpdated: '' };
if (fs.existsSync(filePath)) {
  data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

if (score > data.score) {
  data = { username, score, lastUpdated: new Date().toISOString().slice(0, 10) };
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
  
  // Also update badge JSON for shields.io
  const badgePath = path.join(__dirname, '../static/data/blackjack_highscore_badge.json');
  const badgeJson = {
    schemaVersion: 1,
    label: "Blackjack High Score",
    message: `${data.score} by ${data.username}`,
    color: "blue"
  };
  fs.writeFileSync(badgePath, JSON.stringify(badgeJson, null, 2));
  
  console.log('High score updated!');
} else {
  console.log('Score not high enough to update.');
}
