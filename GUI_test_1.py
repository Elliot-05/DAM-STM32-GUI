#Need to read ports
import serial
import serial.tools.list_ports

#Need to make UI
import tkinter as tk
from tkinter import messagebox
from tkinter import * 
from tkinter import ttk

#To split shell output with multiple characters
import re

#To delay the shell actions, not doing everything at once
import time

#Improvments to be made: 
"""
1. Get title and entry dictionaries into one, make entries variable, titles values
2. Make the toggle switch between hex and int always
3. Find out why registers don't load sometimes
4. Setting limits?
"""

#Gets list of all ports connected to computer
ports = serial.tools.list_ports.comports()

#####################################
#Function that creates scrollable UI
def create_scrollable_canvas(parent):
    # Create canvas and scrollbar
    canvas = tk.Canvas(parent, borderwidth=0, background="#f0f0f0")
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Create inner frame inside canvas to allow entries and text to be put on screen
    inner_frame = tk.Frame(canvas, background="#ffffff")
    canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Configure scrollregion when content changes
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        canvas_width = event.width
        canvas.itemconfig(canvas_window, width=canvas_width)

    inner_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    # Mouse wheel scrolling
    def on_mousewheel(event):
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")
        else:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows/Linux
    canvas.bind_all("<Button-4>", on_mousewheel)    # macOS up
    canvas.bind_all("<Button-5>", on_mousewheel)    # macOS down

    return inner_frame  # Return inner frame to add widgets to

######################################
def check_hexidecimal(str):
    if "0x" in str:
        return True
    else:
        return False

######################################
#Function that creates second window

def second_window(event=None):
    #Function that closes the window
    def close_window(event=None):
        interface.destroy()

    ###################################
    #Function that submits the number and checks to see if fits parameters
    def submit(event = None):
        num_entry = 0
        for key in entry_dictionary.keys():
            entry_values = entry_dictionary[key]
            #Tries to convert the input into an integer, works in hex and int form
            try:
                entered_value = int(entry_values[1].get(),0)
            #If it can't then produce error message
            except:
                messagebox.showerror("Trollface", "Enter a number for " + titles[num_entry])
                return None
            else:
                submit_line = "reeg write DAM " + titles[num_entry] + " " + str(entered_value) + "\n"
                ser.write(submit_line.encode())
                time.sleep(0.01)
            num_entry += 1
        messagebox.showinfo("Title","Data successfully uploaded")
        interface.lift()
        interface.focus_force()
    ##################################
    #Function that gets the values inside the device
    def start_up(event = None):        
        bait_line = "sjifajefea\n"
        ser.write(bait_line.encode())
        time.sleep(0.01)
        #FOR WHATEVER REASON, the write function ignores the second character 
        ser.write("reeg list DAM\n".encode())
        print("WROTE")
        line = ser.read_until(expected="sjifajefea\n")
        print("READ")
        current_address = []

        #Splits into every word, then filters for title and description
        register_list = re.split(r'[\n]+',line.decode())
        for i in range(len(register_list)):
            if "0x" in register_list[i]:
                index = register_list[i].find("0x")
                add = register_list[i][index:index+6]
                current_address.append(add)

        #For loop goes into each line, splits between spaces and uses the first and second words as register name and current number
        bait_line2 = "AFEFSADVSAVDAEAW\n"
        ser.write(bait_line2.encode())
        time.sleep(0.01)
        ser.write("reeg read_all DAM\n".encode())
        print("WROTE2")
        entries = ser.read_until(expected="AFEFSADVSAVDAEAW\n")
        print("READ2")

        #Entry prints out (Register) = (Value)\r\n, so splitting = and \r finds values
        register_read_all = re.split(r'[=\r\s>]+',entries.decode())
        current_values = []
        register_titles = []

        for i in range(len(register_read_all)):
            #Tries to convert hexidecimal string into int
            try:
                int(register_read_all[i],0)
            except:
                pass
            else:
                current_values.append(register_read_all[i])
                register_titles.append(register_read_all[i-1])
        register_info = [register_titles,current_address,current_values]
        return register_info
    ##################################
    #Function that switches entry between hex and int
    def toggle(event = None):
        for key in entry_dictionary.keys():
            entry_values = entry_dictionary[key]
            entry_number = entry_values[1].get()
            entry_values[1].delete(0, END)
            #Tries to convert
            try:
                entry_values[0] = str(hex(int(entry_number)))
            except:
                if entry_number[0:2] == "0x":
                    entry_values[0] = str(int(entry_number,0))
                else:
                    messagebox.showerror("Trollface", "Enter a number for " + key)
            entry_values[1].insert(0, entry_values[0])

    ##################################
    def refresh(event = None):
        info = start_up()
        num = 0
        values = info[2]
        for key in entry_dictionary.keys():
            entry_values = entry_dictionary[key]
            entry_values[1].delete(0, END)
            entry_values[1].insert(0, values[num])
            num += 1
        messagebox.showinfo("Trollface", "Refreshed")
        interface.lift()
        interface.focus_force()
            

    
    #Designated port
    selected_port = combo_box.get()
    
    #Checks if selection valid
    try:
        ser = serial.Serial(port=selected_port[0:4],baudrate=115200,timeout=0.8)
    except:
        messagebox.showerror("Error", "Port not recognised or busy")
        close_window

    #Collects info from startup
    info = start_up()
    titles = info[0]
    address = info[1]
    values = info[2] 

    ########### Graphics start here #####################
    interface = tk.Toplevel()
    interface.title("DAM to comuputer tester")
    interface.geometry("500x500")
    scrollable_frame = create_scrollable_canvas(interface)

    #Submit values of entries
    sub_btn=tk.Button(scrollable_frame ,text = 'Submit: enter', command = submit)
    sub_btn.pack(anchor="ne")
    interface.bind("<Return>",submit)

    #Close window button
    button_close = tk.Button(scrollable_frame , text="Close window: esc", command = interface.destroy)
    button_close.pack(anchor="ne")
    interface.bind('<Escape>', close_window)

    #Toggle button
    button_close = tk.Button(scrollable_frame , text="Toggle: f1", command = toggle)
    button_close.pack(anchor="ne")
    interface.bind('<F1>', toggle)

    #Refresh button
    button_close = tk.Button(scrollable_frame , text="Refresh: f5", command = refresh)
    button_close.pack(anchor="ne")
    interface.bind('<F5>', refresh)

    # Add register titles and values to scrollable area
    entry_dictionary = {}
    title_dictionary = {}
    for i in range(len(titles)):
        default_var = tk.StringVar(value=values[i])
        title_dictionary[titles[i]] = tk.Label(scrollable_frame ,text=titles[i] + ": " + address[i])
        title_dictionary.get(titles[i]).pack(pady=5, padx=10, anchor="w")
        entry_dictionary[titles[i] + " Entry"] = [values[i], tk.Entry(scrollable_frame ,textvariable=default_var)]
        entry_dictionary.get(titles[i] + " Entry")[1].pack(pady=5, padx=10, anchor="w")
    
    
#############################

    

########################################
#Setting up window, start here
root = tk.Tk()
root.title("DAM to comuputer tester")
root.geometry("500x350")


#Combobox to select port
combo_box = ttk.Combobox(root, values=ports)
combo_box.pack()

#Button to Submit port selection  
button_open = tk.Button(root, text="submit", command=second_window)
button_open.pack()
root.bind("<Return>",second_window)


root.mainloop()
