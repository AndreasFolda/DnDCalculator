import tkinter as tk
from tkinter import ttk
import re

class MissRow:
    def __init__(self, parent, row):
        self.row = row
        self.ac_entry = ttk.Entry(parent, width=10)
        self.ac_entry.grid(row=row, column=0, padx=5, pady=5)
        self.bonus_entry = ttk.Entry(parent, width=10)
        self.bonus_entry.grid(row=row, column=1, padx=5, pady=5)
        self.rolls_entry = ttk.Entry(parent, width=10)
        self.rolls_entry.grid(row=row, column=2, padx=5, pady=5)
        self.remove_button = ttk.Button(parent, text="-", command=self.remove)
        self.remove_button.grid(row=row, column=3, padx=5, pady=5)
        self.parent = parent
        self.on_remove = None

    def get_data(self):
        try:
            ac = int(self.ac_entry.get())
            bonus = int(self.bonus_entry.get())
            rolls = int(self.rolls_entry.get())
            return ac, bonus, rolls
        except ValueError:
            return None

    def remove(self):
        for widget in [self.ac_entry, self.bonus_entry, self.rolls_entry, self.remove_button]:
            widget.destroy()
        if self.on_remove:
            self.on_remove(self.row)

class MissCalculator:
    def __init__(self, parent):
        self.parent = parent
        self.rows = []
        self.next_row = 1

        # Header
        ttk.Label(parent, text="AC").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(parent, text="Bonus").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(parent, text="Rolls").grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(parent, text="+", command=self.add_row).grid(row=0, column=3, padx=5, pady=5)

        # Initial row
        self.add_row()

        # Calculate button and result
        self.calculate_button = ttk.Button(parent, text="Calculate", command=self.calculate)
        self.calculate_button.grid(row=99, column=0, columnspan=2, pady=10)
        self.result_label = ttk.Label(parent, text="Probability of Missing: N/A")
        self.result_label.grid(row=100, column=0, columnspan=4, pady=5)

    def add_row(self):
        row = MissRow(self.parent, self.next_row)
        row.on_remove = self.remove_row
        self.rows.append(row)
        self.next_row += 1

    def remove_row(self, row_index):
        self.rows = [row for row in self.rows if row.row != row_index]

    def calculate(self):
        try:
            total_probability = 1.0
            for row in self.rows:
                data = row.get_data()
                if data:
                    ac, bonus, rolls = data
                    hit_chance = max(0, (21 - (ac - bonus)) / 20)
                    miss_chance = 1 - hit_chance
                    total_probability *= miss_chance ** rolls
            self.result_label.config(text=f"Probability of Missing: {total_probability * 100:.2f}%")
        except Exception as e:
            self.result_label.config(text=f"Error: {str(e)}")

def show_disclaimer():
    # Create a modal window
    disclaimer_window = tk.Toplevel(root)
    disclaimer_window.title("Disclaimer")
    disclaimer_window.geometry("400x250")
    disclaimer_window.transient(root)  # Keep the window on top of the main window
    disclaimer_window.grab_set()      # Disable interaction with the main window

    # Disclaimer message
    disclaimer_message = (
        "These calculations provide average probabilities and damage estimates based on input values.\n\n"
        "Please note that averages do not always reflect real gameplay outcomes due to randomness."
        "\n\n Use this tool as a reference, not as a guarantee.\n And do not use it as a base to pick fights with other people."
    )
    ttk.Label(disclaimer_window, text=disclaimer_message, wraplength=380, justify="center").pack(padx=10, pady=10)

    # Checkbox
    accept_var = tk.BooleanVar()
    accept_checkbox = ttk.Checkbutton(disclaimer_window, text="I have read and understand", variable=accept_var)
    accept_checkbox.pack(pady=10)

    # Continue button (disabled initially)
    continue_button = ttk.Button(disclaimer_window, text="Continue", state="disabled", command=disclaimer_window.destroy)
    continue_button.pack(pady=10)

    # Disable the "X" button
    disclaimer_window.protocol("WM_DELETE_WINDOW", lambda: None)
    # Enable the button only if the checkbox is ticked
    def toggle_continue_button():
        continue_button["state"] = "normal" if accept_var.get() else "disabled"

    accept_var.trace_add("write", lambda *args: toggle_continue_button())


def calculate_chance():
    try:
        bonus_to_hit = int(bonus_entry.get())
        ac_target = int(ac_entry.get())
        advantage = advantage_var.get()
        disadvantage = disadvantage_var.get()

        target_roll = ac_target - bonus_to_hit
        if target_roll <= 1:
            target_roll = 1
        if target_roll > 20:
            target_roll = 21

        single_roll_chance = max(0, (21 - target_roll) / 20)

        if advantage and disadvantage:
            result = single_roll_chance  # Cancels out
        elif advantage:
            result = 1 - ((1 - single_roll_chance) ** 2)
        elif disadvantage:
            result = single_roll_chance ** 2
        else:
            result = single_roll_chance

        result_label_hit.config(text=f"Hit Chance: {result * 100:.2f}%")
    except ValueError:
        result_label_hit.config(text="Invalid input. Please enter numbers.")

def calculate_damage():
    try:
        damage_input = damage_entry.get()
        pattern = r"(\d+)d(\d+)"
        dice_matches = re.findall(pattern, damage_input)
        static_bonus = sum(map(int, re.findall(r"(?<!d)(?<!\d)(\d+)", damage_input)))

        total_avg = 0
        for num_dice, dice_sides in dice_matches:
            num_dice = int(num_dice)
            dice_sides = int(dice_sides)
            avg_roll = (dice_sides + 1) / 2
            total_avg += num_dice * avg_roll

        total_avg += static_bonus
        result_label_damage.config(text=f"Average Damage: {total_avg:.2f}")
    except ValueError:
        result_label_damage.config(text="Invalid input. Please enter a valid damage formula.")

def calculate_avg_damage():
    try:
        ac = int(avg_damage_ac_entry.get())
        bonus = int(avg_damage_bonus_entry.get())
        rolls = int(avg_damage_rolls_entry.get())
        damage_formula = avg_damage_formula_entry.get()

        # Calculate hit chance
        hit_chance = max(0, (21 - (ac - bonus)) / 20)

        # Calculate average damage
        pattern = r"(\d+)d(\d+)"
        dice_matches = re.findall(pattern, damage_formula)
        static_bonus = sum(map(int, re.findall(r"(?<!d)(?<!\d)(\d+)", damage_formula)))

        total_avg_damage = 0
        for num_dice, dice_sides in dice_matches:
            num_dice = int(num_dice)
            dice_sides = int(dice_sides)
            avg_roll = (dice_sides + 1) / 2
            total_avg_damage += num_dice * avg_roll

        total_avg_damage += static_bonus

        # Multiply by hit chance and rolls
        avg_damage = total_avg_damage * hit_chance * rolls

        avg_damage_result_label.config(text=f"Average Damage per Turn: {avg_damage:.2f}")
    except ValueError:
        avg_damage_result_label.config(text="Invalid input. Please enter valid numbers and damage formula.")

def calculate_save():
    try:
        modifier = int(modifier_entry.get())
        target_dc = int(dc_entry.get())
        advantage = save_advantage_var.get()
        disadvantage = save_disadvantage_var.get()

        target_roll = target_dc - modifier
        if target_roll <= 1:
            target_roll = 1
        if target_roll > 20:
            target_roll = 21

        single_roll_chance = max(0, (21 - target_roll) / 20)

        if advantage and disadvantage:
            result = single_roll_chance  # Cancels out
        elif advantage:
            result = 1 - ((1 - single_roll_chance) ** 2)
        elif disadvantage:
            result = single_roll_chance ** 2
        else:
            result = single_roll_chance

        result_label_save.config(text=f"Save/Skill Check Success: {result * 100:.2f}%")
    except ValueError:
        result_label_save.config(text="Invalid input. Please enter numbers.")

# Create the main window
root = tk.Tk()
root.title("D&D Calculator")
root.geometry("550x350")
# Call the disclaimer function before displaying the main window
show_disclaimer()
# Create tabs
notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill="both", expand=True)

# Tab 1: Hit Chance
hit_frame = ttk.Frame(notebook)
notebook.add(hit_frame, text="Hit Chance")

# Bonus to hit input
bonus_label = ttk.Label(hit_frame, text="Bonus to Hit:")
bonus_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")
bonus_entry = ttk.Entry(hit_frame, width=50)
bonus_entry.grid(row=0, column=1, padx=5, pady=5)

# AC of target input
ac_label = ttk.Label(hit_frame, text="AC of Target:")
ac_label.grid(row=1, column=0, padx=5, pady=5, sticky="W")
ac_entry = ttk.Entry(hit_frame, width=50)
ac_entry.grid(row=1, column=1, padx=5, pady=5)

# Advantage and Disadvantage checkboxes
advantage_var = tk.BooleanVar()
disadvantage_var = tk.BooleanVar()
advantage_check = ttk.Checkbutton(hit_frame, text="Advantage", variable=advantage_var)
advantage_check.grid(row=2, column=0, padx=5, pady=5, sticky="W")
disadvantage_check = ttk.Checkbutton(hit_frame, text="Disadvantage", variable=disadvantage_var)
disadvantage_check.grid(row=2, column=1, padx=5, pady=5, sticky="W")

# Calculate button for hit chance
calculate_hit_button = ttk.Button(hit_frame, text="Calculate Hit Chance", command=calculate_chance)
calculate_hit_button.grid(row=3, column=0, columnspan=2, pady=10)

# Result label for hit chance
result_label_hit = ttk.Label(hit_frame, text="Hit Chance: N/A")
result_label_hit.grid(row=4, column=0, columnspan=2, pady=5)

# Tab 2: Damage Calculation
damage_frame = ttk.Frame(notebook)
notebook.add(damage_frame, text="Damage Calculation")

# Damage formula input
damage_label = ttk.Label(damage_frame, text="Damage Formula:")
damage_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")
damage_entry = ttk.Entry(damage_frame, width=50)
damage_entry.grid(row=0, column=1, padx=5, pady=5)

# Example text
damage_example_label = ttk.Label(damage_frame, text="Example: 2d12+2d6+5+2d4", font=("Arial", 10, "italic"))
damage_example_label.grid(row=1, column=0, columnspan=2, pady=5)

# Calculate button for damage
calculate_damage_button = ttk.Button(damage_frame, text="Calculate Average Damage", command=calculate_damage)
calculate_damage_button.grid(row=2, column=0, columnspan=2, pady=10)

# Result label for damage calculation
result_label_damage = ttk.Label(damage_frame, text="Average Damage: N/A")
result_label_damage.grid(row=3, column=0, columnspan=2, pady=5)

# Tab 3: Save/Skill Check Calculation
save_frame = ttk.Frame(notebook)
notebook.add(save_frame, text="Save/Skill Check")

# Modifier input
modifier_label = ttk.Label(save_frame, text="Modifier:")
modifier_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")
modifier_entry = ttk.Entry(save_frame, width=50)
modifier_entry.grid(row=0, column=1, padx=5, pady=5)

# Target DC input
dc_label = ttk.Label(save_frame, text="Target DC:")
dc_label.grid(row=1, column=0, padx=5, pady=5, sticky="W")
dc_entry = ttk.Entry(save_frame, width=50)
dc_entry.grid(row=1, column=1, padx=5, pady=5)

# Advantage and Disadvantage checkboxes
save_advantage_var = tk.BooleanVar()
save_disadvantage_var = tk.BooleanVar()
save_advantage_check = ttk.Checkbutton(save_frame, text="Advantage", variable=save_advantage_var)
save_advantage_check.grid(row=2, column=0, padx=5, pady=5, sticky="W")
save_disadvantage_check = ttk.Checkbutton(save_frame, text="Disadvantage", variable=save_disadvantage_var)
save_disadvantage_check.grid(row=2, column=1, padx=5, pady=5, sticky="W")

# Calculate button for save/skill check
calculate_save_button = ttk.Button(save_frame, text="Calculate Save/Skill Check", command=calculate_save)
calculate_save_button.grid(row=3, column=0, columnspan=2, pady=10)

# Result label for save/skill check
result_label_save = ttk.Label(save_frame, text="Save/Skill Check Success: N/A")
result_label_save.grid(row=4, column=0, columnspan=2, pady=5)

# Tab 4: Miss Streak Calculation
miss_frame = ttk.Frame(notebook)
notebook.add(miss_frame, text="Miss Streak")
miss_calculator = MissCalculator(miss_frame)

# Tab 5: Average Damage per Turn
avg_damage_frame = ttk.Frame(notebook)
notebook.add(avg_damage_frame, text="Avg Damage per Turn")

# AC input
avg_damage_ac_label = ttk.Label(avg_damage_frame, text="AC of Target:")
avg_damage_ac_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")
avg_damage_ac_entry = ttk.Entry(avg_damage_frame, width=20)
avg_damage_ac_entry.grid(row=0, column=1, padx=5, pady=5)

# Bonus input
avg_damage_bonus_label = ttk.Label(avg_damage_frame, text="Bonus to Hit:")
avg_damage_bonus_label.grid(row=1, column=0, padx=5, pady=5, sticky="W")
avg_damage_bonus_entry = ttk.Entry(avg_damage_frame, width=20)
avg_damage_bonus_entry.grid(row=1, column=1, padx=5, pady=5)

# Number of Rolls input
avg_damage_rolls_label = ttk.Label(avg_damage_frame, text="Number of Rolls:")
avg_damage_rolls_label.grid(row=2, column=0, padx=5, pady=5, sticky="W")
avg_damage_rolls_entry = ttk.Entry(avg_damage_frame, width=20)
avg_damage_rolls_entry.grid(row=2, column=1, padx=5, pady=5)

# Damage Formula input
avg_damage_formula_label = ttk.Label(avg_damage_frame, text="Damage Formula:")
avg_damage_formula_label.grid(row=3, column=0, padx=5, pady=5, sticky="W")
avg_damage_formula_entry = ttk.Entry(avg_damage_frame, width=50)
avg_damage_formula_entry.grid(row=3, column=1, padx=5, pady=5)

# Calculate button for average damage
avg_damage_calculate_button = ttk.Button(avg_damage_frame, text="Calculate Avg Damage", command=calculate_avg_damage)
avg_damage_calculate_button.grid(row=4, column=0, columnspan=2, pady=10)

# Result label for average damage
avg_damage_result_label = ttk.Label(avg_damage_frame, text="Average Damage per Turn: N/A")
avg_damage_result_label.grid(row=5, column=0, columnspan=2, pady=5)


# Run the application
root.mainloop()