import requests
from bs4 import BeautifulSoup
import json
import re
import sys

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
            product_description = product_description_element.prettify()  if product_description_element else "Descrição não encontrada"

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


# Restante do seu código permanece inalterado
# ...

# URL inicial da categoria
url_categoria = 'https://www.miess.com.br/sex-shop/comestiveis/'
lista_de_produtos = []
links_processados = 0

def processar_pagina(url):
    global links_processados  # Adicionando uma variável global para o contador
    print(f"Iniciando a solicitação à página: {url}")
    response = requests.get(url, headers={'User-Agent': 'Custom User Agent'})

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        produtos = soup.find_all('li', class_='sex-shop-e-produtos-eroticos-com-melhor-preco-|-miess')

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

                detalhes = get_product_details(link_produto)
                # sys.exit()
                if detalhes:
                    detalhes['titulo'] = titulo_produto
                    lista_de_produtos.append(detalhes)
                    links_processados += 1  # Incrementar o contador

        # Encontrar link da próxima página
        next_page_link = soup.find('li', class_='next')
        return next_page_link.find('a')['href'] if next_page_link else None

    else:
        print(f'Falha ao carregar a página. Código de status: {response.status_code}')
        return None


url_atual = url_categoria

while url_atual:
    proxima_url = processar_pagina(url_atual)
    exit
    if proxima_url:
        url_atual = proxima_url
    else:
        break

# Salvar os dados em um arquivo JSON
with open('produtosMiess.json', 'w', encoding='utf-8') as f:
    json.dump(lista_de_produtos, f, ensure_ascii=False, indent=4)

print(f'Dados salvos em produtosMiess.json. Total de {links_processados} links processados.')
