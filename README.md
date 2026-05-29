# Extrator de Documentos do BID (Banco Interamericano de Desenvolvimento)

Este projeto automatiza a extração de links e o download de documentos públicos do portal de projetos do BID (IADB).

Ele utiliza o **Playwright** configurado em modo oculto disfarçado (*stealth headless*) para simular navegação humana e contornar bloqueios de segurança do portal, salvando os arquivos de forma incremental (sem repetir downloads já concluídos) e atualizando o relatório de links em tempo real.

---

# 🚀 Como Instalar e Configurar

## 1. Instalar as Dependências do Python

Certifique-se de ter o Python instalado.

No terminal, navegue até a pasta do projeto e instale as bibliotecas necessárias listadas no arquivo `requirements.txt`:

```bash id="bd3k19"
pip install -r requirements.txt
```

---

## 2. Instalar os Navegadores do Playwright

Após instalar as bibliotecas, rode o comando abaixo no terminal:

```bash id="2t7mqa"
playwright install chromium
```

---

# 📊 Como Preencher o Modelo de Entrada 

O script lê uma planilha Excel para saber quais projetos deve escanear.

Crie um arquivo chamado `projetos_exemplo.xlsx` na raiz do projeto. No caso eu usei projetos_exemplo.xlsx , você pode por o nome que quiser só trocar no main.py nome do arquivo.

Ele precisa ter, obrigatoriamente, uma coluna chamada:

```text id="l9s0pw"
Operation Number
```

Os códigos das operações devem ser inseridos logo abaixo.

## Exemplo de Estrutura da Planilha

| Operation Number |
| ---------------- |
| BR-L1612         |
| HA0078           |
| CO-T1711         |

Você pode adicionar outras colunas se quiser. O script ignora automaticamente colunas extras.

> ⚠️ Atenção:
> O nome da coluna deve ser exatamente `Operation Number` (respeitando maiúsculas, minúsculas e espaços).

O script remove linhas vazias ou duplicadas automaticamente.

---

# ⚙️ Estrutura do `main.py`

O arquivo `main.py` é responsável por inicializar o coletor e iniciar o processo de extração dos documentos.

## Exemplo do Arquivo

```python id="x5j8nc"
from projetos import BID

# input_file:
# Arquivo Excel contendo a coluna "Operation Number"
# com os números das operações a serem processadas.

# base_download_path:
# Diretório onde os documentos baixados serão armazenados,
# organizados automaticamente por projeto.

# output_csv:
# Nome do arquivo CSV onde os links encontrados serão salvos.

# headless:
# Parâmetro booleano que define se o navegador será executado
# em modo oculto (sem interface gráfica) ou visível.
#
# True  = Navegador oculto (mais rápido e silencioso)
# False = Navegador visível (útil para debug)

coletor = BID(
    input_file="projetos_exemplo.xlsx",
    base_download_path="./documentos_baixados",
    output_csv="resultado_links_documentos.csv",
    headless=True
)

coletor.obter_documentos()
```

---

## 🔍 Explicação dos Parâmetros

| Parâmetro            | Descrição                                                       |
| -------------------- | --------------------------------------------------------------- |
| `input_file`         | Caminho do arquivo Excel contendo os códigos das operações      |
| `base_download_path` | Pasta onde os documentos baixados serão armazenados             |
| `output_csv`         | Nome do CSV final contendo todos os links encontrados           |
| `headless`           | Define se o navegador roda oculto (`True`) ou visível (`False`) |

---

# 🏃‍♂️ Como Executar

Com o arquivo `projetos.xlsx` preenchido na raiz, basta rodar o script principal:

```bash id="i1zr9b"
python main.py
```

---

## ▶️ Iniciando a Coleta

A linha abaixo inicia todo o processo de navegação, extração dos links e download dos documentos:

```python id="3d1o4p"
coletor.obter_documentos()
```

Durante a execução, o sistema:

* Navega automaticamente pelos projetos do BID
* Identifica os documentos públicos disponíveis
* Faz download apenas de arquivos ainda não baixados
* Atualiza o CSV incrementalmente
* Registra falhas no `log_erros.csv`
* Mantém a estrutura organizada por projeto

---

# 📂 Arquivos Gerados pelo Script

Enquanto o robô trabalha em silêncio (atualizando o progresso em apenas uma linha no terminal para não poluir a tela), ele gera as seguintes estruturas:

---

## `documentos_baixados`

Pasta principal contendo subpastas organizadas pelo código de cada projeto.

Dentro de cada subpasta estarão os respectivos arquivos:

* `.pdf`
* `.docx`
* `.xlsx`
* etc.

---

## `resultado_links_documentos.csv`

Relatório final gerado no formato longo (*Long Format*).

Este arquivo é salvo incrementalmente, projeto por projeto.

Se a execução for interrompida, o progresso continuará salvo aqui.

---

## `log_erros.csv`

Caso algum link falhe, dê timeout ou retorne erro HTTP, o script não interrompe a execução.

O arquivo problemático é ignorado e a falha é registrada detalhadamente neste log para análise posterior.
