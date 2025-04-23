from django.shortcuts import render

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
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages


def torneio_em_andamento():
    return Batalha.objects.exists() and Batalha.objects.filter(concluida=False).exists()

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

    torneio = Torneio.objects.last()
    if torneio and torneio.finalizado:
        return redirect(f"{reverse('index')}?erro=O torneio foi finalizado. Reinicie o sistema para cadastrar novas startups.")


def deletar_startup(request, id):
    if torneio_em_andamento():
        return redirect('cadastro')  # ou mostrar mensagem de erro
    startup = get_object_or_404(Startup, id=id)
    startup.delete()
    return redirect('cadastro')


# def ranking(request):
#     torneio_iniciado = Batalha.objects.exists()
#     torneio_finalizado = not Batalha.objects.filter(concluida=False).exists()
#
#     if not torneio_iniciado:
#         return render(request, 'torneio/ranking.html', {
#             'ranking_disponivel': False
#         })
#
#     startups = Startup.objects.all().order_by('-pontos')
#
#     return render(request, 'torneio/ranking.html', {
#         'ranking_disponivel': True,
#         'torneio_finalizado': torneio_finalizado,
#         'startups': startups
#     })

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

    torneio = Torneio.objects.last()
    if torneio and torneio.finalizado:
        return redirect(f"{reverse('index')}?erro=O torneio já foi finalizado. Reinicie o sistema para iniciar um novo.")


def batalhas(request):
    batalhas = Batalha.objects.all().order_by('id')
    return render(request, 'torneio/batalhas.html', {'batalhas': batalhas})


def avancar_fase_ou_finalizar():
    if Batalha.objects.filter(concluida=False).exists():
        return None  # Espera todas as batalhas da rodada atual finalizarem

    torneio = Torneio.objects.filter(em_andamento=True).last()
    if not torneio:
        return None

    # Recuperar as batalhas mais recentes, ou seja, a rodada que acabou agora
    batalhas_recentes = []
    startups_vistas = set()

    for b in Batalha.objects.filter(concluida=True).order_by('-id'):
        ids = {b.startup_1_id, b.startup_2_id}
        if not ids.isdisjoint(startups_vistas):
            break  # Achou batalha de rodada anterior
        batalhas_recentes.append(b)
        startups_vistas.update(ids)

    # Pegamos os vencedores da rodada que acabou de terminar
    vencedores_ids = [b.vencedor_id for b in batalhas_recentes]
    if len(set(vencedores_ids)) == 1:
        # Só restou uma startup
        torneio.em_andamento = False
        torneio.finalizado = True
        torneio.save()
        return redirect('campea')

    # Criar a próxima rodada
    startups_vivas = list(Startup.objects.filter(id__in=vencedores_ids))
    random.shuffle(startups_vivas)

    for i in range(0, len(startups_vivas), 2):
        Batalha.objects.create(
            startup_1=startups_vivas[i],
            startup_2=startups_vivas[i + 1]
        )

    return redirect('batalhas')

# def administrar_batalha(request, batalha_id):
#     batalha = get_object_or_404(Batalha, id=batalha_id)
#     startup1 = batalha.startup_1
#     startup2 = batalha.startup_2
#
#     eventos = {
#         'pitch': 6,
#         'bugs': -4,
#         'tracoes': 3,
#         'investidor_irritado': -6,
#         'fake_news': -8
#     }
#
#     contexto = {
#         'batalha': batalha,
#         'eventos': eventos,
#     }
#
#     if request.method == 'POST':
#         evento1 = request.POST.getlist('eventos_startup_1')
#         evento2 = request.POST.getlist('eventos_startup_2')
#
#         def processa_eventos(startup, eventos_lista):
#             pontos = 0
#             eventos_ocorridos = []
#             for ev in eventos_lista:
#                 pontos += eventos.get(ev, 0)
#                 eventos_ocorridos.append(ev)
#                 if ev == 'bugs':
#                     startup.bugs += 1
#                 elif ev == 'fake_news':
#                     startup.fake_news += 1
#                 elif ev == 'tracoes':
#                     startup.tracoes += 1
#                 elif ev == 'investidor_irritado':
#                     startup.investidores_irritados += 1
#             return pontos, eventos_ocorridos
#
#         pontuacao1, eventos_startup_1 = processa_eventos(startup1, evento1)
#         pontuacao2, eventos_startup_2 = processa_eventos(startup2, evento2)
#
#         startup1.pontos += pontuacao1
#         startup2.pontos += pontuacao2
#
#         empate = pontuacao1 == pontuacao2
#         shark_fight = False
#
#         if empate:
#             shark_fight = True
#             bonus = 2
#             if random.choice([True, False]):
#                 pontuacao1 += bonus
#                 startup1.pontos += bonus
#             else:
#                 pontuacao2 += bonus
#                 startup2.pontos += bonus
#
#         vencedor = startup1 if pontuacao1 > pontuacao2 else startup2
#         vencedor.pontos += 30
#
#         startup1.save()
#         startup2.save()
#
#         batalha.concluida = True
#         batalha.vencedor = vencedor
#         batalha.eventos_startup_1 = eventos_startup_1
#         batalha.eventos_startup_2 = eventos_startup_2
#         batalha.shark_fight = shark_fight
#         batalha.save()
#
#         proxima_acao = avancar_fase_ou_finalizar()
#
#         return proxima_acao or redirect('batalhas')
#
#     return render(request, 'torneio/administrar.html', contexto)

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

    contexto = {
        'batalha': batalha,
        'eventos': eventos,
    }

    if request.method == 'POST':
        evento1 = request.POST.getlist('eventos_startup_1')
        evento2 = request.POST.getlist('eventos_startup_2')

        def processa_eventos(startup, eventos_lista):
            pontos = 0
            eventos_ocorridos = []
            for ev in eventos_lista:
                pontos += eventos.get(ev, 0)
                eventos_ocorridos.append(ev)
                if ev == 'bugs':
                    startup.bugs += 1
                elif ev == 'fake_news':
                    startup.fake_news += 1
                elif ev == 'tracoes':
                    startup.tracoes += 1
                elif ev == 'investidor_irritado':
                    startup.investidores_irritados += 1
                elif ev == 'pitch':
                    startup.pitchs += 1
            return pontos, eventos_ocorridos

        pontuacao1, eventos_startup_1 = processa_eventos(startup1, evento1)
        pontuacao2, eventos_startup_2 = processa_eventos(startup2, evento2)

        startup1.pontos += pontuacao1
        startup2.pontos += pontuacao2

        empate = pontuacao1 == pontuacao2
        shark_fight = False

        if empate:
            shark_fight = True
            bonus = 2
            if random.choice([True, False]):
                pontuacao1 += bonus
                startup1.pontos += bonus
            else:
                pontuacao2 += bonus
                startup2.pontos += bonus

        vencedor = startup1 if pontuacao1 > pontuacao2 else startup2
        vencedor.pontos += 30

        # Salva as mudanças de eventos e pontuação
        startup1.save()
        startup2.save()

        batalha.concluida = True
        batalha.vencedor = vencedor
        batalha.eventos_startup_1 = eventos_startup_1
        batalha.eventos_startup_2 = eventos_startup_2
        batalha.shark_fight = shark_fight
        batalha.save()

        proxima_acao = avancar_fase_ou_finalizar()

        return proxima_acao or redirect('batalhas')

    return render(request, 'torneio/administrar.html', contexto)


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
    if Batalha.objects.filter(concluida=False).exists():
        messages.error(request, "O torneio ainda não foi finalizado. Não é possível exportar os dados.")
        return redirect('index')

    startups = Startup.objects.all().order_by('-pontos')
    formato = request.GET.get('formato', '')

    if formato == 'json':
        dados = []
        for s in startups:
            dados.append({
                'Nome': s.nome,
                'Slogan': s.slogan,
                'Ano de Fundação': s.ano_fundacao,
                'Pontos': s.pontos,
                'Pitchs': s.pitchs,
                'Bugs': s.bugs,
                'Trações': s.tracoes,
                'Investidores Irritados': s.investidores_irritados,
                'Penalidades': s.penalidades
            })

        response = HttpResponse(
            json.dumps(dados, cls=DjangoJSONEncoder, ensure_ascii=False, indent=4),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="resultados_torneio.json"'
        return response

    elif formato == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="resultados_torneio.csv"'

        writer = csv.writer(response)
        writer.writerow(['Nome', 'Slogan', 'Ano de Fundação', 'Pontos', 'Pitchs', 'Bugs', 'Trações', 'Investidores Irritados', 'Penalidades'])

        for s in startups:
            writer.writerow([s.nome, s.slogan, s.ano_fundacao, s.pontos, s.pitchs, s.bugs, s.tracoes, s.investidores_irritados, s.penalidades])

        return response

    else:
        messages.error(request, "Formato de exportação inválido.")
        return redirect('index')

