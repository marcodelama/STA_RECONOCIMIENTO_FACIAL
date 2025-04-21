import io
import json
import cv2
import numpy as np
from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import insightface
from .models import SttrImagen, SttmPersonal

# Carga el modelo una sola vez
model = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
model.prepare(ctx_id=0, det_size=(640, 640))

@csrf_exempt
def verificar_rostro(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    id_personal = request.POST.get('n_id_personal')
    archivo = request.FILES.get('cl_imagen_biometrica')
    if not archivo:
        return JsonResponse({'error': 'Imagen es obligatoria'}, status=400)

    # 1) Abrimos con PIL, convertimos a RGB y luego a BGR para InsightFace
    img = Image.open(archivo).convert("RGB")
    img_np = np.array(img)                     # RGB
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # 2) Detectamos rostros + embeddings
    rostros = model.get(img_bgr)
    print(f"Detectados {len(rostros)} rostros en la imagen")

    if not rostros:
        return JsonResponse({'error': 'No se detectó ningún rostro'}, status=400)

    # 3) Extraemos correctamente el embedding (vector 512) del primer rostro
    embedding = rostros[0].embedding            # ya es un array de forma (512,)
    nuevo_encoding = np.array(embedding, dtype=np.float32)

    # 4) Comparamos con los encodings guardados
    imagenes = SttrImagen.objects.filter(n_id_personal=id_personal)
    mejor_distancia = float('inf')
    coincidencia_encontrada = False

    nuevo_encoding = nuevo_encoding / np.linalg.norm(nuevo_encoding)

    for img_bd in imagenes:
        try:
            # Asumiendo que cl_encode es un JSON string de lista de floats
            encoding_guardado = np.array(json.loads(img_bd.cl_encode), dtype=np.float32)
            
            encoding_guardado = encoding_guardado / np.linalg.norm(encoding_guardado)

            similitud = np.dot(nuevo_encoding, encoding_guardado)

            distancia = 1.0 - similitud
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                
            # Umbral más apropiado para distancia coseno normalizada
            if distancia < 0.5:  # Ajusta este valor según tus pruebas
                coincidencia_encontrada = True
        except Exception as e:
            print(f"Error al procesar embedding: {str(e)}")
            continue

    if coincidencia_encontrada:
        return JsonResponse({
            'mensaje': 'Coincidencia confirmada', 
            'distancia': round(float(mejor_distancia), 4)
        }, status=200)
    else:
        return JsonResponse({
            'error': 'No coincide con registros', 
            'mejor_distancia': round(float(mejor_distancia), 4)
        }, status=400)