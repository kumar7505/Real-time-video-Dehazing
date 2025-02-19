import tkinter as tk  # Import tkinter as tk (common practice)
import os
import sys
import subprocess
from tkinter import filedialog
from PIL import Image, ImageTk

def open_image():
    global img
    global img_name
    global submit

    img_name = filedialog.askopenfilename(initialdir="." , title="Select Image" , filetypes=(("images" , "*.jpg"),("images", "*.bmp"),("images", "*.png"))) 
    print(img_name)
    input.insert(0, img_name)

    l1 = tk.Label(root, text="Original Image:")
    l1.grid(column=0, row=2)

    img = ImageTk.PhotoImage(Image.open(img_name).resize((250,250)))
    l2 = tk.Label(root, image=img)
    l2.grid(column=0, row=3)

    submit = tk.Button(root, text="Submit", command=call_haze)
    submit.grid(column=0, row=4)

def call_haze():
    global dehazed

    submit.destroy()

    # Run haze_removal.py via subprocess
    subprocess.call(f"python haze_removal.py {img_name}", shell=True)
    
    msg = tk.Label(root, text="Dehazing completed! Image stored in dehazed folder.")
    msg.grid(column=0, row=4, columnspan=2)

    dehazed_path = os.path.join("./dehazed", "dst.jpg")  # Adjust to where dehazed image is saved

    # Check if the file exists before trying to open it
    if os.path.exists(dehazed_path):
        dehazed = ImageTk.PhotoImage(Image.open(dehazed_path).resize((250, 250)))

        l4 = tk.Label(root, image=dehazed)
        l4.grid(column=1, row=3, padx=10)

    retry = tk.Button(root, text="Retry", command=restart_program)
    retry.grid(column=0, row=5)

    quit = tk.Button(root, text="Quit", command=quit_program)
    quit.grid(column=1, row=5)

def restart_program():
    os.execl(sys.executable, sys.executable, *sys.argv)
     
def quit_program():
    sys.exit() 

root = tk.Tk()  # Use 'tk.Tk()' instead of just 'Tk()' after importing tkinter as tk
root.title("Dehaze")  # Correct way to set window title

label = tk.Label(root, text="Select image or enter image path:")
label.grid(column=0, row=0)

input = tk.Entry(root, width=50)
input.grid(column=0, row=1, padx=10, pady=10)

browse = tk.Button(root, text="Browse", command=open_image)
browse.grid(column=1, row=1)

root.mainloop()
