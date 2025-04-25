console.log('Chess.js is loading!');
console.log('Chess.js is loading!');

// Immediate log to verify script loading
console.log('Chess.js loaded!');

// DOM element references for the board, move log, and status display
const board = document.getElementById('board');
const moveLog = document.getElementById('move-log');
const status = document.getElementById('status');

// Game state management
let gameId = null;
let isPlayerTurn = true;
let selectedCell = null;

// Add this function at the top of your file to get the CSRF token
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// API functions for communicating with Django backend(Had to change for FEN :( )
const api = {
    newGame: async () => {
        console.log('Calling newGame API');
        const response = await fetch('/new_game/', {
            method: 'GET'
        });
        const data = await response.json();
        console.log('newGame response:', data);
        return data;
    },

    makeMove: async (gameId, move) => {
        console.log('Calling makeMove API:', { gameId, move });
        const response = await fetch(`/make_move/${gameId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ move: move })
        });
        const data = await response.json();
        console.log('makeMove response:', data);
        return data;
    },

    getGameState: async (gameId) => {
        const response = await fetch(`/get_game_state/${gameId}/`);
        return await response.json();
    }
};

// FEN to Unicode piece mapping
const fenToUnicode = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
    '.': ''
};

// Convert FEN to board array
function fenToBoard(fen) {
    const board = [];
    const rows = fen.split(' ')[0].split('/');
    
    for (const row of rows) {
        const boardRow = [];
        for (const char of row) {
            if (isNaN(char)) {
                // Convert piece characters to Unicode
                const isWhite = char === char.toUpperCase();
                const piece = isWhite ? 
                    {'P':'♙','R':'♖','N':'♘','B':'♗','Q':'♕','K':'♔'}[char.toUpperCase()] :
                    {'P':'♟','R':'♜','N':'♞','B':'♝','Q':'♛','K':'♚'}[char.toUpperCase()];
                boardRow.push(piece);
            } else {
                // Add empty squares
                for (let i = 0; i < parseInt(char); i++) {
                    boardRow.push('');
                }
            }
        }
        board.push(boardRow);
    }
    return board;
}

// Render the chess board
function renderBoard(board) {
    const boardElement = document.getElementById('board');
    boardElement.innerHTML = '';
    
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const cell = document.createElement('div');
            const isWhite = (row + col) % 2 === 0;
            cell.classList.add('cell', isWhite ? 'white' : 'black');
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.innerHTML = board[row][col];
            boardElement.appendChild(cell);
        }
    }
}

// Create and update the board UI
function createBoard(boardState) {
    board.innerHTML = '';
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const cell = document.createElement('div');
            const isWhite = (row + col) % 2 === 0;
            cell.classList.add('cell', isWhite ? 'white' : 'black');
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.innerHTML = boardState[row][col];
            board.appendChild(cell);
        }
    }
    updateStatus();
}

// Add this function to show move feedback
function showMoveError() {
    const statusEl = document.getElementById('status');
    const originalText = statusEl.innerText;
    statusEl.innerText = "Invalid Move!";
    statusEl.style.color = 'red';
    
    setTimeout(() => {
        statusEl.innerText = originalText;
        statusEl.style.color = '';
    }, 1000);
}

// First, let's add a basic click handler to verify events are working
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded');
    
    const board = document.getElementById('board');
    if (!board) {
        console.error('Could not find board element!');
        return;
    }

    // Remove any existing listeners
    board.removeEventListener('click', handleCellClick);
    
    // Add our click handler
    board.addEventListener('click', handleCellClick);

    // Start the game
    startNewGame();
});

// Modify the handleCellClick function to add more logging
async function handleCellClick(e) {
    console.log('Cell clicked!', e.target);
    
    if (!gameId || !isPlayerTurn) {
        console.log('Game state:', { gameId, isPlayerTurn });
        return;
    }
    
    const target = e.target;
    if (!target.classList.contains('cell')) {
        console.log('Not a cell element');
        return;
    }
    
    const row = parseInt(target.dataset.row);
    const col = parseInt(target.dataset.col);
    const piece = target.innerHTML;
    console.log('Clicked cell:', { row, col, piece });
    
    if (selectedCell) {
        const selectedRow = parseInt(selectedCell.dataset.row);
        const selectedCol = parseInt(selectedCell.dataset.col);
        const selectedPiece = selectedCell.innerHTML;
        
        if (selectedRow === row && selectedCol === col) {
            selectedCell.classList.remove('selected');
            selectedCell = null;
            return;
        }
        
        const move = `${String.fromCharCode(97 + selectedCol)}${8 - selectedRow}${String.fromCharCode(97 + col)}${8 - row}`;
        console.log('Attempting move:', move);
        
        try {
            const response = await api.makeMove(gameId, move);
            
            if (response.success) {
                console.log('Move successful');
                const newBoard = fenToBoard(response.fen);
                createBoard(newBoard);
                moveLog.innerHTML += `${selectedPiece} ${move}<br>`;
                isPlayerTurn = false;
                updateStatus();
            } else {
                console.log('Move failed');
                showMoveError();
            }
        } catch (error) {
            console.error('Move error:', error);
            showMoveError();
        }
        
        selectedCell.classList.remove('selected');
        selectedCell = null;
    } 
    else if (piece && '♔♕♖♗♘♙'.includes(piece)) {
        selectedCell = target;
        selectedCell.classList.add('selected');
        console.log('Selected piece:', piece);
    }
}

// Start a new game
async function startNewGame() {
    console.log('Starting new game...');
    try {
        const response = await api.newGame();
        console.log('New game response:', response);
        gameId = response.game_id;
        console.log('Game ID:', gameId);
        const board = fenToBoard(response.fen);
        createBoard(board);
        isPlayerTurn = true;
        moveLog.innerHTML = '';
        updateStatus();
    } catch (error) {
        console.error('New game error:', error);
    }
}

// Saves the game (placeholder)
function saveGame() {
  alert("Game saved!");
}

// Update the game status
function updateStatus() {
    status.innerText = isPlayerTurn ? "Your Turn" : "AI's Turn";
}

// Poll for AI moves
setInterval(async () => {
    if (gameId && !isPlayerTurn) {
        try {
            const response = await api.getGameState(gameId);
            const currentBoard = fenToBoard(response.fen);
            createBoard(currentBoard);
            
            if (response.status !== 'ACTIVE') {
                alert(`Game Over! ${response.status}`);
            } else {
                isPlayerTurn = true;
                updateStatus();
            }
        } catch (error) {
            console.error('Failed to get game state:', error);
        }
    }
}, 1000);

