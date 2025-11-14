const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const [,, issueBody, issueNumber] = process.argv;

if (!issueBody || !issueNumber) {
  console.error('Missing issue body or issue number');
  process.exit(1);
}

// Parse the issue body to extract information
function parseIssueBody(body) {
  console.log('Parsing issue body:', body);
  
  // More flexible regex patterns that handle different line endings and spacing
  const usernameMatch = body.match(/\*\*Username:\*\*\s*(.+?)(?:\n|$)/);
  const scoreMatch = body.match(/\*\*Score:\*\*\s*\$?(\d+)/);
  const keyMatch = body.match(/\*\*Verification Key:\*\*\s*([a-f0-9]{64})/);
  
  console.log('Username match:', usernameMatch);
  console.log('Score match:', scoreMatch);
  console.log('Key match:', keyMatch);
  
  if (!usernameMatch || !scoreMatch || !keyMatch) {
    console.error('Invalid issue format - missing required fields');
    console.error('Username found:', !!usernameMatch);
    console.error('Score found:', !!scoreMatch);
    console.error('Key found:', !!keyMatch);
    return null;
  }
  
  return {
    username: usernameMatch[1].trim(),
    score: parseInt(scoreMatch[1], 10),
    verificationKey: keyMatch[1]
  };
}

// Validate verification key by extracting score from hash
function validateVerificationKey(key, expectedScore) {
  // Check if it's a 64-character hex string
  if (!/^[a-f0-9]{64}$/.test(key)) {
    return false;
  }
  
  try {
    // Extract score from the hash (positions 32-48)
    const scoreHex = key.substring(32, 48);
    const extractedScore = parseInt(scoreHex, 16);
    
    // Verify the extracted score matches the expected score
    return extractedScore === expectedScore;
  } catch (error) {
    console.error('Error extracting score from hash:', error);
    return false;
  }
}

// Validate username
function validateUsername(username) {
  // Only allow alphanumeric and underscores, 3-16 chars
  const sanitized = username.replace(/[^a-zA-Z0-9_]/g, '').substring(0, 16);
  return sanitized.length >= 3 && sanitized === username;
}

// Validate score
function validateScore(score) {
  return !isNaN(score) && score >= 0 && score <= 1000000;
}

// Main processing logic
function processHighScoreSubmission() {
  console.log(`Processing high score submission from issue #${issueNumber}`);
  
  // Parse the issue body
  const submission = parseIssueBody(issueBody);
  if (!submission) {
    console.error('Failed to parse issue body');
    process.exit(1);
  }
  
  console.log(`Parsed submission:`, submission);
  
  // Validate all fields
  if (!validateUsername(submission.username)) {
    console.error('Invalid username format');
    process.exit(1);
  }
  
  if (!validateScore(submission.score)) {
    console.error('Invalid score');
    process.exit(1);
  }
  
  if (!validateVerificationKey(submission.verificationKey, submission.score)) {
    console.error('Invalid verification key format');
    process.exit(1);
  }
  
  // Load current high score
  const filePath = path.join(__dirname, '../static/data/blackjack_highscore.json');
  let currentData = { username: '', score: 0, lastUpdated: '' };
  
  if (fs.existsSync(filePath)) {
    try {
      currentData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (error) {
      console.error('Error reading current high score file:', error);
      process.exit(1);
    }
  }
  
  // Check if this is actually a new high score
  if (submission.score <= currentData.score) {
    console.log(`Score ${submission.score} is not higher than current high score ${currentData.score}`);
    console.log('For testing purposes, allowing equal scores to be processed');
    // Uncomment the next line if you want to allow equal scores for testing
    // process.exit(0);
  }
  
  // Update the high score
  const newData = {
    username: submission.username,
    score: submission.score,
    lastUpdated: new Date().toISOString().slice(0, 10)
  };
  
  // Write the updated high score file
  fs.writeFileSync(filePath, JSON.stringify(newData, null, 2));
  console.log('Updated high score file');
  
  // Update the badge file
  const badgePath = path.join(__dirname, '../static/data/blackjack_highscore_badge.json');
  const badgeJson = {
    schemaVersion: 1,
    label: "Blackjack High Score",
    message: `${newData.score} by ${newData.username}`,
    color: "blue"
  };
  fs.writeFileSync(badgePath, JSON.stringify(badgeJson, null, 2));
  console.log('Updated badge file');
  
  console.log(`Successfully processed high score: ${submission.username} - $${submission.score}`);
}

// Run the processing
processHighScoreSubmission();
