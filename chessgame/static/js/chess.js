// DOM element references for the board, move log, and status display
const board = document.getElementById('board');
const moveLog = document.getElementById('move-log');
const status = document.getElementById('status');

// Initial setup of the chessboard with Unicode pieces
const initialBoard = [
  ['♜','♞','♝','♛','♚','♝','♞','♜'],
  ['♟','♟','♟','♟','♟','♟','♟','♟'],
  ['','','','','','','',''],
  ['','','','','','','',''],
  ['','','','','','','',''],
  ['','','','','','','',''],
  ['♙','♙','♙','♙','♙','♙','♙','♙'],
  ['♖','♘','♗','♕','♔','♗','♘','♖']
];

// Tracks the turn and selected piece
let isPlayerTurn = true;
let selectedCell = null;

// Builds the board UI and places pieces according to initialBoard
function createBoard() {
    board.innerHTML = '';
    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const cell = document.createElement('div');
        const isWhite = (row + col) % 2 === 0;
        cell.classList.add('cell', isWhite ? 'white' : 'black');
        cell.dataset.row = row;
        cell.dataset.col = col;
        cell.innerHTML = initialBoard[row][col];
        board.appendChild(cell); 
    }
    }
    updateStatus();
}

// Highlights the clicked piece and deselects the previously selected one
board.addEventListener('click', (e) => {
    const target = e.target;
  
    if (!target.classList.contains('cell')) return;
  
    const piece = target.innerHTML;
  
    if (!piece.trim()) return;
  
    if (selectedCell) {
      selectedCell.classList.remove('selected');
    }
  
    selectedCell = target;
    selectedCell.classList.add('selected');
});  

// Resets the board and game state to start a new game
function startNewGame() {
    isPlayerTurn = true;
    createBoard();
    updateStatus();
}

// Saves the game (placeholder)
function saveGame() {
  alert("Game saved!");
}

// Updates to show whose turn it is
function updateStatus() {
    status.innerText = isPlayerTurn ? "Your Turn" : "AI's Turn";
}

// Toggles the turn and updates status each time board is clicked
// (Will change once actual game logic is implemeneted)
board.addEventListener('click', () => {
    isPlayerTurn = !isPlayerTurn;
    updateStatus();
});  

// Initializes the game board
createBoard();

