# Librerias utilizadas
import cv2
import mediapipe as mp
from pydub import AudioSegment
from pydub.playback import play


import pygame

import concurrent.futures
import time
import random as rd

pygame.mixer.init()


def play_sound_acierto():
    pygame.mixer.music.load("./acierto2.wav")  # Carga el sonido
    pygame.mixer.music.play()  # Reproduce el sonido

def play_sound_perdiste():
    pygame.mixer.music.load("perdiste.wav")  # Carga el sonido
    pygame.mixer.music.play()  # Reproduce el sonido


# Para reproduccion de sonidos asincronicos
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

# Landmarks de mediapipe
mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

# Definicion de captura de camara 0, 1, 2,  3 (Dependiendo de qu e camara quiero usar)
cap = cv2.VideoCapture(1)
success, img = cap.read()
height, width, _ = img.shape


# Definicion de color Inical RGB (Solo para
r = 255
g = 255
b = 255

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

# Ancho y alto para definir rangos de aparicion de los circulos
ancho = range(50, width-50)
alto = range(50, height-50)
alto_pies = range(height//2, height-50)

# Posiciones aleatoreas de los circulos en pantalla
posicion_amarillo = (rd.choice(ancho), rd.choice(alto))
posicion_azul = (rd.choice(ancho), rd.choice(alto))
posicion_rojo = (rd.choice(ancho), rd.choice(alto_pies))

TIEMPO = 10  # Tiempo contador constante
contador = 0  # Contador de puntaje
r = 50  # Radio de circulos que aparecen en pantalla
inicio = time.time()
t_anterior = 0
cuenta_atras = TIEMPO
estado = True  # Estado para Jugar o Perder
estado_interno = True  # Estado para reproducir solo una vez el sonido de perdida
contador_objetivo = 10  # NUmero al que la sudicultad sube


while True:
    success, img = cap.read()
    height, width, _ = img.shape
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    print(height, width)
    if estado:
        if results.pose_landmarks is not None:
            # Dibujo de landmarks de cuerpo
            #mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS,
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


            # Colision manos-circulos
            if ((x1_manoIzq in range(posicion_amarillo[0]-r, posicion_amarillo[0]+r)) and (y1_manoIzq in range(posicion_amarillo[1]-r, posicion_amarillo[1]+r)))\
                    and ((x1_manoDer in range(posicion_azul[0]-r, posicion_azul[0]+r)) and (y1_manoDer in range(posicion_azul[1]-r, posicion_azul[1]+r))) and \
                    (((x1_pierDer in range(posicion_rojo[0]-r, posicion_rojo[0]+r)) and (y1_pierDer in range(posicion_rojo[1]-r, posicion_rojo[1]+r))) or \
                     ((x1_pierIzq in range(posicion_rojo[0]-r, posicion_rojo[0]+r)) and (y1_pierIzq in range(posicion_rojo[1]-r, posicion_rojo[1]+r)))):
                posicion_amarillo = (rd.choice(ancho), rd.choice(alto))
                posicion_azul = (rd.choice(ancho), rd.choice(alto))
                posicion_rojo = (rd.choice(ancho), rd.choice(alto_pies))
                contador += 1  # Puntaje suma por acierto
                cuenta_atras = TIEMPO  # Se resetea el tiempo
                executor.submit(play_sound_acierto)  # Sonido de acierto

            # Cuenta Atras
            fin = time.time()
            seg = int(fin - inicio)
            if seg != t_anterior:
                cuenta_atras -= 1
                if cuenta_atras <= 0:
                    print("PERDISTE", contador)
                    estado = False
                    estado_interno = True
                    cuenta_atras = TIEMPO
                t_anterior = seg

            # Subir dificultad
            if contador == contador_objetivo:
                TIEMPO -= 1
                r -= 3
                contador_objetivo = contador_objetivo + 5

            # Posicion de circulos aleatoreros
            cv2.circle(img, posicion_amarillo, r, amarillo, 5)
            cv2.circle(img, posicion_azul, r, azul, 5)
            cv2.circle(img, posicion_rojo, r, rojo, 5)
            cv2.putText(img, str(contador), (20, 60), cv2.FONT_HERSHEY_PLAIN, 5, (181, 255, 36), 10)
            cv2.putText(img, str(cuenta_atras), (width-60, 60), cv2.FONT_HERSHEY_PLAIN, 5, (0, 7, 255), 10)
    else:
        # Estado de perder
        if estado_interno:
            executor.submit(play_sound_perdiste)
            estado_interno = False
        cv2.putText(img, "PERDISTE", (width//4, height//2), cv2.FONT_HERSHEY_PLAIN, 4, (242, 133, 114), 10)
        cv2.putText(img, "Puntaje: "+str(contador), (width // 4, (height//4)*3), cv2.FONT_HERSHEY_PLAIN, 4, (114, 68, 242), 4)
        cv2.putText(img, "Presiona 'R' para reiniciar", (width // 5, (height // 5)), cv2.FONT_HERSHEY_PLAIN, 2, (114, 68, 242), 4)
        posicion_amarillo = (rd.choice(ancho), rd.choice(alto))
        posicion_azul = (rd.choice(ancho), rd.choice(alto))
        posicion_rojo = (rd.choice(ancho), rd.choice(alto_pies))

        # Reiniciar el juego
        key = cv2.waitKey(1)
        if key == 114 or key == 82:
            estado = True
            contador = 0


    #img = cv2.resize(img, (1600, 900))
    cv2.imshow("Imagen2", img) # Mostrar imagen en tiempo real
    key = cv2.waitKey(1)
    # Pitiarse el juego
    if key == ord('q'):
        break



