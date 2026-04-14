import tkinter as tk
from tkinter import font as tkfont
import random
import math
import time

# ── Palette ────────────────────────────────────────────────────────────────────
BG          = "#0D0D1A"
PANEL_BG    = "#13132B"
CELL_BG     = "#1A1A35"
CELL_BORDER = "#2A2A55"
GRID_LINE   = "#1E1E3A"

PLAYER_CLR  = "#00E5FF"   # cyan
TREASURE_CLR= "#FFD700"   # gold
TRAP_CLR    = "#FF3D5A"   # red
EMPTY_CLR   = "#2A2A55"
PATH_CLR    = "#1E4D6B"
VISITED_CLR = "#1A2A3A"
HIGHLIGHT   = "#FFD70033"

TEXT_LIGHT  = "#E8E8FF"
TEXT_DIM    = "#5A5A8A"
TEXT_GOLD   = "#FFD700"
TEXT_CYAN   = "#00E5FF"
TEXT_RED    = "#FF3D5A"
TEXT_GREEN  = "#39FF14"

BTN_PRIMARY = "#7C3AED"
BTN_HOVER   = "#6D28D9"
BTN_SECOND  = "#1E1E4A"
BTN_SEC_HOV = "#2A2A5A"

FONT        = "Consolas"
FONT2       = "Helvetica"

GRID_SIZE   = 10
CELL_PX     = 56
PADDING     = 3

class GreedyTreasureGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Greedy Treasure Hunt  ·  Hill Climbing AI")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.TREASURES   = 8
        self.TRAPS       = 6
        self.score       = 0
        self.moves       = 0
        self.collected   = 0
        self.alive       = True
        self.auto_run    = False
        self.auto_job    = None
        self.speed_var   = tk.IntVar(value=400)
        self.show_scores_var = tk.BooleanVar(value=True)

        self.grid        = []
        self.player_pos  = (0, 0)
        self.path_trail  = []
        self.visited     = set()
        self.step_log    = []

        self._build_ui()
        self.new_game()

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── left panel ──
        left = tk.Frame(self.root, bg=BG, width=220)
        left.pack(side="left", fill="y", padx=(18, 6), pady=18)
        left.pack_propagate(False)

        # Logo
        tk.Label(left, text="⬡", font=(FONT2, 36), bg=BG, fg="#7C3AED").pack()
        tk.Label(left, text="GREEDY HUNT", font=(FONT, 15, "bold"),
                 bg=BG, fg=TEXT_LIGHT).pack()
        tk.Label(left, text="Hill Climbing AI", font=(FONT2, 9),
                 bg=BG, fg=TEXT_DIM).pack(pady=(0, 14))

        tk.Frame(left, bg="#7C3AED", height=1).pack(fill="x", pady=(0, 14))

        # Score cards
        for label, attr, color in [
            ("SCORE",     "score_lbl",     TEXT_GOLD),
            ("TREASURES", "treasure_lbl",  TEXT_GOLD),
            ("MOVES",     "moves_lbl",     TEXT_CYAN),
        ]:
            card = tk.Frame(left, bg=PANEL_BG, bd=0,
                            highlightthickness=1, highlightbackground=CELL_BORDER)
            card.pack(fill="x", pady=4)
            tk.Label(card, text=label, font=(FONT, 8), bg=PANEL_BG, fg=TEXT_DIM).pack(pady=(8,0))
            lbl = tk.Label(card, text="0", font=(FONT, 22, "bold"), bg=PANEL_BG, fg=color)
            lbl.pack(pady=(0, 8))
            setattr(self, attr, lbl)

        tk.Frame(left, bg=CELL_BORDER, height=1).pack(fill="x", pady=12)

        # Legend
        tk.Label(left, text="LEGEND", font=(FONT, 8), bg=BG, fg=TEXT_DIM).pack(anchor="w")
        for sym, desc, clr in [
            ("◆", "Treasure  +10 pts", TEXT_GOLD),
            ("✦", "Trap  −15 pts",     TEXT_RED),
            ("●", "Player",            TEXT_CYAN),
            ("·", "Path trail",        PATH_CLR),
        ]:
            row = tk.Frame(left, bg=BG)
            row.pack(anchor="w", pady=1)
            tk.Label(row, text=sym, font=(FONT, 12, "bold"), bg=BG, fg=clr, width=3).pack(side="left")
            tk.Label(row, text=desc, font=(FONT2, 9), bg=BG, fg=TEXT_DIM).pack(side="left")

        tk.Frame(left, bg=CELL_BORDER, height=1).pack(fill="x", pady=12)

        # Speed slider
        tk.Label(left, text="AI SPEED", font=(FONT, 8), bg=BG, fg=TEXT_DIM).pack(anchor="w")
        spd_row = tk.Frame(left, bg=BG)
        spd_row.pack(fill="x", pady=(4, 10))
        tk.Label(spd_row, text="Fast", font=(FONT2, 8), bg=BG, fg=TEXT_DIM).pack(side="left")
        tk.Scale(spd_row, from_=80, to=800, orient="horizontal",
                 variable=self.speed_var, bg=BG, fg=TEXT_LIGHT,
                 troughcolor=PANEL_BG, highlightthickness=0,
                 showvalue=False, sliderlength=14).pack(side="left", fill="x", expand=True, padx=4)
        tk.Label(spd_row, text="Slow", font=(FONT2, 8), bg=BG, fg=TEXT_DIM).pack(side="right")

        # Show scores checkbox
        tk.Checkbutton(left, text="Show cell scores", font=(FONT2, 9),
                       variable=self.show_scores_var, bg=BG, fg=TEXT_DIM,
                       activebackground=BG, selectcolor=PANEL_BG,
                       command=self._redraw_grid).pack(anchor="w")

        # Buttons
        tk.Frame(left, bg=CELL_BORDER, height=1).pack(fill="x", pady=10)
        self._btn(left, "▶  Auto Play", self.toggle_auto, BTN_PRIMARY, BTN_HOVER, "auto_btn")
        self._btn(left, "↻  New Game",  self.new_game,    BTN_SECOND,  BTN_SEC_HOV)
        self._btn(left, "⟳  Step",      self.step_ai,     BTN_SECOND,  BTN_SEC_HOV)

        # ── center: grid ──
        center = tk.Frame(self.root, bg=BG)
        center.pack(side="left", padx=10, pady=18)

        canvas_size = GRID_SIZE * CELL_PX + (GRID_SIZE + 1) * PADDING + 2
        self.canvas = tk.Canvas(center, width=canvas_size, height=canvas_size,
                                bg=BG, highlightthickness=2,
                                highlightbackground="#7C3AED")
        self.canvas.pack()

        # ── right panel: log ──
        right = tk.Frame(self.root, bg=BG, width=200)
        right.pack(side="left", fill="y", padx=(6, 18), pady=18)
        right.pack_propagate(False)

        tk.Label(right, text="AI LOG", font=(FONT, 10, "bold"),
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 6))
        tk.Frame(right, bg=CELL_BORDER, height=1).pack(fill="x", pady=(0, 8))

        self.log_frame = tk.Frame(right, bg=BG)
        self.log_frame.pack(fill="both", expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var,
                                   font=(FONT2, 11, "bold"),
                                   bg=PANEL_BG, fg=TEXT_CYAN, pady=6)
        self.status_bar.pack(side="bottom", fill="x")

    def _btn(self, parent, text, cmd, bg, hover_bg, attr_name=None):
        b = tk.Button(parent, text=text, font=(FONT2, 10, "bold"),
                      bg=bg, fg=TEXT_LIGHT, relief="flat", bd=0,
                      padx=8, pady=7, cursor="hand2", command=cmd)
        b.pack(fill="x", pady=3)
        b.bind("<Enter>", lambda e: b.config(bg=hover_bg))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        if attr_name:
            setattr(self, attr_name, b)

    # ── Game Setup ─────────────────────────────────────────────────────────────

    def new_game(self):
        if self.auto_job:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None
        self.auto_run  = False
        if hasattr(self, 'auto_btn'):
            self.auto_btn.config(text="▶  Auto Play", bg=BTN_PRIMARY)

        self.score      = 0
        self.moves      = 0
        self.collected  = 0
        self.alive      = True
        self.path_trail = []
        self.visited    = set()
        self.step_log   = []

        self._gen_grid()
        self.player_pos = (0, 0)
        self.visited.add(self.player_pos)

        self._update_stats()
        self._redraw_grid()
        self._clear_log()
        self._log("Game started!", TEXT_GREEN)
        self._log(f"Find {self.TREASURES} treasures", TEXT_GOLD)
        self._log("Avoid the traps!", TEXT_RED)
        self.status_var.set("Ready — Step or Auto Play")

    def _gen_grid(self):
        self.grid = [[{"type": "empty", "score": 0} for _ in range(GRID_SIZE)]
                     for _ in range(GRID_SIZE)]
        placed = {(0, 0)}
        for _ in range(self.TREASURES):
            pos = self._rand_empty(placed)
            if pos:
                r, c = pos
                self.grid[r][c] = {"type": "treasure", "score": 10}
                placed.add(pos)
        for _ in range(self.TRAPS):
            pos = self._rand_empty(placed)
            if pos:
                r, c = pos
                self.grid[r][c] = {"type": "trap", "score": -15}
                placed.add(pos)
        # assign heuristic scores to empty cells (proximity to treasure)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c]["type"] == "empty":
                    self.grid[r][c]["score"] = self._proximity_score(r, c)

    def _rand_empty(self, used):
        candidates = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                      if (r, c) not in used]
        return random.choice(candidates) if candidates else None

    def _proximity_score(self, row, col):
        best = 0
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c]["type"] == "treasure":
                    d = abs(r - row) + abs(c - col)
                    val = max(0, 8 - d)
                    best = max(best, val)
        return best

    # ── Hill Climbing ──────────────────────────────────────────────────────────

    def heuristic(self, pos):
        """
        Hill Climbing heuristic:
        For each unvisited neighbor, score = cell_score + proximity_to_nearest_treasure
        We climb to the neighbor with the highest score.
        """
        r, c = pos
        score = self.grid[r][c]["score"]
        # add distance bonus toward nearest treasure
        nearest = self._dist_to_nearest_treasure(r, c)
        dist_bonus = max(0, 10 - nearest) if nearest < 999 else -5
        return score + dist_bonus

    def _dist_to_nearest_treasure(self, row, col):
        best = 999
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c]["type"] == "treasure":
                    d = abs(r - row) + abs(c - col)
                    best = min(best, d)
        return best

    def hill_climbing_step(self):
        """Return the best neighbor position using Hill Climbing."""
        r, c = self.player_pos
        neighbors = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                h = self.heuristic((nr, nc))
                # penalty for already visited
                if (nr, nc) in self.visited:
                    h -= 8
                neighbors.append(((nr, nc), h))

        if not neighbors:
            return None

        neighbors.sort(key=lambda x: x[1], reverse=True)
        best_pos, best_h = neighbors[0]

        # Log top choices
        for pos, h in neighbors[:3]:
            pr, pc = pos
            cell_type = self.grid[pr][pc]["type"]
            icon = "◆" if cell_type == "treasure" else ("✦" if cell_type == "trap" else "·")
            tag  = " ← chosen" if pos == best_pos else ""
            self._log(f"  {icon}({pr},{pc}) h={h:.1f}{tag}",
                      TEXT_GOLD if cell_type == "treasure" else
                      (TEXT_RED if cell_type == "trap" else TEXT_DIM))
        return best_pos

    def step_ai(self):
        if not self.alive:
            self.status_var.set("Game over — start a new game")
            return
        all_gone = all(
            self.grid[r][c]["type"] != "treasure"
            for r in range(GRID_SIZE) for c in range(GRID_SIZE)
        )
        if all_gone:
            self._win()
            return

        self._log(f"Move {self.moves + 1}", TEXT_CYAN)
        next_pos = self.hill_climbing_step()
        if next_pos is None:
            self.status_var.set("AI is stuck!")
            return

        self.path_trail.append(self.player_pos)
        if len(self.path_trail) > 30:
            self.path_trail.pop(0)

        self.player_pos = next_pos
        self.visited.add(next_pos)
        self.moves += 1

        nr, nc = next_pos
        cell = self.grid[nr][nc]

        if cell["type"] == "treasure":
            self.score     += 10
            self.collected += 1
            self.grid[nr][nc] = {"type": "empty", "score": 0}
            self._log(f"  ★ Treasure! +10", TEXT_GOLD)
            self.status_var.set(f"💰 Treasure collected! ({self.collected}/{self.TREASURES})")
            self._flash(nr, nc, TEXT_GOLD)
        elif cell["type"] == "trap":
            self.score -= 15
            self._log(f"  ✖ TRAP! −15", TEXT_RED)
            self.status_var.set("💥 Hit a trap! −15 pts")
            self._flash(nr, nc, TEXT_RED)
        else:
            self.status_var.set(f"Move {self.moves} — Hill Climbing")

        self._update_stats()
        self._redraw_grid()

        all_gone2 = all(
            self.grid[r][c]["type"] != "treasure"
            for r in range(GRID_SIZE) for c in range(GRID_SIZE)
        )
        if all_gone2:
            self.root.after(400, self._win)

    def _flash(self, r, c, color):
        x1 = PADDING + c * (CELL_PX + PADDING)
        y1 = PADDING + r * (CELL_PX + PADDING)
        x2, y2 = x1 + CELL_PX, y1 + CELL_PX
        rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        self.root.after(180, lambda: self.canvas.delete(rect))

    def _win(self):
        self.auto_run = False
        if self.auto_job:
            self.root.after_cancel(self.auto_job)
        self._log("", "")
        self._log("🏆 ALL TREASURES!", TEXT_GOLD)
        self._log(f"Final score: {self.score}", TEXT_GOLD)
        self.status_var.set(f"🏆 You win!  Score: {self.score}  Moves: {self.moves}")

    def toggle_auto(self):
        self.auto_run = not self.auto_run
        if self.auto_run:
            self.auto_btn.config(text="⏹  Stop", bg="#E94560")
            self._auto_loop()
        else:
            self.auto_btn.config(text="▶  Auto Play", bg=BTN_PRIMARY)
            if self.auto_job:
                self.root.after_cancel(self.auto_job)

    def _auto_loop(self):
        if not self.auto_run:
            return
        all_gone = all(
            self.grid[r][c]["type"] != "treasure"
            for r in range(GRID_SIZE) for c in range(GRID_SIZE)
        )
        if all_gone or not self.alive:
            self.auto_run = False
            self.auto_btn.config(text="▶  Auto Play", bg=BTN_PRIMARY)
            return
        self.step_ai()
        self.auto_job = self.root.after(self.speed_var.get(), self._auto_loop)

    # ── Drawing ────────────────────────────────────────────────────────────────

    def _redraw_grid(self):
        self.canvas.delete("all")
        pr, pc = self.player_pos

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x1 = PADDING + c * (CELL_PX + PADDING)
                y1 = PADDING + r * (CELL_PX + PADDING)
                x2, y2 = x1 + CELL_PX, y1 + CELL_PX
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                is_player  = (r, c) == (pr, pc)
                is_trail   = (r, c) in self.path_trail
                is_visited = (r, c) in self.visited

                cell = self.grid[r][c]

                # background
                if is_player:
                    bg_fill = "#0D2A3A"
                elif is_trail:
                    bg_fill = PATH_CLR
                elif is_visited:
                    bg_fill = VISITED_CLR
                else:
                    bg_fill = CELL_BG

                self.canvas.create_rectangle(x1, y1, x2, y2,
                    fill=bg_fill, outline=CELL_BORDER, width=1)

                # cell content
                if is_player:
                    # player glow ring
                    self.canvas.create_oval(x1+6, y1+6, x2-6, y2-6,
                        fill="#0A3A50", outline=PLAYER_CLR, width=2)
                    self.canvas.create_text(cx, cy, text="●",
                        font=(FONT2, 18, "bold"), fill=PLAYER_CLR)
                elif cell["type"] == "treasure":
                    self.canvas.create_text(cx, cy, text="◆",
                        font=(FONT2, 20, "bold"), fill=TREASURE_CLR)
                elif cell["type"] == "trap":
                    self.canvas.create_text(cx, cy, text="✦",
                        font=(FONT2, 18, "bold"), fill=TRAP_CLR)
                else:
                    if is_trail:
                        self.canvas.create_text(cx, cy + 4, text="·",
                            font=(FONT2, 22, "bold"), fill="#3A6A8A")

                # score overlay
                if self.show_scores_var.get() and not is_player and cell["type"] == "empty":
                    s = cell["score"]
                    if s > 0:
                        self.canvas.create_text(x1+4, y1+4, text=str(s),
                            anchor="nw", font=(FONT, 7), fill="#4A7A9A")

                # coordinates (tiny)
                self.canvas.create_text(x2-4, y2-3, text=f"{r},{c}",
                    anchor="se", font=(FONT, 6), fill="#2A2A4A")

        # player highlight border
        x1 = PADDING + pc * (CELL_PX + PADDING)
        y1 = PADDING + pr * (CELL_PX + PADDING)
        x2, y2 = x1 + CELL_PX, y1 + CELL_PX
        self.canvas.create_rectangle(x1-1, y1-1, x2+1, y2+1,
            fill="", outline=PLAYER_CLR, width=2)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _update_stats(self):
        self.score_lbl.config(text=str(self.score))
        self.treasure_lbl.config(text=f"{self.collected}/{self.TREASURES}")
        self.moves_lbl.config(text=str(self.moves))

    def _log(self, msg, color=TEXT_DIM):
        if len(self.step_log) > 28:
            oldest = self.step_log.pop(0)
            oldest.destroy()
        if msg == "":
            return
        lbl = tk.Label(self.log_frame, text=msg, font=(FONT, 8),
                       bg=BG, fg=color, anchor="w", justify="left")
        lbl.pack(fill="x", pady=0)
        self.step_log.append(lbl)

    def _clear_log(self):
        for w in self.step_log:
            w.destroy()
        self.step_log = []


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    total = GRID_SIZE * CELL_PX + (GRID_SIZE + 1) * PADDING + 2
    root.geometry(f"860x{total + 80}")
    app = GreedyTreasureGame(root)
    root.mainloop()
