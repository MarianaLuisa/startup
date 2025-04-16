from django.db import models

# Create your models here.



class Startup(models.Model):
    nome = models.CharField(max_length=100)
    slogan = models.CharField(max_length=255)
    ano_fundacao = models.IntegerField()
    pontos = models.IntegerField(default=70)

    # Adicione os campos de estatísticas de eventos
    pitchs = models.IntegerField(default=0)
    bugs = models.IntegerField(default=0)
    tracoes = models.IntegerField(default=0)
    investidores_irritados = models.IntegerField(default=0)
    penalidades = models.IntegerField(default=0)

    def __str__(self):
        return self.nome


class Batalha(models.Model):
    startup_1 = models.ForeignKey(Startup, related_name='batalha_startup_1', on_delete=models.CASCADE)
    startup_2 = models.ForeignKey(Startup, related_name='batalha_startup_2', on_delete=models.CASCADE)
    evento = models.CharField(max_length=255, null=True, blank=True)
    vencedor = models.ForeignKey(Startup, related_name='batalhas_vencidas', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.startup_1.nome} vs {self.startup_2.nome}'
