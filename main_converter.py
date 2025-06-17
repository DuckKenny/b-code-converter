import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

# extracting B1 code and converting it to B0 code (single code) / Portisch firmware
def convert_b1_to_b0(b1_line):
    # filter B1 code and validate structure
    b1_end = b1_line.rfind("55")
    if len(b1_line) == 0:
        return 0
    elif b1_end > -1:
        b1_start = b1_line.find("AA B1")
        if b1_start > -1:
            b1_line = b1_line[b1_start:b1_end + len("55")]
        else:
            print("Wrong code format.")
            return None
    else:
        print("Code incomplete.")
        return None
    buckets = b1_line.strip().split()

    # splitting buckets into known values (https://github.com/Portisch/RF-Bridge-EFM8BB1/wiki/Decode-0xB1-sniffed-data)
    timing1 = buckets[3]
    timing2 = buckets[4]
    symbol1 = buckets[5]
    symbol2 = buckets[6]
    payload_tokens = buckets[7:-1]  # catch the rest
    payload_add_len = 0  # count up the front buckets
    i = 1
    while i < 7:
        payload_add_len += len(buckets[i])
        i += 1
    # join payload, calculate bit length and include front buckets
    hex_string = "".join(payload_tokens)
    bit_len = (len(hex_string) + payload_add_len) // 2
    bit_len_hex = f"{bit_len:02X}".upper()

    # assemble B0 code ("04" timing & symbol count / "08" unknown - always 08 what codes I have seen and tested)
    # tested with: https://bbconv.hrbl.pl/ (so far always the same)
    b0_tokens = ["AA", "B0", bit_len_hex, "04", "08", timing1, timing2, symbol1, symbol2] + payload_tokens + ["55"]
    # information on B1: https://github.com/Portisch/RF-Bridge-EFM8BB1/wiki/0xB1
    # information on B0: https://github.com/Portisch/RF-Bridge-EFM8BB1/wiki/0xB0
    return " ".join(b0_tokens)

# splitting up the lines from textbox and converting them
def split_lines_and_convert():
    str_lines = input_box.get("1.0", tk.END).strip()
    output_codes = """"""
    for lines in str_lines.splitlines():
        output = convert_b1_to_b0(lines)
        if output is not None:
            if output != 0:
                output_codes += output + "\n"
        elif output == 0:
            continue
    output_codes = output_codes[:-2]
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, output_codes)

def exit_app():
    root.destroy()  # exit app

root = tk.Tk()
root.title("B-Code Converter")
root.geometry("800x600")

# Layout configuration
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(3, weight=1)

# Input label
input_label = ttk.Label(root, text="Input Tasmota Console Code:")
input_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
# Input Box
input_frame = ttk.Frame(root)
input_frame.grid(row=1, column=0, padx=10, sticky="nsew")
input_frame.columnconfigure(0, weight=1)
input_frame.rowconfigure(0, weight=1)
input_box = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=10)
input_box.grid(row=0, column=0, sticky="nsew")

# Output label
output_label = ttk.Label(root, text="Output of B0 codes:")
output_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
# Output Box
output_frame = ttk.Frame(root)
output_frame.grid(row=3, column=0, padx=10, sticky="nsew")
output_frame.columnconfigure(0, weight=1)
output_frame.rowconfigure(0, weight=1)
output_box = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10)
output_box.grid(row=0, column=0, sticky="nsew")

# Button frame and buttons
button_frame = ttk.Frame(root)
button_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")
button_frame.columnconfigure((0, 1), weight=1)
convert_button = ttk.Button(button_frame, text="Convert", command=split_lines_and_convert)
convert_button.grid(row=0, column=0, sticky="w")
exit_button = ttk.Button(button_frame, text="Exit", command=exit_app)
exit_button.grid(row=0, column=1, sticky="e")

root.mainloop()
