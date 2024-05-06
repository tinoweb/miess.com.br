from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import re
import sys

import requests
import time

# Declare a lista de produtos globalmente
lista_de_produtos = []
links_processados = 0
url_categoria = 'https://www.miess.com.br/moda-praia/maio-plus-size'
lingerie = "lingerie-sexy-e-sensual-no-atacado-e-varejo-|-miess fixVar event-set-tag event-set"
cuidadosPessoais = "cuidados-pessoais---produtos-para-beleza-e-higiene-|-miess"
praia = "moda-praia---biquinis-e-maios-sexies-e-sensuais-|-miess fixVar event-set-tag event-set"


chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument("--proxy-bypass-list=*")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

# Remova o argumento executable_path
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)

def get_next_page_url(base_url, page_number):
    # Adapte a lógica conforme necessário para a estrutura de URL do seu site
    return f"{base_url}#{page_number}"


def get_product_details(url):

    response = requests.get(url, headers={'User-Agent': 'Custom User Agent'})

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')

        # html_content = soup.prettify()
        # with open('lingerie.html', 'w', encoding='utf-8') as file:
        #     file.write(html_content)

        # sys.exit()

        # Encontrar o script contendo as informações de variação
        script_tag = soup.find('script', string=re.compile('var skuJson_0 ='))
        script_content = script_tag.text if script_tag else ''

        # Usar regex para extrair o conteúdo dentro de skuJson_0
        match = re.search(r'var skuJson_0 = (\{.*\});', script_content)
        if match:
            sku_json_str = match.group(1)
            sku_json = json.loads(sku_json_str)

            # Agora você pode acessar as informações de variação em sku_json
            variations_list = []
            for sku in sku_json.get('skus', []):
                variation_name = sku['dimensions'].get('Cor', 'N/A')  # Obtém a cor da variação
                variation_size = sku['dimensions'].get('Tamanho', 'N/A')  # Obtém o tamanho da variação
                variation_image_urls = sku['image']
                variation_sku = sku['sku']
                variation_available = sku['available']
                variation_price = sku['bestPriceFormated']

                variations_list.append({
                    "Nome da variação": variation_name,
                    "Tamanho da variação": variation_size,
                    "Imagens da variação": variation_image_urls,
                    "SKU": variation_sku,
                    "Disponibilidade": variation_available,
                    "Preço da variação": variation_price,
                })

            # Obter o valor do produto do componente <em class="bestPriceCalc">
            product_price_element = variation_price
            product_price = variation_price if product_price_element else "Preço não encontrado"

            # Restante do código permanece inalterado
            product_name = sku_json.get('name', '')
            
            # Adicione a lógica para obter a descrição, se disponível
            product_description_element = soup.find("div", class_="productDescription")
            product_description = product_description_element.prettify() if product_description_element else "Descrição não encontrada"

            # Extrair o valor numérico do preço do produto (removendo o símbolo da moeda e convertendo para float)
            product_price_numeric = float(re.search(r'\d+\.\d+', product_price.replace(",", "."))[0])

            # Calcular o novo preço com um aumento de 150%
            new_price = product_price_numeric * 1.5

            return {
                "Nome do produto": product_name,
                "Descrição do produto": product_description,
                "Variações do produto": variations_list,
                "Preço do produto": product_price,
                "Novo preço (150%)": new_price,
                # Adicione mais informações conforme necessário
            }

    else:
        print(f'Falha ao carregar a página do produto. Código de status: {response.status_code}')
        return None


def extract_total_products(soup):
    try:
        total_products_span = soup.find('span', class_='resultado-busca-numero').find('span', class_='value')

        if total_products_span:
            total_products_text = total_products_span.get_text(strip=True)

            try:
                total_products = int(total_products_text)
                return total_products
            except ValueError:
                print(f'Erro ao converter o valor total de produtos: {total_products_text}')
                return None
        else:
            print('Elemento span não encontrado para o valor total de produtos.')
            return None

    except Exception as e:
        print(f'Erro ao extrair total de produtos: {e}')
        return None


class SairDoLoop(Exception):
    pass


def processar_pagina(url_base):
    global links_processados
    current_page = 1

    driver.get(url_base)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # html_content = soup.prettify()
    # with open('pagina_completa.html', 'w', encoding='utf-8') as file:
    #     file.write(html_content)

    # sys.exit()

    total_products = extract_total_products(soup)
    if total_products is None:
        print("Não foi possível extrair o total de produtos.")
        return
    
    produtos_por_pagina = 36  # Atualize conforme necessário
    numero_de_paginas = -(-total_products // produtos_por_pagina)
    # numero_de_paginas =2

    while current_page <= numero_de_paginas:
        next_url = get_next_page_url(url_base, current_page)
        print(f"Próxima página: {next_url}")

        driver.get(next_url)
        time.sleep(4)  # Espera para garantir que a página carregue completamente
        driver.refresh()  # Recarrega a página para garantir que todos os elementos estejam presentes
        time.sleep(4)  # Espera novamente após recarregar
        
        # Atualiza o soup após recarregar a página
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Encontre todos os produtos na página atual
        produtos = soup.find_all('li', class_=praia)
                                                
        # html_content = soup.prettify()
        # with open('pagina_completa.html', 'w', encoding='utf-8') as file:
        #     file.write(html_content)

        # sys.exit()  
        
        print(f"Encontrados {len(produtos)} produtos.")

        for produto in produtos:
            link_produto_element = produto.find('a', class_='productName')

            if not link_produto_element:
                link_produto_element = produto.find('a', class_='has--lazyload')

            if link_produto_element:
                link_produto = link_produto_element['href']
                titulo_produto = link_produto_element.get('title', '').strip()

                print(f"Processando o produto: {titulo_produto} ---- ")

                detalhes = get_product_details(link_produto)
                if detalhes:
                    detalhes['titulo'] = titulo_produto

                    # Verifica se o produto está esgotado
                    outStock = produto.find('p', class_='outOfStock')
                    if outStock and "Produto Esgotado" in outStock.text:
                        detalhes['ProdutoEsgotado'] = True
                    else:
                        # Opcional: Adicionar a chave com valor False se quiser explicitar produtos não esgotados
                        detalhes['ProdutoEsgotado'] = False

                    lista_de_produtos.append(detalhes)
                    links_processados += 1  # Incrementar o contador

        print(f"Processando página: {current_page} de {numero_de_paginas}")
        current_page += 1

    driver.quit()


url_atual = url_categoria

proxima_url = processar_pagina(url_atual)

# Salvar os dados em um arquivo JSON
with open('produtosMiess.json', 'w', encoding='utf-8') as f:
    json.dump(lista_de_produtos, f, ensure_ascii=False, indent=4)

print(f'Dados salvos em produtosMiess.json. Total de {links_processados} links processados.')
