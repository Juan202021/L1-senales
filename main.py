import customtkinter as ctk
import sounddevice as sd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.signal import resample
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
        
        # Estados de reproducción
        self.playing_high = False
        self.playing_low = False
        
        # Configuración de frecuencias
        self.duracion = 2
        self.fs_high = 44100  # Frecuencia de Nyquist alta
        self.fs_low = 11025    # Frecuencia de Nyquist baja (para demostración)
        self.ventana_filtro = 350
        self.nivel_ruido = 0.1
        
        self.main_container = ctk.CTkFrame(master)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.show_main_menu()
        
    def show_main_menu(self):
        # Limpiar contenedor
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Frame del menú
        menu_frame = ctk.CTkFrame(self.main_container, width=400)
        menu_frame.pack(expand=True, pady=50)
        
        # Botones del menú
        ctk.CTkLabel(menu_frame, 
                   text="Menú",
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
            widget.destroy()
        self.create_audio_interface()
        
    def show_nyquist_interface(self):
        # Limpiar contenedor principal
        for widget in self.main_container.winfo_children():
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
        
        # Botones de control
        ctk.CTkButton(control_frame,
                    text="Grabar Audio (2s)",
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
                                        to=500,
                                        number_of_steps=49,
                                        command=self.update_filter)
        self.filter_slider.set(self.ventana_filtro)
        self.filter_slider.pack(side="left", padx=10)
        
        self.filter_label = ctk.CTkLabel(config_frame, text=f"Valor: {self.ventana_filtro}")
        self.filter_label.pack(side="left", padx=10)

    def update_filter(self, value):
        self.ventana_filtro = int(value)
        self.filter_label.configure(text=f"Valor: {self.ventana_filtro}")
        
    def record_audio(self):
        # Función de grabación y procesamiento
        grabacion = sd.rec(int(self.duracion * self.fs_high), 
                         samplerate=self.fs_high, 
                         channels=1)
        sd.wait()
        
        senal_original = grabacion.flatten()
        senal_original = senal_original / np.max(np.abs(senal_original))
        
        ruido = np.random.normal(0, self.nivel_ruido, len(senal_original))
        self.senal_ruidosa = senal_original + ruido
        self.senal_ruidosa = self.senal_ruidosa / np.max(np.abs(self.senal_ruidosa))
        
        ventana = np.ones(self.ventana_filtro) / self.ventana_filtro
        self.senal_filtrada = np.convolve(self.senal_ruidosa, ventana, mode='same')
        self.senal_filtrada = self.senal_filtrada / np.max(np.abs(self.senal_filtrada))
        
        self.plot_signals()
        
    def plot_signals(self):
        self.figure.clear()
        
        ax1 = self.figure.add_subplot(211)
        ax1.plot(self.senal_ruidosa, color='#00ffaa')
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
        if hasattr(self, 'senal_ruidosa'):
            sd.play(self.senal_ruidosa, self.fs_high)
            sd.wait()
            
    def play_filtered(self):
        if hasattr(self, 'senal_filtrada'):
            sd.play(self.senal_filtrada, self.fs_high)
            sd.wait()
    
    def create_nyquist_interface(self):
        control_frame = ctk.CTkFrame(self.main_container)
        control_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(control_frame,
                    text="Menú Principal",
                    image=self.back_image,
                    command=self.show_main_menu,
                    width=150,
                    height=35,
                    fg_color="transparent",
                    border_width=1).pack(side="left", padx=10)
        
        ctk.CTkButton(control_frame,
                    text="Grabar Alta Frecuencia",
                    image=self.record_image,
                    command=lambda: self.record_nyquist("high"),
                    width=180,
                    height=35).pack(side="left", padx=10)
        
        ctk.CTkButton(control_frame,
                    text="Grabar Baja Frecuencia",
                    image=self.record_image,
                    command=lambda: self.record_nyquist("low"),
                    width=180,
                    height=35).pack(side="left", padx=10)
        
        # Botones modificados con estados
        self.btn_high = ctk.CTkButton(
            control_frame,
            text=" Reproducir Alta",
            image=self.play_image,
            command=lambda: self.toggle_play("high"),
            width=150,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049",
            compound="left"
        )
        self.btn_high.pack(side="left", padx=10)
        
        self.btn_low = ctk.CTkButton(
            control_frame,
            text=" Reproducir Baja",
            image=self.play_image,
            command=lambda: self.toggle_play("low"),
            width=150,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049",
            compound="left"
        )
        self.btn_low.pack(side="left", padx=10)
        
        self.figure_nyquist = Figure(figsize=(8, 5), dpi=100)
        self.canvas_nyquist = FigureCanvasTkAgg(self.figure_nyquist, master=self.main_container)
        self.canvas_nyquist.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
    def record_nyquist(self, tipo):
        """Realiza grabación en la frecuencia especificada"""
        fs = self.fs_high if tipo == "high" else self.fs_low
        print(f"Grabando a {fs} Hz...")
        
        grabacion = sd.rec(int(self.duracion * fs),
                        samplerate=fs,
                        channels=1)
        sd.wait()
        
        senal = grabacion.flatten()
        senal = senal / np.max(np.abs(senal))
        
        if tipo == "high":
            self.senal_high = senal
            self.t_high = np.linspace(0, self.duracion, len(self.senal_high))
        else:
            # Remuestreo para igualar longitud manteniendo características de frecuencia
            self.senal_low = resample(senal, len(self.senal_high))
            self.t_low = np.linspace(0, self.duracion, len(self.senal_low))
        
        self.plot_nyquist()
    
    def plot_nyquist(self):        
        if hasattr(self, 'senal_high') and hasattr(self, 'senal_low'):
            self.figure_nyquist.clear()
        
            ax1 = self.figure_nyquist.add_subplot(211)
            ax1.plot(self.senal_high, color='#00ffaa')
            ax1.set_title(f'Alta Frecuencia ({self.fs_high} Hz)', fontsize=10, color='white')
            ax1.set_facecolor('#2b2b2b')
            ax1.grid(color='#404040')
            
            ax2 = self.figure_nyquist.add_subplot(212)
            ax2.plot(self.senal_low, color='#ff6666')
            ax2.set_title(f'Baja Frecuencia ({self.fs_low} Hz)', fontsize=10, color='white')
            ax2.set_facecolor('#2b2b2b')
            ax2.grid(color='#404040')
            
            self.figure_nyquist.patch.set_facecolor('#333333')
            self.figure_nyquist.tight_layout()
            self.canvas_nyquist.draw()
        else:
            print("No se pudo graficar: plot_nyquist ")

    def toggle_play(self, tipo):
        if tipo == "high":
            self.playing_high = not self.playing_high
            if self.playing_high:
                self.btn_high.configure(image=self.pause_image, text=" Pausar Alta")
                self.play_nyquist("high")
            else:
                self.btn_high.configure(image=self.play_image, text=" Reproducir Alta")
                self.stop_playback("high")
        
        elif tipo == "low":
            self.playing_low = not self.playing_low
            if self.playing_low:
                self.btn_low.configure(image=self.pause_image, text=" Pausar Baja")
                self.play_nyquist("low")
            else:
                self.btn_low.configure(image=self.play_image, text=" Reproducir Baja")
                self.stop_playback("low")
    
    def play_nyquist(self, tipo):
        if tipo == "high" and hasattr(self, 'senal_high'):
            sd.play(self.senal_high, self.fs_high, blocking=False)
            self.btn_low.configure(image=self.play_image, text=" Reproducir Baja")
        elif tipo == "low" and hasattr(self, 'senal_low'):
            sd.play(self.senal_low, self.fs_low, blocking=False)
            self.btn_high.configure(image=self.play_image, text=" Reproducir Alta")

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