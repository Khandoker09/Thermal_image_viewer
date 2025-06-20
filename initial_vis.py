'''
Author: Khandoker Tanjim Ahammad
Date: 06.20.25
Purpose: Read and analyisis .irb file that produce by the Janaoptik vario cam.
parameter: csv file with wather data and .irb image

'''
import os, sys
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button

def find_dimensions(n):
    common = [
        (640,512,1024,2),(512,384,1024,2),(384,288,1024,2),
        (320,240,1024,2),(240,180,1024,2),(160,120,1024,2),
        (128,96,1024,2),(80,60,1024,2),
        (640,512,1024,4),(512,384,1024,4),(384,288,1024,4),
        (320,240,1024,4),(240,180,1024,4),(160,120,1024,4),
        (128,96,1024,4),(80,60,1024,4),
    ]
    for w,h,hdr,bpp in common:
        if n == w*h*bpp + hdr:
            return w,h,hdr,bpp
    return min(common, key=lambda t: abs(n - (t[0]*t[1]*t[3] + t[2])))

class ThermalViewerApp:
    def __init__(self, master):
        self.master = master
        master.title("Thermal Image Viewer")

        # Menu bar with About
        menubar = tk.Menu(master)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        master.config(menu=menubar)

        # File selectors + Save button
        frame = tk.Frame(master)
        frame.pack(padx=10, pady=5, fill='x')

        tk.Button(frame, text="Load IRB File",    command=self.load_irb).pack(side='left', padx=5)
        self.irb_label = tk.Label(frame, text="No IRB selected")
        self.irb_label.pack(side='left', padx=5)

        tk.Button(frame, text="Load Weather File",command=self.load_weather).pack(side='left', padx=5)
        self.csv_label = tk.Label(frame, text="No weather file selected")
        self.csv_label.pack(side='left', padx=5)

        self.save_btn = tk.Button(frame, text="Save Image", command=self.save_image, state='disabled')
        self.save_btn.pack(side='right', padx=5)

        # Canvas for Matplotlib figure
        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(fill='both', expand=True)
        self.canvas = None
        self.fig = None

    def show_about(self):
        messagebox.showinfo(
            "About",
            "This software was created by:\n\n"
            "Khandoker Ahammad\n"
            "Doctoral Researcher\n"
            "University of Hohenheim\n"
            "Institute of Agricultural Engineering\n"
            "Agricultural Engineering in the Tropics and Subtropics\n\n"
            "Garbenstrasse 9\n"
            "70599 Stuttgart\n"
            "Tel.: 0711 / 459 22858\n\n"
            "Creation date : 20.06.25\n"
            "Version: V-1\n\n"
            "Any questions or problems contact:\n"
            "khandoker.ahammad@uni-hohenheim.de"
        )

    def load_irb(self):
        path = filedialog.askopenfilename(filetypes=[("IRB files","*.irb"),("All files","*.*")])
        if not path: return
        self.irb_path = path
        self.irb_label.config(text=os.path.basename(path))
        self.try_render()

    def load_weather(self):
        path = filedialog.askopenfilename(filetypes=[("CSV/Excel","*.csv;*.xls;*.xlsx"),("All files","*.*")])
        if not path: return
        self.csv_path = path
        self.csv_label.config(text=os.path.basename(path))
        self.try_render()

    def save_image(self):
        if not self.fig:
            return
        fname = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG Image","*.png")])
        if fname:
            self.fig.savefig(fname, dpi=150)
            messagebox.showinfo("Saved", f"Image saved to:\n{fname}")

    def try_render(self):
        if hasattr(self, 'irb_path') and hasattr(self, 'csv_path'):
            try:
                self.render_figure()
                self.save_btn.config(state='normal')
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def render_figure(self):
        # Process IRB
        with open(self.irb_path, "rb") as f: raw = f.read()
        nbytes = len(raw)
        w,h,offset,bpp = find_dimensions(nbytes)
        dtype = "<u2" if bpp==2 else "<f4"
        arr = np.frombuffer(raw[offset:offset+w*h*bpp], dtype=dtype)
        arr = arr[:w*h].reshape(h,w).astype(np.float32)
        thermal = arr * (100.0/65535.0)
        thermal = np.fliplr(thermal)

        # Process Weather
        if self.csv_path.lower().endswith(('.xls','.xlsx')):
            df = pd.read_excel(self.csv_path)
        else:
            df = pd.read_csv(self.csv_path, sep=';', decimal=',', engine='python')
        df['DATE'] = pd.to_datetime(df['Tag'], dayfirst=True, format='%d.%m.%Y')
        day = df[df['DATE']==pd.Timestamp("2025-06-06")].iloc[0]
        tmin,tmax = float(day['MIN_TA020']), float(day['MAX_TA020'])
        rhmin,rhmax = float(day['MIN_RH200']), float(day['MAX_RH200'])
        irr = float(day['SUM_GS200'])
        et  = float(day['AVG_LWET200'])
        ws  = float(day['AVG_WV200'])

        txt = (
            "Fusarium Head Blight (FHB) Indicators:\n"
            " • Infected spikelets show altered temps\n"
            "    – Warmer: necrotic tissue / higher metabolic heat\n"
            "    – Cooler: reduced transpiration (stomatal closure)\n"
            " • Early lesions ≈0.5–2 °C diff from healthy tissue\n\n"
            "Weather Station (06 Jun 2025):\n"
            f" • Temperature:       {tmin:.1f} … {tmax:.1f} °C\n"
            f" • Humidity:          {rhmin:.1f} … {rhmax:.1f} %\n"
            f" • Irradiation:       {irr:.1f} MJ/m²\n"
            f" • Evapo-transpiration:{et:.1f} W/m²\n"
            f" • Wind speed:        {ws:.1f} m/s"
        )

        # Build figure
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.fig = plt.Figure(figsize=(8,5), dpi=100)
        gs = GridSpec(3,2, figure=self.fig, width_ratios=[3,2], height_ratios=[8,1,1],
                      wspace=0.1, hspace=0.3)

        ax_img = self.fig.add_subplot(gs[0,0])
        im = ax_img.imshow(thermal, cmap='hot', vmin=0, vmax=100)
        ax_img.axis('off')
        ax_img.set_title("Thermal Image Viewer", fontsize=14)
        self.fig.colorbar(im, ax=ax_img, fraction=0.046, pad=0.02,
                          label="Temperature (°C)")

        ax_txt = self.fig.add_subplot(gs[0,1])
        ax_txt.axis('off')
        ax_txt.text(0,1, txt, va='top', ha='left',
                    fontsize=10, family='monospace', wrap=True)

        ax_min = self.fig.add_subplot(gs[1,0])
        ax_max = self.fig.add_subplot(gs[2,0])
        ax_reset = self.fig.add_subplot(gs[2,1])

        min_slider = Slider(ax_min, "Min (°C)", 0,100,valinit=0,valfmt="%.1f")
        max_slider = Slider(ax_max, "Max (°C)", 0,100,valinit=100,valfmt="%.1f")
        reset_btn = Button(ax_reset, "Reset", color="#FFA07A")

        def update(val):
            lo,hi = min_slider.val, max_slider.val
            if lo>hi: lo,hi=hi,lo; min_slider.set_val(lo); max_slider.set_val(hi)
            im.set_clim(lo,hi); self.fig.canvas.draw_idle()

        def reset(event):
            min_slider.set_val(0); max_slider.set_val(100)
            im.set_clim(0,100); self.fig.canvas.draw_idle()

        min_slider.on_changed(update)
        max_slider.on_changed(update)
        reset_btn.on_clicked(reset)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

if __name__=="__main__":
    root = tk.Tk()
    ThermalViewerApp(root)
    root.mainloop()
