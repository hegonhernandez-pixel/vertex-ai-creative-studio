# render_video.py
import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk

# Jalamos tu nuevo backend modular
from vertex_backend import VertexLabsManager

class CyberpunkVideoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PANDARCADE LAB // VERTEX REPO ENGINE")
        self.root.geometry("600x520")
        self.root.configure(bg="#050508")

        self.carpeta_salida = "videos_generados"
        
        # Enlazamos el backend pasándole nuestra consola de logs
        self.backend = VertexLabsManager(log_callback=self.actualizar_consola_log)

        # ==========================================
        # INTERFAZ GRÁFICA INTERACTIVA (GUI)
        # ==========================================
        
        # --- CABECERA DE ESTADO ---
        self.f_status = tk.Frame(self.root, pady=6)
        self.f_status.pack(fill="x", side="top")
        self.lbl_status = tk.Label(self.f_status, font=("Consolas", 9, "bold"), fg="black")
        self.lbl_status.pack(side="left", padx=15)
        self.actualizar_barra_estado()

        # --- TÍTULO PRINCIPAL ---
        lbl_titulo = tk.Label(self.root, text="// VERTEX CLONE ENGINE //", font=("Arial", 15, "bold"), bg="#050508", fg="#39ff14")
        lbl_titulo.pack(pady=20)

        # --- CUADRO DE TEXTO PROMPT ---
        tk.Label(self.root, text="[root@vertex_repo]$ Prompt para Google Veo:", bg="#050508", fg="#00f0ff", font=("Consolas", 10)).pack(anchor="w", padx=25, pady=2)
        self.txt_prompt = tk.Text(self.root, height=5, bg="#11111b", fg="#39ff14", font=("Consolas", 11), wrap="word", insertbackground="white", highlightthickness=1, highlightbackground="#222233")
        self.txt_prompt.pack(fill="x", padx=25, pady=5)
        self.txt_prompt.insert(tk.END, "Cinematic retro arcade glitch screen displaying KOF 2002, flashing cyan and green neon lights, ultra fluid animation, sci-fi cyberpunk garage style")

        # --- CONSOLA DE MONITOREO EN VIVO ---
        tk.Label(self.root, text="LOGS_DE_TU_REPOSITORIO_VERTEX:", bg="#050508", fg="#7f849c", font=("Consolas", 8, "italic")).pack(anchor="w", padx=25, pady=(10, 2))
        self.txt_log = tk.Text(self.root, height=8, bg="#020204", fg="#a6adc8", font=("Consolas", 10), wrap="word", state="disabled")
        self.txt_log.pack(fill="x", padx=25, pady=5)

        # --- CONTENEDOR DE BOTONES ---
        f_botones = tk.Frame(self.root, bg="#050508")
        f_botones.pack(fill="x", padx=25, pady=15)

        self.btn_render = tk.Button(f_botones, text="🚀 ENVIAR AL MODELO VEO", font=("Arial", 10, "bold"), bg="#00f0ff", fg="black", activebackground="#39ff14", padx=15, pady=6, command=self.ejecutar_render_hilo)
        self.btn_render.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_carpeta = tk.Button(f_botones, text="📁 COPIAS LOCALES", font=("Arial", 10, "bold"), bg="#39ff14", fg="black", activebackground="#00f0ff", padx=15, pady=6, command=self.abrir_carpeta_guardado)
        btn_carpeta.pack(side="right", fill="x", expand=True)

    def actualizar_barra_estado(self):
        listo, mensaje = self.backend.verificar_infraestructura()
        if listo:
            self.f_status.config(bg="#39ff14")
            self.lbl_status.config(bg="#39ff14", text=f"🔒 INSTANCIADO: {mensaje}")
            self.btn_render.config(state="normal", bg="#00f0ff")
        else:
            self.f_status.config(bg="#ff0055")
            self.lbl_status.config(bg="#ff0055", text=f"🚨 PIPELINE INCOMPLETO: {mensaje}")
            self.btn_render.config(state="disabled", bg="#555555")

    def actualizar_consola_log(self, mensaje):
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, f"> {mensaje}\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def abrir_carpeta_guardado(self):
        os.makedirs(self.carpeta_salida, exist_ok=True)
        ruta = os.path.abspath(self.carpeta_salida)
        import subprocess
        os.startfile(ruta) if sys.platform == "win32" else subprocess.Popen(["xdg-open", ruta])

    def ejecutar_render_hilo(self):
        prompt = self.txt_prompt.get("1.0", tk.END).strip()
        if not prompt: return

        self.btn_render.config(state="disabled", bg="#555555")
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.config(state="disabled")

        threading.Thread(target=self._proceso_segundo_plano, args=(prompt,), daemon=True).start()

    def _proceso_segundo_plano(self, prompt_texto):
        exito, resultado = self.backend.generar_video_veo(prompt_texto, self.carpeta_salida)
        self.root.after(0, self.finalizar_gui, exito)

    def finalizar_gui(self, exito):
        self.actualizar_barra_estado()
        if exito:
            messagebox.showinfo("¡Éxito!", "El video de Google Veo se ha canibalizado e inyectado con éxito.")
        else:
            messagebox.showerror("Fallo", "Revisa los logs de la terminal para diagnosticar el error.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CyberpunkVideoGUI(root)
    root.mainloop()
