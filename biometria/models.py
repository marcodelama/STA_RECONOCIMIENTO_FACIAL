from django.db import models

class SttmPersonal(models.Model):
    n_id_personal = models.BigIntegerField(primary_key=True)
    c_codigo_uni = models.CharField(max_length=9, blank=True, null=True, db_comment='9')
    v_nombre = models.CharField(max_length=75)
    v_ape_pat = models.CharField(max_length=50)
    v_ape_mat = models.CharField(max_length=50)
    v_nro_doc = models.CharField(max_length=12)
    v_correo = models.CharField(max_length=100)
    v_celular = models.CharField(max_length=9, blank=True, null=True)
    n_nro_ruc = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'sttm_personal'


class SttrAsistencia(models.Model):
    n_id_asistencia = models.BigIntegerField(primary_key=True)
    t_hora_llegada = models.DateTimeField(blank=True, null=True)
    t_hora_salida = models.DateTimeField(blank=True, null=True)
    n_id_asignacion = models.ForeignKey('SttxAsignacion', models.DO_NOTHING, db_column='n_id_asignacion')

    class Meta:
        managed = False
        db_table = 'sttr_asistencia'



class SttrImagen(models.Model):
    n_id_imagen = models.BigIntegerField(primary_key=True)
    d_fecha_creacion = models.DateField()
    cl_encode = models.TextField(blank=True, null=True)
    cl_ruta_archivo = models.ImageField(upload_to='personas/')
    n_id_personal = models.ForeignKey(SttmPersonal, models.DO_NOTHING, db_column='n_id_personal')

    class Meta:
        managed = False
        db_table = 'sttr_imagen'


class SttrTurno(models.Model):
    n_id_turno = models.BigIntegerField(primary_key=True)
    d_fecha = models.DateField()
    t_hora_inicio = models.DateField()

    class Meta:
        managed = False
        db_table = 'sttr_turno'

class SttxAsignacion(models.Model):
    n_id_asignacion = models.BigIntegerField(primary_key=True)
    n_id_personal = models.ForeignKey(SttmPersonal, models.DO_NOTHING, db_column='n_id_personal')
    c_disponibilidad = models.CharField(max_length=1)
    n_id_turno = models.ForeignKey(SttrTurno, models.DO_NOTHING, db_column='n_id_turno', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sttx_asignacion'

