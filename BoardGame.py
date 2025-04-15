#Example Flask App for a hexaganal tile game
#Logic is in this python file

from flask import Flask, render_template, request, redirect, url_for
import json
import os
import random

app = Flask(__name__)
BOARD_SIZE = 10
WINNING_TERRITORY = 70
STATE_FILE = "game_state.json"
RPS_CHOICES = ["Rock", "Paper", "Scissors"]

def empty_game():
    return {
        "turn": "Player 1",
        "positions": {
            "Player 1": [[0, 0], [0, 1]],
            "Player 2": [[9, 9], [9, 8]]
        },
        "captured": {},
        "winner": None,
        "message": "",
        "rps_result": None
    }

def load_game():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return empty_game()

def save_game(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_neighbors(x, y):
    dirs = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]
    return [(x+dx, y+dy) for dx, dy in dirs if 0 <= x+dx < BOARD_SIZE and 0 <= y+dy < BOARD_SIZE]

def check_winner(captured):
    count1 = sum(1 for v in captured.values() if v == "Player 1")
    count2 = sum(1 for v in captured.values() if v == "Player 2")
    if count1 >= WINNING_TERRITORY:
        return "Player 1"
    elif count2 >= WINNING_TERRITORY:
        return "Player 2"
    return None

def play_rps(p1, p2):
    win_map = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}
    if win_map[p1] == p2:
        return 1
    elif win_map[p2] == p1:
        return 2
    return 0

@app.route('/')
def index():
    state = load_game()
    return render_template('index.html', state=state, board_size=BOARD_SIZE)

@app.route('/move', methods=['POST'])
def move():
    piece_id = int(request.form['piece_id'])
    x = int(request.form['x'])
    y = int(request.form['y'])

    state = load_game()
    player = state["turn"]
    opponent = "Player 2" if player == "Player 1" else "Player 1"

    if state["winner"]:
        return redirect('/')

    state["positions"][player][piece_id] = [x, y]
    rps_summary = ""

    for cx, cy in get_neighbors(x, y) + [(x, y)]:
        key = f"{cx},{cy}"
        if key in state["captured"] and state["captured"][key] != player:
            # RPS battle
            p1_choice = random.choice(RPS_CHOICES)
            p2_choice = random.choice(RPS_CHOICES)
            result = play_rps(p1_choice, p2_choice)
            if result == 1:
                state["captured"][key] = player
                rps_summary += f"{player} wins RPS at ({cx},{cy}) with {p1_choice} vs {p2_choice}<br>"
            elif result == 2:
                rps_summary += f"{opponent} wins RPS at ({cx},{cy}) with {p2_choice} vs {p1_choice}<br>"
            else:
                rps_summary += f"RPS tie at ({cx},{cy}) — {p1_choice} vs {p2_choice}<br>"
        else:
            state["captured"][key] = player

    # Check for winner
    winner = check_winner(state["captured"])
    if winner:
        state["winner"] = winner
        state["message"] = f"{winner} wins the game!"
    else:
        state["message"] = rps_summary or f"{player} moved piece {piece_id+1} to ({x},{y})"
        state["turn"] = opponent

    save_game(state)
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    save_game(empty_game())
    return redirect('/')

# Keep track of the current player

if __name__ == "__main__":
    app.run(debug=True)
