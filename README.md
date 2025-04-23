# Startup Rush - Sistema de Torneio de Startups

## Descrição

O **Startup Rush** é um sistema baseado em torneio para startups, onde diferentes equipes competem entre si em um campeonato. Cada startup possui um **slogan** e **pontos**, e o sistema permite que as equipes batalhem entre si até que uma startup seja coroada campeã. O sistema conta com funcionalidades como cadastro de startups, administração de batalhas e exibição do ranking final.

## Funcionalidades

- **Cadastro de Startups**: Permite registrar novas startups no sistema, com informações como nome, slogan e ano de fundação.
- **Início de Torneio**: Após o cadastro das startups, o torneio pode ser iniciado, gerando automaticamente batalhas entre as equipes.
- **Administração de Batalhas**: As batalhas podem ser visualizadas em tempo real. As startups competem entre si, e a pontuação é registrada.
- **Ranking de Startups**: Exibe o ranking das startups com base na pontuação obtida durante o torneio.
- **Campeão**: Após o término das batalhas, a startup vencedora é exibida como campeã, com a opção de reiniciar o torneio.
- **Reiniciar o Sistema**: Permite reiniciar o torneio e limpar todas as informações, caso o usuário deseje.

## Fluxo do Sistema

1. **Cadastro de Startups**: As startups podem ser registradas através da página de cadastro. O sistema verifica se o nome da startup já está cadastrado e limita o número de startups a um máximo de 8.
2. **Início do Torneio**: O torneio pode ser iniciado quando houver de 4 a 8 startups cadastradas. Se o número de startups for inválido, o sistema mostrará uma mensagem de erro.
3. **Batalhas**: Quando o torneio é iniciado, o sistema cria batalhas entre as startups e acompanha a pontuação de cada uma.
4. **Ranking**: As startups podem ser visualizadas no ranking geral, que exibe a posição das startups com base nos pontos acumulados.
5. **Campeão**: Após o término das batalhas, o sistema exibe a startup campeã e oferece a opção de reiniciar o sistema.
6. **Reiniciar o Sistema**: Ao reiniciar, todas as informações (startups e torneios) são apagadas, permitindo que o sistema comece do zero.

## Como Rodar o Sistema

### Requisitos

- **Python** (>= 3.8)
- **Django** (>= 5.0)
- **Banco de Dados**: SQLite (configuração padrão) ou qualquer outro banco suportado pelo Django

### Passos para Instalar e Rodar

1. **Clonar o repositório**:
   ```bash
   git clone https://github.com/MarianaLuisa/startup.git
   cd startup_rush
   ```

2. **Criar um ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Para Linux/Mac
   venv\Scripts\activate     # Para Windows
   ```

3. **Instalar as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Aplicar as migrações do banco de dados**:
   ```bash
   python manage.py migrate
   ```

5. **Rodar o servidor local**:
   ```bash
   python manage.py runserver
   ```

6. **Acessar o sistema**:
   - Abra o navegador e acesse: `http://127.0.0.1:8000`


## Deploy

   Sistema online:
   [Startup Rush no Render](https://startup-rush.onrender.com)


### Como Usar

1. **Cadastrar Startups**: Acesse a página de cadastro, informe o nome, slogan e ano de fundação da startup e clique em "Cadastrar".
2. **Iniciar Torneio**: Depois de cadastrar de 4 a 8 startups, clique no botão "Iniciar Torneio" para começar a competição.
3. **Visualizar Batalhas**: As batalhas entre as startups serão exibidas na página de batalhas. Acompanhe o andamento do torneio.
4. **Visualizar Ranking**: Consulte o ranking final das startups para ver as equipes mais pontuadas.
5. **Reiniciar Sistema**: Caso deseje reiniciar o torneio, você pode apagar todos os dados de startups e resultados através da opção "Reiniciar Sistema".

## Estrutura do Projeto

```
startup_rush/
│
├── torneio/                # Contém as views, models e templates do torneio
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   └── ...
│
├── startup_rush/
│   ├── settings.py        # Configurações do Django
│   ├── urls.py            # URLs principais do projeto
│   └── wsgi.py
│
└── manage.py              # Script para rodar o servidor
```

## Tecnologias Usadas

- **Django**: Framework web usado para desenvolver o sistema.
- **Tailwind CSS**: Framework CSS para estilizar as páginas de maneira responsiva e moderna.
- **SQLite**: Banco de dados padrão usado para armazenar informações das startups, torneios e batalhas.
