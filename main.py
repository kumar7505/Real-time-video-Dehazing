import tkinter as tk  # Import tkinter as tk (common practice)
import os
import sys
import subprocess
from tkinter import filedialog
from PIL import Image, ImageTk

def open_image():
    global img, img_name, submit

    img_name = filedialog.askopenfilename(
        initialdir=".",
        title="Select Image",
        filetypes=(("Images", "*.jpg;*.png;*.bmp"),)
    )

    if not img_name:
        return  # Exit if no file is selected

    try:
        input.delete(0, tk.END)
        input.insert(0, img_name)

        l1 = tk.Label(root, text="Original Image:")
        l1.grid(column=0, row=2, pady=5)

        img = Image.open(img_name).resize((250, 250))
        img = ImageTk.PhotoImage(img)

        l2 = tk.Label(root, image=img)
        l2.grid(column=0, row=3, pady=5)

        submit = tk.Button(root, text="Submit", command=call_haze)
        submit.grid(column=0, row=4, pady=10)

    except Exception as e:
        print(f"Error loading image: {e}")


def call_haze():
    global dehazed

    submit.destroy()

    try:
        result = subprocess.run(
            ["python", "haze_removal.py", img_name], 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(result.stdout)  # Log output to console

        msg = tk.Label(root, text="Dehazing completed! Image stored in dehazed folder.")
        msg.grid(column=0, row=4, columnspan=2, pady=5)

        dehazed_path = os.path.join("./dehazed", "dst.jpg")
        
        if os.path.exists(dehazed_path):
            dehazed = ImageTk.PhotoImage(Image.open(dehazed_path).resize((250, 250)))

            l4 = tk.Label(root, image=dehazed)
            l4.grid(column=1, row=3, padx=10, pady=5)

    except subprocess.CalledProcessError as e:
        print(f"Error during haze removal: {e.stderr}")
        msg = tk.Label(root, text="Error during processing. Check console for details.", fg="red")
        msg.grid(column=0, row=4, columnspan=2)


def restart_program():
    for widget in root.winfo_children():
        widget.destroy()
    build_ui()  # Function to rebuild UI without restarting the entire app
     
def quit_program():
    root.destroy()

root = tk.Tk()  # Use 'tk.Tk()' instead of just 'Tk()' after importing tkinter as tk
root.title("Dehaze")  # Correct way to set window title

label = tk.Label(root, text="Select image or enter image path:")
label.grid(column=0, row=0)

input = tk.Entry(root, width=50)
input.grid(column=0, row=1, padx=10, pady=10)

browse = tk.Button(root, text="Browse", command=open_image)
browse.grid(column=1, row=1)

root.mainloop()
