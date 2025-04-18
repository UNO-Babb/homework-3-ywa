from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Constants
BOARD_SIZE = 10
WINNING_PERCENTAGE = 0.7

# Initial Game State
game_state = {
    "board": [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
    "players": {
        "Player 1": {"color": "red", "pieces": {"p1": [0, 0], "p2": [0, 1]}},  # Player 1 pieces
        "Player 2": {"color": "blue", "pieces": {"p1": [9, 9], "p2": [9, 8]}}   # Player 2 pieces
    },
    "turn": "Player 1",
    "winner": ""
}

# Initial ownership of cells
for pname, pdata in game_state["players"].items():
    for _, (x, y) in pdata["pieces"].items():
        game_state["board"][y][x] = pname

# Functions to check winning condition
def check_winner():
    red_count = sum(1 for row in game_state["board"] for cell in row if cell == "Player 1")
    blue_count = sum(1 for row in game_state["board"] for cell in row if cell == "Player 2")

    total_cells = BOARD_SIZE * BOARD_SIZE
    if red_count / total_cells >= WINNING_PERCENTAGE:
        return "Player 1"
    elif blue_count / total_cells >= WINNING_PERCENTAGE:
        return "Player 2"
    return None

# RPS function to resolve conflicts
def resolve_rps(player1, player2):
    moves = ["rock", "paper", "scissors"]
    p1_move = random.choice(moves)
    p2_move = random.choice(moves)

    if p1_move == p2_move:
        return None  # Tie
    elif (p1_move == "rock" and p2_move == "scissors") or \
         (p1_move == "paper" and p2_move == "rock") or \
         (p1_move == "scissors" and p2_move == "paper"):
        return player1  # Player 1 wins
    else:
        return player2  # Player 2 wins

@app.route('/')
def index():
    return render_template('index.html', state=game_state, board_size=BOARD_SIZE)

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    pname = data["player"]
    piece = data["piece"]
    direction = data["direction"]

    dx, dy = 0, 0
    if direction == "up": dy = -1
    elif direction == "down": dy = 1
    elif direction == "left": dx = -1
    elif direction == "right": dx = 1

    x, y = game_state["players"][pname]["pieces"][piece]
    nx, ny = x + dx, y + dy

    # Check if the new position is within bounds
    if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
        # Check for conflicts with the opponent's piece
        if game_state["board"][ny][nx] and game_state["board"][ny][nx] != pname:
            opponent = "Player 1" if pname == "Player 2" else "Player 2"
            winner = resolve_rps(pname, opponent)
            if winner == pname:
                # Player wins and takes the space
                game_state["players"][pname]["pieces"][piece] = [nx, ny]
                game_state["board"][ny][nx] = pname
        else:
            game_state["players"][pname]["pieces"][piece] = [nx, ny]
            game_state["board"][ny][nx] = pname

    # Switch turn
    game_state["turn"] = "Player 2" if pname == "Player 1" else "Player 1"

    # Check for winner
    winner = check_winner()
    if winner:
        game_state["winner"] = winner

    return jsonify(success=True, winner=game_state["winner"])

if __name__ == '__main__':
    app.run(debug=True)
