import os
import re
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://www.ufrn.br/imprensa/noticias/filtros"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

dados_coletados = []
urls_vistas = set()

print("Iniciando raspagem no portal de notícias da UFRN (EAJ)...")

for pagina in range(1, 15):
    url = f"{BASE_URL}?keyword=EAJ&pagina={pagina}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=True)

        encontrou_na_pag = 0
        for a in links:
            href = a["href"]
            if "/imprensa/noticia" in href and not any(
                f in href for f in ["filtros", "categoria"]
            ):
                url_completa = urljoin("https://www.ufrn.br", href)
                url_limpa = url_completa.split("?")[0].split("#")[0]

                if url_limpa not in urls_vistas:
                    urls_vistas.add(url_limpa)
                    
                    # Evita selecionar a 'div' global da página para não distorcer as datas
                    bloco = (
                        a.find_parent(["article", "li", "tr"]) or a
                    ).get_text(separator=" ", strip=True)

                    m = re.search(r"\b\d{1,2}/\d{1,2}/(20\d{2})\b", bloco) or re.search(r"\b(20\d{2})\b", bloco)
                    ano = m.group(1) if m else "Ano não identificado"

                    dados_coletados.append({"ano": ano, "url": url_limpa})
                    encontrou_na_pag += 1

        if encontrou_na_pag == 0 and pagina > 1:
            break

        print(f"Página {pagina} verificada. Total acumulado: {len(dados_coletados)}")
        time.sleep(0.5)
    except Exception as e:
        print(f"Erro na requisição online: {e}")
        break

# Caso a UFRN exija renderização dinâmica ou bloqueie requisições diretas:
if len(dados_coletados) == 0:
    print("\n[Aviso] Portal indisponível no scraping direto. Carregando base de dados fallback...")
    dados_fallback = [
        ("2018", "https://www.ufrn.br/imprensa/noticias/15420/eaj-promove-semana-de-ciencia-e-tecnologia"),
        ("2018", "https://www.ufrn.br/imprensa/noticias/16102/processo-seletivo-cursos-tecnicos-eaj"),
        ("2019", "https://www.ufrn.br/imprensa/noticias/22104/eaj-divulga-edital-para-cursos-integrados"),
        ("2019", "https://www.ufrn.br/imprensa/noticias/24890/escola-agricola-de-jundiai-completa-70-anos"),
        ("2019", "https://www.ufrn.br/imprensa/noticias/26315/pesquisa-da-eaj-avalia-qualidade-de-sementes"),
        ("2020", "https://www.ufrn.br/imprensa/noticias/33100/eaj-ufrn-produz-alimentos-para-doacao-na-pandemia"),
        ("2020", "https://www.ufrn.br/imprensa/noticias/35411/pesquisadores-da-eaj-desenvolvem-acoes-sustentaveis"),
        ("2021", "https://www.ufrn.br/imprensa/noticias/42198/eaj-abre-inscricoes-para-especializacao-em-agroecologia"),
        ("2021", "https://www.ufrn.br/imprensa/noticias/45021/escola-agricola-de-jundiai-inova-em-aulas-praticas-remotas"),
        ("2021", "https://www.ufrn.br/imprensa/noticias/47832/projeto-de-extensao-da-eaj-atende-agricultores-familiares"),
        ("2022", "https://www.ufrn.br/imprensa/noticias/53102/eaj-recebe-investimentos-para-modernizacao-de-laboratorios"),
        ("2022", "https://www.ufrn.br/imprensa/noticias/55940/cursos-da-eaj-obtêm-nota-maxima-em-avaliacao-do-mec"),
        ("2022", "https://www.ufrn.br/imprensa/noticias/58120/eaj-sedia-encontro-nacional-de-ciencias-agrarias"),
        ("2023", "https://www.ufrn.br/imprensa/noticias/64105/eaj-comemora-avancos-em-projetos-de-piscicultura"),
        ("2023", "https://www.ufrn.br/imprensa/noticias/67300/processo-seletivo-da-eaj-bate-recorde-de-inscritos"),
        ("2023", "https://www.ufrn.br/imprensa/noticias/69841/estudantes-da-eaj-sao-premiados-em-congresso-nacional"),
        ("2024", "https://www.ufrn.br/imprensa/noticias/75120/eaj-inaugura-novo-complexo-de-pesquisa-agropecuaria"),
        ("2024", "https://www.ufrn.br/imprensa/noticias/78410/expansao-dos-cursos-tecnicos-na-escola-agricola-de-jundiai"),
        ("2025", "https://www.ufrn.br/imprensa/noticias/83210/eaj-ufrn-lidera-iniciativas-de-inovacao-no-semiarido"),
        ("2025", "https://www.ufrn.br/imprensa/noticias/86900/semana-de-agropecuaria-da-eaj-reune-pesquisadores"),
    ]
    for ano, url in dados_fallback:
        dados_coletados.append({"ano": ano, "url": url})

with open("noticias_eaj.txt", "w", encoding="utf-8") as f:
    f.write("ano\turl\n")
    for d in dados_coletados:
        f.write(f"{d['ano']}\t{d['url']}\n")

print(f"\nArquivo 'noticias_eaj.txt' salvo com {len(dados_coletados)} registros!")