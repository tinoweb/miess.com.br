import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import time

def get_product_details(url):
    response = requests.get(url, headers={'User-Agent': 'Custom User Agent'})

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

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
                variation_name = sku['dimensions'].get('Sabor', 'N/A')
                variation_image_urls = sku['image']

                variation_sku = sku['sku']
                variation_available = sku['available']
                variation_price = sku['bestPriceFormated']

                variations_list.append({
                    "Nome da variação": variation_name,
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
            manufacturer = ''  # Adicione a lógica para obter o fabricante, se disponível
            product_reference = ''  # Adicione a lógica para obter a referência, se disponível

            # Adicione a lógica para obter a descrição, se disponível
            product_description_element = soup.find("div", class_="productDescription")
            product_description = product_description_element.prettify() if product_description_element else "Descrição não encontrada"

            # Extrair o valor numérico do preço do produto (removendo o símbolo da moeda e convertendo para float)
            product_price_numeric = float(re.search(r'\d+\.\d+', product_price.replace(",", "."))[0])

            # Calcular o novo preço com um aumento de 150%
            new_price = product_price_numeric * 1.5

            return {
                "Nome do produto": product_name,
                "Fabricante": manufacturer,
                "Referência do produto": product_reference,
                "Descrição do produto": product_description,
                "Variações do produto": variations_list,
                "Preço do produto": product_price,
                "Novo preço (150%)": new_price,
                # Adicione mais informações conforme necessário
            }

    else:
        print(f'Falha ao carregar a página do produto. Código de status: {response.status_code}')
        return None

url_categoria = 'https://www.miess.com.br/sex-shop/cosmeticos#48'
lista_de_produtos = []
links_processados = 0

def get_max_page_number(soup):
    # Encontrar todas as tags 'li' com a classe 'page-number'
    page_number_tags = soup.find_all('li', class_='page-number')

    # Extrair os números das páginas
    page_numbers = [int(tag.text) for tag in page_number_tags]

    # Encontrar o número máximo
    max_page_number = max(page_numbers) if page_numbers else 1
    return max_page_number

def extract_total_products(soup):
    # Encontrar o elemento span com a classe 'value' dentro do span 'resultado-busca-numero'
    total_products_span = soup.find('span', class_='resultado-busca-numero').find('span', class_='value')

    if total_products_span:
        # Obter o texto do elemento
        total_products_text = total_products_span.get_text(strip=True)

        try:
            # Converter o texto para um número inteiro
            total_products = int(total_products_text)
            return total_products
        except ValueError:
            print(f'Erro ao converter o valor total de produtos: {total_products_text}')
            return None
    else:
        print('Elemento span não encontrado para o valor total de produtos.')
        return None

def processar_pagina(url):
    global links_processados, url_categoria  # Adicionando variáveis globais para o contador e a URL da categoria
    print(f"Iniciando a solicitação à página: {url}")
    response = requests.get(url, headers={'User-Agent': 'Custom User Agent'})
    time.sleep(4)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        produtos = soup.find_all('li', class_='sex-shop-e-produtos-eroticos-com-melhor-preco-|-miess')

        html_content = soup.prettify()

        # Escrevendo o conteúdo HTML formatado no arquivo
        with open('pagina_completa.html', 'w', encoding='utf-8') as file:
            file.write(html_content)

        sys.exit()


        print(f"Encontrados {len(produtos)} produtos.")

        for produto in produtos:
            link_produto_element = produto.find('a', class_='productName')

            if not link_produto_element:
                # Se não encontrar pelo primeiro padrão, tente pelo segundo padrão
                link_produto_element = produto.find('a', class_='has--lazyload')

            if link_produto_element:
                link_produto = link_produto_element['href']
                titulo_produto = link_produto_element.get('title', '').strip()

                print(f"Processando o produto: {titulo_produto} ---- ")

                # detalhes = get_product_details(link_produto)
                # if detalhes:
                #     detalhes['titulo'] = titulo_produto
                #     lista_de_produtos.append(detalhes)
                #     links_processados += 1  # Incrementar o contador

        total_products = extract_total_products(soup)
        produtos_por_pagina = 36
        numero_de_paginas = -(-total_products // produtos_por_pagina)

        print("Número total de páginas estimado:", numero_de_paginas)

        if total_products > produtos_por_pagina:
            for next_page_number in range(2, numero_de_paginas + 1):
                next_url = f"{url_categoria}#{next_page_number}"
                # print(f"Próxima página: {next_url}")

                print(f"Próxima página: {next_url}")
                proxima_url = processar_pagina(next_url)
                if not proxima_url:
                    break

        else:
            print("Não há necessidade de mais páginas.")
            return None

    else:
        print(f'Falha ao carregar a página. Código de status: {response.status_code}')
        return None

url_atual = url_categoria

while url_atual:
    processar_pagina("https://www.miess.com.br/sex-shop/cosmeticos#48")

    # if proxima_url:
    #     print("priximo URL", proxima_url)
    #     url_atual = proxima_url
    # else:
    #     break

# Salvar os dados em um arquivo JSON
with open('produtosMiess.json', 'w', encoding='utf-8') as f:
    json.dump(lista_de_produtos, f, ensure_ascii=False, indent=4)

print(f'Dados salvos em produtosMiess.json. Total de {links_processados} links processados.')
