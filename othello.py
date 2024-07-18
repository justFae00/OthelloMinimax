import tkinter as tk
from tkinter import messagebox

# Constants
BOARD_SIZE = 8
CELL_SIZE = 60
PADDING = 5
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE
AI_DELAY = 500  # Delay in milliseconds for AI move

# Colors
COLORS = {
    "WHITE": "snow",
    "BLACK": "black",
    "GREEN": "PaleGreen2",
    "RED": "salmon",
    "BLUE": "SkyBlue1"
}

# Directions for checking valid moves
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 1),
              (1, -1), (1, 0), (1, 1)]


class OthelloGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Othello")
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg=COLORS["GREEN"])
        self.canvas.pack()
        self.score_label = tk.Label(root, text="Black: 2, White: 2", font=("Berlin Sans FB Demi", 13))
        self.score_label.pack()

        # Initialize the board with the starting positions
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.board[3][3], self.board[4][4] = 1, 1
        self.board[3][4], self.board[4][3] = -1, -1
        self.current_player = 1  # Black starts

        self.draw_board()
        self.update_score()
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_hover)


    #Draws the Othello board and pieces.
    def draw_board(self):
        self.canvas.delete("all")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1, y1 = col * CELL_SIZE, row * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["GREEN"], outline=COLORS["WHITE"])
                if self.board[row][col] == 1:
                    self.canvas.create_oval(x1 + PADDING, y1 + PADDING, x2 - PADDING, y2 - PADDING, fill=COLORS["BLACK"])
                elif self.board[row][col] == -1:
                    self.canvas.create_oval(x1 + PADDING, y1 + PADDING, x2 - PADDING, y2 - PADDING, fill=COLORS["WHITE"])


    #Checks if a move is valid for the given player.
    def is_valid_move(self, board, row, col, player):
        if board[row][col] != 0:
            return False

        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == -player:
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if board[r][c] == player:
                        return True
                    elif board[r][c] == 0:
                        break
                    r += dr
                    c += dc
        return False
    
    
    #Returns a list of valid moves for the given player.
    def get_valid_moves(self, player):
        valid_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(self.board, row, col, player):
                    valid_moves.append((row, col))
        return valid_moves

    
    #Applies a move for the given player and flips the opponent's pieces.
    def apply_move(self, row, col, player):
        self.board[row][col] = player
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == -player:
                cells_to_flip = []
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if self.board[r][c] == player:
                        for fr, fc in cells_to_flip:
                            self.board[fr][fc] = player
                        break
                    elif self.board[r][c] == 0:
                        break
                    cells_to_flip.append((r, c))
                    r += dr
                    c += dc
        self.update_score()

    
    #Calculates and returns the score for both players.
    def get_score(self):
        black_score = sum(row.count(1) for row in self.board)
        white_score = sum(row.count(-1) for row in self.board)
        return black_score, white_score


    #Updates the score display.
    def update_score(self):
        black_score, white_score = self.get_score()
        self.score_label.config(text=f"Black: {black_score}, White: {white_score}")
    
    
    #Checks if the game is over.
    def is_game_over(self):
        return not self.get_valid_moves(1) and not self.get_valid_moves(-1)

    
    #Minimax algorithm with alpha-beta pruning for the AI to find the best move.
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        valid_moves = self.get_valid_moves(maximizing_player)
        if depth == 0 or not valid_moves:
            black_score, white_score = self.get_score()
            return black_score - white_score if maximizing_player == 1 else white_score - black_score

        if maximizing_player == 1:
            max_eval = -float('inf')
            for move in valid_moves:
                new_board = [row[:] for row in board]
                self.apply_move_to_board(new_board, move[0], move[1], maximizing_player)
                eval = self.minimax(new_board, depth - 1, alpha, beta, -maximizing_player)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                new_board = [row[:] for row in board]
                self.apply_move_to_board(new_board, move[0], move[1], maximizing_player)
                eval = self.minimax(new_board, depth - 1, alpha, beta, -maximizing_player)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
        
    
    #Applies a move to a given board (used by minimax).
    def apply_move_to_board(self, board, row, col, player):
        board[row][col] = player
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == -player:
                cells_to_flip = []
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if board[r][c] == player:
                        for fr, fc in cells_to_flip:
                            board[fr][fc] = player
                        break
                    elif board[r][c] == 0:
                        break
                    cells_to_flip.append((r, c))
                    r += dr
                    c += dc
    
    
    #Finds the best move for the given player using minimax with alpha-beta pruning.
    def best_move(self, player):
        best_eval = -float('inf')
        best_move = None
        valid_moves = self.get_valid_moves(player)
        for move in valid_moves:
            new_board = [row[:] for row in self.board]
            self.apply_move_to_board(new_board, move[0], move[1], player)
            move_eval = self.minimax(new_board, 3, -float('inf'), float('inf'), -player)
            if move_eval > best_eval:
                best_eval = move_eval
                best_move = move
        return best_move


    #Handles the click event for player moves.
    def on_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        valid_moves = self.get_valid_moves(self.current_player)
        if (row, col) in valid_moves:
            self.apply_move(row, col, self.current_player)
            self.current_player *= -1
            self.draw_board()

            if self.is_game_over():
                self.end_game()
                return

            if self.current_player == -1:
                self.root.after(AI_DELAY, self.ai_move)


    #Handles the AI move with a delay.
    def ai_move(self):
        ai_move = self.best_move(self.current_player)
        if ai_move:
            self.apply_move(ai_move[0], ai_move[1], self.current_player)
            self.current_player *= -1
            self.draw_board()

            if self.is_game_over():
                self.end_game()


    #Ends the game and shows the result.
    def end_game(self):
        black_score, white_score = self.get_score()
        result_text = f"Player {black_score}, AI {white_score}"
        winner = "Player" if black_score > white_score else "AI" if white_score > black_score else "Draw"
        messagebox.showinfo("Game Over", f"{winner} wins!\n\n{result_text}")
        self.root.quit()


    #Handles the hover event to highlight valid moves.
    def on_hover(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        self.draw_board()
        valid_moves = self.get_valid_moves(self.current_player)
        x1, y1 = col * CELL_SIZE, row * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        if (row, col) in valid_moves:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["BLUE"], outline=COLORS["WHITE"])
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["RED"], outline=COLORS["WHITE"])
            self.canvas.config(cursor="")


if __name__ == "__main__":
    root = tk.Tk()
    game = OthelloGame(root)
    root.mainloop()
