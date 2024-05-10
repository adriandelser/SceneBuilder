import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from tkinter import Tk, filedialog
from pathlib import Path

# Initialize Tkinter just once
root = Tk()
root.withdraw()  # Hide the main window

def save_file_dialog(event):
    filename = filedialog.asksaveasfilename(defaultextension=".txt")
    
    if filename:
        filepath = Path(filename)
        print("Selected file for saving:", filepath)
        # You can perform further actions for saving to the selected file here

# Create a sample Matplotlib figure and axis
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title('Matplotlib GUI')  # Set window title

# Create a button within the plot for saving
save_button_ax = plt.axes([0.7, 0.05, 0.2, 0.075])
save_button = Button(save_button_ax, 'Save File')

# Connect the button's event handler to the save_file_dialog function
save_button.on_clicked(save_file_dialog)

plt.show()
