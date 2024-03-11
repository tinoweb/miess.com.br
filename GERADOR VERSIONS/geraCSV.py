import csv
import json  # Adiciona esta linha para importar o módulo json


def convert_to_csv(json_filename, csv_filename):
    # Carregar dados do arquivo JSON
    with open(json_filename, 'r', encoding='utf-8') as jsonfile:
        product_data_list = json.load(jsonfile)

    # Criar ou abrir o arquivo CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Definir os nomes das colunas
        fieldnames = [
            "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Product Type",
            "Tags", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
            "Variant SKU", "Variant Price", "Compare At Price", "Image Src", "Published",
            "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy",
            "Variant Fulfillment Service", "Variant Requires Shipping", "Variant Taxable",
            "Gift Card", "SEO Title", "SEO Description", "Status"
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Escrever o cabeçalho no arquivo CSV
        writer.writeheader()

        # Iterar sobre cada produto no arquivo JSON
        for product_data in product_data_list:
            # Iterar sobre cada variação do produto e escrever no CSV
            for variation in product_data["Variações do produto"]:
                writer.writerow({
                    "Handle": product_data["titulo"].lower().replace(" ", "-"),
                    "Title": product_data["titulo"],
                    "Body (HTML)": product_data["Descrição do produto"],
                    "Vendor": product_data["Fabricante"],
                    "Product Category": "comestiveis",
                    "Product Type": "Comestiveis",
                    "Tags": "comestiveis",
                    "Variant SKU": str(variation["SKU"]),
                    "Variant Price": variation.get("Preço da variação", "").replace("R$ ", "").replace(",", ".").strip(),
                    "Compare At Price": "",  # Adicione o preço de comparação, se disponível
                    "Image Src": variation["Imagens da variação"],
                    "Published": "TRUE",  # Assumindo que todos os produtos são publicados
                    "Variant Inventory Tracker": "shopify",
                    "Variant Inventory Qty": "",  # Adicione a quantidade em estoque, se disponível
                    "Variant Inventory Policy": "deny",
                    "Variant Fulfillment Service": "manual",
                    "Variant Requires Shipping": "TRUE",
                    "Variant Taxable": "TRUE",  # Assumindo que a variação é tributável
                    "Gift Card": "FALSE",
                    "SEO Title": "",
                    "SEO Description": "",
                    "Status": "active"  # Assumindo que a variação está ativa
                })

# Exemplo de uso
convert_to_csv('produtosMiess.json', 'produtosMiess.csv')
