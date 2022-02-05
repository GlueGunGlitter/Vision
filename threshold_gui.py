import tkinter as tk
from tkSliderWidget import Slider


root = tk.Tk()

slider_h = Slider(root, width = 400, height = 60, min_val = 0, max_val = 180, init_lis = [20, 75], show_value = True)
slider_s = Slider(root, width = 400, height = 60, min_val = 0, max_val = 255, init_lis = [20, 75], show_value = True)
slider_v = Slider(root, width = 400, height = 60, min_val = 0, max_val = 255, init_lis = [20, 75], show_value = True)

slider_h.pack()
slider_s.pack()
slider_v.pack()

root.title("Threshold Calibration")

def update(main_func=None):

    root.update()

def get_values():
    h = slider_h.getValues()
    s = slider_s.getValues()
    v = slider_v.getValues()

    return ((h[0], s[0], v[0]), (h[1], s[1], v[1]))

