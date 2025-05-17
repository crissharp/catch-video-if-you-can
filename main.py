import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog
import threading
import yt_dlp
import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *


# --- Funciones de descarga ---
def analyze_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Missing URL", "Please enter a YouTube URL first.")
        return

    try:
        status_label.config(text="Analyzing video formats...")
        ydl_opts = {
                        'quiet': True,
                        'noplaylist': True,
                        'no_warnings': True,
                        'user_agent': 'Mozilla/5.0',  # <-- importante
                        'cookiefile': 'bilibili.tv_cookies.txt',  # <-- si ya lo usas desde consola con cookies
                        'force_generic_extractor': False
                    }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            

            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])

            format_id_map.clear()
            video_formats = []
            audio_formats = []

            for fmt in formats:
                f_id = fmt.get("format_id")
                height = fmt.get("height")
                ext = fmt.get("ext")
                acodec = fmt.get("acodec")
                vcodec = fmt.get("vcodec")

                # Clasificar como video o audio
                if vcodec != 'none' and height:
                    video_formats.append((f_id, height, ext))
                if acodec != 'none' and vcodec == 'none':
                    audio_formats.append((f_id, ext))

            # Elegir mejor audio (prioridad al 140 si existe)
            best_audio_id = "140"
            available_audio_ids = [a[0] for a in audio_formats]
            if best_audio_id not in available_audio_ids and available_audio_ids:
                best_audio_id = available_audio_ids[0]  # Usa el primero disponible

            if not video_formats or not best_audio_id:
                raise Exception("No valid video+audio combinations found.")

            # Armar la lista para mostrar
            display_list = []
            for vid_id, height, ext in video_formats:
                combo_id = f"{vid_id}+{best_audio_id}"
                label = f"{height}p - {ext} ({combo_id})"
                format_id_map[label] = combo_id
                display_list.append(label)

            resolution_combo['values'] = display_list
            selected_format_id.set(display_list[-1])
            resolution_combo.current(len(display_list) - 1)
            resolution_combo.pack()

            status_label.config(text="Select resolution to download.")
    except Exception as e:
        status_label.config(text="❌ Error analyzing video: " + str(e))


# Descarga el segmento del video entre start_time y end_time
def download_segment(url, start_time, end_time, status_label):
    def run():
        status_label.config(text="Downloading...")

        is_full_download = (start_time == "00:00:00" and end_time == "00:00:00")


        if is_full_download:
            print ("format: ", selected_format_id.get())
            options = {                
                'format': format_id_map.get(selected_format_id.get(), 'bestvideo+bestaudio/best'),
                'outtmpl': os.path.join(download_dir, '%(title)s_%(height)sp.%(ext)s'),
                'merge_output_format': 'mp4',  # Descarga completa y la une en mp4
                'progress_hooks': [progress_hook],
                'nocolor': True,

            }
        else:
            print(f"Descargando desde {start_time} hasta {end_time}...")
            options = {
                'format': format_id_map.get(selected_format_id.get(), 'bestvideo+bestaudio/best'),
                'outtmpl': os.path.join(download_dir, '%(title)s_%(height)sp.%(ext)s'),
                'download_sections': [f"*{start_time}-{end_time}"],  # Nota: usar formato tipo 00:00:30
                'postprocessor_args': ['-ss', start_time, '-to', end_time],  # Por si acaso para recortar exacto
                'merge_output_format': 'mp4',  # Descarga completa y la une en mp4
                'progress_hooks': [progress_hook],
                'nocolor': True,

            }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            status_label.config(text="✅ Download complete!")
        except Exception as e:
            status_label.config(text="❌ Error: " + str(e))
            print(f"Error downloading: {e}")

    # Ejecutar en segundo plano para no congelar la interfaz
    threading.Thread(target=run).start()

# Inicia la descarga cuando el usuario presiona el botón
def on_download_click():
    url = url_entry.get().strip()
    start_time = start_entry.get().strip()
    end_time = end_entry.get().strip()

    if not url or not start_time or not end_time:
        messagebox.showwarning("Missing fields", "Please fill in all the fields.")
        return

    download_segment(url, start_time, end_time, status_label)

def select_download_folder():
    global download_dir
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        download_dir = folder_selected
        folder_label.config(text=f"Folder: {download_dir}")

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        progress_var.set(f"{percent}")
    elif d['status'] == 'finished':
        progress_var.set("✅ Download finished.")



# --- Interfaz gráfica ---
__version__ = "1.0.0"
root = tb.Window(themename="darkly")  # otros: cyborg, darkly, solar, etc.
root.iconbitmap("icon.ico")
selected_format_id = tk.StringVar()
format_id_map = {}  # Diccionario: visible label → format_id
video_formats = []
audio_formats = []


download_dir = os.getcwd()  # Por defecto, carpeta actual
root.title(f"Catch Video if You Can v{__version__}")
root.geometry("420x420")



folder_label = tk.Label(root, text=f"Folder: {download_dir}", fg="gray")
folder_label.pack()

folder_button = tk.Button(root, text="Choose Folder", command=select_download_folder)
folder_button.pack(pady=5)


tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.insert(0, "https://www.youtube.com/watch?v=DHA_HuGA-Mc")  # Valor por defecto
url_entry.pack()


tk.Label(root, text="Start (hh:mm:ss):").pack(pady=5)
start_entry = tk.Entry(root, width=20)
start_entry.insert(0, "00:00:00")  # Valor por defecto
start_entry.pack()

tk.Label(root, text="End (hh:mm:ss):").pack(pady=5)
end_entry = tk.Entry(root, width=20)
end_entry.insert(0, "00:00:00") # Valor por defecto
end_entry.pack()

analyze_button = tk.Button(root, text="Analyze Video", command=analyze_video)
analyze_button.pack(pady=5)

tk.Label(root, text="Resolution:").pack()
resolution_combo = ttk.Combobox(root, textvariable=selected_format_id, state="readonly")
resolution_combo.pack()


download_button = tk.Button(root, text="Download Video", command=on_download_click)
download_button.pack(pady=15)

status_label = tk.Label(root, text="", fg="blue")
status_label.pack(pady=5)

progress_var = tk.StringVar()
progress_label = tk.Label(root, textvariable=progress_var, fg="green")
progress_label.pack()

version_label = tb.Label(root, text=f"Version {__version__}", font=("Segoe UI", 8))
version_label.pack(side="bottom", pady=5)




root.mainloop()
