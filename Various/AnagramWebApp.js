
    const options = { month: 'long', day: 'numeric', year: 'numeric' };
    document.getElementById("date").innerHTML = new Date(document.lastModified).toLocaleDateString('en-US', options);

    let scrabbleDictionary = [];

    // Load the dictionary from the file
    fetch('./ScrabbleDictionary.txt')
        .then(response => response.text())
        .then(text => {
            scrabbleDictionary = text.split('\n').map(word => word.trim().toUpperCase());
        })
        .catch(error => console.error('Error loading dictionary:', error));

    function printAllAnagrams() {
        const userLetters = document.getElementById('userLetters').value.toUpperCase();
        const anagrams = findAnagrams(userLetters, scrabbleDictionary);
        displayAnagrams(anagrams);
    }

    function findAnagrams(letters, dictionary) {
        const validAnagrams = [];
        const letterCount = countLetters(letters);

        for (const word of dictionary) {
            if (canCreateWord(word, letterCount)) {
                validAnagrams.push(word);
            }
        }

        return validAnagrams;
    }

    function countLetters(letters) {
        const letterCount = {};
        for (const letter of letters) {
            letterCount[letter] = (letterCount[letter] || 0) + 1;
        }
        return letterCount;
    }

    function canCreateWord(word, letterCount) {
        let wordPattern = word.replace(/\?/g, '.');
        const wordRegex = new RegExp('^' + wordPattern + '$', 'i');

        if (!wordRegex.test(Object.keys(letterCount).join(''))) {
            return false;
        }

        for (const letter in letterCount) {
            if (!word.includes(letter)) {
                return false;
            }
        }

        return true;
    }

    function displayAnagrams(anagrams) {
        const outputElement = document.getElementById('anagramsOutput');

        if (!anagrams || anagrams.length === 0) {
            outputElement.textContent = 'No valid words found';
            return;
        }

        const anagramsByLength = {};
        for (const word of anagrams) {
            if (word.length > 0) {
                const length = word.length;
                anagramsByLength[length] = anagramsByLength[length] || [];
                anagramsByLength[length].push(word);
            }
        }
        outputElement.innerHTML = '';

        const lengths = Object.keys(anagramsByLength).map(Number).sort((a, b) => b - a);

        for (const length of lengths) {
            const words = anagramsByLength[length];
            outputElement.innerHTML += `<p>Words with length ${length}: ${words.join(', ')}</p>`;
        }
    }
