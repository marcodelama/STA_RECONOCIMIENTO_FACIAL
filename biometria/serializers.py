import io
import json
import numpy as np
import cv2
from PIL import Image
from rest_framework import serializers
from django.utils import timezone
import insightface
from .models import SttrImagen, SttmPersonal

# Inicializar modelo InsightFace a nivel de módulo
eager_model = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
eager_model.prepare(ctx_id=0, det_size=(640, 640))

class ImagenBiometricaInsightSerializer(serializers.Serializer):
    n_id_personal = serializers.IntegerField()
    cl_imagen_biometrica = serializers.ImageField()

    def validate_n_id_personal(self, value):
        if not SttmPersonal.objects.filter(n_id_personal=value).exists():
            raise serializers.ValidationError("Personal no encontrado")
        return value

    def create(self, validated_data):
        id_personal = validated_data['n_id_personal']
        archivo = validated_data['cl_imagen_biometrica']

        # Leer bytes de la imagen para reutilizar
        archivo_bytes = archivo.read()

        # 1) Procesamiento para InsightFace (RGB->BGR)
        img_pil = Image.open(io.BytesIO(archivo_bytes)).convert('RGB')
        img_np = np.array(img_pil)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # 2) Detectar rostro y generar embedding InsightFace
        rostros = eager_model.get(img_bgr)
        if not rostros:
            raise serializers.ValidationError("No se detectó ningún rostro en la imagen")
        insight_embedding = np.array(rostros[0].embedding, dtype=np.float32)

        # 3) Validar duplicados y coincidencias
        # Filtrar solo encodings de 512 dimensiones
        imgs_propias = SttrImagen.objects.filter(n_id_personal__n_id_personal=id_personal)
        coincide_con_propio = False

        insight_embedding = insight_embedding / np.linalg.norm(insight_embedding)

        for img_existente in imgs_propias:
            saved = json.loads(img_existente.cl_encode)
            saved_arr = np.array(saved, dtype=np.float32)

            saved_arr = saved_arr / np.linalg.norm(saved_arr)

            similitud = np.dot(insight_embedding, saved_arr)

            distancia = 1.0 - similitud

            if saved_arr.shape[0] != insight_embedding.shape[0]:
                # Ignorar registros antiguos de otro formato
                continue

            if distancia < 0.1:
                raise serializers.ValidationError({
                    "error": "La persona ya tiene una imagen muy similar registrada",
                    "distancia": round(float(distancia), 4)
                })
            
            if distancia < 0.5:
                coincide_con_propio = True

        otros = SttrImagen.objects.exclude(n_id_personal__n_id_personal=id_personal)
        for img_existente in otros:
            saved = json.loads(img_existente.cl_encode)
            saved_arr = np.array(saved, dtype=np.float32)

            saved_arr = saved_arr / np.linalg.norm(saved_arr)

            similitud = np.dot(insight_embedding, saved_arr)

            distancia = 1.0 - similitud

            if saved_arr.shape[0] != insight_embedding.shape[0]:
                continue
            
            if distancia < 0.4:
                per = img_existente.n_id_personal
                raise serializers.ValidationError({
                    "error": "Esta imagen corresponde a otro personal ya registrado",
                    "distancia": round(float(distancia), 4),
                    "personal_existente": {
                        "id": per.n_id_personal,
                        "nombre": f"{per.v_nombre} {per.v_ape_pat} {per.v_ape_mat}"
                    }
                })
            
        if imgs_propias.exists() and not coincide_con_propio:
            raise serializers.ValidationError({
                "error": "La imagen no coincide con ninguna de las registradas para este personal",
                "sugerencia": "Por favor, verifique que la imagen corresponda a la persona correcta",
                "distancia":distancia
            })

        # 4) Guardar nueva imagen y embedding
        personal = SttmPersonal.objects.get(n_id_personal=id_personal)
        instancia = SttrImagen.objects.create(
            n_id_personal    = personal,
            cl_ruta_archivo  = archivo,
            cl_encode        = json.dumps(insight_embedding.tolist()),
            d_fecha_creacion = timezone.now()
        )
        return instancia