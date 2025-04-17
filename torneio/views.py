from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Startup, Batalha, Torneio
import random
import csv
import json
from django.http import HttpResponse, JsonResponse
from .models import Startup
from django.shortcuts import get_object_or_404
from django.db.models import Q

def torneio_em_andamento():
    return Batalha.objects.exists() and Batalha.objects.filter(concluida=False).exists()

# 1. Página Inicial
def index(request):
    startups = Startup.objects.all()
    pode_iniciar = 4 <= startups.count() <= 8 and startups.count() % 2 == 0
    erro = request.GET.get('erro')
    sucesso = request.GET.get('sucesso')
    torneio = Torneio.objects.last()
    torneio_em_andamento = torneio.em_andamento if torneio else False
    torneio_finalizado = torneio.finalizado if torneio else False

    return render(request, 'torneio/index.html', {
        'pode_iniciar': pode_iniciar,
        'erro': erro,
        'sucesso': sucesso,
        'torneio_em_andamento': torneio_em_andamento,
        'torneio_finalizado': torneio_finalizado,
    })



def cadastro(request):
    if torneio_em_andamento():
        return render(request, 'torneio/torneio_em_andamento.html')

    startups = Startup.objects.all().order_by('nome')
    erro = None
    sucesso = None

    if request.method == 'POST':
        nome = request.POST.get('nome')
        slogan = request.POST.get('slogan')
        ano_fundacao = request.POST.get('ano_fundacao')

        if Startup.objects.filter(nome=nome).exists():
            erro = 'Nome já cadastrado.'
        elif startups.count() >= 8:
            erro = 'Número máximo de startups atingido.'
        else:
            Startup.objects.create(
                nome=nome,
                slogan=slogan,
                ano_fundacao=ano_fundacao,
            )
            sucesso = 'Startup cadastrada com sucesso.'

    return render(request, 'torneio/cadastro.html', {
        'startups': startups,
        'erro': erro,
        'sucesso': sucesso,
    })

def deletar_startup(request, id):
    if torneio_em_andamento():
        return redirect('cadastro')  # ou mostrar mensagem de erro
    startup = get_object_or_404(Startup, id=id)
    startup.delete()
    return redirect('cadastro')

# View para Ranking Geral

def ranking(request):
    torneio_iniciado = Batalha.objects.exists()
    torneio_finalizado = not Batalha.objects.filter(concluida=False).exists()

    if not torneio_iniciado:
        return render(request, 'torneio/ranking.html', {
            'ranking_disponivel': False
        })

    startups = Startup.objects.all().order_by('-pontos')

    return render(request, 'torneio/ranking.html', {
        'ranking_disponivel': True,
        'torneio_finalizado': torneio_finalizado,
        'startups': startups
    })


def iniciar_torneio(request):
    startups = list(Startup.objects.all())
    total = len(startups)

    if total not in [4, 8]:
        return render(request, 'torneio/index.html', {
            'erro': "O torneio só pode ser iniciado com 4 ou 8 startups cadastradas.",
            'pode_iniciar': 4 <= total <= 8 and total % 2 == 0,
            'torneio_em_andamento': torneio_em_andamento()
        })

    torneio = Torneio.objects.create(em_andamento=True)
    random.shuffle(startups)

    for i in range(0, total, 2):
        Batalha.objects.create(startup_1=startups[i], startup_2=startups[i + 1])

    return redirect('batalhas')


def batalhas(request):
    batalhas = Batalha.objects.all().order_by('id')
    return render(request, 'torneio/batalhas.html', {'batalhas': batalhas})

def avancar_fase_ou_finalizar():
    if Batalha.objects.filter(concluida=False).exists():
        return None  # Ainda há batalhas em andamento

    torneio = Torneio.objects.filter(em_andamento=True).last()
    startups_vivas = Startup.objects.filter(
        Q(id__in=Batalha.objects.values_list('startup_1', flat=True)) |
        Q(id__in=Batalha.objects.values_list('startup_2', flat=True))
    ).order_by('-pontos')

    startups_vivas = list(startups_vivas[:len(startups_vivas) // 2])
    if len(startups_vivas) % 2 != 0:
        startups_vivas.pop()

    if len(startups_vivas) == 2:
        final_existente = Batalha.objects.filter(
            Q(startup_1=startups_vivas[0], startup_2=startups_vivas[1]) |
            Q(startup_1=startups_vivas[1], startup_2=startups_vivas[0]),
            concluida=True
        ).exists()

        if final_existente:
            torneio.em_andamento = False
            torneio.finalizado = True
            torneio.save()
            return redirect('campea')
        else:
            Batalha.objects.create(startup_1=startups_vivas[0], startup_2=startups_vivas[1])
            return redirect('batalhas')

    elif len(startups_vivas) >= 2:
        random.shuffle(startups_vivas)
        for i in range(0, len(startups_vivas), 2):
            Batalha.objects.create(startup_1=startups_vivas[i], startup_2=startups_vivas[i + 1])
        return redirect('batalhas')

    else:
        torneio.em_andamento = False
        torneio.finalizado = True
        torneio.save()
        return redirect('campea')


def administrar_batalha(request, batalha_id):
    batalha = get_object_or_404(Batalha, id=batalha_id)
    startup1 = batalha.startup_1
    startup2 = batalha.startup_2

    eventos = {
        'pitch': 6,
        'bugs': -4,
        'tracoes': 3,
        'investidor_irritado': -6,
        'fake_news': -8
    }

    if request.method == 'POST':
        evento1 = request.POST.getlist('eventos_startup_1')
        evento2 = request.POST.getlist('eventos_startup_2')

        pontuacao1 = 0
        pontuacao2 = 0

        # Registro dos eventos e cálculo da pontuação para startup 1
        for ev in evento1:
            pontuacao1 += eventos.get(ev, 0)
            if ev == 'bugs':
                startup1.bugs += 1
            elif ev == 'fake_news':
                startup1.fake_news += 1
            elif ev == 'tracoes':
                startup1.tracoes += 1
            elif ev == 'investidor_irritado':
                startup1.investidores_irritados += 1

        # Registro dos eventos e cálculo da pontuação para startup 2
        for ev in evento2:
            pontuacao2 += eventos.get(ev, 0)
            if ev == 'bugs':
                startup2.bugs += 1
            elif ev == 'fake_news':
                startup2.fake_news += 1
            elif ev == 'tracoes':
                startup2.tracoes += 1
            elif ev == 'investidor_irritado':
                startup2.investidores_irritados += 1

        startup1.pontos += pontuacao1
        startup2.pontos += pontuacao2

        # Empate = Shark Fight
        if startup1.pontos == startup2.pontos:
            if random.choice([True, False]):
                startup1.pontos += 2
            else:
                startup2.pontos += 2

        vencedor = startup1 if startup1.pontos > startup2.pontos else startup2
        vencedor.pontos += 30

        startup1.save()
        startup2.save()

        # Marcar a batalha como concluída
        batalha.concluida = True
        batalha.save()

        proxima_acao = avancar_fase_ou_finalizar()

        if proxima_acao:
            return proxima_acao

        # Caso ainda haja batalhas para administrar, não redirecionar
        return redirect('batalhas')  # Continua redirecionando para batalhas se a rodada não terminou

    return render(request, 'torneio/administrar.html', {
        'batalha': batalha,
        'eventos': eventos
    })

def campea(request):
    campea = Startup.objects.order_by('-pontos').first()
    return render(request, 'torneio/campea.html', {'campea': campea})


def historico(request, start_id):
    startup = Startup.objects.get(id=start_id)
    batalhas = Batalha.objects.filter(startup_1=startup) | Batalha.objects.filter(startup_2=startup)
    return render(request, 'torneio/historico.html', {'startup': startup, 'batalhas': batalhas})


def reiniciar_sistema(request):
    Startup.objects.all().delete()
    Batalha.objects.all().delete()
    Torneio.objects.all().delete()
    return redirect(f"{reverse('index')}?sucesso=Sistema reiniciado com sucesso.")

def exportar_dados(request):
    # Verifica se o torneio foi finalizado
    if Batalha.objects.filter(concluida=False).exists():
        return redirect('/?erro=O torneio ainda não foi finalizado. Não é possível exportar os dados.')

    # Obtém os dados das startups
    startups = Startup.objects.all().order_by('-pontos')

    # Checa o parâmetro de formato no URL
    formato = request.GET.get('formato', '')

    if formato == 'json':
        # Gera o arquivo JSON
        dados = []
        for startup in startups:
            dados.append({
                'Nome': startup.nome,
                'Slogan': startup.slogan,
                'Ano de Fundação': startup.ano_fundacao,
                'Pontos': startup.pontos,
                'Pitchs': startup.pitchs,
                'Bugs': startup.bugs,
                'Trações': startup.tracoes,
                'Investidores Irritados': startup.investidores_irritados,
                'Penalidades': startup.penalidades
            })

        # Resetando os dados do torneio
        Batalha.objects.all().delete()
        Startup.objects.update(pontos=0, pitchs=0, bugs=0, tracoes=0, investidores_irritados=0, penalidades=0)

        return JsonResponse(dados, safe=False)

    elif formato == 'csv':
        # Gera o arquivo CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="resultados_torneio.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ['Nome', 'Slogan', 'Ano de Fundação', 'Pontos', 'pitchs', 'Bugs', 'Trações', 'Investidores Irritados',
             'Penalidades'])

        for startup in startups:
            writer.writerow(
                [startup.nome, startup.slogan, startup.ano_fundacao, startup.pontos, startup.pitchs, startup.bugs,
                 startup.tracoes, startup.investidores_irritados, startup.penalidades])

        # Resetando os dados do torneio
        Batalha.objects.all().delete()
        Startup.objects.update(pontos=0, pitchs=0, bugs=0, tracoes=0, investidores_irritados=0, penalidades=0)

        return response
    else:
        # Se o formato não for especificado ou for inválido
        return redirect('/?erro=Formato de exportação inválido.')


