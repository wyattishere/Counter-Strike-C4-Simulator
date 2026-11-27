import math
import random
import tkinter as tk

BOMB_CODE = "".join(str(random.randint(0, 9)) for _ in range(7))
AUTO_GUESS_DELAY_MS = 100
BOMB_TIMER_SECONDS = 20
current_input = ""
is_planted = False
is_defused = False
is_detonated = False
defuse_window = None
wave_monitor_window = None
wave_monitor_canvases = []
wave_animation_job_id = None
bomb_code_window = None
bomb_timer_window = None
bomb_timer_job_id = None
pending_reset_id = None


def update_display():
  masked = current_input.ljust(7, "*")
  display_var.set(masked)


def wave_frequency(position):
  if position <= 2:
    return position
  return 2 + (position - 2) * 2


def on_key_press(key):
  global current_input, is_planted, pending_reset_id

  if is_planted or is_defused:
    return

  if pending_reset_id is not None:
    root.after_cancel(pending_reset_id)
    pending_reset_id = None
    display.config(fg="#39ff14")
    status_label.config(text="ENTER CODE (* CLEAR | # ENTER)", fg="#888888")

  if key == "*":
    current_input = ""
    display.config(fg="#39ff14")
    update_display()

  elif key == "#":
    if current_input == BOMB_CODE:
      plant_bomb()
    else:
      current_input = ""
      display.config(fg="#ff3b30")
      status_label.config(text="INVALID CODE", fg="#ff3b30")
      update_display()
      pending_reset_id = root.after(600, reset_keypad)

  else:
    if len(current_input) < 7:
      current_input += key
      update_display()


def plant_bomb():
  global is_planted, pending_reset_id, bomb_code_window
  if pending_reset_id is not None:
    root.after_cancel(pending_reset_id)
    pending_reset_id = None
  if bomb_code_window and bomb_code_window.winfo_exists():
    bomb_code_window.destroy()
  bomb_code_window = None
  is_planted = True
  display_var.set("*******")
  display.config(fg="#ff3b30")
  status_label.config(text="BOMB HAS BEEN PLANTED", fg="#ff3b30")
  defuse_btn.place(x=8, y=8)
  start_bomb_timer()


def start_bomb_timer():
  global bomb_timer_window
  bomb_timer_window = tk.Toplevel(root)
  bomb_timer_window.title("Bomb Timer")
  bomb_timer_window.configure(bg="#16181a")
  bomb_timer_window.resizable(False, False)
  bomb_timer_window.attributes("-topmost", True)
  bomb_timer_window.update_idletasks()
  x = (bomb_timer_window.winfo_screenwidth() - 240) // 2
  bomb_timer_window.geometry(f"240x80+{x}+20")

  timer_label = tk.Label(
      bomb_timer_window,
      font=("Courier", 18, "bold"),
      bg="#16181a",
      fg="#ff3b30",
  )
  timer_label.pack(expand=True, fill="both", padx=10, pady=10)
  update_bomb_timer(BOMB_TIMER_SECONDS, timer_label)


def flatline_wave_monitor():
  global wave_animation_job_id
  if wave_animation_job_id is not None and wave_monitor_window:
    if wave_monitor_window.winfo_exists():
      wave_monitor_window.after_cancel(wave_animation_job_id)
  wave_animation_job_id = None

  for canvas in wave_monitor_canvases:
    if canvas.winfo_exists():
      canvas.delete("signal")
      canvas.create_line(0, 15, 460, 15, fill="#00e5ff", width=2, tags="signal")
      canvas.create_line(0, 21, 460, 21, fill="#ff3b30", width=2, tags="signal")


def close_defusal_windows():
  global defuse_window, wave_monitor_window
  if wave_monitor_window and wave_monitor_window.winfo_exists():
    wave_monitor_window.destroy()
  if defuse_window and defuse_window.winfo_exists():
    defuse_window.destroy()
  wave_monitor_window = None
  defuse_window = None


def update_bomb_timer(seconds_left, timer_label):
  global bomb_timer_job_id, defuse_window, is_detonated
  if seconds_left <= 0:
    is_detonated = True
    timer_label.config(text="BOMB DETONATED!", fg="#ff3b30")
    status_label.config(text="BOMB DETONATED", fg="#ff3b30")
    flatline_wave_monitor()
    root.after(280, close_defusal_windows)
    bomb_timer_job_id = root.after(2500, root.destroy)
    return

  timer_label.config(
      text=f"DETONATION IN {seconds_left:02d}",
      fg="#ff3b30" if seconds_left <= 5 else "#ff9f0a",
  )
  bomb_timer_job_id = root.after(
      1000, lambda: update_bomb_timer(seconds_left - 1, timer_label)
  )


def stop_bomb_timer():
  global bomb_timer_window, bomb_timer_job_id
  if bomb_timer_job_id is not None:
    root.after_cancel(bomb_timer_job_id)
    bomb_timer_job_id = None
  if bomb_timer_window and bomb_timer_window.winfo_exists():
    bomb_timer_window.destroy()
  bomb_timer_window = None


def bomb_defused():
  global is_defused, defuse_window, pending_reset_id
  if is_detonated:
    return
  if pending_reset_id is not None:
    root.after_cancel(pending_reset_id)
    pending_reset_id = None
  is_defused = True
  display_var.set(BOMB_CODE)
  display.config(fg="#00e5ff")
  status_label.config(text="BOMB HAS BEEN DEFUSED", fg="#00e5ff")
  defuse_btn.place_forget()
  stop_bomb_timer()
  if defuse_window and defuse_window.winfo_exists():
    defuse_window.destroy()
  root.after(3500, root.destroy)


def reset_keypad():
  global current_input, is_planted, is_defused, defuse_window, pending_reset_id
  if is_detonated:
    return
  if pending_reset_id is not None:
    root.after_cancel(pending_reset_id)
    pending_reset_id = None
  stop_bomb_timer()
  current_input = ""
  is_planted = False
  is_defused = False
  display.config(fg="#39ff14")
  status_label.config(text="ENTER CODE (* CLEAR | # ENTER)", fg="#888888")
  defuse_btn.place_forget()
  if defuse_window and defuse_window.winfo_exists():
    defuse_window.destroy()
  update_display()


def open_defuse_window():
  global defuse_window, wave_monitor_window, wave_monitor_canvases
  global wave_animation_job_id
  if defuse_window and defuse_window.winfo_exists():
    defuse_window.focus()
    if wave_monitor_window and wave_monitor_window.winfo_exists():
      wave_monitor_window.deiconify()
      wave_monitor_window.lift()
    return

  defuse_window = tk.Toplevel(root)
  defuse_window.title("Defusal Kit")
  defuse_window.geometry("510x300")
  defuse_window.configure(bg="#16181a")
  defuse_window.resizable(False, False)

  defuse_status = tk.Label(
      defuse_window,
      text="STEP 1: ALIGN ALL 7 SLIDERS TO THE CYAN MARKERS",
      font=("Courier", 10, "bold"),
      bg="#16181a",
      fg="#ff9f0a",
  )
  defuse_status.pack(pady=(15, 10))

  grid_frame = tk.Frame(defuse_window, bg="#16181a")
  grid_frame.pack(pady=5)

  entries = []
  sliders = []
  defuse_code = "".join(str(random.randint(0, 9)) for _ in range(7))
  target_notches = [random.randint(1, 5) for _ in range(7)]
  locked = [False] * 7
  sliders_aligned = False
  slider_guess_running = False
  slider_guess_job_id = None
  auto_running = False
  auto_job_id = None
  defuse_scheduled = False

  def check_all_solved():
    nonlocal defuse_scheduled
    if all(locked) and not defuse_scheduled:
      defuse_scheduled = True
      defuse_status.config(text="DECRYPTION COMPLETE", fg="#39ff14")
      auto_btn.config(state="disabled")
      manual_btn.config(state="disabled")
      defuse_window.after(400, bomb_defused)

  def auto_guess_step(idx=0):
    nonlocal auto_job_id, auto_running
    if (
        not defuse_window.winfo_exists()
        or is_defused
        or is_detonated
        or not auto_running
    ):
      return

    while idx < 7 and locked[idx]:
      idx += 1

    if idx >= 7:
      check_all_solved()
      return

    guess = str(random.randint(0, 9))
    entries[idx].config(state="normal")
    entries[idx].delete(0, tk.END)
    entries[idx].insert(0, guess)

    if guess == defuse_code[idx]:
      locked[idx] = True
      entries[idx].config(
          fg="#39ff14", state="readonly", readonlybackground="#0d1117"
      )
      check_all_solved()
      if not all(locked):
        auto_job_id = defuse_window.after(
            AUTO_GUESS_DELAY_MS, lambda: auto_guess_step(idx + 1)
        )
    else:
      entries[idx].config(fg="#ff9f0a")
      auto_job_id = defuse_window.after(
          AUTO_GUESS_DELAY_MS, lambda: auto_guess_step(idx)
      )

  def start_auto_decrypt():
    nonlocal auto_running
    if not sliders_aligned or auto_running:
      return
    auto_running = True
    defuse_status.config(text="MODE: AUTO-DECRYPT RUNNING...", fg="#00e5ff")
    auto_btn.config(bg="#005f73", fg="#00e5ff", relief="sunken")
    manual_btn.config(bg="#2b3035", fg="#aaaaaa", relief="raised")

    for i in range(7):
      if not locked[i]:
        entries[i].config(state="readonly", readonlybackground="#0d1117")
    auto_guess_step(0)

  def start_manual_decrypt():
    nonlocal auto_running, auto_job_id
    if not sliders_aligned:
      return
    auto_running = False
    if auto_job_id is not None:
      defuse_window.after_cancel(auto_job_id)
      auto_job_id = None

    defuse_status.config(text="MODE: MANUAL OVERRIDE (TYPE DIGITS)", fg="#39ff14")
    manual_btn.config(bg="#1b4332", fg="#39ff14", relief="sunken")
    auto_btn.config(bg="#2b3035", fg="#aaaaaa", relief="raised")

    first_unlocked = None
    for i in range(7):
      if not locked[i]:
        entries[i].config(state="normal", fg="white")
        if first_unlocked is None:
          first_unlocked = entries[i]
    if first_unlocked:
      defuse_window.lift()
      defuse_window.focus_set()
      defuse_window.after_idle(first_unlocked.focus_set)

  def check_sliders(*args):
    nonlocal sliders_aligned
    if sliders_aligned:
      return

    if all(sliders[i].get() == target_notches[i] for i in range(7)):
      sliders_aligned = True
      defuse_status.config(
          text="STEP 2: SELECT DECRYPTION MODE BELOW", fg="#00e5ff"
      )
      for i in range(7):
        sliders[i].config(state="disabled", troughcolor="#1b4332")

      slider_guess_btn.config(state="disabled")
      auto_btn.config(state="normal", bg="#343a40", fg="white")
      manual_btn.config(state="normal", bg="#343a40", fg="white")

  def start_slider_guess():
    nonlocal slider_guess_running
    if sliders_aligned or slider_guess_running or is_detonated:
      return

    slider_guess_running = True
    slider_guess_btn.config(state="disabled", bg="#005f73", fg="#00e5ff")
    defuse_status.config(text="MODE: AUTO SLIDER SWEEPING LEFT TO RIGHT...", fg="#00e5ff")

    for slider in sliders:
      slider.config(state="disabled")

    sweep_slider()

  def sweep_slider(idx=0):
    nonlocal slider_guess_running, slider_guess_job_id
    if (
        not defuse_window.winfo_exists()
        or is_detonated
        or not slider_guess_running
    ):
      return

    if idx >= len(sliders):
      slider_guess_running = False
      check_sliders()
      return

    slider = sliders[idx]
    current_value = slider.get()
    if current_value == target_notches[idx]:
      defuse_status.config(
          text=f"AUTO SLIDER: {idx + 1}/7 LOCKED", fg="#00e5ff"
      )
      slider_guess_job_id = defuse_window.after(
          120, lambda: sweep_slider(idx + 1)
      )
      return

    defuse_status.config(
        text=f"AUTO SLIDER: SWEEPING {idx + 1}/7", fg="#00e5ff"
    )
    next_value = current_value + 1 if current_value < 5 else 1
    slider.config(state="normal")
    slider.set(next_value)
    slider.config(state="disabled")
    next_idx = idx + 1 if next_value == target_notches[idx] else idx
    slider_guess_job_id = defuse_window.after(
        120, lambda: sweep_slider(next_idx)
    )

  def on_manual_type(event, idx):
    if not sliders_aligned or auto_running or is_detonated or locked[idx]:
      return "break"

    entry = entries[idx]
    if event.keysym in ("BackSpace", "Delete"):
      entry.delete(0, tk.END)
      entry.config(fg="white")
      return "break"

    char = event.char
    if not char.isdigit() and event.keysym.startswith("KP_"):
      char = event.keysym[-1]
    if not char.isdigit():
      return "break"

    entry.delete(0, tk.END)
    entry.insert(0, char)
    if char == defuse_code[idx]:
      locked[idx] = True
      entry.config(
          fg="#39ff14", state="readonly", readonlybackground="#0d1117"
      )
      for next_i in range(7):
        if not locked[next_i]:
          entries[next_i].focus_set()
          break
      check_all_solved()
    else:
      entry.config(fg="#ff3b30")
    return "break"

  for i in range(7):
    col_frame = tk.Frame(grid_frame, bg="#16181a")
    col_frame.grid(row=0, column=i, padx=6)

    marker_canvas = tk.Canvas(
        col_frame, width=48, height=18, bg="#16181a", highlightthickness=0
    )
    marker_canvas.pack(pady=(0, 4))
    marker_canvas.create_line(4, 14, 44, 14, fill="#444444", width=2)
    target_x = 4 + (target_notches[i] - 1) * 10
    marker_canvas.create_line(
        target_x - 3, 6, target_x + 3, 6, fill="#00e5ff", width=3
    )
    marker_canvas.create_line(
        target_x, 6, target_x, 14, fill="#00e5ff", width=2
    )

    ent = tk.Entry(
        col_frame,
        width=2,
        font=("Courier", 20, "bold"),
        justify="center",
        bg="#0d1117",
        fg="white",
        disabledbackground="#090b0d",
        insertbackground="white",
        bd=3,
        relief="sunken",
        state="disabled",
    )
    ent.pack(pady=4)
    ent.bind("<KeyPress>", lambda e, idx=i: on_manual_type(e, idx))
    entries.append(ent)

    sld = tk.Scale(
        col_frame,
        from_=1,
        to=5,
        orient="horizontal",
        length=48,
        sliderlength=10,
        showvalue=False,
        bg="#16181a",
        fg="white",
        troughcolor="#343a40",
        highlightthickness=0,
    )
    start_val = (target_notches[i] % 5) + 1
    sld.set(start_val)
    sld.pack(pady=(4, 0))
    sliders.append(sld)

  wave_monitor_window = tk.Toplevel(defuse_window)
  wave_monitor_window.title("Slider Wave Monitor")
  wave_monitor_window.configure(bg="#16181a")
  wave_monitor_window.resizable(False, False)

  monitor_width = 500
  monitor_height = 500
  defuse_window.update_idletasks()
  monitor_x = defuse_window.winfo_x() + defuse_window.winfo_width() + 10
  if monitor_x + monitor_width > wave_monitor_window.winfo_screenwidth():
    monitor_x = max(0, defuse_window.winfo_x() - monitor_width - 10)
  monitor_y = max(10, defuse_window.winfo_y())
  wave_monitor_window.geometry(
      f"{monitor_width}x{monitor_height}+{monitor_x}+{monitor_y}"
  )

  tk.Label(
      wave_monitor_window,
      text="SLIDER FREQUENCY MONITOR",
      font=("Courier", 12, "bold"),
      bg="#16181a",
      fg="white",
  ).pack(pady=(12, 4))

  legend = tk.Frame(wave_monitor_window, bg="#16181a")
  legend.pack(pady=(0, 8))
  tk.Label(
      legend,
      text="CYAN: MARKER",
      font=("Courier", 9, "bold"),
      bg="#16181a",
      fg="#00e5ff",
  ).pack(side="left", padx=8)
  tk.Label(
      legend,
      text="RED: CURRENT POSITION",
      font=("Courier", 9, "bold"),
      bg="#16181a",
      fg="#ff3b30",
  ).pack(side="left", padx=8)

  wave_rows = []
  for i in range(7):
    row = tk.Frame(wave_monitor_window, bg="#16181a")
    row.pack(fill="x", padx=12, pady=2)
    wave_label = tk.Label(
        row,
        text=f"SLIDER {i + 1}",
        font=("Courier", 9, "bold"),
        bg="#16181a",
        fg="white",
        anchor="w",
    )
    wave_label.pack(fill="x")
    wave_canvas = tk.Canvas(
        row,
        width=460,
        height=36,
        bg="#0d1117",
        highlightthickness=1,
        highlightbackground="#343a40",
    )
    wave_canvas.pack(fill="x")
    wave_rows.append((wave_canvas, wave_label))

  wave_monitor_canvases = [canvas for canvas, _ in wave_rows]

  def draw_wave(canvas, frequency, phase, color):
    width = 460
    height = 36
    points = []
    for sample in range(91):
      x = sample * width / 90
      y = height / 2 + math.sin(
          2 * math.pi * frequency * x / width + phase
      ) * 11
      points.extend((x, y))
    canvas.create_line(
        *points, fill=color, width=2, smooth=True, tags="signal"
    )

  wave_phase = 0.0

  def animate_wave_screens():
    nonlocal wave_phase
    global wave_animation_job_id
    if not wave_monitor_window.winfo_exists():
      return

    wave_phase = (wave_phase + 0.16) % (2 * math.pi)
    for i, (canvas, wave_label) in enumerate(wave_rows):
      marker_position = target_notches[i]
      current_position = sliders[i].get()
      wave_label.config(
          text=(
              f"SLIDER {i + 1}    MARKER: {marker_position}    "
              f"POSITION: {current_position}"
          )
      )
      canvas.delete("signal")
      draw_wave(
          canvas, wave_frequency(marker_position), wave_phase, "#00e5ff"
      )
      draw_wave(
          canvas,
          wave_frequency(current_position),
          wave_phase + 0.4,
          "#ff3b30",
      )

    wave_animation_job_id = wave_monitor_window.after(
        50, animate_wave_screens
    )

  wave_monitor_window.protocol(
      "WM_DELETE_WINDOW", wave_monitor_window.withdraw
  )
  wave_animation_job_id = wave_monitor_window.after(
      50, animate_wave_screens
  )

  btn_frame = tk.Frame(defuse_window, bg="#16181a")
  btn_frame.pack(pady=(20, 10))

  auto_btn = tk.Button(
      btn_frame,
      text="AUTO DECRYPT",
      font=("Courier", 10, "bold"),
      width=15,
      bg="#22252a",
      fg="#555555",
      state="disabled",
      bd=3,
      relief="raised",
      cursor="hand2",
      command=start_auto_decrypt,
  )
  auto_btn.grid(row=0, column=0, padx=10)

  manual_btn = tk.Button(
      btn_frame,
      text="MANUAL DECRYPT",
      font=("Courier", 10, "bold"),
      width=15,
      bg="#22252a",
      fg="#555555",
      state="disabled",
      bd=3,
      relief="raised",
      cursor="hand2",
      command=start_manual_decrypt,
  )
  manual_btn.grid(row=0, column=1, padx=10)

  slider_guess_btn = tk.Button(
      btn_frame,
      text="AUTO SLIDER",
      font=("Courier", 10, "bold"),
      width=15,
      bg="#005f73",
      fg="#00e5ff",
      bd=3,
      relief="raised",
      cursor="hand2",
      command=start_slider_guess,
  )
  slider_guess_btn.grid(row=0, column=2, padx=10)

  for slider in sliders:
    slider.config(command=check_sliders)


def open_bomb_code_window():
  global bomb_code_window
  if bomb_code_window and bomb_code_window.winfo_exists():
    bomb_code_window.lift()
    return

  bomb_code_window = tk.Toplevel(root)
  bomb_code_window.title("Bomb Code")
  bomb_code_window.geometry("240x120+20+20")
  bomb_code_window.configure(bg="#16181a")
  bomb_code_window.resizable(False, False)

  tk.Label(
      bomb_code_window,
      text="ARMING CODE",
      font=("Courier", 10, "bold"),
      bg="#16181a",
      fg="#888888",
  ).pack(pady=(15, 2))
  tk.Label(
      bomb_code_window,
      text=BOMB_CODE,
      font=("Courier", 24, "bold"),
      bg="#16181a",
      fg="#39ff14",
  ).pack()


root = tk.Tk()
root.title("C4 Explosive")
root.geometry("300x450")
root.configure(bg="#1e2022")

display_var = tk.StringVar()
display = tk.Entry(
    root,
    textvariable=display_var,
    font=("Courier", 28, "bold"),
    justify="center",
    bg="#0d1117",
    fg="#39ff14",
    readonlybackground="#0d1117",
    bd=5,
    relief="sunken",
    state="readonly",
)
display.grid(row=0, column=0, columnspan=3, padx=15, pady=(35, 5), sticky="nsew")

defuse_btn = tk.Button(
    root,
    text="[DEFUSE]",
    font=("Courier", 9, "bold"),
    bg="#005f73",
    fg="#00e5ff",
    activebackground="#0a9396",
    bd=2,
    relief="raised",
    cursor="hand2",
    command=open_defuse_window,
)

status_label = tk.Label(
    root,
    text="ENTER CODE (* CLEAR | # ENTER)",
    font=("Arial", 8, "bold"),
    bg="#1e2022",
    fg="#888888",
)
status_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))

keys = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["*", "0", "#"],
]

for r, row in enumerate(keys, start=2):
  for c, key in enumerate(row):
    btn = tk.Button(
        root,
        text=key,
        font=("Arial", 16, "bold"),
        bg="#343a40",
        fg="white",
        activebackground="#495057",
        activeforeground="white",
        bd=3,
        relief="raised",
        command=lambda k=key: on_key_press(k),
    )
    btn.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

status_label.bind("<Double-Button-1>", lambda e: reset_keypad())
root.grid_rowconfigure(0, weight=2)
for i in range(2, 6):
    root.grid_rowconfigure(i, weight=1)
for i in range(3):
    root.grid_columnconfigure(i, weight=1)
update_display()
open_bomb_code_window()
root.mainloop() 