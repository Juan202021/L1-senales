import customtkinter as ctk
import tkinter as tk
import sounddevice as sd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PIL import Image

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AudioApp:
    def __init__(self, master):
        self.master = master
        master.title("Análisis de Señales")
        master.geometry("1200x900")

        # Cargar imágenes para los botones
        self.back_image = ctk.CTkImage(light_image=Image.open("./Assets/Img/back.png"),
                                      dark_image=Image.open("./Assets/Img/back.png"),
                                      size=(20, 20))

        self.play_image = ctk.CTkImage(light_image=Image.open("./Assets/Img/play.png"),
                                      dark_image=Image.open("./Assets/Img/play.png"),
                                      size=(20, 20))
                                      
        self.pause_image = ctk.CTkImage(light_image=Image.open("./Assets/Img/pause.png"),
                                       dark_image=Image.open("./Assets/Img/pause.png"),
                                       size=(20, 20))
        
        self.record_image = ctk.CTkImage(light_image=Image.open("./Assets/Img/mic.png"),
                                      dark_image=Image.open("./Assets/Img/mic.png"),
                                      size=(20, 20))
        
        # Cargar la imagen de fondo
        bg_image = Image.open("./Assets/Img/bg.webp")

        # Convertir la imagen PIL a CTkImage
        self.bg = ctk.CTkImage(bg_image, size=(1900, 1000))  # Ajusta el tamaño al de la ventana

        # Estados de reproducción
        self.playing_high = False
        self.playing_low = False
        
        # Configuración de frecuencias
        self.duracion = 2
        self.fs_high = 44100  # Frecuencia de Nyquist alta
        self.fs_low = 11025    # Frecuencia de Nyquist baja (para demostración)
        self.m = 50 #50 #60 #80 #260
        self.nivel_ruido = 0.1
        
        self.main_container = ctk.CTkFrame(master)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Crear un CTkLabel para el fondo
        self.background_label = ctk.CTkLabel(self.main_container, image=self.bg, text="")
        self.background_label.place(relwidth=1, relheight=1)  # Ocupa todo el espacio del frame
        
        self.show_main_menu()
        
    def show_main_menu(self):
        # Limpiar contenedor
        for widget in self.main_container.winfo_children():
            if widget != self.background_label:  # No destruir el fondo
                widget.destroy()
        
        # Frame del menú
        menu_frame = ctk.CTkFrame(self.main_container, width=400)
        menu_frame.pack(expand=True, pady=50)
        
        # Botones del menú
        ctk.CTkLabel(menu_frame, 
                   text="Análisis de Señales",
                   font=("Helvetica", 24, "bold")).pack(pady=40)
        
        ctk.CTkButton(menu_frame,
                    text="Filtrado de Audio",
                    command=self.show_audio_interface,
                    width=300,
                    height=50,
                    font=("Helvetica", 14)).pack(padx=50)
        
        ctk.CTkButton(menu_frame,
                    text="Demostración Nyquist",
                    command=self.show_nyquist_interface,
                    width=300,
                    height=50,
                    font=("Helvetica", 14)).pack(pady=30, padx=50)
        
    def show_audio_interface(self):
        # Limpiar contenedor principal
        for widget in self.main_container.winfo_children():
            if widget != self.background_label:  # No destruir el fondo
                widget.destroy()
        self.create_audio_interface()
        
    def show_nyquist_interface(self):
        # Limpiar contenedor principal
        for widget in self.main_container.winfo_children():
            if widget != self.background_label:  # No destruir el fondo
                widget.destroy()
        self.create_nyquist_interface()
    
    # Sección para filtrado de audio (original)
    def create_audio_interface(self):
        # Frame superior con botones
        control_frame = ctk.CTkFrame(self.main_container)
        control_frame.pack(fill="x", pady=10)

        # Botón de regreso
        ctk.CTkButton(control_frame,
                    text="Menú Principal",
                    image=self.back_image,
                    command=self.show_main_menu,
                    width=150,
                    height=35,
                    fg_color="transparent",
                    border_width=1).pack(side="left", padx=10)

        # Campo para tiempo de grabación
        time_frame = ctk.CTkFrame(control_frame)
        time_frame.pack(side="left", padx=10)

        ctk.CTkLabel(time_frame, 
                    text="Tiempo (s):", 
                    font=("Arial", 11)).pack(side="left", padx=5)
        
        self.entry_time_audio = ctk.CTkEntry(time_frame, 
                                            width=100,
                                            placeholder_text="2")
        self.entry_time_audio.pack(side="left", padx=5)

        # Botones de control
        ctk.CTkButton(control_frame,
                    text="Grabar Audio",
                    image=self.record_image,
                    command=self.record_audio,
                    width=150,
                    height=35,
                    fg_color="#4CAF50",
                    hover_color="#45a049",
                    compound="left").pack(side="left", padx=10)
        
        ctk.CTkButton(control_frame,
                    text="Reproducir Original",
                    image=self.play_image,
                    command=self.play_original,
                    width=150,
                    height=35).pack(side="left", padx=10)
        
        ctk.CTkButton(control_frame,
                    text="Reproducir Filtrado",
                    image=self.play_image,
                    command=self.play_filtered,
                    width=150,
                    height=35).pack(side="left", padx=10)

        # Área de gráficos
        graph_frame = ctk.CTkFrame(self.main_container)
        graph_frame.pack(fill="both", expand=True)
        
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel de configuración
        config_frame = ctk.CTkFrame(self.main_container)
        config_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(config_frame, text="Tamaño del Filtro:").pack(side="left", padx=10)
        self.filter_slider = ctk.CTkSlider(config_frame,
                                        from_=10,
                                        to=2000,
                                        number_of_steps=199,
                                        command=self.update_filter, width=500)
        self.filter_slider.set(self.m)
        self.filter_slider.pack(side="left", padx=10)
        
        self.filter_label = ctk.CTkLabel(config_frame, text=f"Valor: {self.m}")
        self.filter_label.pack(side="left", padx=10)

    def update_filter(self, value):
        self.m = int(value)
        self.filter_label.configure(text=f"Valor: {self.m}")
        
    def filtro_media_movil(self):
        ventana = []
        self.senal_filtrada = []
        
        for i in range(len(self.senal_original)):
            ventana.append(self.senal_original[i])
            
            # Mantener ventana de tamaño máximo m
            if len(ventana) > self.m:
                ventana.pop(0)  # Eliminar el elemento más antiguo (FIFO)
            
            # Calcular media solo si la ventana está llena
            if len(ventana) == self.m:
                media = sum(ventana) / self.m
                self.senal_filtrada.append(media)
            else:
                self.senal_filtrada.append(self.senal_original[i])

    def record_audio(self):
        # Obtener tiempo de grabación
        self.duracion = float(self.entry_time_audio.get())
        if self.duracion <= 0:
            raise ValueError("El tiempo debe ser mayor a 0")
        
        # Función de grabación y procesamiento
        grabacion = sd.rec(int(self.duracion * self.fs_high), 
                         samplerate=self.fs_high, 
                         channels=1)
        sd.wait()
        
        self.senal_original = grabacion.flatten()
        self.senal_original = self.senal_original / np.max(np.abs(self.senal_original))
        
        self.filtro_media_movil()
        
        self.plot_signals()
        
    def plot_signals(self):
        self.figure.clear()
        
        ax1 = self.figure.add_subplot(211)
        ax1.plot(self.senal_original, color='#00ffaa')
        ax1.set_title('Señal con Ruido', fontsize=10, color='white')
        ax1.set_facecolor('#2b2b2b')
        ax1.grid(color='#404040')
        
        ax2 = self.figure.add_subplot(212)
        ax2.plot(self.senal_filtrada, color='#ff6666')
        ax2.set_title('Señal Filtrada', fontsize=10, color='white')
        ax2.set_facecolor('#2b2b2b')
        ax2.grid(color='#404040')
        
        self.figure.patch.set_facecolor('#333333')
        self.figure.tight_layout()
        self.canvas.draw()
        
    def play_original(self):
        if hasattr(self, 'senal_original'):
            sd.play(self.senal_original, self.fs_high)
            sd.wait()
            
    def play_filtered(self):
        if hasattr(self, 'senal_filtrada'):
            sd.play(self.senal_filtrada, self.fs_high)
            sd.wait()
    
    def create_nyquist_interface(self):
        control_frame = ctk.CTkFrame(self.main_container)
        control_frame.pack(fill="x", pady=10, padx=10)

        # Botón de regreso
        ctk.CTkButton(control_frame,
                    text="Menú Principal",
                    image=self.back_image,
                    command=self.show_main_menu,
                    width=150,
                    height=35,
                    fg_color="transparent",
                    border_width=1).pack(side="left", padx=5, pady=5)

        # Marco para centrar los inputs y botones
        center_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        center_frame.pack(side="left", expand=True)  # Centrar horizontalmente

        # Campo para tiempo de grabación
        time_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        time_frame.pack(pady=5)

        ctk.CTkLabel(time_frame, 
                    text="Tiempo (s):", 
                    font=("Arial", 11)).pack(side="left", padx=5)
        
        self.entry_time = ctk.CTkEntry(time_frame, 
                                    width=100,
                                    placeholder_text="2")
        self.entry_time.pack(side="left", padx=5)

        # Frecuencia alta
        freq_high_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        freq_high_frame.pack(pady=5)

        ctk.CTkLabel(freq_high_frame, 
                    text="Frec Alta (Hz):", 
                    font=("Arial", 11)).pack(side="left", padx=5)
        
        self.entry_fs_high = ctk.CTkEntry(freq_high_frame, 
                                        width=100,
                                        placeholder_text="44100")
        self.entry_fs_high.pack(side="left", padx=5)
        
        ctk.CTkButton(freq_high_frame,
                    text="Grabar",
                    image=self.record_image,
                    command=lambda: self.record_nyquist("high"),
                    width=120,
                    height=35).pack(side="left", padx=5)
        
        self.btn_high = ctk.CTkButton(
            freq_high_frame,
            text=" Reproducir",
            image=self.play_image,
            command=lambda: self.toggle_play("high"),
            width=120,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049",
            compound="left"
        )
        self.btn_high.pack(side="left", padx=5)

        # Frecuencia baja
        freq_low_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        freq_low_frame.pack(pady=5)

        ctk.CTkLabel(freq_low_frame, 
                    text="Frec Baja (Hz):", 
                    font=("Arial", 11)).pack(side="left", padx=5)
        
        self.entry_fs_low = ctk.CTkEntry(freq_low_frame, 
                                        width=100,
                                        placeholder_text="11025")
        self.entry_fs_low.pack(side="left", padx=5)
        
        ctk.CTkButton(freq_low_frame,
                    text="Grabar",
                    image=self.record_image,
                    command=lambda: self.record_nyquist("low"),
                    width=120,
                    height=35).pack(side="left", padx=5)
        
        self.btn_low = ctk.CTkButton(
            freq_low_frame,
            text=" Reproducir",
            image=self.play_image,
            command=lambda: self.toggle_play("low"),
            width=120,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049",
            compound="left"
        )
        self.btn_low.pack(side="left", padx=5)

        # Gráfico
        self.figure_nyquist = Figure(figsize=(8, 5), dpi=100)
        self.canvas_nyquist = FigureCanvasTkAgg(self.figure_nyquist, master=self.main_container)
        self.canvas_nyquist.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def record_nyquist(self, tipo):
        try:
            # Obtener tiempo de grabación
            self.duracion = float(self.entry_time.get())
            if self.duracion <= 0:
                raise ValueError("El tiempo debe ser mayor a 0")
        
            # Obtener frecuencia del campo correspondiente
            if tipo == "high":
                fs = int(self.entry_fs_high.get())
            else:
                fs = int(self.entry_fs_low.get())
                
            # Validar frecuencia
            if fs <= 0:
                raise ValueError("La frecuencia debe ser mayor a 0")
                
            print(f"Grabando a {fs} Hz...")
            
            grabacion = sd.rec(int(self.duracion * fs),
                            samplerate=fs,
                            channels=1)
            sd.wait()
            
            senal = grabacion.flatten()
            senal = senal / np.max(np.abs(senal))
            
            # Almacenar con la frecuencia usada
            if tipo == "high":
                self.fs_high = fs
                self.senal_high = senal
            else:
                self.fs_low = fs
                # self.senal_low = senal
                self.senal_low = []
                for i in range(len(senal)):
                    if i % 2 == 0 and i != 0:
                        self.senal_low.append(sum([senal[i], senal[i-1]])/2)
                        self.senal_low.append(sum([senal[i], senal[i-1]])/2)
                        self.senal_low.append(senal[i])
                    else:
                        self.senal_low.append(senal[i])
                print(len(self.senal_low))
            self.plot_nyquist()
            
        except Exception as e:
            print(f"Error: {e}")
            #tk.messagebox.showerror("Error", f"Frecuencia inválida: {str(e)}")
    
    def plot_nyquist(self):
        if hasattr(self, 'senal_high') and hasattr(self, 'senal_low'):
            self.figure_nyquist.clear()
            
            # Crear ejes de tiempo para ambas señales
            time_high = np.linspace(0, self.duracion, len(self.senal_high))
            time_low = np.linspace(0, self.duracion, len(self.senal_low))
            
            # Configurar estilo del gráfico
            plt_style = {
                'axes.facecolor': '#2b2b2b',
                'axes.edgecolor': 'white',
                'axes.labelcolor': 'white',
                'xtick.color': 'white',
                'ytick.color': 'white',
                'grid.color': '#404040'
            }
            
            with plt.rc_context(plt_style):
                # Gráfico para alta frecuencia
                ax1 = self.figure_nyquist.add_subplot(211)
                ax1.plot(time_high, self.senal_high, '#00ffaa', linewidth=0.8)
                ax1.set_title(f'Alta Frecuencia ({self.fs_high} Hz)', fontsize=10, pad=10, color="white")
                ax1.set_ylabel('Amplitud', fontsize=8)
                ax1.grid(True, linestyle='--', alpha=0.5)
                ax1.set_xlim(0, self.duracion)
                
                # Gráfico para baja frecuencia
                ax2 = self.figure_nyquist.add_subplot(212)
                ax2.plot(time_low, self.senal_low, '#ff6666', linewidth=0.8)
                ax2.set_title(f'Baja Frecuencia ({self.fs_low} Hz)', fontsize=10, pad=10, color="white")
                ax2.set_xlabel('Tiempo (s)', fontsize=8)
                ax2.set_ylabel('Amplitud', fontsize=8)
                ax2.grid(True, linestyle='--', alpha=0.5)
                ax2.set_xlim(0, self.duracion)
                
                # Ajustar espacios
                self.figure_nyquist.subplots_adjust(hspace=0.4)
                self.figure_nyquist.patch.set_facecolor('#333333')
                
            self.canvas_nyquist.draw()
        else:
            print("Error: No hay señales grabadas para graficar")

    def toggle_play(self, tipo):
        if tipo == "high":
            self.playing_high = not self.playing_high
            if self.playing_high:
                self.btn_high.configure(image=self.pause_image, text=" Pausar")
                self.play_nyquist("high")
            else:
                self.btn_high.configure(image=self.play_image, text=" Reproducir")
                self.stop_playback("high")
        
        elif tipo == "low":
            self.playing_low = not self.playing_low
            if self.playing_low:
                self.btn_low.configure(image=self.pause_image, text=" Pausar")
                self.play_nyquist("low")
            else:
                self.btn_low.configure(image=self.play_image, text=" Reproducir")
                self.stop_playback("low")
    
    def play_nyquist(self, tipo):
        if tipo == "high" and hasattr(self, 'senal_high'):
            sd.play(self.senal_high, self.fs_high, blocking=False)
            self.btn_low.configure(image=self.play_image, text=" Reproducir")
        elif tipo == "low" and hasattr(self, 'senal_low'):
            sd.play(self.senal_low, self.fs_low, blocking=False)
            self.btn_high.configure(image=self.play_image, text=" Reproducir")

    def stop_playback(self, tipo):
        sd.stop()
        if tipo == "high":
            self.playing_high = False
        else:
            self.playing_low = False

if __name__ == "__main__":
    root = ctk.CTk()
    app = AudioApp(root)
    root.mainloop()