## IRB Thermal Image Viewer

An interactive desktop tool for visualizing radiometric `.irb` files [Jenoptik VarioCAM](https://scitech.com.au/uploads/pdf/cameras/jenoptik/VarioCAM.pdf) alongside local weather station data, built with Python, Tkinter and Matplotlib.

### Features

* **IRB Loader**
  Reads raw FLIR‐style `.irb` files (Jenoptik VarioCAM/Thermal Imaging cameras) and maps the 16-bit counts linearly to 0–100 °C.

* **Weather Data Integration**
  Imports daily‐mean weather metrics (temperature, humidity, irradiation, evapotranspiration, wind speed) from a user-selected CSV/Excel file (e.g. Hohenheim station data).

* **Interactive Visualization**

  * **Thermal map** with Matplotlib “hot” colormap
  * **Colorbar** legend
  * **Min/Max sliders** to adjust display range in real time
  * **Save Image** button exports the current view to PNG

* **About Dialog**
  Includes an “About” tab with author, affiliation, contact info, creation date and version.

* **Standalone EXE**
  Packaged via PyInstaller (`--onefile --windowed`) for easy distribution on Windows.

---

### Requirements

* Python 3.7+
* Packages: `numpy`, `pandas`, `matplotlib`, `tkinter`, `pyinstaller` (for packaging)
* Jenoptik VarioCAM IRB files and matching weather CSV/Excel (e.g. `Tag_103.csv`)

---

### Usage

1. **Launch** the application:

   ```bash
   python thermal_viewer.py
   ```
2. **Load IRB**: Click **Load IRB File** and select your `.irb`.
3. **Load Weather**: Click **Load Weather File** to import station data.
4. **Adjust Sliders**: Tweak Min/Max °C to highlight temperature contrasts.
5. **Save Image**: Click **Save Image** to export the current view.
6. **About**: Under **Help → About**, view author and version details.

To build a Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed thermal_viewer.py
```

---

### Code Structure

* **`ThermalViewerApp`** (Tkinter)

  * File‐picker buttons and labels for IRB and weather files
  * **Matplotlib** figure embedded via `FigureCanvasTkAgg`
  * **Sliders** (`matplotlib.widgets.Slider`) for dynamic color scaling
  * **About** dialog with author/contact metadata
  * **Save Image** functionality

* **IRB Processing**

  * `find_dimensions()` — matches file size to known (width,height,header,bpp) combos
  * Buffer‐reading with `numpy.frombuffer` → float32 → Celsius conversion
  * `np.fliplr()` to correct image orientation

* **Weather Parsing**

  * Supports `.csv`, `.xls`, `.xlsx` via `pandas.read_csv` / `read_excel`
  * Parses German date format (`DD.MM.YYYY`)
  * Extracts 06 Jun 2025 metrics:

    * Min/Max Air Temp (`MIN_TA020`/`MAX_TA020`)
    * Min/Max Rel. Humidity (`MIN_RH200`/`MAX_RH200`)
    * Global irradiation (`SUM_GS200`)
    * Evapotranspiration (`AVG_LWET200`)
    * Wind speed (`AVG_WV200`)

* **Visualization Layout**

  * **GridSpec** divides window: image + colorbar on left, text panel on right, sliders below.
  * Text panel auto-wraps and uses monospace for neat alignment.

---

### Author & Version

> **Khandoker Ahammad**
> Doctoral Researcher, University of Hohenheim
> Institute of Agricultural Engineering
> Agricultural Engineering in the Tropics and Subtropics
>
> Garbenstrasse 9 • 70599 Stuttgart
> Tel.: 0711 / 459 22858
>
> **Creation date:** 20.06.2025
> **Version:** V-1
> **Contact:** [khandoker.ahammad@uni-hohenheim.de](mailto:khandoker.ahammad@uni-hohenheim.de)
