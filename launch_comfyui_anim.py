import os, sys, time, shutil, random, json

# ------------------------------------------------------------
# ANSI colour / style definitions (no external dependencies)
# ------------------------------------------------------------
# Enable VT processing on Windows (enables ANSI colours)
if os.name == 'nt':
    os.system('')   # enables VT processing in conhost.exe

# Basic colours
RESET   = '\x1b[0m'
WHITE   = '\x1b[37m'
GREY    = '\x1b[90m'          # bright black = grey on most terminals
LIME    = '\x1b[38;5;46m'     # bright lime‑green

# Options‑menu highlighting (matches original colorama values)
ACTIVE  = '\x1b[1m\x1b[48;5;15m\x1b[38;5;93m'   # bold, white bg, bright yellow fg
PREV    = '\x1b[48;5;237m\x1b[38;5;226m'        # dark grey bg, yellow fg
TITLE   = '\x1b[4m\x1b[38;5;240m'               # underline, grey fg

# ------------------------------------------------------------
# Configuration defaults (used when JSON does not exist or is malformed)
# ------------------------------------------------------------
DEFAULT_CONFIG = {
    "main_path": "ComfyUI\\main.py",
    "args": [
        "--windows-standalone-build",
        "--disable-auto-launch",
        "--use-sage-attention",
        "--async-offload",
        "--disable-api-nodes"
#       ("--cache-lru", "10"),
#       "--normalvram",
#       "--lowvram",
#       "--cache-none",
#       "--disable-smart-memory",
        "--enable-dynamic-vram",
    ],
    "unet": "",
    "text_enc": "",
    "vae": ""
}

# ------------------------------------------------------------
# Visual animation constants
# ------------------------------------------------------------
TARGET = "ComfyUI"
CHARSET = list("|/-\\*+#@%")
FRAME_DELAY = 0.03
SETTLE_MAX_FRAMES = 30
MIN_FRAMES_BEFORE_SETTLE = 5
FINAL_DISPLAY_TIME = 1.5

# ------------------------------------------------------------
# Tiny bitmap font (5 rows high) – replaces pyfiglet
# ------------------------------------------------------------
_FONT_5X = {
    "C": [" ███ ", "█   █", "█    ", "█   █", " ███ "],
    "O": [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    "M": ["█   █", "██ ██", "█ █ █", "█   █", "█   █"],
    "F": ["█████", "█    ", "███  ", "█    ", "█    "],
    "Y": ["█   █", "█   █", " █ █ ", "  █  ", "  █  "],
    "U": ["█   █", "█   █", "█   █", "█   █", " ███ "],
    "I": [" ███ ", "  █  ", "  █  ", "  █  ", " ███ "],
    " ": ["     ", "     ", "     ", "     ", "     "],
}

def _char_to_rows(ch: str) -> list[str]:
    """Return the 5‑row bitmap for a single uppercase character."""
    return _FONT_5X.get(ch.upper(), _FONT_5X[" "])

def figlet_render(word: str, font: str = "slant") -> list[str]:
    """
    Mimic pyfiglet.figlet_format(word, font=font) → list of strings.
    We ignore the *font* argument and just use our built‑in 5×5 bitmap.
    The function returns the lines **without** trailing newline.
    """
    rows = ["" for _ in range(5)]          # we have 5 rows
    for ch in word:
        char_rows = _char_to_rows(ch)
        for i, r in enumerate(char_rows):
            rows[i] += r + " "              # one space between letters
    # strip trailing spaces that belong to the inter‑letter gap
    return [r.rstrip() for r in rows]

def normalize(lines):
    if not lines:
        return []
    w = max(len(l) for l in lines)
    return [l.ljust(w) for l in lines]

# ------------------------------------------------------------
# Helper utilities
# ------------------------------------------------------------
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ------------------------------------------------------------
# Animation (cursor hidden during the random‑character phase)
# ------------------------------------------------------------
def animate_reveal():
    raw = figlet_render(TARGET)
    fig = normalize(raw)
    h, w = len(fig), len(fig[0]) if fig else (0, 0)

    settled = [[False] * w for _ in range(h)]
    target  = [[fig[r][c] for c in range(w)] for r in range(h)]

    # pre‑mark spaces as already settled
    for r in range(h):
        for c in range(w):
            if target[r][c] == " ":
                settled[r][c] = True

    rand = [[random.choice(CHARSET) for _ in range(w)] for _ in range(h)]
    elapsed = [[0] * w for _ in range(h)]
    settle_at = [[random.randint(MIN_FRAMES_BEFORE_SETTLE, SETTLE_MAX_FRAMES) for _ in range(w)]
                for _ in range(h)]

    TOP_MARGIN = 4  # blank lines above the logo

    # Hide cursor during the random‑character animation to reduce flicker
    print('\x1b[?25l', end='')  # hide cursor
    while True:
        any_unsettled = False
        for r in range(h):
            for c in range(w):
                if not settled[r][c]:
                    any_unsettled = True
                    elapsed[r][c] += 1
                    rand[r][c] = random.choice(CHARSET)
                    if elapsed[r][c] >= settle_at[r][c]:
                        settled[r][c] = True
        if not any_unsettled:
            break

        clear_screen()
        print("\n" * TOP_MARGIN, end="")  # top padding
        for r in range(h):
            line = []
            for c in range(w):
                if settled[r][c]:
                    ch, col = target[r][c], WHITE
                else:
                    ch, col = rand[r][c], GREY
                line.append(f"{col}{ch}{RESET}" if ch != " " else " ")
            print(''.join(line).center(shutil.get_terminal_size((80, 20)).columns))
        time.sleep(FRAME_DELAY)

    # Show cursor again and display the final lime‑green logo
    print('\x1b[?25h', end='')  # show cursor
    clear_screen()
    print("\n" * TOP_MARGIN, end="")
    for r in range(h):
        line = []
        for c in range(w):
            ch = target[r][c]
            line.append(f"{LIME}{ch}{RESET}" if ch != " " else " ")
        print(''.join(line).center(shutil.get_terminal_size((80, 20)).columns))
    time.sleep(FINAL_DISPLAY_TIME)

# ------------------------------------------------------------
# Configuration handling
# ------------------------------------------------------------
def load_config(path="Comfylaunchconfig.json") -> dict:
    if not os.path.isfile(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    # ensure required keys exist & correct types
    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)
    if not isinstance(cfg.get("args"), list):
        cfg["args"] = DEFAULT_CONFIG["args"].copy()
    for key in ["main_path", "unet", "text_enc", "vae"]:
        if not isinstance(cfg.get(key), str):
            cfg[key] = DEFAULT_CONFIG[key]
    return cfg

def save_config(cfg: dict, path="Comfylaunchconfig.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

# ------------------------------------------------------------
# Menu for selecting precision flags
# ------------------------------------------------------------
def options_menu(cfg: dict, config_path="Comfylaunchconfig.json") -> dict:
    unet_opts = [
        "--fp32-unet", "--fp64-unet", "--bf16-unet", "--fp16-unet",
        "--fp8_e4m3fn-unet", "--fp8_e5m2-unet", "--fp8_e8m0fnu-unet", "(none)"
    ]
    txt_opts = [
        "--fp8_e4m3fn-text-enc", "--fp8_e5m2-text-enc",
        "--fp16-text-enc", "--fp32-text-enc", "--bf16-text-enc", "(none)"
    ]
    vae_opts = [
        "--fp16-vae", "--fp32-vae", "--bf16-vae", "--cpu-vae", "(none)"
    ]

    def idx_for(opt_list, stored):
        if not stored:
            return opt_list.index("(none)")
        try:
            return opt_list.index(stored)
        except ValueError:
            return opt_list.index("(none)")

    idx_unet = idx_for(unet_opts, cfg.get("unet", ""))
    idx_txt  = idx_for(txt_opts,  cfg.get("text_enc", ""))
    idx_vae  = idx_for(vae_opts,  cfg.get("vae", ""))
    col = 0   # 0=unet, 1=text, 2=vae

    def fmt_cell(text, width, active, previous):
        if text is None:
            return " " * width
        pad = " " * max(0, width - len(text))
        if active:
            return ACTIVE + text + RESET + pad
        if previous:
            return PREV + text + RESET + pad
        return text + pad

    while True:
        os.system('cls')
        col_w = 30
        title_line = (
            TITLE + "UNET OPTIONS".ljust(col_w) +
            TITLE + "TEXT ENCODER OPTIONS".ljust(col_w) +
            TITLE + "VAE OPTIONS".ljust(col_w) + RESET
        )
        print(" " + title_line)
        rows = max(len(unet_opts), len(txt_opts), len(vae_opts))
        for i in range(rows):
            left = fmt_cell(unet_opts[i] if i < len(unet_opts) else None,
                            col_w, col == 0 and i == idx_unet, i == idx_unet)
            mid  = fmt_cell(txt_opts[i] if i < len(txt_opts) else None,
                            col_w, col == 1 and i == idx_txt,  i == idx_txt)
            right = fmt_cell(vae_opts[i] if i < len(vae_opts) else None,
                             col_w, col == 2 and i == idx_vae, i == idx_vae)
            print(" " + left + mid + right)

        print()
        print("Current command preview:")
        preview_cfg = cfg.copy()
        preview_cfg["unet"]    = "" if unet_opts[idx_unet]    == "(none)" else unet_opts[idx_unet]
        preview_cfg["text_enc"]= "" if txt_opts[idx_txt]   == "(none)" else txt_opts[idx_txt]
        preview_cfg["vae"]     = "" if vae_opts[idx_vae]   == "(none)" else vae_opts[idx_vae]
        print(" " + build_command(preview_cfg))
        print("\nNavigate with Arrow keys, Enter to confirm, Esc to cancel.")
        import msvcrt
        key = msvcrt.getch()
        if key == b"\xe0":              # special prefix
            key = msvcrt.getch()
        if key == b"H":                 # up
            if col == 0:   idx_unet = (idx_unet - 1) % len(unet_opts)
            elif col == 1: idx_txt  = (idx_txt  - 1) % len(txt_opts)
            else:          idx_vae  = (idx_vae  - 1) % len(vae_opts)
        elif key == b"P":               # down
            if col == 0:   idx_unet = (idx_unet + 1) % len(unet_opts)
            elif col == 1: idx_txt  = (idx_txt  + 1) % len(txt_opts)
            else:          idx_vae  = (idx_vae  + 1) % len(vae_opts)
        elif key == b"K":               # left
            col = (col - 1) % 3
        elif key == b"M":               # right
            col = (col + 1) % 3
        elif key == b"\r":              # Enter → save and exit
            cfg["unet"]    = "" if unet_opts[idx_unet]    == "(none)" else unet_opts[idx_unet]
            cfg["text_enc"]= "" if txt_opts[idx_txt]   == "(none)" else txt_opts[idx_txt]
            cfg["vae"]     = "" if vae_opts[idx_vae]   == "(none)" else vae_opts[idx_vae]
            save_config(cfg, config_path)
            return cfg
        elif key == b"\x1b":            # Esc → cancel
            return cfg

# ------------------------------------------------------------
# Build full command line from config
# ------------------------------------------------------------
def build_command(cfg: dict) -> str:
    python_exe = os.path.join(".", "python_embeded", "python.exe")
    if not os.path.isfile(python_exe):
        python_exe = sys.executable
    parts = [python_exe, "-s", cfg.get("main_path", "ComfyUI\\main.py")]
    parts.extend(cfg.get("args", []))
    for key in ["unet", "text_enc", "vae"]:
        val = cfg.get(key, "")
        if val:
            parts.append(val)
    return " ".join(parts)

# ------------------------------------------------------------
# Preview & wait for user action
# ------------------------------------------------------------
def preview_and_wait(cfg_path="Comfylaunchconfig.json") -> dict:
    cfg = load_config(cfg_path)
    while True:
        clear_screen()
        animate_reveal()
        cmd = build_command(cfg)
        print("\nPreview command (read‑only):")
        print("\033[38;5;240m" + cmd + "\033[0m")
        print("\nPress any key to launch, or 'O' to open options menu.")
        key = getch()
        if key is None:
            continue
        if key.lower() == 'o':
            cfg = options_menu(cfg, cfg_path)   # may modify cfg
        else:
            return cfg

# ------------------------------------------------------------
# Launch ComfyUI
# ------------------------------------------------------------
def launch_comfyui(cfg: dict):
    python_exe = os.path.join(".", "python_embeded", "python.exe")
    if not os.path.isfile(python_exe):
        python_exe = sys.executable
    cmd_parts = [python_exe, "-s", cfg.get("main_path", "ComfyUI\\main.py")]
    cmd_parts.extend(cfg.get("args", []))
    for key in ["unet", "text_enc", "vae"]:
        val = cfg.get(key, "")
        if val:
            cmd_parts.append(val)

    env = os.environ.copy()
    env["PYTHONNOUSERSITE"] = "1"
    subprocess.Popen(
        cmd_parts,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=os.getcwd(),
        env=env
    )

# ------------------------------------------------------------
# Cross‑platform single‑character input
# ------------------------------------------------------------
def getch():
    try:
        import termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch
    except Exception:
        import msvcrt
        ch = msvcrt.getch()
        if ch in {b"\x00", b"\xe0"}:
            msvcrt.getch()
            return None
        return ch.decode('utf-8', errors='ignore')

# ------------------------------------------------------------
# Locate the ComfyUI root directory (contains python_embeded & ComfyUI)
# ------------------------------------------------------------
def find_comfyui_root(start_path: str) -> str | None:
    cur = os.path.abspath(start_path)
    for _ in range(4):
        if os.path.isdir(os.path.join(cur, "python_embeded")) and os.path.isdir(os.path.join(cur, "ComfyUI")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return None

# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = find_comfyui_root(script_dir)
    if not root:
        print("Error: Could not locate the ComfyUI root directory (needs python_embeded and ComfyUI folders).")
        input("Press Enter to exit...")
        return
    os.chdir(root)
    print(f"Changed to ComfyUI directory: {root}")

    try:
        cfg = preview_and_wait()
        launch_comfyui(cfg)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()