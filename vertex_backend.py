# vertex_backend.py
import os
import time

try:
    # Canibalizamos directamente los servicios oficiales de tu repositorio clonado
    from services.video_service import VideoService
    from services.image_service import ImageService
    from common.config import ProjectConfig
    REPOSITORIO_VALIDO = True
except ImportError:
    REPOSITORIO_VALIDO = False

class VertexLabsManager:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.ARCHIVO_CREDS = "google_creds.json"
        
        # Inyectar las credenciales en el entorno de Google antes de arrancar
        self.configurar_entorno_seguro()

    def log(self, mensaje):
        if self.log_callback:
            self.log_callback(mensaje)
        else:
            print(f"[VERTEX-LOG]: {mensaje}")

    def configurar_entorno_seguro(self):
        """ Enlaza el archivo JSON de Google de forma analítica en el sistema """
        if os.path.exists(self.ARCHIVO_CREDS):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(self.ARCHIVO_CREDS)
            return True
        return False

    def verificar_infraestructura(self):
        """ Comprueba si los archivos clonados y las credenciales están listos """
        if not REPOSITORIO_VALIDO:
            return False, "Estructura del repositorio no detectada. Coloca el script en la raíz."
        if not os.path.exists(self.ARCHIVO_CREDS):
            return False, "Falta el archivo google_creds.json en el taller."
        return True, "Infraestructura Google Vertex lista para operar."

    def generar_video_veo(self, prompt_texto, ruta_salida):
        """ Invoca el VideoService de tu clon para escupir el clip MP4 """
        listo, mensaje = self.verificar_infraestructura()
        if not listo:
            self.log(f"❌ Abortando: {mensaje}")
            return False, mensaje

        self.log("📡 Conectando con el núcleo de Google Veo a través de tu repositorio...")
        try:
            # Canibalismo puro: instanciamos tu servicio clonado
            video_service = VideoService()
            
            self.log("🔮 La GPU de Google está procesando los vectores cinemáticos...")
            # Llamada nativa configurada por Google en tus carpetas
            video_bytes = video_service.generate_video(
                prompt=prompt_texto,
                aspect_ratio="1:1",
                duration_seconds=5 # Formato ideal para Shorts de 40s
            )

            if video_bytes:
                os.makedirs(ruta_salida, exist_ok=True)
                nombre_archivo = f"veo_render_{int(time.time())}.mp4"
                ruta_final = os.path.join(ruta_salida, nombre_archivo)
                
                with open(ruta_final, "wb") as f:
                    f.write(video_bytes)
                
                self.log(f"💾 [ÉXITO] Archivo binario guardado en: {nombre_archivo}")
                return True, ruta_final
            else:
                return False, "El modelo terminó pero devolvió un flujo vacío."

        except Exception as e:
            self.log(f"❌ Fallo crítico en el pipeline: {str(e)}")
            return False, str(e)
