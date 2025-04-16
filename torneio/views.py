from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Startup, Batalha
import random
import csv
import json
from django.http import HttpResponse
from .models import Startup


# 1. Página Inicial
def index(request):
    return render(request, 'torneio/index.html')


# 2. Cadastro de Startups
def cadastro(request):
    startups = Startup.objects.all()
    erro = None

    if request.method == 'POST':
        nome = request.POST.get('nome')
        slogan = request.POST.get('slogan')
        ano_fundacao = request.POST.get('ano_fundacao')

        if Startup.objects.filter(nome=nome).exists():
            erro = 'Nome já cadastrado.'
        elif len(startups) >= 8:
            erro = 'Número máximo de startups atingido.'
        else:
            Startup.objects.create(
                nome=nome,
                slogan=slogan,
                ano_fundacao=ano_fundacao,
            )
            return redirect('index')

    return render(request, 'torneio/cadastro.html', {'erro': erro, 'startups': startups})


# View para Ranking Geral
def ranking(request):
    startups = Startup.objects.all().order_by('-pontuacao')
    return render(request, 'torneio/ranking.html', {'startups': startups})

# View para listar Batalhas (pode mostrar todas ou somente as atuais)
def batalhas(request):
    batalhas = Batalha.objects.all()
    return render(request, 'torneio/batalhas.html', {'batalhas': batalhas})


# 3. Iniciar Torneio
def iniciar_torneio(request):
    startups = list(Startup.objects.all())
    erro = None

    if len(startups) < 4 or len(startups) > 8 or len(startups) % 2 != 0:
        erro = 'Cadastre entre 4 e 8 startups (número par).'
        return render(request, 'torneio/index.html', {'erro': erro})

    if Batalha.objects.filter(concluida=False).exists():
        erro = 'Já existe um torneio em andamento.'
        return render(request, 'torneio/index.html', {'erro': erro})

    random.shuffle(startups)

    for i in range(0, len(startups), 2):
        Batalha.objects.create(startup_1=startups[i], startup_2=startups[i + 1])

    return redirect('batalhas')

# 4. Administração de Batalhas
def administrar_batalha(request, batalha_id):
    batalha = Batalha.objects.get(id=batalha_id)
    startup1 = batalha.startup_1
    startup2 = batalha.startup_2

    eventos = {
        'pitch': 6,
        'produto_bugs': -4,
        'tracao': 3,
        'investidor_irritado': -6,
        'fake_news': -8
    }

    if request.method == 'POST':
        evento1 = request.POST.getlist('eventos_startup_1')
        evento2 = request.POST.getlist('eventos_startup_2')

        pontuacao1 = 0
        pontuacao2 = 0

        for ev in evento1:
            pontuacao1 += eventos.get(ev, 0)
            setattr(startup1, ev + 's', getattr(startup1, ev + 's') + 1)

        for ev in evento2:
            pontuacao2 += eventos.get(ev, 0)
            setattr(startup2, ev + 's', getattr(startup2, ev + 's') + 1)

        startup1.pontos += pontuacao1
        startup2.pontos += pontuacao2

        # Decidir vencedor
        if startup1.pontos == startup2.pontos:
            # Shark Fight
            if random.choice([True, False]):
                startup1.pontos += 2
            else:
                startup2.pontos += 2

        vencedor = startup1 if startup1.pontos > startup2.pontos else startup2
        vencedor.pontos += 30  # bônus da vitória

        startup1.save()
        startup2.save()

        batalha.concluida = True
        batalha.save()

        return redirect('batalhas')  # ou outra página

    return render(request, 'torneio/administrar.html', {
        'batalha': batalha,
        'eventos': eventos
    })

# 6. Exibir Histórico de Batalhas de uma Startup
def historico(request, start_id):
    startup = Startup.objects.get(id=start_id)
    batalhas = Batalha.objects.filter(startup_1=startup) | Batalha.objects.filter(startup_2=startup)
    return render(request, 'torneio/historico.html', {'startup': startup, 'batalhas': batalhas})

def exportar_json(request):
    startups = Startup.objects.all()
    data = []
    for s in startups:
        data.append({
            'nome': s.nome,
            'slogan': s.slogan,
            'ano_fundacao': s.ano_fundacao,
            'pontuacao': s.pontuacao,
            'pitchs': s.pitchs,
            'bugs': s.bugs,
            'tracoes': s.tracoes,
            'investidores_irritados': s.investidores_irritados,
            'penalidades': s.penalidades
        })
    response = HttpResponse(json.dumps(data, indent=4), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="startups.json"'
    return response


def exportar_csv(request):
    startups = Startup.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="startups.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nome', 'Slogan', 'Ano Fundação', 'Pontuação', 'Pitchs', 'Bugs', 'Trações', 'Investidores Irritados', 'Penalidades'])
    for s in startups:
        writer.writerow([s.nome, s.slogan, s.ano_fundacao, s.pontuacao, s.pitchs, s.bugs, s.tracoes, s.investidores_irritados, s.penalidades])

    return response
