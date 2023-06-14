
######################Importar librerias#######################

 # Biblioteca para generar números aleatorios
import random as rd 

# Biblioteca para trabajar con el tiempo
import time  

# Biblioteca para trabajar con rutas de archivos y directorios
from pathlib import Path  

# Biblioteca para operaciones en paralelo o en segundo plano
import concurrent.futures  

# Biblioteca para crear videojuegos y aplicaciones multimedia
import pygame  

# Biblioteca para procesamiento de imágenes y visión por computadora
import cv2  

# Biblioteca para detección y seguimiento de manos, rostros, etc.
import mediapipe as mp  

 # Biblioteca para manipular archivos de audio
from pydub import AudioSegment 

 # Biblioteca para reproducir archivos de audio
from pydub.playback import play 

###############################################################

#############Definicion de variables globales##################

# Ejecutor asincronico
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

# Landmarks de mediapipe
mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()
# Definicion de la camara
camera = 1  # Dependiendo de la camara a utilizar el valor varia (0, 1, 2, 3)

cap = cv2.VideoCapture(camera)
success, img = cap.read()
height, width, _ = img.shape

# Definicion de color Inical RGB
r = 114
g = 133
b = 242


# Landmarks de Mediapipe para las exptemidades
manoIzq = 20  # Mano izquierda
manoDer = 19  # Mano derecha
pierIzq = 28  # Pierna izquierda
pierDer = 27  # Pierna derecha

# Colores Twister circulos y extremidades
amarillo = (0, 255, 255)
azul = (255, 0, 0)
rojo = (0, 0, 255)
verde = (0, 255, 0)
color_textos = (242, 133, 114)
color_textos2 = (114, 68, 242)
color_textos3 = (245, 180, 127)

# Ancho y alto para definir rangos de aparicion de los circulos
ancho = range(50, width-50)  # Rango válido para la coordenada x
alto = range(50, height-50)  # Rango válido para la coordenada y
alto_pies = range(height//2, height-50)  # Rango válido para la coordenada y de los pies

posicion_amarillo = (rd.choice(ancho), rd.choice(alto))
posicion_azul = (rd.choice(ancho), rd.choice(alto))
posicion_rojo = (rd.choice(ancho), rd.choice(alto_pies))


# Estados del juego
estado_modo = 0  # 0=Menu / 1=SoloManos / 2=PiesManosRandom / 3=Evolutivo
estado_juego = True  # Estado para Jugar o Perder
estado_interno = True  # Estado para reproducir solo una vez el sonido de perdida

# Tiempo del juego
TIEMPO = 10  # Tiempo contador constante
inicio = time.time()
t_anterior = 0
cuenta_atras = TIEMPO
contador_objetivo = 10  # NUmero al que la sudicultad sube

# Contadores
contador = 0  # Contador de puntaje

# Asignaciones
radio_circulo = 50  # Radio de circulos que aparecen en pantalla
x_centro = width//2
y_centro = height//2
alto_rectangulo = 50
ancho_rectangulo = width//2

texto0 = "Selecciona el modo de juego"
texto1 = "Solo manos"
texto2 = "Pies y manos"
texto3 = "Evolutivo"

rectangulo0 = ((x_centro - ancho_rectangulo // 2, y_centro - 3*alto_rectangulo // 2 - alto_rectangulo*3),
               (x_centro + ancho_rectangulo // 2, y_centro - alto_rectangulo // 2 - alto_rectangulo*3))

rectangulo1 = ((x_centro - ancho_rectangulo // 2, y_centro - 3*alto_rectangulo // 2 - alto_rectangulo),
               (x_centro + ancho_rectangulo // 2, y_centro - alto_rectangulo // 2 - alto_rectangulo))

rectangulo2 = ((x_centro - ancho_rectangulo // 2, y_centro - alto_rectangulo // 2),
               (x_centro + ancho_rectangulo // 2, y_centro + alto_rectangulo // 2))

rectangulo3 = ((x_centro - ancho_rectangulo // 2, y_centro + alto_rectangulo // 2 + alto_rectangulo),
               (x_centro + ancho_rectangulo // 2, y_centro + 3*alto_rectangulo // 2 + alto_rectangulo))

# Calcular el tamaño del texto
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1

tamaño_texto0 = cv2.getTextSize(texto0, font, font_scale, 2)[0]
tamaño_texto1 = cv2.getTextSize(texto1, font, font_scale, 2)[0]
tamaño_texto2 = cv2.getTextSize(texto2, font, font_scale, 2)[0]
tamaño_texto3 = cv2.getTextSize(texto3, font, font_scale, 2)[0]

# Calcular la posición del texto como el centro de cada rectangulo ajustado por el tamaño del texto
pos_texto0 = (rectangulo0[0][0] + (ancho_rectangulo - tamaño_texto0[0]) // 2, rectangulo0[0][1] + (alto_rectangulo + tamaño_texto1[1]) // 2)
pos_texto1 = (rectangulo1[0][0] + (ancho_rectangulo - tamaño_texto1[0]) // 2, rectangulo1[0][1] + (alto_rectangulo + tamaño_texto1[1]) // 2)
pos_texto2 = (rectangulo2[0][0] + (ancho_rectangulo - tamaño_texto2[0]) // 2, rectangulo2[0][1] + (alto_rectangulo + tamaño_texto2[1]) // 2)
pos_texto3 = (rectangulo3[0][0] + (ancho_rectangulo - tamaño_texto3[0]) // 2, rectangulo3[0][1] + (alto_rectangulo + tamaño_texto3[1]) // 2)


# Direcciones de sonido
ruta_acierto2 = Path('./sonidos/acierto2.wav').resolve()
ruta_perdiste = Path('./sonidos/perdiste.wav').resolve()

###############################################################

################### Definicion de funciones ###################
def dibujar_rectangulo(img, rectangulo, texto, posicion_texto, condicion):
    if condicion:
        color_rectangulo = azul
        color_texto = (255, 255, 255)
    else:
        color_rectangulo = amarillo
        color_texto = (0, 0, 0)

    cv2.rectangle(img, rectangulo[0], rectangulo[1], color_rectangulo, -1)
    cv2.putText(img, texto, posicion_texto, font, font_scale, color_texto, 2, cv2.LINE_AA)

def play_sound(sound):
    pygame.mixer.music.load(sound)  # Carga el sonido
    pygame.mixer.music.play()  # Reproduce el sonido

###############################################################

#############Inicio de bucle principal de juego################

pygame.mixer.init()

cv2.namedWindow("Imagen2", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Imagen2", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)



while True:
    success, img = cap.read()
    height, width, _ = img.shape
    img = cv2.flip(img, 1)
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)

    if estado_modo == 0:
        print("MENU")
        if results.pose_landmarks is not None:
            # Dibujo de landmarks de cuerpo
            # mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS,
            #                      mpDraw.DrawingSpec(color=(b, g, r), thickness=3, circle_radius=1),
            #                      mpDraw.DrawingSpec(color=(r, g, b), thickness=3, circle_radius=4))

            # Puntos manos
            x1_manoIzq = int(results.pose_landmarks.landmark[manoIzq].x * width)
            y1_manoIzq = int(results.pose_landmarks.landmark[manoIzq].y * height)

            x1_manoDer = int(results.pose_landmarks.landmark[manoDer].x * width)
            y1_manoDer = int(results.pose_landmarks.landmark[manoDer].y * height)

            # Dibujo de circulo manos
            cv2.circle(img, (x1_manoIzq, y1_manoIzq), 7, amarillo, 10)
            cv2.circle(img, (x1_manoDer, y1_manoDer), 7, azul, 10)

            # Cambio color menu 1
            dibujar_rectangulo(img, rectangulo1, texto1, pos_texto1,
                               (x1_manoIzq in range(x_centro - ancho_rectangulo // 2,
                                                    x_centro + ancho_rectangulo // 2)) and
                               (y1_manoIzq in range(y_centro - 3 * alto_rectangulo // 2 - alto_rectangulo,
                                                    y_centro - alto_rectangulo // 2 - alto_rectangulo)))
            # Cambio color menu 2
            dibujar_rectangulo(img, rectangulo2, texto2, pos_texto2,
                               (x1_manoIzq in range(x_centro - ancho_rectangulo // 2,
                                                    x_centro + ancho_rectangulo // 2)) and
                               (y1_manoIzq in range(y_centro - alto_rectangulo // 2, y_centro + alto_rectangulo // 2)))

            # Cambio color menu 3
            """dibujar_rectangulo(img, rectangulo3, texto3, pos_texto3,
                               (x1_manoIzq in range(x_centro - ancho_rectangulo // 2,
                                                    x_centro + ancho_rectangulo // 2)) and
                               (y1_manoIzq in range(y_centro + alto_rectangulo // 2 + alto_rectangulo,
                                                    y_centro + 3 * alto_rectangulo // 2 + alto_rectangulo)))"""

            # Deteccion de colision para seleccion de estado 1 (Solo manos)
            if ((x1_manoIzq in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (y1_manoIzq in range(y_centro - 3 * alto_rectangulo // 2 - alto_rectangulo, y_centro - alto_rectangulo // 2 - alto_rectangulo))) and \
                    ((x1_manoDer in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (y1_manoDer in range(y_centro - 3 * alto_rectangulo // 2 - alto_rectangulo, y_centro - alto_rectangulo // 2 - alto_rectangulo))):
                estado_modo = 1
                executor.submit(play_sound(ruta_acierto2))

            elif ((x1_manoIzq in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (y1_manoIzq in range(y_centro - alto_rectangulo // 2, y_centro + alto_rectangulo // 2))) and \
                    ((x1_manoDer in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (y1_manoDer in range(y_centro - alto_rectangulo // 2, y_centro + alto_rectangulo // 2))):
                estado_modo = 2
                executor.submit(play_sound(ruta_acierto2))

            """elif ((x1_manoIzq in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (y1_manoIzq in range(y_centro + alto_rectangulo // 2 + alto_rectangulo,y_centro + 3 * alto_rectangulo // 2 + alto_rectangulo))) and \
                    ((x1_manoDer in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (y1_manoDer in range(y_centro + alto_rectangulo // 2 + alto_rectangulo, y_centro + 3 * alto_rectangulo // 2 + alto_rectangulo))):
                estado_modo = 3
                executor.submit(play_sound(ruta_acierto2))"""


        cv2.putText(img, texto0, pos_texto0, font, font_scale, color_textos2, 2, cv2.LINE_AA)

    elif estado_modo == 1:
        print("Solo Manos")
        if results.pose_landmarks is not None:
            # Dibujo de landmarks de cuerpo
            # mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS,
            #                      mpDraw.DrawingSpec(color=(b, g, r), thickness=3, circle_radius=1),
            #                      mpDraw.DrawingSpec(color=(r, g, b), thickness=3, circle_radius=4))

            # Puntos manos
            x1_manoIzq = int(results.pose_landmarks.landmark[manoIzq].x * width)
            y1_manoIzq = int(results.pose_landmarks.landmark[manoIzq].y * height)

            x1_manoDer = int(results.pose_landmarks.landmark[manoDer].x * width)
            y1_manoDer = int(results.pose_landmarks.landmark[manoDer].y * height)


            # Dibujo de circulo manos
            cv2.circle(img, (x1_manoIzq, y1_manoIzq), 7, amarillo, 10)
            cv2.circle(img, (x1_manoDer, y1_manoDer), 7, azul, 10)

        if estado_juego:
                # Colision manos-circulos
                if ((x1_manoIzq in range(posicion_amarillo[0]-radio_circulo, posicion_amarillo[0]+radio_circulo)) and (y1_manoIzq in range(posicion_amarillo[1]-radio_circulo, posicion_amarillo[1]+radio_circulo)))\
                        and ((x1_manoDer in range(posicion_azul[0]-radio_circulo, posicion_azul[0]+radio_circulo)) and (y1_manoDer in range(posicion_azul[1]-radio_circulo, posicion_azul[1]+radio_circulo))):

                    posicion_amarillo = (rd.choice(ancho), rd.choice(alto))
                    posicion_azul = (rd.choice(ancho), rd.choice(alto))
                    contador += 1  # Puntaje suma por acierto
                    cuenta_atras = TIEMPO  # Se resetea el tiempo
                    executor.submit(play_sound(ruta_acierto2))  # Sonido de acierto


                # Cuenta Atras
                fin = time.time()

                seg = int(fin - inicio)

                if seg != t_anterior:
                    cuenta_atras -= 1

                    if cuenta_atras <= 0:
                        print("PERDISTE", contador)
                        estado_juego = False
                        estado_interno = True
                        cuenta_atras = TIEMPO

                    t_anterior = seg

                # Subir dificultad
                if contador == contador_objetivo:
                    TIEMPO -= 1
                    radio_circulo -= 3
                    contador_objetivo = contador_objetivo + 5

                # Posicion de circulos aleatoreros
                cv2.circle(img, posicion_amarillo, radio_circulo, amarillo, 5)
                cv2.circle(img, posicion_azul, radio_circulo, azul, 5)

                cv2.putText(img, str(contador), (20, 60), cv2.FONT_HERSHEY_PLAIN, 5, (181, 255, 36), 10)
                cv2.putText(img, str(cuenta_atras), (width-60, 60), cv2.FONT_HERSHEY_PLAIN, 5, (0, 7, 255), 10)
        else:
            # Estado de perder
            if estado_interno:
                executor.submit(play_sound(ruta_perdiste))  # Sonido de perder
                estado_interno = False
            cv2.putText(img, "PERDISTE", (width//4 +20, height//2), cv2.FONT_HERSHEY_PLAIN, 4, (242, 133, 114), 10)
            cv2.putText(img, "Puntaje: "+str(contador), (width // 4 , (height//2)+alto_rectangulo), cv2.FONT_HERSHEY_PLAIN, 4, (114, 68, 242), 4)
            dibujar_rectangulo(img, rectangulo1, "> Reiniciar!", pos_texto1,
                               (x1_manoIzq in range(x_centro - ancho_rectangulo // 2,
                                                    x_centro + ancho_rectangulo // 2)) and
                               (y1_manoIzq in range(y_centro - 3 * alto_rectangulo // 2 - alto_rectangulo,
                                                    y_centro - alto_rectangulo // 2 - alto_rectangulo)))

            dibujar_rectangulo(img, rectangulo3, "MENU <", pos_texto3,
                               (x1_manoIzq in range(x_centro - ancho_rectangulo // 2,
                                                    x_centro + ancho_rectangulo // 2)) and
                               (y1_manoIzq in range(y_centro + alto_rectangulo // 2 + alto_rectangulo,
                                                    y_centro + 3 * alto_rectangulo // 2 + alto_rectangulo)))



            posicion_amarillo = (rd.choice(ancho), rd.choice(alto))
            posicion_azul = (rd.choice(ancho), rd.choice(alto))

            # Reiniciar el juego
            if ((x1_manoIzq in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (
                    y1_manoIzq in range(y_centro - 3 * alto_rectangulo // 2 - alto_rectangulo,
                                        y_centro - alto_rectangulo // 2 - alto_rectangulo))) and \
                    ((x1_manoDer in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (
                            y1_manoDer in range(y_centro - 3 * alto_rectangulo // 2 - alto_rectangulo,
                                                y_centro - alto_rectangulo // 2 - alto_rectangulo))):
                executor.submit(play_sound(ruta_acierto2))
                estado_juego = True
                contador = 0
                TIEMPO = 10
                radio_circulo = 50
                contador_objetivo = 10

            elif ((x1_manoIzq in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (y1_manoIzq in range(y_centro + alto_rectangulo // 2 + alto_rectangulo,y_centro + 3 * alto_rectangulo // 2 + alto_rectangulo))) and \
                    ((x1_manoDer in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (y1_manoDer in range(y_centro + alto_rectangulo // 2 + alto_rectangulo, y_centro + 3 * alto_rectangulo // 2 + alto_rectangulo))):
                executor.submit(play_sound(ruta_acierto2))
                estado_juego = True
                estado_modo = 0
                TIEMPO = 10
                contador = 0
                radio_circulo = 50
                contador_objetivo = 10
            
    elif estado_modo == 2:
        if results.pose_landmarks is not None:
            # Dibujo de landmarks de cuerpo
            # mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS,
            #                      mpDraw.DrawingSpec(color=(b, g, r), thickness=3, circle_radius=1),
            #                      mpDraw.DrawingSpec(color=(r, g, b), thickness=3, circle_radius=4))

            # Puntos manos
            x1_manoIzq = int(results.pose_landmarks.landmark[manoIzq].x * width)
            y1_manoIzq = int(results.pose_landmarks.landmark[manoIzq].y * height)

            x1_manoDer = int(results.pose_landmarks.landmark[manoDer].x * width)
            y1_manoDer = int(results.pose_landmarks.landmark[manoDer].y * height)

            # Puntos piernas
            x1_pierIzq = int(results.pose_landmarks.landmark[pierIzq].x * width)
            y1_pierIzq = int(results.pose_landmarks.landmark[pierIzq].y * height)

            x1_pierDer = int(results.pose_landmarks.landmark[pierDer].x * width)
            y1_pierDer = int(results.pose_landmarks.landmark[pierDer].y * height)

            # Dibujo de circulo manos
            cv2.circle(img, (x1_manoIzq, y1_manoIzq), 7, amarillo, 10)
            cv2.circle(img, (x1_manoDer, y1_manoDer), 7, azul, 10)

            # Dibujo de circulo piernas
            cv2.circle(img, (x1_pierIzq, y1_pierIzq), 7, rojo, 10)
            cv2.circle(img, (x1_pierDer, y1_pierDer), 7, rojo, 10)
        if estado_juego:
                # Colision manos-circulos
                if ((x1_manoIzq in range(posicion_amarillo[0]-radio_circulo, posicion_amarillo[0]+radio_circulo)) and (y1_manoIzq in range(posicion_amarillo[1]-radio_circulo, posicion_amarillo[1]+radio_circulo)))\
                        and ((x1_manoDer in range(posicion_azul[0]-radio_circulo, posicion_azul[0]+radio_circulo)) and (y1_manoDer in range(posicion_azul[1]-radio_circulo, posicion_azul[1]+radio_circulo))) and \
                        (((x1_pierDer in range(posicion_rojo[0]-radio_circulo, posicion_rojo[0]+radio_circulo)) and (y1_pierDer in range(posicion_rojo[1]-radio_circulo, posicion_rojo[1]+radio_circulo))) or \
                         ((x1_pierIzq in range(posicion_rojo[0]-radio_circulo, posicion_rojo[0]+radio_circulo)) and (y1_pierIzq in range(posicion_rojo[1]-radio_circulo, posicion_rojo[1]+radio_circulo)))):

                    posicion_amarillo = (rd.choice(ancho), rd.choice(alto))
                    posicion_azul = (rd.choice(ancho), rd.choice(alto))
                    posicion_rojo = (rd.choice(ancho), rd.choice(alto_pies))
                    contador += 1  # Puntaje suma por acierto
                    cuenta_atras = TIEMPO  # Se resetea el tiempo
                    executor.submit(play_sound(ruta_acierto2))  # Sonido de acierto


                # Cuenta Atras
                fin = time.time()

                seg = int(fin - inicio)

                if seg != t_anterior:
                    cuenta_atras -= 1

                    if cuenta_atras <= 0:
                        print("PERDISTE", contador)
                        estado_juego = False
                        estado_interno = True
                        cuenta_atras = TIEMPO

                    t_anterior = seg

                # Subir dificultad
                if contador == contador_objetivo:
                    TIEMPO -= 1
                    radio_circulo -= 3
                    contador_objetivo = contador_objetivo + 5

                # Posicion de circulos aleatoreros
                cv2.circle(img, posicion_amarillo, radio_circulo, amarillo, 5)
                cv2.circle(img, posicion_azul, radio_circulo, azul, 5)
                cv2.circle(img, posicion_rojo, radio_circulo, rojo, 5)

                cv2.putText(img, str(contador), (20, 60), cv2.FONT_HERSHEY_PLAIN, 5, (181, 255, 36), 10)
                cv2.putText(img, str(cuenta_atras), (width-60, 60), cv2.FONT_HERSHEY_PLAIN, 5, (0, 7, 255), 10)
        else:
            # Estado de perder
            if estado_interno:
                executor.submit(play_sound(ruta_perdiste))  # Sonido de perder
                estado_interno = False
            cv2.putText(img, "PERDISTE", (width//4 +20, height//2), cv2.FONT_HERSHEY_PLAIN, 4, (242, 133, 114), 10)
            cv2.putText(img, "Puntaje: "+str(contador), (width // 4 , (height//2)+alto_rectangulo), cv2.FONT_HERSHEY_PLAIN, 4, (114, 68, 242), 4)
            dibujar_rectangulo(img, rectangulo1, "> Reiniciar!", pos_texto1,
                               (x1_manoIzq in range(x_centro - ancho_rectangulo // 2,
                                                    x_centro + ancho_rectangulo // 2)) and
                               (y1_manoIzq in range(y_centro - 3 * alto_rectangulo // 2 - alto_rectangulo,
                                                    y_centro - alto_rectangulo // 2 - alto_rectangulo)))

            dibujar_rectangulo(img, rectangulo3, "MENU <", pos_texto3,
                               (x1_manoIzq in range(x_centro - ancho_rectangulo // 2,
                                                    x_centro + ancho_rectangulo // 2)) and
                               (y1_manoIzq in range(y_centro + alto_rectangulo // 2 + alto_rectangulo,
                                                    y_centro + 3 * alto_rectangulo // 2 + alto_rectangulo)))



            posicion_amarillo = (rd.choice(ancho), rd.choice(alto))
            posicion_azul = (rd.choice(ancho), rd.choice(alto))
            posicion_rojo = (rd.choice(ancho), rd.choice(alto_pies))

            # Reiniciar el juego
            if ((x1_manoIzq in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (
                    y1_manoIzq in range(y_centro - 3 * alto_rectangulo // 2 - alto_rectangulo,
                                        y_centro - alto_rectangulo // 2 - alto_rectangulo))) and \
                    ((x1_manoDer in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (
                            y1_manoDer in range(y_centro - 3 * alto_rectangulo // 2 - alto_rectangulo,
                                                y_centro - alto_rectangulo // 2 - alto_rectangulo))):
                executor.submit(play_sound(ruta_acierto2))
                estado_juego = True
                contador = 0
                TIEMPO = 10
                radio_circulo = 50
                contador_objetivo = 10
            elif ((x1_manoIzq in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (y1_manoIzq in range(y_centro + alto_rectangulo // 2 + alto_rectangulo,y_centro + 3 * alto_rectangulo // 2 + alto_rectangulo))) and \
                    ((x1_manoDer in range(x_centro - ancho_rectangulo // 2, x_centro + ancho_rectangulo // 2)) and (y1_manoDer in range(y_centro + alto_rectangulo // 2 + alto_rectangulo, y_centro + 3 * alto_rectangulo // 2 + alto_rectangulo))):
                executor.submit(play_sound(ruta_acierto2))
                estado_juego = True
                estado_modo = 0
                executor.submit(play_sound(ruta_acierto2))
                TIEMPO = 10
                contador = 0
                radio_circulo = 50
                contador_objetivo = 10

    #img = cv2.resize(img, (1600, 900))
    cv2.imshow("Imagen2", img) # Mostrar imagen en tiempo real
    key = cv2.waitKey(1)
    # Pitiarse el juego
    if key == ord('q'):
        break

###############################################################
