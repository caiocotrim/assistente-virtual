import re
from pathlib import Path

import fitz
from PIL import Image

# ==============================
# Caminhos
# ==============================

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[2]

DADOS_BRUTOS = ROOT / "base-de-dados" / "dados-brutos"

# ==============================
# Configurações gerais
# ==============================

ZOOM = 3  # fator de ampliação usado no fitz.Matrix ao renderizar páginas
MARGEM_PT = 8  # margem (em pontos, escala do PDF) para não cortar rente ao texto


def renderiza_pagina_inteira(page, zoom=ZOOM):
    """Renderiza a página inteira como uma imagem PIL, sem recortes."""

    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)

    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def salva_imagem(img, pasta_saida, nome_arquivo):
    nome_arquivo = re.sub(r'[\\/*?:"<>|]', "", nome_arquivo)
    img.save(pasta_saida / f"{nome_arquivo}.jpg", quality=95)


# ==================================================================
# BSI — várias disciplinas por página e ementas que atravessam
# quebras de página. Pipeline específico (o mais elaborado).
# ==================================================================

# Textos fixos que se repetem em toda página (cabeçalho institucional
# com logo/campus e rodapé com numeração) e que devem ser excluídos do
# recorte sempre que uma ementa atravessa uma quebra de página.
BSI_MARCADOR_CABECALHO_PAGINA = "Campus Vitória da Conquista"
BSI_MARCADOR_RODAPE = "Projeto Pedagógico de Curso"

# Textos que compõem o cabeçalho da mini-tabela de cada disciplina
# (ficam impressos ACIMA da linha do código, mas pertencem a ela)
BSI_MARCADORES_CABECALHO_DISCIPLINA = {
    "CÓDIGO",
    "COMPONENTE CURRICULAR",
    "CARGA HORÁRIA",
    "Teórica",
    "Prática",
    "Extensão",
}

bsi_regex_codigo = re.compile(r"^[A-Z]{3}\d{2}$")


def bsi_extrai_linhas_com_posicao(page):
    """
    Retorna as linhas de texto da página como lista de dicionários
    {"texto": str, "y": float}, ordenadas de cima para baixo.
    """

    linhas = []

    dados = page.get_text("dict")

    for bloco in dados["blocks"]:

        if bloco.get("type") != 0:  # ignora blocos que não são texto
            continue

        for linha in bloco["lines"]:

            texto = "".join(
                span["text"] for span in linha["spans"]
            ).strip()

            if not texto:
                continue

            linhas.append(
                {
                    "texto": texto,
                    "y": linha["bbox"][1],
                }
            )

    linhas.sort(key=lambda l: l["y"])

    return linhas


def bsi_acha_topo_real(linhas, indice_codigo):
    """
    Procura, a partir da linha do código da disciplina, olhando para
    trás (na mesma página), o cabeçalho da mini-tabela ("CÓDIGO",
    "CARGA HORÁRIA", "Teórica/Prática/Extensão" e a linha com os
    valores de carga horária), que pertence visualmente a esta
    disciplina mas é impresso ACIMA da linha do código.
    """

    y_topo = linhas[indice_codigo]["y"]

    for k in range(indice_codigo - 1, max(-1, indice_codigo - 8), -1):

        texto = linhas[k]["texto"]

        eh_cabecalho = (
            texto in BSI_MARCADORES_CABECALHO_DISCIPLINA
            or "horas" in texto.lower()
            or re.fullmatch(r"[\d\s\-–/]+", texto) is not None
        )

        if not eh_cabecalho:
            break

        y_topo = linhas[k]["y"]

    return y_topo


def bsi_faixa_util_da_pagina(page):
    """
    Retorna (topo, rodape): a faixa vertical (em pontos) da página
    que exclui o cabeçalho fixo (logo + campus) e o rodapé (numeração
    de página) — elementos que se repetem em toda página e não
    pertencem a nenhuma ementa específica.
    """

    topo = 0.0
    rodape = page.rect.height

    for rect in page.search_for(BSI_MARCADOR_CABECALHO_PAGINA):
        topo = max(topo, rect.y1)

    for rect in page.search_for(BSI_MARCADOR_RODAPE):
        rodape = min(rodape, rect.y0)

    return topo, rodape


def bsi_localiza_disciplinas(doc):
    """
    Varre o documento inteiro e retorna a lista de disciplinas
    encontradas, cada uma com código, nome, página/posição de início
    e (depois de calculado) página/posição de fim.
    """

    disciplinas = []

    for numero_pagina in range(len(doc)):

        texto_pagina = doc[numero_pagina].get_text()

        if (
            "CÓDIGO" not in texto_pagina
            or "COMPONENTE CURRICULAR" not in texto_pagina
            or "EMENTA" not in texto_pagina
        ):
            continue

        linhas = bsi_extrai_linhas_com_posicao(doc[numero_pagina])

        for i, linha in enumerate(linhas):

            if not bsi_regex_codigo.fullmatch(linha["texto"]):
                continue

            codigo = linha["texto"]
            nome = None

            for j in range(i + 1, min(i + 8, len(linhas))):

                candidato = linhas[j]["texto"]

                if candidato in ("CRÉDITOS", "PRÉ-REQUISITOS", "EMENTA"):
                    break

                if bsi_regex_codigo.fullmatch(candidato):
                    continue

                if "horas" in candidato.lower():
                    continue

                if candidato.isdigit():
                    continue

                nome = candidato
                break

            if codigo and nome:

                disciplinas.append(
                    {
                        "codigo": codigo,
                        "nome": nome,
                        "pagina_inicio": numero_pagina,
                        "y_inicio": bsi_acha_topo_real(linhas, i),
                    }
                )

    for i in range(len(disciplinas)):

        if i < len(disciplinas) - 1:
            disciplinas[i]["pagina_fim"] = disciplinas[i + 1]["pagina_inicio"]
            disciplinas[i]["y_fim"] = disciplinas[i + 1]["y_inicio"]
        else:
            disciplinas[i]["pagina_fim"] = len(doc) - 1
            disciplinas[i]["y_fim"] = None

    return disciplinas


def bsi_exporta_disciplina(doc, disc, pasta_saida):

    imagens = []

    for pagina in range(disc["pagina_inicio"], disc["pagina_fim"] + 1):

        page = doc[pagina]

        topo_pagina, rodape_pagina = bsi_faixa_util_da_pagina(page)

        img = renderiza_pagina_inteira(page)

        if pagina == disc["pagina_inicio"]:
            topo = max(0, int((disc["y_inicio"] - MARGEM_PT) * ZOOM))
        else:
            topo = int(topo_pagina * ZOOM)

        if pagina == disc["pagina_fim"] and disc["y_fim"] is not None:
            base = min(img.height, int((disc["y_fim"] - MARGEM_PT) * ZOOM))
        else:
            base = int(rodape_pagina * ZOOM)

        base = max(base, topo + 1)

        img = img.crop((0, topo, img.width, base))
        imagens.append(img)

    largura = max(i.width for i in imagens)
    altura = sum(i.height for i in imagens)

    final = Image.new("RGB", (largura, altura), "white")

    y = 0
    for img in imagens:
        final.paste(img, (0, y))
        y += img.height

    salva_imagem(final, pasta_saida, f'{disc["codigo"]}_{disc["nome"]}')


def bsi_processa_pdf(caminho_pdf, pasta_saida):

    pasta_saida.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(caminho_pdf)

    disciplinas = bsi_localiza_disciplinas(doc)

    for disc in disciplinas:
        print(f'  {disc["codigo"]} - {disc["nome"]}')
        bsi_exporta_disciplina(doc, disc, pasta_saida)

    doc.close()

    return len(disciplinas)


# ==================================================================
# Civil, Elétrica, Química e Ambiental — cada disciplina ocupa
# exatamente UMA página do PDF (formato bem mais simples: sem
# disciplinas dividindo página, sem ementa atravessando página).
# Cada curso tem seu próprio jeito de reconhecer a página e extrair
# o nome da disciplina (nenhum desses PPCs usa código de forma
# confiável — o nome é a chave).
# ==================================================================

def extrai_palavras(page):
    """fitz retorna tuplas (x0, y0, x1, y1, texto, bloco, linha, palavra)."""
    return page.get_text("words")


# ---- Elétrica: nome fica entre "COMPONENTE CURRICULAR" e "CARGA HORÁRIA" ----

def eh_pagina_eletrica(texto):
    return (
        "CÓDIGO" in texto
        and "COMPONENTE CURRICULAR" in texto
        and "EMENTA" in texto
    )

def nome_eletrica(page, texto):

    blocos = page.get_text("dict")["blocks"]

    linhas = []

    for bloco in blocos:

        if bloco.get("type") != 0:
            continue

        for linha in bloco["lines"]:

            t = "".join(
                span["text"]
                for span in linha["spans"]
            ).strip()

            if not t:
                continue

            linhas.append(
                {
                    "texto": t,
                    "y": linha["bbox"][1]
                }
            )

    linhas.sort(key=lambda x: x["y"])

    for i, linha in enumerate(linhas):

        if "COMPONENTE CURRICULAR" in linha["texto"]:

            for j in range(i + 1, min(i + 8, len(linhas))):

                t = linhas[j]["texto"].strip()

                if (
                    "PRÉ-REQUISITOS" in t
                    or "CO-REQUISITOS" in t
                    or "EMENTA" in t
                ):
                    break

                if t == "":
                    continue

                if t.isdigit():
                    continue

                if "CRÉDITOS" in t:
                    continue

                return t

    return None

# ---- Química: nome fica à esquerda, entre "Carga Horária (h)" e "Período:" ----

def eh_pagina_quimica(texto):
    return (
        "Carga Horária (h)" in texto
        and "Pré-Requisito:" in texto
        and "Ementa:" in texto
    )


def nome_quimica(page, texto):
    palavras = extrai_palavras(page)

    top_carga = top_periodo = None

    for x0, y0, x1, y1, palavra, *_ in palavras:
        if palavra == "Horária" and top_carga is None:
            top_carga = y0
        if palavra == "Período:" and top_periodo is None:
            top_periodo = y0

    if top_carga is None or top_periodo is None:
        return None

    candidatos = [
        (y0, x0, palavra)
        for x0, y0, x1, y1, palavra, *_ in palavras
        if top_carga - 1 < y0 < top_periodo - 1 and x0 < 270
    ]
    candidatos.sort(key=lambda t: (round(t[0]), t[1]))

    return " ".join(t[2] for t in candidatos).strip()


# ---- Civil: nome fica na mesma linha da palavra "CARGA" (à esquerda dela) ----

def eh_pagina_civil(texto):
    return "EMENTA:" in texto and "CARGA HORÁRIA" in texto


def nome_civil(page, texto):
    palavras = extrai_palavras(page)

    top_carga = None

    for x0, y0, x1, y1, palavra, *_ in palavras:
        if palavra == "CARGA":
            top_carga = y0
            break

    if top_carga is None:
        return None

    candidatos = [
        (x0, palavra)
        for x0, y0, x1, y1, palavra, *_ in palavras
        if abs(y0 - top_carga) < 3 and x0 < 300
    ]
    candidatos.sort(key=lambda t: t[0])

    return " ".join(t[1] for t in candidatos).strip()


# ---- Ambiental: nome vem de um subtítulo tipo "14.1.1 Nome da Disciplina" ----

REGEX_SUBSECAO_AMBIENTAL = re.compile(r"^\d+\.\d+\.\d+\s+(.+)$")


def eh_pagina_ambiental(texto):
    if "Ementa:" not in texto:
        return False
    return any(
        REGEX_SUBSECAO_AMBIENTAL.match(linha.strip())
        for linha in texto.splitlines()
    )


def nome_ambiental(page, texto):
    for linha in texto.splitlines():
        m = REGEX_SUBSECAO_AMBIENTAL.match(linha.strip())
        if m:
            return m.group(1).strip()
    return None


# Mapa: nome da pasta do curso -> (função que reconhece a página,
# função que extrai o nome da disciplina daquela página)
CONFIG_PAGINA_UNICA = {
    "eletrica": (eh_pagina_eletrica, nome_eletrica),
    "quimica": (eh_pagina_quimica, nome_quimica),
    "civil": (eh_pagina_civil, nome_civil),
    "ambiental": (eh_pagina_ambiental, nome_ambiental),
}


def processa_pdf_pagina_unica(caminho_pdf, pasta_saida, eh_pagina, extrai_nome):
    """
    Processa um PPC em que cada disciplina ocupa exatamente uma
    página do PDF. Muito mais simples que o pipeline do BSI: não há
    recorte, cada página vira uma imagem inteira.
    """

    pasta_saida.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(caminho_pdf)

    total = 0

    for numero_pagina in range(len(doc)):

        page = doc[numero_pagina]
        texto = page.get_text()

        if not eh_pagina(texto):
            continue

        nome = extrai_nome(page, texto)

        if not nome:
            print(
                f"  [aviso] pág {numero_pagina+1}: reconhecida como "
                f"disciplina, mas não consegui extrair o nome"
            )
            continue

        img = renderiza_pagina_inteira(page)
        nome_arquivo = f"{numero_pagina+1:03d}_{nome}"
        salva_imagem(img, pasta_saida, nome_arquivo)

        print(f"  pág {numero_pagina+1}: {nome}")
        total += 1

    doc.close()

    return total


# ==============================
# Execução: BSI + demais cursos
# ==============================

if __name__ == "__main__":

    resumo = {}

    # ---- BSI: pipeline específico ----
    pasta_bsi = DADOS_BRUTOS / "bsi"
    pdf_bsi = pasta_bsi / "ppc_bsi.pdf"
    pasta_saida_bsi = pasta_bsi / "ementas"

    print("\n=== bsi ===")
    if pdf_bsi.exists():
        total = bsi_processa_pdf(pdf_bsi, pasta_saida_bsi)
        resumo["bsi"] = total
        print(f"  {total} disciplinas exportadas.")
    else:
        print(f"  [aviso] PDF não encontrado: {pdf_bsi}")

    # ---- demais cursos: uma disciplina por página ----
    for curso, (eh_pagina, extrai_nome) in CONFIG_PAGINA_UNICA.items():

        pasta_curso = DADOS_BRUTOS / curso
        caminho_pdf = pasta_curso / f"ppc_{curso}.pdf"
        pasta_saida = pasta_curso / "ementas"

        print(f"\n=== {curso} ===")

        if not caminho_pdf.exists():
            print(f"  [aviso] PDF não encontrado: {caminho_pdf}")
            continue

        total = processa_pdf_pagina_unica(
            caminho_pdf, pasta_saida, eh_pagina, extrai_nome
        )
        resumo[curso] = total

        print(f"  {total} disciplinas exportadas.")

    print("\n==============================")
    print("Resumo geral:")
    for curso, total in resumo.items():
        print(f"  {curso}: {total} disciplinas")
    print("==============================")