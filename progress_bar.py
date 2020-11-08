import curses

def print_progress_bar(screen, first_number, second_number, info='', suffix=''):
	curses.curs_set(False)
	curses.use_default_colors()

	screen.clear()

	bar_length = 100
	percent = f"{(first_number / float(second_number))*100:.7f}"
	filled_ammount = int(bar_length * first_number // second_number)

	screen.addstr(0, 0, "Progress: |")
	for _ in range(filled_ammount):
		screen.addstr('█')
	for _ in range(bar_length - filled_ammount):
		screen.addstr('-')
	screen.addstr(f"| {percent}% Complete {suffix}\n{info}")
	
	screen.refresh()