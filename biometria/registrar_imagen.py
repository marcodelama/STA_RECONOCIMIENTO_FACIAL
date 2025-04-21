from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers   import MultiPartParser
from rest_framework.response  import Response
from drf_yasg.utils           import swagger_auto_schema
from drf_yasg import openapi
from .serializers             import ImagenBiometricaInsightSerializer

@swagger_auto_schema(
    method='post',
    request_body=ImagenBiometricaInsightSerializer,
    responses={
        201: openapi.Response('Imagen registrada con InsightFace'),
        400: 'Error de validación',
        405: 'Método no permitido',
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser])
def api_registrar_imagen_insight(request):
    serializer = ImagenBiometricaInsightSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    instancia = serializer.save()
    per = instancia.n_id_personal
    return Response(
        {"mensaje": f"Imagen registrada para {per.v_nombre} {per.v_ape_pat} {per.v_ape_mat}"},
        status=201
    )