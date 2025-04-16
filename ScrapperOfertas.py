
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from math import ceil
class ScraperOfertas:
    def __init__(self,busqueda_="",n_paginas_ = 1):
        self.busqueda  = busqueda_
        self.n_paginas = n_paginas_
        self.ofertas = []
        self.headers   = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
    
    def buscar_mercadoLibre(self):
        producto = self.busqueda
        producto = producto.replace(" ","-").strip()
        for i in range(self.n_paginas):
            start = i * 50
            url = f"https://listado.mercadolibre.com.mx/{producto}/_Desde_{start}_NoIndex_True"
            print(f"Scrapeando ML página {i + 1}...")

            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.find_all("li", class_="ui-search-layout__item")

            for item in items:
                title_tag = item.find("h3", class_="poly-component__title-wrapper")
                price_tag = item.find("span", class_="andes-money-amount")
                link_tag = item.find("a", class_="poly-component__title")
                image_tag = item.find("img", class_="poly-component__picture")
                highlight_tag =item.find("span",class_="poly-component__highlight")
                condition_tag =item.find("span",class_="poly-component__item-condition")
                if title_tag and price_tag and link_tag and image_tag and not condition_tag:
                    if highlight_tag:
                        highlight = highlight_tag.get_text(strip=True)
                    else:
                        highlight = "" 
                    title = title_tag.get_text(strip=True)
                    price = price_tag.get_text(strip=True)
                    price_int = int(price.replace("$","").replace(",","").strip())
                    link = link_tag["href"]
                    image_url = image_tag.get("data-src") or image_tag.get("data-lazy") or image_tag.get("src") #Mercado Libre usa lazy loading
                    self.ofertas.append({
                        "Tag":        highlight,
                        "Titulo":     title,
                        "Precio":     price,
                        "Precio_int": price_int,
                        "Enlace":     link,
                        "Imagen":     image_url
                    })

        if self.n_paginas > 1:
            time.sleep(3)# Espera entre páginas para no saturar el sitio
    def crear_html_ML(self,ofertas,cont_html,items_pag,cont_items,total_paginas) -> int: 
                html = f'''
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Ofertas de {self.busqueda} en MercadoLibre</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background: #f2f2f2;
                            padding: 20px;
                        }}
                        .header {{
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            margin-bottom: 10px;
                        }}
                        .pagination {{
                            display: flex;
                            gap: 5px;
                            border-color: red;
                        }}
                        .pagination a {{
                            padding: 5px 10px;
                            background: #ccc;
                            color: black;
                            text-decoration: none;
                            border-radius: 4px;
                            font-weight: bold;
                        }}
                        .pagination a.active {{
                            background: #3483fa;
                            color: white;
                        }}
                        h1 {{
                            margin: 0;
                            color: #333;
                        }}
                        .grid {{
                            display: grid;
                            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                            gap: 20px;
                            margin-top: 30px;
                        }}
                        .card {{
                            background: white;
                            border-radius: 10px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                            overflow: hidden;
                            transition: transform 0.2s ease;
                        }}
                        .card:hover {{
                            transform: scale(1.03);
                        }}
                        .card img {{
                            width: 100%;
                            height: 200px;
                            object-fit: contain;
                            background: #fafafa;
                        }}
                        .card .info {{
                            padding: 15px;
                        }}
                        .card h3 {{
                            font-size: 1.1em;
                            margin: 0 0 10px;
                        }}
                        .card p {{
                            margin: 0;
                            color: #007600;
                            font-weight: bold;
                        }}
                        .card a {{
                            display: block;
                            margin-top: 10px;
                            text-align: center;
                            background: #3483fa;
                            color: white;
                            padding: 10px;
                            border-radius: 5px;
                            text-decoration: none;
                        }}
                        .card a:hover {{
                            background: #2968c8;
                        }}
                        .card h4 {{
                            text-align: center;
                            margin: 0;
                            color: #9400D3;
                            font-weight: bold;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <div class="pagination">
                '''

                # Botones de paginación
                nombre_archivo = self.busqueda.replace(" ", "_")
                for i in range(total_paginas):
                    clase = "active" if i == cont_html else ""
                    html += f'<a href="ofertas_{nombre_archivo}_{i}.html" class="{clase}">{i+1}</a>'

                html += f'''
                        </div>
                        <h1>Ofertas de {self.busqueda} en MercadoLibre</h1>
                    </div>
                    <div class="grid">
                '''

                # Renderizar productos
                cont_tmp = 1
                items_pag += 1
                for i in range(cont_items, len(ofertas)):
                    if cont_tmp % items_pag == 0:
                        break
                    html += f'''
                        <div class="card">
                            <h4>{ofertas[i]["Tag"]}</h4>
                            <img src="{ofertas[i]["Imagen"]}" alt="Imagen del producto">
                            <div class="info">
                                <h3>{ofertas[i]["Titulo"]}</h3>
                                <p>{ofertas[i]["Precio"]}</p>
                                <a href="{ofertas[i]["Enlace"]}" target="_blank">Ver en MercadoLibre</a>
                            </div>
                        </div>
                    '''
                    cont_items += 1
                    cont_tmp += 1

                html += '''
                    </div>
                </body>
                </html>
                '''

                # Guardar archivo
                os.makedirs(f"PaginasHTML/{nombre_archivo}", exist_ok=True)
                with open(f"PaginasHTML/{nombre_archivo}/ofertas_{nombre_archivo}_{cont_html}.html", "w", encoding="utf-8") as file:
                    file.write(html)

                return cont_items



    def mostrar_resultados_mercadoLibre_html(self,orden=1):
        self.ofertas = sorted(self.ofertas,
                 key = lambda x:( 
                     x["Tag"]=="",
                     x["Precio_int"]*orden)
                )
        tamanio = len(self.ofertas)
        items_por_pagina=24
        cont_items = 0
        cont_html = 0
        while cont_items<len(self.ofertas)-1:
            cont_items=self.crear_html_ML(self.ofertas,cont_html,items_por_pagina,cont_items,total_paginas=ceil(tamanio/items_por_pagina))
            cont_html+=1
        # Crear HTML
       

def main():
    scraper = ScraperOfertas("Samsung S24",2)
    scraper.buscar_mercadoLibre()
    scraper.mostrar_resultados_mercadoLibre_html()
main()