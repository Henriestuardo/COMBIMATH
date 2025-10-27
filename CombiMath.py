import pygame
import random
import sys
import json
import os
from datetime import datetime

# ------------------ CombiMath - CON SISTEMA DE USUARIOS ------------------

pygame.init()

# Configuración de pantalla
ANCHO = 800
ALTO = 670
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("CombiMath - Aventura Espacial")
reloj = pygame.time.Clock()

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0)
AZUL = (100, 150, 255)
NARANJA = (255, 165, 0)
MORADO = (200, 100, 255)
CYAN = (0, 255, 255)
VERDE_OSCURO = (0, 180, 0)
DORADO = (255, 215, 0)
GRIS = (150, 150, 150)

# Rutas de sonido
RUTA_MUSICA_MENU = "sonidos/menu_music.mp3"
RUTA_SONIDO_COMPRA = "sonidos/compra.wav"
RUTA_MUSICA_JUEGO = "sonidos/juego_music.mp3"

# Intentar cargar sonidos
sonido_compra = None
try:
    pygame.mixer.init()
    if os.path.exists(RUTA_SONIDO_COMPRA):
        sonido_compra = pygame.mixer.Sound(RUTA_SONIDO_COMPRA)
    if os.path.exists(RUTA_MUSICA_MENU):
        pygame.mixer.music.load(RUTA_MUSICA_MENU)
        pygame.mixer.music.set_volume(0.4)
except Exception:
    sonido_compra = None

# SISTEMA DE USUARIOS Y GUARDADO
def cargar_usuarios():
    """Carga la base de datos de usuarios desde JSON"""
    if os.path.exists('combimath_usuarios.json'):
        try:
            with open('combimath_usuarios.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando usuarios: {e}")
    return {"usuarios": {}, "usuario_actual": None}

def guardar_usuarios(datos):
    """Guarda la base de datos de usuarios en JSON"""
    try:
        with open('combimath_usuarios.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando usuarios: {e}")

def crear_usuario(nombre):
    """Crea un nuevo usuario con datos iniciales"""
    return {
        'nombre': nombre,
        'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'monedas': 0,
        'objetivos_totales': 0,
        'mejor_combo': 0,
        'mejor_puntuacion': 0,
        'mejor_nivel': 1,
        'tiempo_total_jugado': 0,
        'partidas_jugadas': 0,
        'naves_desbloqueadas': ['basica'],
        'fondos_desbloqueados': ['espacio'],
        'nave_actual': 'basica',
        'fondo_actual': 'espacio',
        'logros': {
            'primer_objetivo': False,
            'objetivos_10': False,
            'combo_x5': False,
            'nivel_5': False,
            'nivel_10': False,
        },
        'historial_partidas': []
    }

def agregar_al_historial(usuario, puntos, nivel, objetivos, tiempo, combo_max):
    """Agrega una partida al historial del usuario"""
    partida = {
        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'puntos': puntos,
        'nivel': nivel,
        'objetivos': objetivos,
        'tiempo': tiempo,
        'combo_maximo': combo_max
    }
    usuario['historial_partidas'].insert(0, partida)

    if len(usuario['historial_partidas']) > 20:
        usuario['historial_partidas'] = usuario['historial_partidas'][:20]

# Cargar datos de usuarios
datos_usuarios = cargar_usuarios()

# CATÁLOGO DE ITEMS
catalogo_naves = {
    'basica': {'nombre': 'Cohete Básico', 'precio': 0, 'color': AZUL},
    'roja': {'nombre': 'Cohete Rojo', 'precio': 50, 'color': ROJO},
    'verde': {'nombre': 'Cohete Verde', 'precio': 75, 'color': VERDE},
    'dorada': {'nombre': 'Cohete Dorado', 'precio': 100, 'color': DORADO},
}

catalogo_fondos = {
    'espacio': {'nombre': 'Espacio Profundo', 'precio': 0},
    'nebulosa': {'nombre': 'Nebulosa Rosa', 'precio': 60},
    'galaxia': {'nombre': 'Galaxia Azul', 'precio': 90},
}

logros_info = {
    'primer_objetivo': {'nombre': 'Primer Paso', 'desc': 'Completa tu primer objetivo'},
    'objetivos_10': {'nombre': 'Matemático', 'desc': 'Completa 10 objetivos'},
    'combo_x5': {'nombre': 'Combo Maestro', 'desc': 'Consigue un combo x5'},
    'nivel_5': {'nombre': 'Explorador', 'desc': 'Alcanza el nivel 5'},
    'nivel_10': {'nombre': 'Leyenda', 'desc': 'Alcanza el nivel 10'},
}

# CARGAR IMÁGENES
def cargar_imagen_nave(nombre_archivo, color_fallback):
    try:
        img = pygame.image.load(nombre_archivo)
        return pygame.transform.scale(img, (50, 40))
    
    except Exception:
        surf = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.rect(surf, (50, 50, 50), (0, 0, 50, 40))
        pygame.draw.rect(surf, color_fallback, (0, 0, 50, 40), 2)

        fuente_temp = pygame.font.Font(None, 32)
        texto = fuente_temp.render("?", True, color_fallback)

        surf.blit(texto, (18, 8))
        return surf

def cargar_imagen_fondo(nombre_archivo, color_base=(5, 5, 25)):
    try:
        img = pygame.image.load(nombre_archivo)
        return pygame.transform.scale(img, (ANCHO, ALTO))
    
    except Exception:
        surf = pygame.Surface((ANCHO, ALTO))
        surf.fill(color_base)

        for _ in range(100):
            x, y = random.randint(0, ANCHO), random.randint(0, ALTO)
            pygame.draw.circle(surf, BLANCO, (x, y), random.randint(1, 2))
        return surf

naves_imagenes = {
    'basica': cargar_imagen_nave('nave_roja.png', AZUL),
    'roja': cargar_imagen_nave('nave_verde.png', ROJO),
    'verde': cargar_imagen_nave('nave_basica.png', VERDE),
    'dorada': cargar_imagen_nave('nave_dorada.png', DORADO),
}

fondos_imagenes = {
    'espacio': cargar_imagen_fondo('fondo_espacio.png', (5, 5, 25)),
    'nebulosa': cargar_imagen_fondo('fondo_nebulosa.png', (30, 10, 40)),
    'galaxia': cargar_imagen_fondo('fondo_galaxia.png', (10, 20, 50)),
}

try:
    corazon_imagen = pygame.image.load("Corazon.png")
    corazon_imagen = pygame.transform.scale(corazon_imagen, (22, 22))

except Exception:
    corazon_imagen = pygame.Surface((22, 22), pygame.SRCALPHA)
    pygame.draw.circle(corazon_imagen, ROJO, (7, 9), 6)
    pygame.draw.circle(corazon_imagen, ROJO, (15, 9), 6)
    pygame.draw.polygon(corazon_imagen, ROJO, [(2, 11), (20, 11), (11, 21)])

try:
    moneda_imagen = pygame.image.load("moneda.png")
    moneda_imagen = pygame.transform.scale(moneda_imagen, (20, 20))

except Exception:
    moneda_imagen = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(moneda_imagen, DORADO, (10, 10), 10)
    pygame.draw.circle(moneda_imagen, AMARILLO, (10, 10), 7)

try:
    basurero_imagen = pygame.image.load("basurero.png")
    basurero_imagen = pygame.transform.scale(basurero_imagen, (40, 40))

except Exception:
    basurero_imagen = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(basurero_imagen, (100, 100, 100), (5, 5, 30, 5), border_radius=2)
    pygame.draw.rect(basurero_imagen, (150, 150, 150), (8, 12, 24, 25), border_radius=3)
    pygame.draw.line(basurero_imagen, (100, 100, 100), (14, 16), (14, 32), 2)
    pygame.draw.line(basurero_imagen, (100, 100, 100), (20, 16), (20, 32), 2)
    pygame.draw.line(basurero_imagen, (100, 100, 100), (26, 16), (26, 32), 2)

# VARIABLES DEL JUEGO
jugador_x = ANCHO // 2
jugador_y = ALTO - 80
velocidad_jugador = 10
meteoritos = []
particulas = []
inventario = []
max_inventario = 8
puntos = 0
vidas = 3
vidas_maximas = 5
nivel = 1
objetivo_actual = 0
combo = 0
combo_maximo = 0
objetivos_completados = 0
tiempo_mensaje = 0
mensaje_actual = ""
color_mensaje = BLANCO
numero_seleccionado_1 = None
numero_seleccionado_2 = None
tiempo_inicio_partida = 0
tiempo_partida = 0

# ESTADOS DEL JUEGO
MENU = 0
JUGANDO = 1
PAUSADO = 2
GAME_OVER = 3
TIENDA = 4
LOGROS = 5
COMO_JUGAR = 6
SELECCION_USUARIO = 7
ESTADISTICAS = 8
HISTORIAL = 9
INSTRUCCIONES_POPUP = 10 
estado_juego = SELECCION_USUARIO

logro_desbloqueado = None
tiempo_logro = 0

fuente_pequena = pygame.font.Font(None, 24)
fuente = pygame.font.Font(None, 32)
fuente_grande = pygame.font.Font(None, 48)
fuente_titulo = pygame.font.Font(None, 72)

# Funciones de generación
def generar_objetivo(nivel):
    if nivel <= 2:
        return random.randint(10, 25)
    elif nivel <= 4:
        return random.randint(20, 40)
    else:
        return random.randint(30, 60)

def generar_numero_meteorito(nivel):
    if nivel <= 2:
        return random.randint(1, 10)
    elif nivel <= 4:
        return random.randint(1, 15)
    else:
        return random.randint(1, 20)

# Clases
class Particula:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.vida = 40
        self.color = color
        self.tamano = random.randint(2, 6)
    
    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1
        self.vy += 0.15
    
    def dibujar(self):
        if self.vida > 0:
            alpha = int((self.vida / 40) * 255)
            s = pygame.Surface((self.tamano * 2, self.tamano * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.tamano, self.tamano), self.tamano)
            pantalla.blit(s, (int(self.x), int(self.y)))

class Meteorito:
    def __init__(self):
        self.x = random.randint(40, ANCHO - 80)
        self.y = -70
        self.velocidad = random.uniform(2, 3) + (nivel * 0.2)
        self.numero = generar_numero_meteorito(nivel)
        self.tamano = 45
        self.pulsacion = random.uniform(0, 6.28)
        
    def mover(self):
        self.y += self.velocidad
        self.pulsacion += 0.1
        
    def dibujar(self):
        escala = 1 + 0.15 * abs(pygame.math.Vector2(0, self.pulsacion).length() % 2 - 1)
        tamano_actual = int(self.tamano * escala)

        pygame.draw.circle(pantalla, NARANJA, 
            (int(self.x + self.tamano // 2), int(self.y + self.tamano // 2)), 
            tamano_actual // 2, 3)
        
        pygame.draw.circle(pantalla, (180, 80, 0), 
            (int(self.x + self.tamano // 2), int(self.y + self.tamano // 2)), 
            tamano_actual // 2 - 3)
        
        texto = fuente_grande.render(str(self.numero), True, BLANCO)
        rect = texto.get_rect(center=(int(self.x + self.tamano // 2), int(self.y + self.tamano // 2)))
        pantalla.blit(texto, rect)

# Efectos
def crear_explosion(x, y, color, cantidad=20):
    for _ in range(cantidad):
        particulas.append(Particula(x, y, color))

# Utilidades
def verificar_colision_jugador(meteorito):
    return (jugador_x < meteorito.x + meteorito.tamano and
        jugador_x + 50 > meteorito.x and
        jugador_y < meteorito.y + meteorito.tamano and
        jugador_y + 40 > meteorito.y)

def verificar_objetivo_en_inventario():
    return objetivo_actual in inventario

def mostrar_mensaje(texto, color, duracion=120):
    global mensaje_actual, color_mensaje, tiempo_mensaje
    mensaje_actual = texto
    color_mensaje = color
    tiempo_mensaje = duracion

def verificar_logro(nombre_logro):
    global logro_desbloqueado, tiempo_logro
    usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
    if not usuario_actual['logros'][nombre_logro]:
        usuario_actual['logros'][nombre_logro] = True
        logro_desbloqueado = nombre_logro
        tiempo_logro = 180
        guardar_usuarios(datos_usuarios)

def reiniciar_juego():
    global jugador_x, jugador_y, meteoritos, particulas, puntos, vidas, nivel
    global objetivo_actual, inventario, combo, combo_maximo, estado_juego
    global numero_seleccionado_1, numero_seleccionado_2
    global objetivos_completados, tiempo_mensaje, mensaje_actual, tiempo_inicio_partida, tiempo_partida
    jugador_x = ANCHO // 2
    jugador_y = ALTO - 80
    meteoritos.clear()
    particulas.clear()
    inventario.clear()
    puntos = 0
    vidas = 3
    nivel = 1
    objetivo_actual = generar_objetivo(nivel)
    combo = 0
    combo_maximo = 0
    objetivos_completados = 0
    tiempo_mensaje = 0
    mensaje_actual = ""
    numero_seleccionado_1 = None
    numero_seleccionado_2 = None
    tiempo_inicio_partida = pygame.time.get_ticks()
    tiempo_partida = 0
    estado_juego = JUGANDO

# Botones
def dibujar_boton(texto, x, y, ancho, alto, color, color_hover):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_sobre = x < mouse_x < x + ancho and y < mouse_y < y + alto
    color_actual = color_hover if mouse_sobre else color
    pygame.draw.rect(pantalla, color_actual, (x, y, ancho, alto), border_radius=10)
    pygame.draw.rect(pantalla, BLANCO, (x, y, ancho, alto), 3, border_radius=10)
    texto_render = fuente.render(texto, True, BLANCO)
    texto_rect = texto_render.get_rect(center=(x + ancho // 2, y + alto // 2))
    pantalla.blit(texto_render, texto_rect)
    return mouse_sobre

def get_rect_inventario(indice):
    panel_y = 80
    x_inicio = 180
    espacio = 60
    x = x_inicio + (indice * espacio)
    return pygame.Rect(x, panel_y + 10, 55, 55)

def get_rect_basurero():
    return pygame.Rect(ANCHO - 70, 85, 50, 50)

# DIBUJAR PANTALLAS
def dibujar_seleccion_usuario():
    fondo_actual = fondos_imagenes['espacio']
    pantalla.blit(fondo_actual, (0, 0))
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect())
    pantalla.blit(overlay, (0, 0))
    
    titulo = fuente_titulo.render("COMBIMATH", True, CYAN)
    subtitulo = fuente_grande.render("Selecciona tu Usuario", True, AMARILLO)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 60))
    pantalla.blit(subtitulo, (ANCHO // 2 - subtitulo.get_width() // 2, 140))
    
    y = 200
    botones_usuarios = []
    botones_eliminar = []
    
    for nombre_usuario in datos_usuarios["usuarios"]:
        usuario = datos_usuarios["usuarios"][nombre_usuario]
        texto_usuario = fuente.render(f"{nombre_usuario} - Nivel: {usuario['mejor_nivel']} - Puntos: {usuario['mejor_puntuacion']}", True, BLANCO)
        pantalla.blit(texto_usuario, (ANCHO // 2 - texto_usuario.get_width() // 2, y))
        
        btn_seleccionar = dibujar_boton("SELECCIONAR", ANCHO // 2 - 140, y + 30, 120, 30, VERDE_OSCURO, VERDE)
        btn_eliminar = dibujar_boton("ELIMINAR", ANCHO // 2 + 20, y + 30, 120, 30, (120, 0, 0), ROJO)
        botones_usuarios.append((nombre_usuario, btn_seleccionar))
        botones_eliminar.append((nombre_usuario, btn_eliminar))
        y += 80
    btn_nuevo = dibujar_boton("NUEVO USUARIO", ANCHO // 2 - 100, y + 20, 200, 40, AZUL, CYAN)
    
    return botones_usuarios, botones_eliminar, btn_nuevo

def dibujar_crear_usuario():
    fondo_actual = fondos_imagenes['espacio']
    pantalla.blit(fondo_actual, (0, 0))
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 220), overlay.get_rect())
    pantalla.blit(overlay, (0, 0))
    
    panel_ancho = 500
    panel_alto = 400
    panel_x = ANCHO // 2 - panel_ancho // 2
    panel_y = 135
    
    pygame.draw.rect(pantalla, (20, 20, 50, 230), (panel_x, panel_y, panel_ancho, panel_alto), border_radius=15)
    pygame.draw.rect(pantalla, CYAN, (panel_x, panel_y, panel_ancho, panel_alto), 4, border_radius=15)
    
    titulo = fuente_titulo.render("NUEVO USUARIO", True, CYAN)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 80))
    
    instruccion = fuente.render("Escribe tu nombre de usuario:", True, BLANCO)
    pantalla.blit(instruccion, (ANCHO // 2 - instruccion.get_width() // 2, 180))
    
    info = fuente_pequena.render("(Máximo 15 caracteres)", True, GRIS)
    pantalla.blit(info, (ANCHO // 2 - info.get_width() // 2, 210))
    
    campo_ancho = 350
    campo_x = ANCHO // 2 - campo_ancho // 2
    pygame.draw.rect(pantalla, (30, 30, 70), (campo_x, 250, campo_ancho, 55), border_radius=10)
    pygame.draw.rect(pantalla, CYAN, (campo_x, 250, campo_ancho, 55), 3, border_radius=10)
    
    if pygame.time.get_ticks() % 1000 < 500:
        pygame.draw.line(pantalla, CYAN, (campo_x + 15, 260), (campo_x + 15, 295), 2)
    
    btn_crear = dibujar_boton("CREAR Y JUGAR", ANCHO // 2 - 120, 340, 240, 55, VERDE_OSCURO, VERDE)
    btn_volver = dibujar_boton("CANCELAR", ANCHO // 2 - 100, 420, 200, 50, (80, 0, 0), ROJO)
    
    consejo = fuente_pequena.render("Presiona ENTER para crear o ESC para cancelar", True, AMARILLO)
    pantalla.blit(consejo, (ANCHO // 2 - consejo.get_width() // 2, 500))
    
    return btn_crear, btn_volver

def dibujar_menu():
    try:
        if os.path.exists(RUTA_MUSICA_MENU) and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(RUTA_MUSICA_MENU)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.4)
    except Exception:
        pass

    usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
    fondo_actual = fondos_imagenes[usuario_actual['fondo_actual']]
    pantalla.blit(fondo_actual, (0, 0))
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect())
    pantalla.blit(overlay, (0, 0))
    
    titulo = fuente_titulo.render("COMBIMATH", True, CYAN)
    subtitulo = fuente_grande.render("Aventura Espacial", True, AMARILLO)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 60))
    pantalla.blit(subtitulo, (ANCHO // 2 - subtitulo.get_width() // 2, 140))
    
    texto_usuario = fuente.render(f"Jugador: {datos_usuarios['usuario_actual']}", True, BLANCO)
    pantalla.blit(texto_usuario, (ANCHO // 2 - texto_usuario.get_width() // 2, 190))
    
    pantalla.blit(moneda_imagen, (ANCHO // 2 - 60, 220))
    texto_monedas = fuente_grande.render(str(usuario_actual['monedas']), True, DORADO)
    pantalla.blit(texto_monedas, (ANCHO // 2 - 30, 215))
    
    btn_jugar = dibujar_boton("JUGAR", ANCHO // 2 - 100, 265, 200, 50, VERDE_OSCURO, VERDE)
    btn_tienda = dibujar_boton("TIENDA", ANCHO // 2 - 100, 330, 200, 50, (100, 50, 0), NARANJA)
    btn_logros = dibujar_boton("LOGROS", ANCHO // 2 - 100, 395, 200, 50, (80, 0, 120), MORADO)
    btn_estadisticas = dibujar_boton("ESTADÍSTICAS", ANCHO // 2 - 100, 460, 200, 50, (0, 80, 120), CYAN)
    btn_como_jugar = dibujar_boton("¿CÓMO JUGAR?", ANCHO // 2 - 100, 525, 200, 50, (80, 80, 0), AMARILLO)
    btn_usuarios = dibujar_boton("CAMBIAR USUARIO", ANCHO // 2 - 100, 590, 200, 50, (60, 60, 100), (100, 100, 180))
    
    inst = fuente_pequena.render("Suma números para alcanzar el objetivo", True, BLANCO)
    pantalla.blit(inst, (ANCHO // 2 - inst.get_width() // 2, 650))
    
    return btn_jugar, btn_tienda, btn_logros, btn_estadisticas, btn_como_jugar, btn_usuarios

def dibujar_estadisticas():
    usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
    fondo_actual = fondos_imagenes[usuario_actual['fondo_actual']]
    pantalla.blit(fondo_actual, (0, 0))
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 220), overlay.get_rect())
    pantalla.blit(overlay, (0, 0))
    
    titulo = fuente_titulo.render("ESTADÍSTICAS", True, CYAN)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))
    
    texto_usuario = fuente_grande.render(f"Jugador: {datos_usuarios['usuario_actual']}", True, AMARILLO)
    pantalla.blit(texto_usuario, (ANCHO // 2 - texto_usuario.get_width() // 2, 100))
    
    stats = [
        f"Fecha de creación: {usuario_actual['fecha_creacion']}",
        f"Partidas jugadas: {usuario_actual['partidas_jugadas']}",
        f"Tiempo total jugado: {usuario_actual['tiempo_total_jugado'] // 60} minutos",
        f"Mejor puntuación: {usuario_actual['mejor_puntuacion']}",
        f"Mejor nivel alcanzado: {usuario_actual['mejor_nivel']}",
        f"Mejor combo: x{usuario_actual['mejor_combo']}",
        f"Objetivos completados: {usuario_actual['objetivos_totales']}",
        f"Monedas totales: {usuario_actual['monedas']}",
    ]
    
    y = 160
    for stat in stats:
        texto = fuente.render(stat, True, BLANCO)
        pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, y))
        y += 40
    
    btn_historial = dibujar_boton("VER HISTORIAL", ANCHO // 2 - 100, 500, 200, 50, MORADO, (200, 100, 255))
    btn_volver = dibujar_boton("VOLVER", ANCHO // 2 - 100, 570, 200, 50, (80, 0, 0), ROJO)
    
    return btn_historial, btn_volver

def dibujar_historial():
    usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
    fondo_actual = fondos_imagenes[usuario_actual['fondo_actual']]
    pantalla.blit(fondo_actual, (0, 0))
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 220), overlay.get_rect())
    pantalla.blit(overlay, (0, 0))
    
    titulo = fuente_titulo.render("HISTORIAL", True, MORADO)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))
    
    if not usuario_actual['historial_partidas']:
        texto_vacio = fuente_grande.render("No hay partidas registradas", True, BLANCO)
        pantalla.blit(texto_vacio, (ANCHO // 2 - texto_vacio.get_width() // 2, 200))
    else:
        y = 100
        for i, partida in enumerate(usuario_actual['historial_partidas'][:10]):  # Mostrar solo las 10 más recientes
            texto_partida = fuente_pequena.render(
                f"{partida['fecha']} - Puntos: {partida['puntos']} - Nivel: {partida['nivel']} - "
                f"Objetivos: {partida['objetivos']} - Tiempo: {partida['tiempo']}s - Combo: x{partida['combo_maximo']}",
                True, BLANCO
            )
            pantalla.blit(texto_partida, (50, y))
            y += 30
            
            if y > ALTO - 100:
                break
    
    btn_volver = dibujar_boton("VOLVER", ANCHO // 2 - 100, ALTO - 80, 200, 50, (80, 0, 0), ROJO)
    return btn_volver

# ... (las funciones dibujar_tienda, dibujar_logros, dibujar_inventario, etc. se mantienen igual pero usando datos_usuarios)

def dibujar_tienda():
    usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
    fondo_actual = fondos_imagenes[usuario_actual['fondo_actual']]
    pantalla.blit(fondo_actual, (0, 0))
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 220), overlay.get_rect())
    pantalla.blit(overlay, (0, 0))
    titulo = fuente_titulo.render("TIENDA", True, DORADO)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))
    pantalla.blit(moneda_imagen, (ANCHO // 2 - 50, 100))
    texto_monedas = fuente_grande.render(str(usuario_actual['monedas']), True, DORADO)
    pantalla.blit(texto_monedas, (ANCHO // 2 - 20, 95))
    texto_naves = fuente_grande.render("NAVES", True, CYAN)
    pantalla.blit(texto_naves, (60, 155))
    botones_naves = []
    x_nave = 60
    for nave_id, nave_info in catalogo_naves.items():
        desbloqueada = nave_id in usuario_actual['naves_desbloqueadas']
        equipada = nave_id == usuario_actual['nave_actual']
        color_cuadro = VERDE if equipada else ((60, 60, 80) if desbloqueada else (40, 40, 60))
        pygame.draw.rect(pantalla, color_cuadro, (x_nave, 200, 150, 145), border_radius=10)
        pygame.draw.rect(pantalla, DORADO if equipada else BLANCO, (x_nave, 200, 150, 145), 3, border_radius=10)
        nave_img = naves_imagenes[nave_id]
        pantalla.blit(nave_img, (x_nave + 50, 220))
        texto_nombre = fuente_pequena.render(nave_info['nombre'], True, BLANCO)
        pantalla.blit(texto_nombre, (x_nave + 75 - texto_nombre.get_width() // 2, 275))
        if equipada:
            mouse_sobre = dibujar_boton("EQUIPADA", x_nave + 15, 300, 120, 35, VERDE, VERDE)
        elif desbloqueada:
            mouse_sobre = dibujar_boton("EQUIPAR", x_nave + 15, 300, 120, 35, AZUL, CYAN)
        else:
            btn_rect = pygame.Rect(x_nave + 15, 300, 120, 35)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_sobre = btn_rect.collidepoint(mouse_x, mouse_y)
            btn_color = AMARILLO if mouse_sobre else NARANJA
            pygame.draw.rect(pantalla, btn_color, btn_rect, border_radius=10)
            pygame.draw.rect(pantalla, BLANCO, btn_rect, 2, border_radius=10)
            mini_moneda = pygame.transform.scale(moneda_imagen, (22, 22))
            pantalla.blit(mini_moneda, (x_nave + 40, 305))
            texto_precio = fuente_grande.render(str(nave_info['precio']), True, BLANCO)
            pantalla.blit(texto_precio, (x_nave + 65, 302))
        botones_naves.append((nave_id, mouse_sobre, desbloqueada, equipada))
        x_nave += 170
    
    # Sección FONDOS
    texto_fondos = fuente_grande.render("FONDOS", True, CYAN)
    pantalla.blit(texto_fondos, (60, 375))
    botones_fondos = []
    x_fondo = 60
    for fondo_id, fondo_info in catalogo_fondos.items():
        desbloqueado = fondo_id in usuario_actual['fondos_desbloqueados']

        equipado = fondo_id == usuario_actual['fondo_actual']
        color_cuadro = VERDE if equipado else ((60, 60, 80) if desbloqueado else (40, 40, 60))

        pygame.draw.rect(pantalla, color_cuadro, (x_fondo, 420, 220, 125), border_radius=10)
        pygame.draw.rect(pantalla, DORADO if equipado else BLANCO, (x_fondo, 420, 220, 125), 3, border_radius=10)

        mini_fondo = pygame.transform.scale(fondos_imagenes[fondo_id], (200, 65))
        pantalla.blit(mini_fondo, (x_fondo + 10, 430))

        texto_nombre = fuente_pequena.render(fondo_info['nombre'], True, BLANCO)
        pantalla.blit(texto_nombre, (x_fondo + 110 - texto_nombre.get_width() // 2, 520))

        if equipado:
            mouse_sobre = dibujar_boton("EQUIPADO", x_fondo + 50, 540, 120, 35, VERDE, VERDE)
        elif desbloqueado:
            mouse_sobre = dibujar_boton("EQUIPAR", x_fondo + 50, 540, 120, 35, AZUL, CYAN)
        else:
            btn_rect = pygame.Rect(x_fondo + 60, 540, 120, 35)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_sobre = btn_rect.collidepoint(mouse_x, mouse_y)
            btn_color = AMARILLO if mouse_sobre else NARANJA

            pygame.draw.rect(pantalla, btn_color, btn_rect, border_radius=10)
            pygame.draw.rect(pantalla, BLANCO, btn_rect, 2, border_radius=10)

            mini_moneda = pygame.transform.scale(moneda_imagen, (20, 20))
            pantalla.blit(mini_moneda, (x_fondo + 65, 547))

            texto_precio = fuente.render(str(fondo_info['precio']), True, BLANCO)
            pantalla.blit(texto_precio, (x_fondo + 90, 545))

        botones_fondos.append((fondo_id, mouse_sobre, desbloqueado, equipado))
        x_fondo += 240

    btn_volver = dibujar_boton("VOLVER", ANCHO // 2 - 100, 580, 200, 50, (80, 0, 0), ROJO)
    return botones_naves, botones_fondos, btn_volver

def dibujar_logros():
    usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
    fondo_actual = fondos_imagenes[usuario_actual['fondo_actual']]
    pantalla.blit(fondo_actual, (0, 0))
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 220), overlay.get_rect())
    pantalla.blit(overlay, (0, 0))
    titulo = fuente_titulo.render("LOGROS", True, MORADO)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))
    stats_texto = [
        f"Objetivos completados: {usuario_actual['objetivos_totales']}",
        f"Mejor combo: x{usuario_actual['mejor_combo']}",
        f"Mejor puntuacion: {usuario_actual['mejor_puntuacion']}",
        f"Mejor nivel: {usuario_actual['mejor_nivel']}",
    ]
    y_stats = 140
    for stat in stats_texto:
        texto = fuente.render(stat, True, CYAN)
        pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, y_stats))
        y_stats += 35
    y_logro = 290
    logro_num = 1
    for logro_id, logro_data in logros_info.items():
        desbloqueado = usuario_actual['logros'][logro_id]
        color_cuadro = (0, 80, 0) if desbloqueado else (40, 40, 60)
        pygame.draw.rect(pantalla, color_cuadro, (100, y_logro, 600, 50), border_radius=10)
        pygame.draw.rect(pantalla, VERDE if desbloqueado else (100, 100, 100), (100, y_logro, 600, 50), 3, border_radius=10)
        texto_num = fuente_grande.render(f"{logro_num}.", True, BLANCO if desbloqueado else (120, 120, 120))
        pantalla.blit(texto_num, (120, y_logro + 10))
        texto_nombre = fuente.render(logro_data['nombre'], True, BLANCO if desbloqueado else (150, 150, 150))
        texto_desc = fuente_pequena.render(logro_data['desc'], True, BLANCO if desbloqueado else (120, 120, 120))
        pantalla.blit(texto_nombre, (180, y_logro + 5))
        pantalla.blit(texto_desc, (180, y_logro + 28))
        if desbloqueado:
            check_texto = fuente_grande.render("✓", True, VERDE)
            pantalla.blit(check_texto, (660, y_logro + 8))
        y_logro += 60
        logro_num += 1
    btn_volver = dibujar_boton("VOLVER", ANCHO // 2 - 100, 590, 200, 50, (80, 0, 0), ROJO)
    return btn_volver

def dibujar_inventario():
    panel_y = 80
    panel_alto = 75
    pygame.draw.rect(pantalla, (0, 0, 0, 200), (10, panel_y, ANCHO - 20, panel_alto), border_radius=10)
    tiene_objetivo = verificar_objetivo_en_inventario()
    color_borde = VERDE if tiene_objetivo else CYAN
    grosor_borde = 4 if tiene_objetivo else 3
    pygame.draw.rect(pantalla, color_borde, (10, panel_y, ANCHO - 20, panel_alto), grosor_borde, border_radius=10)
    texto_inv = fuente.render("INVENTARIO:", True, color_borde)
    pantalla.blit(texto_inv, (20, panel_y + 5))
    if tiene_objetivo:
        texto_listo = fuente_pequena.render("¡ESPACIO!", True, VERDE)
        pantalla.blit(texto_listo, (20, panel_y + 45))
    else:
        texto_suma = fuente_pequena.render("Click para", True, BLANCO)
        texto_suma2 = fuente_pequena.render("SUMAR", True, AMARILLO)
        pantalla.blit(texto_suma, (20, panel_y + 38))
        pantalla.blit(texto_suma2, (20, panel_y + 55))
    for i, num in enumerate(inventario):
        rect = get_rect_inventario(i)
        es_objetivo = (num == objetivo_actual)
        es_seleccionado = (i == numero_seleccionado_1)
        if es_objetivo:
            color_cuadro = (0, 100, 0)
            color_borde_num = VERDE
            grosor = 4
        elif es_seleccionado:
            color_cuadro = (80, 80, 0)
            color_borde_num = AMARILLO
            grosor = 4
        else:
            color_cuadro = (40, 40, 70)
            color_borde_num = NARANJA
            grosor = 2
        pygame.draw.rect(pantalla, color_cuadro, rect, border_radius=8)
        pygame.draw.rect(pantalla, color_borde_num, rect, grosor, border_radius=8)
        texto_num = fuente_grande.render(str(num), True, BLANCO)
        rect_num = texto_num.get_rect(center=rect.center)
        pantalla.blit(texto_num, rect_num)
        if es_objetivo:
            pygame.draw.circle(pantalla, AMARILLO, (rect.right - 8, rect.top + 8), 8)
            texto_star = fuente_pequena.render("★", True, NEGRO)
            pantalla.blit(texto_star, (rect.right - 12, rect.top + 2))
    if numero_seleccionado_1 is not None:
        rect_basurero = get_rect_basurero()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_sobre_basurero = rect_basurero.collidepoint(mouse_x, mouse_y)
        color_basurero = (120, 0, 0) if mouse_sobre_basurero else (80, 0, 0)
        pygame.draw.rect(pantalla, color_basurero, rect_basurero, border_radius=8)
        pygame.draw.rect(pantalla, ROJO if mouse_sobre_basurero else (150, 150, 150), rect_basurero, 3, border_radius=8)
        pantalla.blit(basurero_imagen, (rect_basurero.x + 5, rect_basurero.y + 5))
        texto_basurero = fuente_pequena.render("Eliminar", True, BLANCO)
        pantalla.blit(texto_basurero, (rect_basurero.x + 25 - texto_basurero.get_width() // 2, rect_basurero.bottom + 3))
    color_capacidad = ROJO if len(inventario) >= max_inventario else BLANCO
    texto_cap = fuente_pequena.render(f"{len(inventario)}/{max_inventario}", True, color_capacidad)
    pantalla.blit(texto_cap, (ANCHO - 80, panel_y + 30))

def dibujar_notificacion_logro():
    if tiempo_logro > 0 and logro_desbloqueado:
        alpha = min(255, tiempo_logro * 2)
        panel_y = 200
        panel_ancho = 400
        panel_alto = 100
        panel_x = ANCHO // 2 - panel_ancho // 2
        s = pygame.Surface((panel_ancho, panel_alto), pygame.SRCALPHA)
        pygame.draw.rect(s, (50, 0, 100, min(230, alpha)), (0, 0, panel_ancho, panel_alto), border_radius=15)
        pygame.draw.rect(s, (200, 150, 255, alpha), (0, 0, panel_ancho, panel_alto), 4, border_radius=15)
        pantalla.blit(s, (panel_x, panel_y))
        texto_titulo = fuente_grande.render("¡LOGRO DESBLOQUEADO!", True, AMARILLO)
        pantalla.blit(texto_titulo, (panel_x + panel_ancho // 2 - texto_titulo.get_width() // 2, panel_y + 15))
        logro_info = logros_info[logro_desbloqueado]
        texto_nombre = fuente.render(logro_info['nombre'], True, BLANCO)
        texto_desc = fuente_pequena.render(logro_info['desc'], True, CYAN)
        pantalla.blit(texto_nombre, (panel_x + panel_ancho // 2 - texto_nombre.get_width() // 2, panel_y + 55))
        pantalla.blit(texto_desc, (panel_x + panel_ancho // 2 - texto_desc.get_width() // 2, panel_y + 80))

def dibujar_popup_instrucciones():
    # Fondo semitransparente
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
    pantalla.blit(overlay, (0, 0))
    
    # Panel del popup - Hazlo más alto para que quepa todo
    panel_ancho = 700
    panel_alto = 550
    panel_x = ANCHO // 2 - panel_ancho // 2
    panel_y = ALTO // 2 - panel_alto // 2
    
    pygame.draw.rect(pantalla, (20, 20, 50), (panel_x, panel_y, panel_ancho, panel_alto), border_radius=15)
    pygame.draw.rect(pantalla, CYAN, (panel_x, panel_y, panel_ancho, panel_alto), 4, border_radius=15)
    
    # Título
    titulo = fuente_titulo.render("INSTRUCCIONES", True, AMARILLO)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, panel_y + 20))
    
    # Instrucciones con scroll
    instrucciones = [
        "CONTROLES PRINCIPALES:",
        "• Teclas A/D o Flechas: Mover nave izquierda/derecha",
        "• Click en números: Seleccionar para sumar", 
        "• Tecla ESPACIO: Entregar objetivo si está en inventario",
        "• Tecla ESC: Pausar el juego",
        "• Tecla R: Reiniciar partida",
        "• Tecla M: Volver al menú principal",
        "",
        "OBJETIVO DEL JUEGO:",
        "• Atrapar meteoritos con números",
        "• Combinar números haciendo clic en ellos",
        "• Alcanzar el número objetivo para ganar puntos",
        "• Completar objetivos para subir de nivel",
        "• Los objetivos están ubicados en la parte superior izquierda"
        ""
    ]
    
    area_texto_y = panel_y + 70
    area_texto_alto = 400 
    area_texto_x = panel_x + 20
    area_texto_ancho = panel_ancho - 40
    
    # Dibujar área de texto
    pygame.draw.rect(pantalla, (10, 15, 30), (area_texto_x, area_texto_y, area_texto_ancho, area_texto_alto), border_radius=10)
    
    # Dibujar instrucciones
    y = area_texto_y + 20
    for linea in instrucciones:
        if ":" in linea and not linea.startswith(" "):
            texto = fuente.render(linea, True, CYAN)
            pantalla.blit(texto, (area_texto_x + 40, y))
            y += 35
        elif linea == "":
            y += 15
        else:
            texto = fuente_pequena.render(linea, True, BLANCO)
            pantalla.blit(texto, (area_texto_x + 50, y))
            y += 25
            
            # Si el texto se sale de la pantalla, detén el dibujo
            if y > area_texto_y + area_texto_alto - 30:
                break  # Esto evitará que se dibuje fuera del área
    
    # Botón de cerrar
    btn_cerrar = dibujar_boton("ENTENDIDO", ANCHO // 2 - 100, panel_y + panel_alto - 60, 200, 50, VERDE_OSCURO, VERDE)
    return btn_cerrar

def dibujar_como_jugar():
    usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
    fondo_actual = fondos_imagenes[usuario_actual['fondo_actual']]
    pantalla.blit(fondo_actual, (0, 0))
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (10, 15, 40, 220), overlay.get_rect())
    pantalla.blit(overlay, (0, 0))
    
    # Solo mostrar un mensaje simple y el botón
    texto_titulo = fuente_titulo.render("¿CÓMO JUGAR?", True, AMARILLO)
    pantalla.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, 150))
    
    # Cambiar el estado directamente al hacer clic en el área del título o un botón pequeño
    mouse_x, mouse_y = pygame.mouse.get_pos()
    rect_titulo = texto_titulo.get_rect(center=(ANCHO // 2, 150))
    
    # Dibuja un botón más pequeño y claro
    btn_ver = dibujar_boton("VER INSTRUCCIONES", ANCHO // 2 - 120, 250, 240, 50, AZUL, CYAN)
    
    # Opcional: También puedes hacer que al hacer clic en cualquier parte del panel se abran las instrucciones
    # Pero por simplicidad, usaremos el botón.
    
    btn_volver = dibujar_boton("VOLVER", ANCHO // 2 - 100, 350, 200, 50, (80, 0, 0), ROJO)
    
    return btn_ver, btn_volver

# Variables de ejecución
ejecutando = True
contador_meteoritos = 0
creando_usuario = False
nombre_nuevo_usuario = ""

# Iniciar objetivo inicial
objetivo_actual = generar_objetivo(nivel)

# Bucle principal
while ejecutando:
    dt = reloj.tick(60) / 1000.0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        elif evento.type == pygame.KEYDOWN:
            if creando_usuario:
                if evento.key == pygame.K_RETURN and nombre_nuevo_usuario.strip():
                    # Crear nuevo usuario
                    if nombre_nuevo_usuario not in datos_usuarios["usuarios"]:
                        datos_usuarios["usuarios"][nombre_nuevo_usuario] = crear_usuario(nombre_nuevo_usuario)
                        datos_usuarios["usuario_actual"] = nombre_nuevo_usuario
                        guardar_usuarios(datos_usuarios)
                        creando_usuario = False
                        nombre_nuevo_usuario = ""
                        estado_juego = MENU
                elif evento.key == pygame.K_BACKSPACE:
                    nombre_nuevo_usuario = nombre_nuevo_usuario[:-1]
                elif evento.key == pygame.K_ESCAPE:
                    creando_usuario = False
                    nombre_nuevo_usuario = ""
                else:
                    # Solo permitir caracteres alfanuméricos y espacios
                    if evento.unicode.isalnum() or evento.unicode == ' ':
                        if len(nombre_nuevo_usuario) < 15:
                            nombre_nuevo_usuario += evento.unicode
            
            elif estado_juego == JUGANDO:
                if evento.key == pygame.K_ESCAPE:
                    estado_juego = PAUSADO
                elif evento.key == pygame.K_r:
                    reiniciar_juego()
                elif evento.key == pygame.K_SPACE:
                    # Entregar objetivo si lo tienes
                    if verificar_objetivo_en_inventario():
                        try:
                            inventario.remove(objetivo_actual)
                        except Exception:
                            pass
                        usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
                        monedas_ganadas = 5
                        if combo >= 2:
                            monedas_ganadas += 2
                        if combo >= 3:
                            monedas_ganadas += 4
                        if combo >= 5:
                            monedas_ganadas += 10
                        usuario_actual['monedas'] += monedas_ganadas
                        puntos_ganados = 100 + (combo * 50) + (nivel * 20)
                        puntos += puntos_ganados
                        combo += 1
                        if combo > combo_maximo:
                            combo_maximo = combo
                        objetivos_completados += 1
                        usuario_actual['objetivos_totales'] += 1
                        if combo > usuario_actual['mejor_combo']:
                            usuario_actual['mejor_combo'] = combo
                        if puntos > usuario_actual['mejor_puntuacion']:
                            usuario_actual['mejor_puntuacion'] = puntos
                        if nivel > usuario_actual['mejor_nivel']:
                            usuario_actual['mejor_nivel'] = nivel
                        if usuario_actual['objetivos_totales'] >= 1:
                            verificar_logro('primer_objetivo')
                        if usuario_actual['objetivos_totales'] >= 10:
                            verificar_logro('objetivos_10')
                        if combo >= 5:
                            verificar_logro('combo_x5')
                        if nivel >= 5:
                            verificar_logro('nivel_5')
                        if nivel >= 10:
                            verificar_logro('nivel_10')
                        guardar_usuarios(datos_usuarios)
                        if vidas < vidas_maximas:
                            vidas += 1
                            mostrar_mensaje(f"¡OBJETIVO ENTREGADO! +{puntos_ganados} pts | +{monedas_ganadas} +1 VIDA", VERDE, 120)
                        else:
                            mostrar_mensaje(f"¡OBJETIVO ENTREGADO! +{puntos_ganados} pts | +{monedas_ganadas} ", VERDE, 120)
                        crear_explosion(jugador_x + 25, jugador_y - 30, VERDE, 50)
                        crear_explosion(ANCHO // 2, 50, AMARILLO, 30)
                        objetivo_actual = generar_objetivo(nivel)
                    else:
                        mostrar_mensaje("¡No tienes el objetivo!", ROJO, 90)
            
            elif estado_juego == PAUSADO:
                if evento.key == pygame.K_ESCAPE:
                    estado_juego = JUGANDO
                elif evento.key == pygame.K_r:
                    reiniciar_juego()
                elif evento.key == pygame.K_m:
                    meteoritos.clear()
                    particulas.clear()
                    inventario.clear()
                    numero_seleccionado_1 = None
                    numero_seleccionado_2 = None
                    estado_juego = MENU
            
            elif estado_juego == GAME_OVER:
                if evento.key == pygame.K_r:
                    reiniciar_juego()
                elif evento.key == pygame.K_ESCAPE:
                    try:
                        pygame.mixer.music.load(RUTA_MUSICA_MENU)
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0.4)
                    except Exception:
                        pass
                    estado_juego = MENU
        
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = evento.pos

            if estado_juego == SELECCION_USUARIO:
                if creando_usuario:
                    btn_crear, btn_volver = dibujar_crear_usuario()
                    if btn_crear and nombre_nuevo_usuario.strip():
                        if nombre_nuevo_usuario not in datos_usuarios["usuarios"]:
                            datos_usuarios["usuarios"][nombre_nuevo_usuario] = crear_usuario(nombre_nuevo_usuario)
                            datos_usuarios["usuario_actual"] = nombre_nuevo_usuario
                            guardar_usuarios(datos_usuarios)
                            creando_usuario = False
                            nombre_nuevo_usuario = ""
                            estado_juego = MENU
                    elif btn_volver:
                        creando_usuario = False
                        nombre_nuevo_usuario = ""
                else:
                    botones_usuarios, botones_eliminar, btn_nuevo = dibujar_seleccion_usuario()
                    for nombre_usuario, btn_seleccionar in botones_usuarios:
                        if btn_seleccionar:
                            datos_usuarios["usuario_actual"] = nombre_usuario
                            guardar_usuarios(datos_usuarios)
                            estado_juego = MENU
                            break
                    # Manejar eliminación de usuario
                    for nombre_usuario, btn_eliminar in botones_eliminar:
                        if btn_eliminar:
                            if len(datos_usuarios["usuarios"]) > 1:  # No eliminar si es el único usuario
                                del datos_usuarios["usuarios"][nombre_usuario]
                                if datos_usuarios["usuario_actual"] == nombre_usuario:
                                    # Si eliminamos el usuario actual, seleccionar otro
                                    otros_usuarios = list(datos_usuarios["usuarios"].keys())
                                    datos_usuarios["usuario_actual"] = otros_usuarios[0] if otros_usuarios else None
                                guardar_usuarios(datos_usuarios)
                                mostrar_mensaje(f"Usuario {nombre_usuario} eliminado", NARANJA, 90)
                            else:
                                mostrar_mensaje("No puedes eliminar el único usuario", ROJO, 90)
                            break

                    if btn_nuevo:
                        creando_usuario = True
            
            elif estado_juego == MENU:
                btn_jugar, btn_tienda, btn_logros, btn_estadisticas, btn_como_jugar, btn_usuarios = dibujar_menu()
                if btn_jugar:
                    try:
                        pygame.mixer.music.load(RUTA_MUSICA_JUEGO)
                        pygame.mixer.music.play(-1) 
                        pygame.mixer.music.set_volume(0.4)
                    except Exception:
                        pass
                    reiniciar_juego()
                elif btn_tienda:
                    estado_juego = TIENDA
                elif btn_logros:
                    estado_juego = LOGROS
                elif btn_estadisticas:
                    estado_juego = ESTADISTICAS
                elif btn_como_jugar:
                    estado_juego = COMO_JUGAR
                elif btn_usuarios: 
                    estado_juego = SELECCION_USUARIO
            
            elif estado_juego == ESTADISTICAS:
                btn_historial, btn_volver = dibujar_estadisticas()
                if btn_historial:
                    estado_juego = HISTORIAL
                elif btn_volver:
                    estado_juego = MENU
            
            elif estado_juego == HISTORIAL:
                btn_volver = dibujar_historial()
                if btn_volver:
                    estado_juego = ESTADISTICAS
            
            elif estado_juego == TIENDA:
                botones_naves, botones_fondos, btn_volver = dibujar_tienda()
                usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
                for nave_id, mouse_sobre, desbloqueada, equipada in botones_naves:
                    if mouse_sobre:
                        if equipada:
                            pass
                        elif desbloqueada:
                            usuario_actual['nave_actual'] = nave_id
                            guardar_usuarios(datos_usuarios)
                        else:
                            precio = catalogo_naves[nave_id]['precio']
                            if usuario_actual['monedas'] >= precio:
                                usuario_actual['monedas'] -= precio
                                usuario_actual['naves_desbloqueadas'].append(nave_id)
                                usuario_actual['nave_actual'] = nave_id
                                guardar_usuarios(datos_usuarios)
                                crear_explosion(ANCHO // 2, ALTO // 2, DORADO, 50)
                                try:
                                    if sonido_compra:
                                        sonido_compra.play()
                                except Exception:
                                    pass
                for fondo_id, mouse_sobre, desbloqueado, equipado in botones_fondos:
                    if mouse_sobre:
                        if equipado:
                            pass
                        elif desbloqueado:
                            usuario_actual['fondo_actual'] = fondo_id
                            guardar_usuarios(datos_usuarios)
                        else:
                            precio = catalogo_fondos[fondo_id]['precio']
                            if usuario_actual['monedas'] >= precio:
                                usuario_actual['monedas'] -= precio
                                usuario_actual['fondos_desbloqueados'].append(fondo_id)
                                usuario_actual['fondo_actual'] = fondo_id
                                guardar_usuarios(datos_usuarios)
                                crear_explosion(ANCHO // 2, ALTO // 2, DORADO, 50)
                                try:
                                    if sonido_compra:
                                        sonido_compra.play()
                                except Exception:
                                    pass
                if btn_volver:
                    estado_juego = MENU
            
            elif estado_juego == LOGROS:
                btn_volver = dibujar_logros()
                if btn_volver:
                    estado_juego = MENU
            
            elif estado_juego == COMO_JUGAR:
                btn_ver, btn_volver = dibujar_como_jugar()
                if btn_ver:  # Al hacer clic en "VER INSTRUCCIONES"
                    estado_juego = INSTRUCCIONES_POPUP  # Cambia directamente al popup
                elif btn_volver:
                    estado_juego = MENU
            elif estado_juego == INSTRUCCIONES_POPUP:
                btn_cerrar = dibujar_popup_instrucciones()
                if btn_cerrar:
                    estado_juego = COMO_JUGAR

            elif estado_juego == GAME_OVER:
                if ANCHO // 2 - 100 < mouse_x < ANCHO // 2 + 100 and 450 < mouse_y < 500:
                    reiniciar_juego()
                elif ANCHO // 2 - 100 < mouse_x < ANCHO // 2 + 100 and 520 < mouse_y < 570:
                    try:
                        pygame.mixer.music.load(RUTA_MUSICA_MENU)
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0.4)
                    except Exception:
                        pass
                    estado_juego = MENU
            
            elif estado_juego == JUGANDO:
                # Manejo de inventario con clicks
                if numero_seleccionado_1 is not None:
                    rect_basurero = get_rect_basurero()
                    if rect_basurero.collidepoint(mouse_x, mouse_y):
                        try:
                            inventario.pop(numero_seleccionado_1)
                        except Exception:
                            pass
                        numero_seleccionado_1 = None
                        mostrar_mensaje("¡Número eliminado!", NARANJA, 60)
                        crear_explosion(rect_basurero.centerx, rect_basurero.centery, ROJO, 15)
                        continue
                for i in range(len(inventario)):
                    rect = get_rect_inventario(i)
                    if rect.collidepoint(mouse_x, mouse_y):
                        if numero_seleccionado_1 is None:
                            numero_seleccionado_1 = i
                        elif numero_seleccionado_1 == i:
                            numero_seleccionado_1 = None
                        elif numero_seleccionado_2 is None:
                            numero_seleccionado_2 = i
                            usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
                            num1 = inventario[numero_seleccionado_1]
                            num2 = inventario[numero_seleccionado_2]
                            resultado = num1 + num2
                            indices = sorted([numero_seleccionado_1, numero_seleccionado_2], reverse=True)
                            for idx in indices:
                                inventario.pop(idx)
                            inventario.append(resultado)
                            crear_explosion(ANCHO // 2, 120, VERDE, 25)
                            if resultado == objetivo_actual:
                                crear_explosion(ANCHO // 2, ALTO // 2, AMARILLO, 50)
                                crear_explosion(jugador_x + 25, jugador_y - 30, VERDE, 40)
                                monedas_ganadas = 5
                                if combo >= 2:
                                    monedas_ganadas += 2
                                if combo >= 3:
                                    monedas_ganadas += 4
                                if combo >= 5:
                                    monedas_ganadas += 10
                                usuario_actual['monedas'] += monedas_ganadas
                                puntos_ganados = 100 + (combo * 50) + (nivel * 20)
                                puntos += puntos_ganados
                                combo += 1
                                if combo > combo_maximo:
                                    combo_maximo = combo
                                objetivos_completados += 1
                                usuario_actual['objetivos_totales'] += 1
                                if combo > usuario_actual['mejor_combo']:
                                    usuario_actual['mejor_combo'] = combo
                                if puntos > usuario_actual['mejor_puntuacion']:
                                    usuario_actual['mejor_puntuacion'] = puntos
                                if nivel > usuario_actual['mejor_nivel']:
                                    usuario_actual['mejor_nivel'] = nivel
                                if usuario_actual['objetivos_totales'] >= 1:
                                    verificar_logro('primer_objetivo')
                                if usuario_actual['objetivos_totales'] >= 10:
                                    verificar_logro('objetivos_10')
                                if combo >= 5:
                                    verificar_logro('combo_x5')
                                if nivel >= 5:
                                    verificar_logro('nivel_5')
                                if nivel >= 10:
                                    verificar_logro('nivel_10')
                                guardar_usuarios(datos_usuarios)
                                if vidas < vidas_maximas:
                                    vidas += 1
                                    mostrar_mensaje(f"¡{num1} + {num2} = {resultado}! ¡OBJETIVO! +{puntos_ganados} pts | +{monedas_ganadas} +1 VIDA", VERDE, 150)
                                else:
                                    mostrar_mensaje(f"¡{num1} + {num2} = {resultado}! ¡OBJETIVO! +{puntos_ganados} pts | +{monedas_ganadas} ", VERDE, 150)
                                objetivo_actual = generar_objetivo(nivel)
                            else:
                                mostrar_mensaje(f"¡{num1} + {num2} = {resultado}!", VERDE, 90)
                            numero_seleccionado_1 = None
                            numero_seleccionado_2 = None
                        break

    # Lógica del juego cuando está en JUGANDO
    if estado_juego == JUGANDO:
        # Actualizar tiempo de partida
        tiempo_partida = (pygame.time.get_ticks() - tiempo_inicio_partida) // 1000
        
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            jugador_x = max(0, jugador_x - velocidad_jugador)
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            jugador_x = min(ANCHO - 50, jugador_x + velocidad_jugador)
        
        contador_meteoritos += 1
        frecuencia = max(45, 85 - (nivel * 4))
        if contador_meteoritos > frecuencia:
            meteoritos.append(Meteorito())
            contador_meteoritos = 0
        
        for meteorito in meteoritos[:]:
            meteorito.mover()
            if verificar_colision_jugador(meteorito):
                if len(inventario) < max_inventario:
                    inventario.append(meteorito.numero)
                    crear_explosion(meteorito.x + 25, meteorito.y + 25, NARANJA, 15)
                else:
                    mostrar_mensaje("¡Inventario lleno! Combina números", AMARILLO, 70)
                meteoritos.remove(meteorito)
            elif meteorito.y > ALTO:
                meteoritos.remove(meteorito)
                vidas -= 1
                combo = 0
                crear_explosion(meteorito.x + 25, ALTO - 20, ROJO, 20)
                mostrar_mensaje("¡Meteorito perdido! -1 VIDA", ROJO)
        
        nivel = min(10, (objetivos_completados // 3) + 1)
        
        if tiempo_mensaje > 0:
            tiempo_mensaje -= 1
        
        if tiempo_logro > 0:
            tiempo_logro -= 1
        
        if vidas <= 0:
            # Guardar estadísticas de la partida
            usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
            usuario_actual['partidas_jugadas'] += 1
            usuario_actual['tiempo_total_jugado'] += tiempo_partida
            agregar_al_historial(usuario_actual, puntos, nivel, objetivos_completados, tiempo_partida, combo_maximo)
            guardar_usuarios(datos_usuarios)
            estado_juego = GAME_OVER

    # Actualizar partículas
    for particula in particulas[:]:
        particula.actualizar()
        if particula.vida <= 0:
            particulas.remove(particula)

    # DIBUJADO GLOBAL
    if datos_usuarios["usuario_actual"]:
        usuario_actual = datos_usuarios["usuarios"][datos_usuarios["usuario_actual"]]
        fondo_actual = fondos_imagenes[usuario_actual['fondo_actual']]
    else:
        fondo_actual = fondos_imagenes['espacio']
    
    pantalla.blit(fondo_actual, (0, 0))

    if estado_juego == SELECCION_USUARIO:
        if creando_usuario:
            dibujar_crear_usuario()
            # Dibujar nombre de usuario actual
            texto_nombre = fuente.render(nombre_nuevo_usuario, True, BLANCO)
            pantalla.blit(texto_nombre, (ANCHO // 2 - texto_nombre.get_width() // 2, 265))
        else:
            dibujar_seleccion_usuario()
    
    elif estado_juego == MENU:
        dibujar_menu()
    
    elif estado_juego == ESTADISTICAS:
        dibujar_estadisticas()
    
    elif estado_juego == HISTORIAL:
        dibujar_historial()
    
    elif estado_juego == TIENDA:
        dibujar_tienda()
    
    elif estado_juego == LOGROS:
        dibujar_logros()
    
    elif estado_juego == COMO_JUGAR:
        dibujar_como_jugar()

    elif estado_juego == INSTRUCCIONES_POPUP:
        # Dibujar la pantalla de "Cómo jugar" de fondo
        dibujar_como_jugar()
        # Dibujar el popup encima
        dibujar_popup_instrucciones()
    
    elif estado_juego in [JUGANDO, PAUSADO]:
        for particula in particulas:
            particula.dibujar()
        
        if datos_usuarios["usuario_actual"]:
            nave_actual = naves_imagenes[usuario_actual['nave_actual']]
            pantalla.blit(nave_actual, (jugador_x, jugador_y))
        
        for meteorito in meteoritos:
            meteorito.dibujar()
        
        # Panel de objetivo
        pygame.draw.rect(pantalla, (0, 0, 0, 200), (10, 10, 160, 60), border_radius=10)
        pygame.draw.rect(pantalla, AMARILLO, (10, 10, 160, 60), 3, border_radius=10)
        texto_obj = fuente_pequena.render("OBJETIVO:", True, AMARILLO)
        texto_num = fuente_grande.render(str(objetivo_actual), True, BLANCO)
        pantalla.blit(texto_obj, (20, 15))
        pantalla.blit(texto_num, (85 - texto_num.get_width() // 2, 35))
        
        # Panel de estadísticas
        stats_x = ANCHO - 170
        pygame.draw.rect(pantalla, (0, 0, 0, 200), (stats_x, 10, 160, 140), border_radius=10)
        pygame.draw.rect(pantalla, CYAN, (stats_x, 10, 160, 140), 3, border_radius=10)
        
        texto_puntos = fuente_pequena.render(f"Puntos: {puntos}", True, BLANCO)
        texto_vidas_label = fuente_pequena.render("Vidas:", True, BLANCO)
        texto_nivel = fuente_pequena.render(f"Nivel: {nivel}", True, CYAN)
        texto_tiempo = fuente_pequena.render(f"Tiempo: {tiempo_partida}s", True, BLANCO)
        
        pantalla.blit(texto_puntos, (stats_x + 10, 20))
        pantalla.blit(texto_vidas_label, (stats_x + 10, 45))
        pantalla.blit(texto_nivel, (stats_x + 10, 70))
        pantalla.blit(texto_tiempo, (stats_x + 10, 95))
        
        for i in range(vidas):
            corazon_x = stats_x + 65 + (i * 25)
            corazon_y = 45
            pantalla.blit(corazon_imagen, (corazon_x, corazon_y))
        
        pantalla.blit(moneda_imagen, (stats_x + 10, 120))
        if datos_usuarios["usuario_actual"]:
            texto_monedas = fuente_pequena.render(str(usuario_actual['monedas']), True, DORADO)
            pantalla.blit(texto_monedas, (stats_x + 35, 123))
        
        if combo > 0:
            texto_combo = fuente_grande.render(f"COMBO x{combo}!", True, MORADO)
            rect_combo = texto_combo.get_rect(center=(ANCHO // 2, 30))
            pantalla.blit(texto_combo, rect_combo)
        
        if tiempo_mensaje > 0:
            alpha = min(255, tiempo_mensaje * 3)

            s_mensaje = pygame.Surface((ANCHO, 50), pygame.SRCALPHA)
            pygame.draw.rect(s_mensaje, (0, 0, 0, min(200, alpha)), (0, 0, ANCHO, 50), border_radius=10)

            texto_msg = fuente.render(mensaje_actual, True, color_mensaje)
            rect_msg = texto_msg.get_rect(center=(ANCHO // 2, 25))
            pantalla.blit(s_mensaje, (0, 175))
            pantalla.blit(texto_msg, (rect_msg.x, 185))
        
        dibujar_inventario()
        dibujar_notificacion_logro()
        
        if estado_juego == PAUSADO:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
            pantalla.blit(overlay, (0, 0))
            
            texto_pausa = fuente_titulo.render("PAUSA", True, CYAN)
            pantalla.blit(texto_pausa, (ANCHO // 2 - texto_pausa.get_width() // 2, 180))
            
            texto_continuar = fuente.render("ESC - Continuar", True, BLANCO)
            texto_reiniciar = fuente.render("R - Reiniciar", True, BLANCO)
            texto_menu = fuente.render("M - Volver al Menu", True, AMARILLO)
            
            pantalla.blit(texto_continuar, (ANCHO // 2 - texto_continuar.get_width() // 2, 280))
            pantalla.blit(texto_reiniciar, (ANCHO // 2 - texto_reiniciar.get_width() // 2, 320))
            pantalla.blit(texto_menu, (ANCHO // 2 - texto_menu.get_width() // 2, 360))
    
    elif estado_juego == GAME_OVER:
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect())
        pantalla.blit(overlay, (0, 0))
        
        texto_game_over = fuente_titulo.render("GAME OVER", True, ROJO)
        texto_puntos_final = fuente_grande.render(f"Puntuación: {puntos}", True, BLANCO)
        texto_nivel_final = fuente.render(f"Nivel alcanzado: {nivel}", True, CYAN)
        texto_objetivos = fuente.render(f"Objetivos: {objetivos_completados}", True, VERDE)
        texto_tiempo_final = fuente.render(f"Tiempo: {tiempo_partida} segundos", True, AMARILLO)
        texto_combo_final = fuente.render(f"Combo máximo: x{combo_maximo}", True, MORADO)
        
        if datos_usuarios["usuario_actual"]:
            texto_monedas_ganadas = fuente_grande.render(f"Monedas totales: {usuario_actual['monedas']}", True, DORADO)
        else:
            texto_monedas_ganadas = fuente_grande.render("Monedas totales: 0", True, DORADO)
        
        pantalla.blit(texto_game_over, (ANCHO // 2 - texto_game_over.get_width() // 2, 120))
        pantalla.blit(texto_puntos_final, (ANCHO // 2 - texto_puntos_final.get_width() // 2, 200))
        pantalla.blit(texto_objetivos, (ANCHO // 2 - texto_objetivos.get_width() // 2, 240))
        pantalla.blit(texto_nivel_final, (ANCHO // 2 - texto_nivel_final.get_width() // 2, 280))
        pantalla.blit(texto_tiempo_final, (ANCHO // 2 - texto_tiempo_final.get_width() // 2, 320))
        pantalla.blit(texto_combo_final, (ANCHO // 2 - texto_combo_final.get_width() // 2, 360))
        pantalla.blit(texto_monedas_ganadas, (ANCHO // 2 - texto_monedas_ganadas.get_width() // 2, 400))
        
        if dibujar_boton("REINICIAR", ANCHO // 2 - 100, 450, 200, 50, VERDE_OSCURO, VERDE):
            pass
        if dibujar_boton("MENÚ", ANCHO // 2 - 100, 520, 200, 50, AZUL, CYAN):
            pass

    pygame.display.flip()

# Al salir
try:
    pygame.mixer.music.stop()
except Exception:
    pass
pygame.quit()
sys.exit()