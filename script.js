function secretFunction() {
    confetti.start();
    setTimeout(function() {
        confetti.stop();
    }, 7000); // 7 seconds
}

function generateHexGrid(width, height) {
    let grid = '';
    for (let h = 0; h < height; h++) {
        let line = '';
        for (let w = 0; w < width; w++) {
            line += (w % 19 === 0 && w !== 0) ? "    " : Math.floor(Math.random() * 256).toString(16).padStart(2, '0').toUpperCase() + " ";
        }
        grid += line.trim() + '\n';
    }
    return grid;
}

function updateBackgroundHex() {
    const hexElement = document.getElementById('hexBackground');
    hexElement.textContent = generateHexGrid(200, 20);
}

// setInterval(updateBackgroundHex, 1000)

function typeText2dArray(asciiArtArray, id, speed) {
    const container = document.getElementById(id);
    container.innerHTML = '';

    // Determine the size of the canvas
    let canvasWidth = 0;
    let canvasHeight = 0;
    asciiArtArray.forEach(letter => {
        canvasWidth += letter[0].length;
        canvasHeight = Math.max(canvasHeight, letter.length);
    });

    // Initialize the canvas with empty spaces
    const canvas = Array(canvasHeight).fill('').map(() => Array(canvasWidth).fill(' '));

    function mergeLetter(letter, startCol) {
        for (let row = 0; row < letter.length; row++) {
            for (let col = 0; col < letter[row].length; col++) {
                const char = letter[row][col];
                if (char !== ' ') {
                    canvas[row][startCol + col] = char;
                }
            }
        }
    }

    function printCanvas() {
        container.innerHTML = canvas.map(row => row.join('')).join('\n');
    }

    let letterIndex = 0;
    let currentCol = 0;
    const totalLetters = asciiArtArray.length;

    function type() {
        if (letterIndex < totalLetters) {
            const letter = asciiArtArray[letterIndex];
            mergeLetter(letter, currentCol);
            currentCol += letter[0].length;

            letterIndex++;
            setTimeout(type, speed);
            printCanvas();
        }
    }

    type();
}

function typeHTML(text, id, speed) {
    const element = document.getElementById(id);
    let index = 0;

    function type() {
        if (index < text.length) {
            // Use innerHTML to correctly interpret HTML tags
            element.innerHTML += text[index];
            index++;
            setTimeout(type, speed);
        }
    }

    type();
}

function typeText(text, id, speed, includeCursor) {
    const container = document.getElementById(id);
    container.innerHTML = '';

    // Pre-allocate lines
    const lines = text.split('\n');
    const numberOfLines = lines.length;

    const measurementSpan = document.createElement('span');
    measurementSpan.style.visibility = 'hidden';
    measurementSpan.style.whiteSpace = 'pre';
    measurementSpan.textContent = 'A';
    container.appendChild(measurementSpan);
    const lineHeight = measurementSpan.offsetHeight;
    container.removeChild(measurementSpan);

    container.style.height = `${numberOfLines * lineHeight}px`;

    let index = 0;
    const startTime = performance.now();

    let cursor;
    if (includeCursor) {
        cursor = document.createElement('span');
        cursor.textContent = '▌';
        cursor.style.animation = 'blink 1s step-end infinite';
        container.appendChild(cursor);
    }

    function type() {
        const currentTime = performance.now();
        const elapsedTime = currentTime - startTime;
        const expectedTime = index * speed;
        const remainingTime = Math.max(0, expectedTime - elapsedTime);

        if (index < text.length) {
            let char = text[index];
            let span = document.createElement('span');
            
            if (char === '\n') {
                container.appendChild(document.createElement('br'));
                index++;
            } else if (char === ' ') {
                let spaceCount = 0;
                while (text[index] === ' ') {
                    spaceCount++;
                    index++;
                }
                span.textContent = ' '.repeat(spaceCount);
                if (includeCursor) {
                    container.insertBefore(span, cursor);
                } else {
                    container.appendChild(span);
                }
            } else {
                span.textContent = char;
                index++;
                if (includeCursor) {
                    container.insertBefore(span, cursor);
                } else {
                    container.appendChild(span);
                }
            }

            setTimeout(type, remainingTime);
        } else if (includeCursor) {
            container.appendChild(cursor); // Make sure the cursor is at the end
        }
    }

    type();
}


// CSS for cursor blinking
const style = document.createElement('style');
style.textContent = `
    @keyframes blink {
        50% { opacity: 0; }
    }
    .cursor {
        display: inline-block;
        white-space: pre;
    }
    span {
        white-space: pre;
    }
`;
document.head.appendChild(style);


function chessStats() { 
    document.addEventListener('DOMContentLoaded', function() {
        const username = 'EricSpencer00';
        const statsDiv = document.getElementById('stats');

        fetch(`https://api.chess.com/pub/player/${username}/stats`)
            .then(response => response.json())
            .then(data => {
                if (data && data.chess_blitz && data.chess_bullet && data.chess_rapid) {
                    const { chess_blitz, chess_bullet, chess_rapid } = data;
                    const statsHTML = `
                        <h2>Chess.com Stats for ${username}</h2>
                        <p><strong>Blitz:</strong> ${chess_blitz.last.rating}</p>
                        <p><strong>Bullet:</strong> ${chess_bullet.last.rating}</p>
                        <p><strong>Rapid:</strong> ${chess_rapid.last.rating}</p>
                    `;
                    statsDiv.innerHTML = statsHTML;
                } else {
                    statsDiv.innerHTML = '<p>Stats not available for the user.</p>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                statsDiv.innerHTML = '<p>There was an error fetching the data. Please try again later.</p>';
            });
    });
}

function getRandomAsciiArt() {
    return asciiNameArray[Math.floor(Math.random() * asciiNameArray.length)];
}

/* Mobile browser width in spaces below, X's inclusive

X                                                                            X

*/



const asciiNameArray = [`
    ______     _         _____                                
   / ____/____(_)____   / ___/____  ___  ____  ________  _____
  / __/ / ___/ / ___/   \\__ \\/ __ \\/ _ \\/ __ \\/ ___/ _ \\/ ___/
 / /___/ /  / / /__    ___/ / /_/ /  __/ / / / /__/  __/ /    
/_____/_/  /_/\\___/   /____/ .___/\\___/_/ /_/\\___/\\___/_/     
                          /_/`,`
 ____  ____  __  ___    ____  ____  ____  __ _   ___  ____  ____ 
(  __)(  _ \\(  )/ __)  / ___)(  _ \\(  __)(  ( \\ / __)(  __)(  _ \\
 ) _)  )   / )(( (__   \\___ \\ ) __/ ) _) /    /( (__  ) _)  )   /
(____)(__\\_)(__)\\___)  (____/(__)  (____)\\_)__) \\___)(____)(__\\_)`,`
______     _        _____                                
|  ___|   (_)      /  ___|                                
| |__ _ __ _  ___  \\ \`--. _ __   ___ _ __   ___ ___ _ __ 
|  __| '__| |/ __|  \`--. \\ '_ \\ / _ \\ '_ \\ / __/ _ \\ '__|
| |__| |  | | (__  /\\__/ / |_) |  __/ | | | (_|  __/ |   
\\____/_|  |_|\\___| \\____/| .__/ \\___|_| |_|\\___\\___|_|   
                         | |                             
                         |_|                             `,`
   ___  ____   ____   __       _____ ____   ___  ____     __    ___  ____  
  /  _]|    \\ |    | /  ]     / ___/|    \\ /  _]|    \\   /  ]  /  _]|    \\ 
 /  [_ |  D  ) |  | /  /     (   \\_ |  o  )  [_ |  _  | /  /  /  [_ |  D  )
|    _]|    /  |  |/  /       \\__  ||   _/    _]|  |  |/  /  |    _]|    / 
|   [_ |    \\  |  /   \\_      /  \\ ||  | |   [_ |  |  /   \\_ |   [_ |    \\ 
|     ||  .  \\ |  \\     |     \\    ||  | |     ||  |  \\     ||     ||  .  \\
|_____||__|\\_||____\\____|      \\___||__| |_____||__|__|\\____||_____||__|\\_|`,`
.----..----. .-. .---.     .----..----. .----..-. .-. .---. .----..----. 
| {_  | {}  }| |/  ___}   { {__  | {}  }| {_  |  \`| |/  ___}| {_  | {}  }
| {__ | .-. \\| |\\     }   .-._} }| .--' | {__ | |\\  |\\     }| {__ | .-. \\
\`----'\`-' \`-'\`-' \`---'    \`----' \`-'    \`----'\`-' \`-' \`---' \`----'\`-' \`-'`,`
   __     _        __                                
  /__\\ __(_) ___  / _\\_ __   ___ _ __   ___ ___ _ __ 
 /_\\| '__| |/ __| \\ \\| '_ \\ / _ \\ '_ \\ / __/ _ \\ '__|
//__| |  | | (__  _\\ \\ |_) |  __/ | | | (_|  __/ |   
\\__/|_|  |_|\\___| \\__/ .__/ \\___|_| |_|\\___\\___|_|   
                     |_|                             `,`
                                          
 _____     _        _____                         
|   __|___|_|___   |   __|___ ___ ___ ___ ___ ___ 
|   __|  _| |  _|  |__   | . | -_|   |  _| -_|  _|
|_____|_| |_|___|  |_____|  _|___|_|_|___|___|_|  
                         |_|                      `,`
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░        ░░       ░░░        ░░░      ░░░░░░░░░░      ░░░
▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒
▓      ▓▓▓▓       ▓▓▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓      ▓▓▓
█  ████████  ███  ██████  █████  ████  ██████████████  ██
█        ██  ████  ██        ███      ██████████      ███
█████████████████████████████████████████████████████████`,`
 ______     ______     __     ______        ______
/\\  ___\\   /\\  == \\   /\\ \\   /\\  ___\\      /\\  ___\\
\\ \\  __\\   \\ \\  __<   \\ \\ \\  \\ \\ \\____     \\ \\___  \\
 \\ \\_____\\  \\ \\_\\ \\_\\  \\ \\_\\  \\ \\_____\\     \\/\\_____\\
  \\/_____/   \\/_/ /_/   \\/_/   \\/_____/      \\/_____/ `,`
                      .-.
  .--.    ___ .-.    ( __)   .--.          .--.
 /    \\  (   )   \\   (''")  /    \\       /  _  \\
|  .-. ;  | ' .-. ;   | |  |  .-. ;     . .' \`. ;
|  | | |  |  / (___)  | |  |  |(___)    | '   | |
|  |/  |  | |         | |  |  |         _\\_\`.(___)
|  ' _.'  | |         | |  |  | ___    (   ). '.
|  .'.-.  | |         | |  |  '(   )    | |  \`\\ |
'  \`-' /  | |         | |  '  \`-' |     ; '._,' '
 \`.__.'  (___)       (___)  \`.__,'       '.___.'   `,`
███████╗██████╗ ██╗ ██████╗    ███████╗ 
██╔════╝██╔══██╗██║██╔════╝    ██╔════╝
█████╗  ██████╔╝██║██║         ███████╗
██╔══╝  ██╔══██╗██║██║         ╚════██║
███████╗██║  ██║██║╚██████╗    ███████║
╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝    ╚══════╝`,`
     _______                            ______    
    //   / /                           //   ) )   
   //____     __     ( )  ___         ((      
  / ____    //  ) ) / / //   ) )        \\\\    
 //        //      / / //                 ) )
//____/ / //      / / ((____       ((___ / /  `,`
.-. .-. .-. .-.   .-. .-. .-. . . .-. .-. .-. 
|-  |(   |  |     \`-. |-' |-  |\\| |   |-  |(  
\`-' ' ' \`-' \`-'   \`-' '   \`-' ' \` \`-' \`-' ' '`,` 
:::::::::: :::::::::  ::::::::::: ::::::::          ::::::::  
:+:        :+:    :+:     :+:    :+:    :+:        :+:    :+:  
+#++:++#   +#++:++#:      +#+    +#+               +#++:++#++    
+#+        +#+    +#+     +#+    +#+                      +#+     
#+#        #+#    #+#     #+#    #+#    #+#        #+#    #+#      
########## ###    ### ########### ########          ########        `,`
_|_|_|_|            _|                  _|_|_|   
_|        _|  _|_|        _|_|_|      _|        
_|_|_|    _|_|      _|  _|              _|_|    
_|        _|        _|  _|                  _|  
_|_|_|_|  _|        _|    _|_|_|      _|_|_|    `,`
8888888888         d8b                .d8888b.  
888                Y8P               d88P  Y88b 
888                                  Y88b.      
8888888    888d888 888  .d8888b       "Y888b.   
888        888P"   888 d88P"             "Y88b. 
888        888     888 888                 "888 
888        888     888 Y88b.         Y88b  d88P 
8888888888 888     888  "Y8888P       "Y8888P"  `,`
____ ____ _ ____    ____ ___  ____ _  _ ____ ____ ____ 
|___ |__/ | |       [__  |__] |___ |\\ | |    |___ |__/ 
|___ |  \\ | |___    ___] |    |___ | \\| |___ |___ |  \\ `,`
69 114 105 99  83 112 101 110 99 101 114
E  r   i   c   S  p   e   n   c  e   r`,`
 ___       _        ___
| __> _ _ <_> ___  / __> ___  ___ ._ _  ___  ___  _ _ 
| _> | '_>| |/ | ' \\__ \\| . \\/ ._>| ' |/ | '/ ._>| '_>
|___>|_|  |_|\\_|_. <___/|  _/\\___.|_|_|\\_|_.\\___.|_|  
                        |_|                           `,`
45 72 69 63  53 70 65 6E 63 65 72
E  r  i  c   S  p  e  n  c  e  r
`,`
  _   ,_   .  __      ,   ,_    _   ,__,   __   _   ,_ 
_(/__/ (__/__(_,_   _/_)__/_)__(/__/ / (__(_,__(/__/ (_
                         /
                        /
                
Eric Spencer`,`
 ___  __     __      __   __   ___       __   ___  __  
|__  |__) | /  \`    /__\` |__) |__  |\\ | /  \` |__  |__) 
|___ |  \\ | \\__,    .__/ |    |___ | \\| \\__, |___ |  \\ `,`

█████████████████████████████████████████████████████████████████████
█▄─▄▄─█▄─▄▄▀█▄─▄█─▄▄▄─███─▄▄▄▄█▄─▄▄─█▄─▄▄─█▄─▀█▄─▄█─▄▄▄─█▄─▄▄─█▄─▄▄▀█
██─▄█▀██─▄─▄██─██─███▀███▄▄▄▄─██─▄▄▄██─▄█▀██─█▄▀─██─███▀██─▄█▀██─▄─▄█
▀▄▄▄▄▄▀▄▄▀▄▄▀▄▄▄▀▄▄▄▄▄▀▀▀▄▄▄▄▄▀▄▄▄▀▀▀▄▄▄▄▄▀▄▄▄▀▀▄▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀`,`

███████╗██████╗░██╗░█████╗░░░░██████╗██████╗░███████╗███╗░░██╗░█████╗░███████╗██████╗░
██╔════╝██╔══██╗██║██╔══██╗░░██╔════╝██╔══██╗██╔════╝████╗░██║██╔══██╗██╔════╝██╔══██╗
█████╗░░██████╔╝██║██║░░╚═╝░░╚█████╗░██████╔╝█████╗░░██╔██╗██║██║░░╚═╝█████╗░░██████╔╝
██╔══╝░░██╔══██╗██║██║░░██╗░░░╚═══██╗██╔═══╝░██╔══╝░░██║╚████║██║░░██╗██╔══╝░░██╔══██╗
███████╗██║░░██║██║╚█████╔╝░░██████╔╝██║░░░░░███████╗██║░╚███║╚█████╔╝███████╗██║░░██║
╚══════╝╚═╝░░╚═╝╚═╝░╚════╝░░░╚═════╝░╚═╝░░░░░╚══════╝╚═╝░░╚══╝░╚════╝░╚══════╝╚═╝░░╚═╝
`,`
    _______  ________   ________  ________      ________  ________  ________  ________  ________  ________  ________ 
  ╱╱       ╲╱        ╲ ╱        ╲╱        ╲    ╱        ╲╱        ╲╱        ╲╱    ╱   ╲╱        ╲╱        ╲╱        ╲
 ╱╱        ╱         ╱_╱       ╱╱         ╱   ╱        _╱         ╱         ╱         ╱         ╱         ╱         ╱
╱        _╱        _╱╱         ╱       --╱   ╱-        ╱       __╱        _╱         ╱       --╱        _╱        _╱ 
╲________╱╲____╱___╱ ╲________╱╲________╱    ╲_______╱╱╲______╱  ╲________╱╲__╱_____╱╲________╱╲________╱╲____╱___╱  
`,`
░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓██████▓▒░        ░▒▓███████▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░        
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░        
░▒▓██████▓▒░ ░▒▓███████▓▒░░▒▓█▓▒░▒▓█▓▒░              ░▒▓██████▓▒░  
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░                    ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░             ░▒▓█▓▒░ 
░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓██████▓▒░       ░▒▓███████▓▒░  
`,`                                                                                     
┏┓  •   ┏┓           
┣ ┏┓┓┏  ┗┓┏┓┏┓┏┓┏┏┓┏┓
┗┛┛ ┗┗  ┗┛┣┛┗ ┛┗┗┗ ┛ 
          ┛          
`,`
 _______  ______    ___   _______    _______ 
|       ||    _ |  |   | |       |  |       |
|    ___||   | ||  |   | |       |  |  _____|
|   |___ |   |_||_ |   | |       |  | |_____ 
|    ___||    __  ||   | |      _|  |_____  |
|   |___ |   |  | ||   | |     |_    _____| |
|_______||___|  |_||___| |_______|  |_______|
`,`
                     _______ .______       __    ______ 
                    |   ____||   _  \\     |  |  /      |
                    |  |__   |  |_)  |    |  | |  ,----'
                    |   __|  |      /     |  | |  |     
                    |  |____ |  |\\  \\----.|  | |  \`----.
                    |_______|| _| \`._____||__|  \\______|
     _______..______    _______ .__   __.   ______  _______ .______      
    /       ||   _  \\  |   ____||  \\ |  |  /      ||   ____||   _  \\     
   |   (----\`|  |_)  | |  |__   |   \\|  | |  ,----'|  |__   |  |_)  |    
    \\   \\    |   ___/  |   __|  |  . \`  | |  |     |   __|  |      /     
.----)   |   |  |      |  |____ |  |\\   | |  \`----.|  |____ |  |\\  \\----.
|_______/    | _|      |_______||__| \\__|  \\______||_______|| _| \`._____|
`,`
███████ ██████  ██  ██████     ███████ 
██      ██   ██ ██ ██          ██      
█████   ██████  ██ ██          ███████ 
██      ██   ██ ██ ██               ██ 
███████ ██   ██ ██  ██████     ███████
`,`
   ▄████████    ▄████████  ▄█   ▄████████         ▄████████ 
  ███    ███   ███    ███ ███  ███    ███        ███    ███ 
  ███    █▀    ███    ███ ███▌ ███    █▀         ███    █▀  
 ▄███▄▄▄      ▄███▄▄▄▄██▀ ███▌ ███               ███        
▀▀███▀▀▀     ▀▀███▀▀▀▀▀   ███▌ ███             ▀███████████ 
  ███    █▄  ▀███████████ ███  ███    █▄                ███ 
  ███    ███   ███    ███ ███  ███    ███         ▄█    ███ 
  ██████████   ███    ███ █▀   ████████▀        ▄████████▀  
               ███    ███                                   
`,`
 ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄       ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌     ▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌ ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀      ▐░█▀▀▀▀▀▀▀▀▀ 
▐░▌          ▐░▌       ▐░▌     ▐░▌     ▐░▌               ▐░▌          
▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌     ▐░▌     ▐░▌               ▐░█▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░▌               ▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀█░█▀▀      ▐░▌     ▐░▌                ▀▀▀▀▀▀▀▀▀█░▌
▐░▌          ▐░▌     ▐░▌       ▐░▌     ▐░▌                         ▐░▌
▐░█▄▄▄▄▄▄▄▄▄ ▐░▌      ▐░▌  ▄▄▄▄█░█▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄       ▄▄▄▄▄▄▄▄▄█░▌
▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌     ▐░░░░░░░░░░░▌
 ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀       ▀▀▀▀▀▀▀▀▀▀▀ 
`,`
▄▄▄ .▄▄▄  ▪   ▄▄·     .▄▄ ·  ▄▄▄·▄▄▄ . ▐ ▄  ▄▄· ▄▄▄ .▄▄▄  
▀▄.▀·▀▄ █·██ ▐█ ▌▪    ▐█ ▀. ▐█ ▄█▀▄.▀·•█▌▐█▐█ ▌▪▀▄.▀·▀▄ █·
▐▀▀▪▄▐▀▀▄ ▐█·██ ▄▄    ▄▀▀▀█▄ ██▀·▐▀▀▪▄▐█▐▐▌██ ▄▄▐▀▀▪▄▐▀▀▄ 
▐█▄▄▌▐█•█▌▐█▌▐███▌    ▐█▄▪▐█▐█▪·•▐█▄▄▌██▐█▌▐███▌▐█▄▄▌▐█•█▌
 ▀▀▀ .▀  ▀▀▀▀·▀▀▀      ▀▀▀▀ .▀    ▀▀▀ ▀▀ █▪·▀▀▀  ▀▀▀ .▀  ▀
`,`
888888 88""Yb 88  dP""b8     .dP"Y8 
88__   88__dP 88 dP   \`"     \`Ybo." 
88""   88"Yb  88 Yb          o.\`Y8b 
888888 88  Yb 88  YboodP     8bodP' 
`,`
  sSSs   .S_sSSs     .S    sSSs          sSSs  
 d%%SP  .SS~YS%%b   .SS   d%%SP         d%%SP  
d%S'    S%S   \`S%b  S%S  d%S'          d%S'    
S%S     S%S    S%S  S%S  S%S           S%|     
S&S     S%S    d*S  S&S  S&S           S&S     
S&S_Ss  S&S   .S*S  S&S  S&S           Y&Ss    
S&S~SP  S&S_sdSSS   S&S  S&S           \`S&&S   
S&S     S&S~YSY%b   S&S  S&S             \`S*S  
S*b     S*S   \`S%b  S*S  S*b              l*S  
S*S.    S*S    S%S  S*S  S*S.            .S*P  
 SSSbs  S*S    S&S  S*S   SSSbs        sSS*S   
  YSSP  S*S    SSS  S*S    YSSP        YSS'    
        SP          SP                         
        Y           Y                          
`,`
 ____                         ______                             
|            |\`\`\`\`\`\`\`\`\`, |  .~      ~.                    ..'''' 
|______      |'''|'''''  | |                           .''       
|            |    \`.     | |                        ..'          
|___________ |      \`.   |  \`.______.'        ....''             
`,`
EEEE                  SSS                             
E        ii          S                                
EEE  rrr     ccc      SSS  ppp  eee nnn   ccc eee rrr 
E    r   ii c            S p  p e e n  n c    e e r   
EEEE r   ii  ccc     SSSS  ppp  ee  n  n  ccc ee  r   
                           p                          
                           p                          
`,`
######## ########  ####  ######      ######  
##       ##     ##  ##  ##    ##    ##    ## 
##       ##     ##  ##  ##          ##       
######   ########   ##  ##           ######  
##       ##   ##    ##  ##                ## 
##       ##    ##   ##  ##    ##    ##    ## 
######## ##     ## ####  ######      ######  
`,`
 .____                        _____                                         
 /      .___  \`   ___        (      \\,___,   ___  , __     ___    ___  .___ 
 |__.   /   \\ | .'   \`        \`--.  |    \\ .'   \` |'  \`. .'   \` .'   \` /   \\
 |      |   ' | |                |  |    | |----' |    | |      |----' |   '
 /----/ /     /  \`._.'      \\___.'  |\`---' \`.___, /    |  \`._.' \`.___, /    
                                    \\
`,`
_______________________________________
    _____                          __  
    /    '         ,             /    )
---/__------)__--------__--------\\-----
  /        /   ) /   /   '        \\    
_/____ ___/_____/___(___ _____(____/___
`,`
 __             __                  
|_  __ o  _    (_  _  _ __  _  _  __
|__ |  | (_    __)|_)(/_| |(_ (/_ | 
                  |
`,`
.___          __.                  
[__ ._.* _.  (__ ._  _ ._  _. _ ._.
[___[  |(_.  .__)[_)(/,[ )(_.(/,[  
                 |                 
`,`
   __             ()                         
  /  \`            /\\                         
 /--  __  o _.   /  )  _   _  ____  _. _  __ 
(___,/ (_<_(__  /__/__/_)_</_/ / <_(__</_/ (_
                     /                       
                    '                        
`,`
8""""                   8""""8                                   
8     eeeee  e  eeee    8      eeeee eeee eeeee eeee eeee eeeee  
8eeee 8   8  8  8  8    8eeeee 8   8 8    8   8 8  8 8    8   8  
88    8eee8e 8e 8e          88 8eee8 8eee 8e  8 8e   8eee 8eee8e 
88    88   8 88 88      e   88 88    88   88  8 88   88   88   8 
88eee 88   8 88 88e8    8eee88 88    88ee 88  8 88e8 88ee 88   8 
                                                                 
`,`
69 114 105 99  83 112 101 110 99 101 114 
E  r   i   c   S  p   e   n   c  e   r
`,`
          .-                      .-.                               
  .---;\`-'      .-.         .--.-'                                  
 (   (_)   ).--.\`-'.-.     (  (_).-.   .-..  .-.  .-.    .-.  ).--. 
  )--     /    /  (         \`-.  /  )./.-'_)/   )(     ./.-'_/      
 (      //  _.(__. \`---'  _    )/\`-' (__.''/   (  \`---'(__.'/       
 \`\___.'                 (_.--'/                \`-                  
`,`
 +-+-+-+-+ +-+-+-+-+-+-+-+
 |E|r|i|c| |S|p|e|n|c|e|r|
 +-+-+-+-+ +-+-+-+-+-+-+-+
`,`
    _  _  _  _  _                 _                          _  _  _  _     
   (_)(_)(_)(_)(_)               (_)                       _(_)(_)(_)(_)_   
   (_)           _       _  _  _  _      _  _  _          (_)          (_)  
   (_) _  _     (_)_  _ (_)(_)(_)(_)   _(_)(_)(_)         (_)_  _  _  _     
   (_)(_)(_)      (_)(_)         (_)  (_)                   (_)(_)(_)(_)_   
   (_)            (_)            (_)  (_)                  _           (_)  
   (_) _  _  _  _ (_)          _ (_) _(_)_  _  _          (_)_  _  _  _(_)  
   (_)(_)(_)(_)(_)(_)         (_)(_)(_) (_)(_)(_)           (_)(_)(_)(_)    
`,`
  ____ ____  __   ___     __  ____   ____ __  __   ___  ____ ____ 
 ||    || \\\\ ||  //      (( \\ || \\\\ ||    ||\\ ||  //   ||    || \\\\
 ||==  ||_// || ((        \\\\  ||_// ||==  ||\\\\|| ((    ||==  ||_//
 ||___ || \\\\ ||  \\\\__    \\_)) ||    ||___ || \\||  \\\\__ ||___ || \\\\
`,`
 ____ 
|    |
||_| |
|_||_|
 ____ 
|_   |
 / | |
|/\\__/
 ____ 
|____|
 ____ 
| _  |
| ||_|
|_|                                                                               

 _ __ 
| |  \\
| || |
\\__|_|
`,`
                                                 
                       ,,                        
\`7MM"""YMM             db               .M"""bgd 
  MM    \`7                             ,MI    "Y 
  MM   d    \`7Mb,od8 \`7MM  ,p6"bo      \`MMb.     
  MMmmMM      MM' "'   MM 6M'  OO        \`YMMNq. 
  MM   Y  ,   MM       MM 8M           .     \`MM 
  MM     ,M   MM       MM YM.    ,     Mb     dM 
.JMMmmmmMMM .JMML.   .JMML.YMbmd'      P"Ybmmd"  
`,`
__        __     ____      ____    ______       __
  \\    ___) |    \\  (_    _)  /  __)     )  ____) 
   |  (__   |     )   |  |   |  /       (  (___   
   |   __)  |    /    |  |   | |         \\___  \\  
   |  (___  | |\\ \\   _|  |_  |  \\__      ____)  ) 
__/       )_| |_\\ \\_(      )__\\    )____(      (__
`,`
45 72 69 63  53 70 65 6E 63 65 72 
E  r  i  c   S  p  e  n  c  e  r
`,`
                                
.oPYo.        o          .oPYo. 
8.                       8      
\`boo   oPYo. o8 .oPYo.   \`Yooo. 
.P     8  \`'  8 8    '       \`8 
8      8      8 8    .        8 
\`YooP' 8      8 \`YooP'   \`YooP' 
:.....:..:::::..:.....::::.....:
::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::
`,`
                                                     
    _/_/_/_/            _/                  _/_/_/   
   _/        _/  _/_/        _/_/_/      _/          
  _/_/_/    _/_/      _/  _/              _/_/       
 _/        _/        _/  _/                  _/      
_/_/_/_/  _/        _/    _/_/_/      _/_/_/         
`,`
EEEEEEE        iii            SSSSS                                              
EE      rr rr        cccc    SS      pp pp     eee  nn nnn    cccc   eee  rr rr  
EEEEE   rrr  r iii cc         SSSSS  ppp  pp ee   e nnn  nn cc     ee   e rrr  r 
EE      rr     iii cc             SS pppppp  eeeee  nn   nn cc     eeeee  rr     
EEEEEEE rr     iii  ccccc     SSSSS  pp       eeeee nn   nn  ccccc  eeeee rr     
                                     pp                                          
`

];

largeAsciiNameArray = [`
EEEEEEEEEEEEEEEEEEEEEE                     iiii                              SSSSSSSSSSSSSSS 
E::::::::::::::::::::E                    i::::i                           SS:::::::::::::::S
E::::::::::::::::::::E                     iiii                           S:::::SSSSSS::::::S
EE::::::EEEEEEEEE::::E                                                    S:::::S     SSSSSSS
  E:::::E       EEEEEErrrrr   rrrrrrrrr  iiiiiii     cccccccccccccccc     S:::::S            
  E:::::E             r::::rrr:::::::::r i:::::i   cc:::::::::::::::c     S:::::S            
  E::::::EEEEEEEEEE   r:::::::::::::::::r i::::i  c:::::::::::::::::c      S::::SSSS         
  E:::::::::::::::E   rr::::::rrrrr::::::ri::::i c:::::::cccccc:::::c       SS::::::SSSSS    
  E:::::::::::::::E    r:::::r     r:::::ri::::i c::::::c     ccccccc         SSS::::::::SS  
  E::::::EEEEEEEEEE    r:::::r     rrrrrrri::::i c:::::c                         SSSSSS::::S 
  E:::::E              r:::::r            i::::i c:::::c                              S:::::S
  E:::::E       EEEEEE r:::::r            i::::i c::::::c     ccccccc                 S:::::S
EE::::::EEEEEEEE:::::E r:::::r           i::::::ic:::::::cccccc:::::c     SSSSSSS     S:::::S
E::::::::::::::::::::E r:::::r           i::::::i c:::::::::::::::::c     S::::::SSSSSS:::::S
E::::::::::::::::::::E r:::::r           i::::::i  cc:::::::::::::::c     S:::::::::::::::SS 
EEEEEEEEEEEEEEEEEEEEEE rrrrrrr           iiiiiiii    cccccccccccccccc      SSSSSSSSSSSSSSS   
`,`
sSSs   .S_sSSs     .S    sSSs          sSSs   .S_sSSs      sSSs   .S_sSSs      sSSs    sSSs   .S_sSSs    
d%%SP  .SS~YS%%b   .SS   d%%SP         d%%SP  .SS~YS%%b    d%%SP  .SS~YS%%b    d%%SP   d%%SP  .SS~YS%%b   
d%S'    S%S   \`S%b  S%S  d%S'          d%S'    S%S   \`S%b  d%S'    S%S   \`S%b  d%S'    d%S'    S%S   \`S%b  
S%S     S%S    S%S  S%S  S%S           S%|     S%S    S%S  S%S     S%S    S%S  S%S     S%S     S%S    S%S  
S&S     S%S    d*S  S&S  S&S           S&S     S%S    d*S  S&S     S%S    S&S  S&S     S&S     S%S    d*S  
S&S_Ss  S&S   .S*S  S&S  S&S           Y&Ss    S&S   .S*S  S&S_Ss  S&S    S&S  S&S     S&S_Ss  S&S   .S*S  
S&S~SP  S&S_sdSSS   S&S  S&S           \`S&&S   S&S_sdSSS   S&S~SP  S&S    S&S  S&S     S&S~SP  S&S_sdSSS   
S&S     S&S~YSY%b   S&S  S&S             \`S*S  S&S~YSSY    S&S     S&S    S&S  S&S     S&S     S&S~YSY%b   
S*b     S*S   \`S%b  S*S  S*b              l*S  S*S         S*b     S*S    S*S  S*b     S*b     S*S   \`S%b  
S*S.    S*S    S%S  S*S  S*S.            .S*P  S*S         S*S.    S*S    S*S  S*S.    S*S.    S*S    S%S  
SSSbs  S*S    S&S  S*S   SSSbs        sSS*S   S*S          SSSbs  S*S    S*S   SSSbs   SSSbs  S*S    S&S  
 YSSP  S*S    SSS  S*S    YSSP        YSS'    S*S           YSSP  S*S    SSS    YSSP    YSSP  S*S    SSS  
       SP          SP                         SP                  SP                          SP          
       Y           Y                          Y                   Y                           Y          
`,`
_______ ______  _ _______     ______ ______ _______ _______ _______ _______ ______  
(_______|_____ \\| (_______)   / _____|_____ (_______|_______|_______|_______|_____ \\ 
 _____   _____) ) |_         ( (____  _____) )____   _     _ _       _____   _____) )
|  ___) |  __  /| | |         \\____ \\|  ____/  ___) | |   | | |     |  ___) |  __  / 
| |_____| |  \\ \\| | |_____    _____) ) |    | |_____| |   | | |_____| |_____| |  \\ \\ 
|_______)_|   |_|_|\\______)  (______/|_|    |_______)_|   |_|\\______)_______)_|   |_|
`,`
dMMMMMP dMMMMb  dMP .aMMMb        .dMMMb  dMMMMb  dMMMMMP dMMMMb  .aMMMb  dMMMMMP dMMMMb 
dMP     dMP.dMP amr dMP"VMP       dMP" VP dMP.dMP dMP     dMP dMP dMP"VMP dMP     dMP.dMP 
dMMMP   dMMMMK" dMP dMP            VMMMb  dMMMMP" dMMMP   dMP dMP dMP     dMMMP   dMMMMK"  
dMP     dMP"AMF dMP dMP.aMP       dP .dMP dMP     dMP     dMP dMP dMP.aMP dMP     dMP"AMF   
dMMMMMP dMP dMP dMP  VMMMP"        VMMMP" dMP     dMMMMMP dMP dMP  VMMMP" dMMMMMP dMP dMP    
`,`
                  d8,                                                                     
                 \`8P                                                                      
                                                                                          
 d8888b  88bd88b  88b d8888b     .d888b,?88,.d88b, d8888b  88bd88b  d8888b d8888b  88bd88b
d8b_,dP  88P'  \`  88Pd8P' \`P     ?8b,   \`?88'  ?88d8b_,dP  88P' ?8bd8P' \`Pd8b_,dP  88P'  \`
88b     d88      d88 88b           \`?8b   88b  d8P88b     d88   88P88b    88b     d88     
\`?888P'd88'     d88' \`?888P'    \`?888P'   888888P'\`?888P'd88'   88b\`?888P'\`?888P'd88'     
                                          88P'                                            
                                         d88                                              
                                         ?8P                                              
`,`
___________      .__           _________                                        
\\_   _____/______|__| ____    /   _____/_____   ____   ____   ____  ___________ 
 |    __)_\\_  __ \\  |/ ___\\   \\_____  \\\\____ \\_/ __ \\ /    \\_/ ___\\/ __ \\_  __ \\
 |        \\|  | \\/  \  \\___    /        \\  |_> >  ___/|   |  \\  \\__\\  ___/|  | \\/
/_______  /|__|  |__|\\___  > /_______  /   __/ \\___  >___|  /\\___  >___  >__|   
        \\/               \\/          \\/|__|        \\/     \\/     \\/    \\/       
`,`
01000101 01110010 01101001 01100011  01010011 01110000 01100101 01101110 01100011 01100101 01110010 
E        r        i        c         S        p        e        n        c        e        r
`,`
'||''''|           ||              .|'''.|                                                    
 ||  .    ... ..  ...    ....      ||..  '  ... ...    ....  .. ...     ....    ....  ... ..  
 ||''|     ||' ''  ||  .|   ''      ''|||.   ||'  || .|...||  ||  ||  .|   '' .|...||  ||' '' 
 ||        ||      ||  ||         .     '||  ||    | ||       ||  ||  ||      ||       ||     
.||.....| .||.    .||.  '|...'    |'....|'   ||...'   '|...' .||. ||.  '|...'  '|...' .||.    
                                             ||                                               
                                            ''''                                              
`,`
▓█████  ██▀███   ██▓ ▄████▄       ██████  ██▓███  ▓█████  ███▄    █  ▄████▄  ▓█████  ██▀███  
▓█   ▀ ▓██ ▒ ██▒▓██▒▒██▀ ▀█     ▒██    ▒ ▓██░  ██▒▓█   ▀  ██ ▀█   █ ▒██▀ ▀█  ▓█   ▀ ▓██ ▒ ██▒
▒███   ▓██ ░▄█ ▒▒██▒▒▓█    ▄    ░ ▓██▄   ▓██░ ██▓▒▒███   ▓██  ▀█ ██▒▒▓█    ▄ ▒███   ▓██ ░▄█ ▒
▒▓█  ▄ ▒██▀▀█▄  ░██░▒▓▓▄ ▄██▒     ▒   ██▒▒██▄█▓▒ ▒▒▓█  ▄ ▓██▒  ▐▌██▒▒▓▓▄ ▄██▒▒▓█  ▄ ▒██▀▀█▄  
░▒████▒░██▓ ▒██▒░██░▒ ▓███▀ ░   ▒██████▒▒▒██▒ ░  ░░▒████▒▒██░   ▓██░▒ ▓███▀ ░░▒████▒░██▓ ▒██▒
░░ ▒░ ░░ ▒▓ ░▒▓░░▓  ░ ░▒ ▒  ░   ▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░░░ ▒░ ░░ ▒░   ▒ ▒ ░ ░▒ ▒  ░░░ ▒░ ░░ ▒▓ ░▒▓░
 ░ ░  ░  ░▒ ░ ▒░ ▒ ░  ░  ▒      ░ ░▒  ░ ░░▒ ░      ░ ░  ░░ ░░   ░ ▒░  ░  ▒    ░ ░  ░  ░▒ ░ ▒░
   ░     ░░   ░  ▒ ░░           ░  ░  ░  ░░          ░      ░   ░ ░ ░           ░     ░░   ░ 
   ░  ░   ░      ░  ░ ░               ░              ░  ░         ░ ░ ░         ░  ░   ░     
                    ░                                               ░                        
`,`
███████ ██████  ██  ██████     ███████ ██████  ███████ ███    ██  ██████ ███████ ██████  
██      ██   ██ ██ ██          ██      ██   ██ ██      ████   ██ ██      ██      ██   ██ 
█████   ██████  ██ ██          ███████ ██████  █████   ██ ██  ██ ██      █████   ██████  
██      ██   ██ ██ ██               ██ ██      ██      ██  ██ ██ ██      ██      ██   ██ 
███████ ██   ██ ██  ██████     ███████ ██      ███████ ██   ████  ██████ ███████ ██   ██ 
`,`
███████╗██████╗ ██╗ ██████╗    ███████╗██████╗ ███████╗███╗   ██╗ ██████╗███████╗██████╗ 
██╔════╝██╔══██╗██║██╔════╝    ██╔════╝██╔══██╗██╔════╝████╗  ██║██╔════╝██╔════╝██╔══██╗
█████╗  ██████╔╝██║██║         ███████╗██████╔╝█████╗  ██╔██╗ ██║██║     █████╗  ██████╔╝
██╔══╝  ██╔══██╗██║██║         ╚════██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║     ██╔══╝  ██╔══██╗
███████╗██║  ██║██║╚██████╗    ███████║██║     ███████╗██║ ╚████║╚██████╗███████╗██║  ██║
╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝    ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝
`,`
  ▄████████    ▄████████  ▄█   ▄████████         ▄████████    ▄███████▄    ▄████████ ███▄▄▄▄    ▄████████    ▄████████    ▄████████ 
  ███    ███   ███    ███ ███  ███    ███        ███    ███   ███    ███   ███    ███ ███▀▀▀██▄ ███    ███   ███    ███   ███    ███ 
  ███    █▀    ███    ███ ███▌ ███    █▀         ███    █▀    ███    ███   ███    █▀  ███   ███ ███    █▀    ███    █▀    ███    ███ 
 ▄███▄▄▄      ▄███▄▄▄▄██▀ ███▌ ███               ███          ███    ███  ▄███▄▄▄     ███   ███ ███         ▄███▄▄▄      ▄███▄▄▄▄██▀ 
▀▀███▀▀▀     ▀▀███▀▀▀▀▀   ███▌ ███             ▀███████████ ▀█████████▀  ▀▀███▀▀▀     ███   ███ ███        ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   
  ███    █▄  ▀███████████ ███  ███    █▄                ███   ███          ███    █▄  ███   ███ ███    █▄    ███    █▄  ▀███████████ 
  ███    ███   ███    ███ ███  ███    ███         ▄█    ███   ███          ███    ███ ███   ███ ███    ███   ███    ███   ███    ███ 
  ██████████   ███    ███ █▀   ████████▀        ▄████████▀   ▄████▀        ██████████  ▀█   █▀  ████████▀    ██████████   ███    ███ 
               ███    ███                                                                                                 ███    ███ 
`,`
d88888b d8888b. d888888b  .o88b.      .d8888. d8888b. d88888b d8b   db  .o88b. d88888b d8888b. 
88'     88  \`8D   \`88'   d8P  Y8      88'  YP 88  \`8D 88'     888o  88 d8P  Y8 88'     88  \`8D 
88ooooo 88oobY'    88    8P           \`8bo.   88oodD' 88ooooo 88V8o 88 8P      88ooooo 88oobY' 
88~~~~~ 88\`8b      88    8b             \`Y8b. 88~~~   88~~~~~ 88 V8o88 8b      88~~~~~ 88\`8b   
88.     88 \`88.   .88.   Y8b  d8      db   8D 88      88.     88  V888 Y8b  d8 88.     88 \`88. 
Y88888P 88   YD Y888888P  \`Y88P'      \`8888Y' 88      Y88888P VP   V8P  \`Y88P' Y88888P 88   YD 
`,`
8888888888 8888888b.  8888888 .d8888b.        .d8888b.  8888888b.  8888888888 888b    888  .d8888b.  8888888888 8888888b.  
888        888   Y88b   888  d88P  Y88b      d88P  Y88b 888   Y88b 888        8888b   888 d88P  Y88b 888        888   Y88b 
888        888    888   888  888    888      Y88b.      888    888 888        88888b  888 888    888 888        888    888 
8888888    888   d88P   888  888              "Y888b.   888   d88P 8888888    888Y88b 888 888        8888888    888   d88P 
888        8888888P"    888  888                 "Y88b. 8888888P"  888        888 Y88b888 888        888        8888888P"  
888        888 T88b     888  888    888            "888 888        888        888  Y88888 888    888 888        888 T88b   
888        888  T88b    888  Y88b  d88P      Y88b  d88P 888        888        888   Y8888 Y88b  d88P 888        888  T88b  
8888888888 888   T88b 8888888 "Y8888P"        "Y8888P"  888        8888888888 888    Y888  "Y8888P"  8888888888 888   T88b 
`,`
\`7MM"""YMM  \`7MM"""Mq.  \`7MMF' .g8"""bgd      .M"""bgd \`7MM"""Mq.\`7MM"""YMM  \`7MN.   \`7MF' .g8"""bgd \`7MM"""YMM  \`7MM"""Mq.  
  MM    \`7    MM   \`MM.   MM .dP'     \`M     ,MI    "Y   MM   \`MM. MM    \`7    MMN.    M .dP'     \`M   MM    \`7    MM   \`MM. 
  MM   d      MM   ,M9    MM dM'       \`     \`MMb.       MM   ,M9  MM   d      M YMb   M dM'       \`   MM   d      MM   ,M9  
  MMmmMM      MMmmdM9     MM MM                \`YMMNq.   MMmmdM9   MMmmMM      M  \`MN. M MM            MMmmMM      MMmmdM9   
  MM   Y  ,   MM  YM.     MM MM.             .     \`MM   MM        MM   Y  ,   M   \`MM.M MM.           MM   Y  ,   MM  YM.   
  MM     ,M   MM   \`Mb.   MM \`Mb.     ,'     Mb     dM   MM        MM     ,M   M     YMM \`Mb.     ,'   MM     ,M   MM   \`Mb. 
.JMMmmmmMMM .JMML. .JMM..JMML. \`"bmmmd'      P"Ybmmd"  .JMML.    .JMMmmmmMMM .JML.    YM   \`"bmmmd'  .JMMmmmmMMM .JMML. .JMM.
`,`
ooooooooooo oooooooooo  ooooo  oooooooo8       oooooooo8 oooooooooo ooooooooooo oooo   oooo  oooooooo8 ooooooooooo oooooooooo  
 888    88   888    888  888 o888     88      888         888    888 888    88   8888o  88 o888     88  888    88   888    888 
 888ooo8     888oooo88   888 888               888oooooo  888oooo88  888ooo8     88 888o88 888          888ooo8     888oooo88  
 888    oo   888  88o    888 888o     oo              888 888        888    oo   88   8888 888o     oo  888    oo   888  88o   
o888ooo8888 o888o  88o8 o888o 888oooo88       o88oooo888 o888o      o888ooo8888 o88o    88  888oooo88  o888ooo8888 o888o  88o8
`,`
                                                                                                            
@@@@@@@@  @@@@@@@   @@@   @@@@@@@      @@@@@@   @@@@@@@   @@@@@@@@  @@@  @@@   @@@@@@@  @@@@@@@@  @@@@@@@   
@@@@@@@@  @@@@@@@@  @@@  @@@@@@@@     @@@@@@@   @@@@@@@@  @@@@@@@@  @@@@ @@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  
@@!       @@!  @@@  @@!  !@@          !@@       @@!  @@@  @@!       @@!@!@@@  !@@       @@!       @@!  @@@  
!@!       !@!  @!@  !@!  !@!          !@!       !@!  @!@  !@!       !@!!@!@!  !@!       !@!       !@!  @!@  
@!!!:!    @!@!!@!   !!@  !@!          !!@@!!    @!@@!@!   @!!!:!    @!@ !!@!  !@!       @!!!:!    @!@!!@!   
!!!!!:    !!@!@!    !!!  !!!           !!@!!!   !!@!!!    !!!!!:    !@!  !!!  !!!       !!!!!:    !!@!@!    
!!:       !!: :!!   !!:  :!!               !:!  !!:       !!:       !!:  !!!  :!!       !!:       !!: :!!   
:!:       :!:  !:!  :!:  :!:              !:!   :!:       :!:       :!:  !:!  :!:       :!:       :!:  !:!  
 :: ::::  ::   :::   ::   ::: :::     :::: ::    ::        :: ::::   ::   ::   ::: :::   :: ::::  ::   :::  
: :: ::    :   : :  :     :: :: :     :: : :     :        : :: ::   ::    :    :: :: :  : :: ::    :   : :  
`
]

tinyAsciiNameArray = [`
E very
R ed
I tem
C arefully

S tored
P rotects
E verything
N eatly
C onserved,
E vading
R uin
`,`
/ˈɛrɪk/
/ˈspɛnsər/
`,`
EH-rik
SPEN-sər
`,`
ERIC SPENCER
* **   * ** 
 *    * *  *
     *      
            
     *      
   *     *  
            
*      ** * 
            
      *     
            
 **        *
`,`
Echo
Romeo
India
Charlie

Sierra
Papa
Echo
November
Charlie
Echo
Romeo
`,`
Ερικ
Σπενσερ

Eric
Spencer
`
]


