
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
from os import makedirs
from math import ceil

class ScraperOfertas:
    def __init__(self,busqueda_="",n_paginas_ = 1):
        self.busqueda  = busqueda_
        self.n_paginas = n_paginas_
        self.ofertas = []
        self.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
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
                discount_tag = item.find("span",class_="andes-money-amount__discount")
                if title_tag and price_tag and link_tag and image_tag  and not condition_tag:
                    highlight = highlight_tag.get_text(strip=True) if highlight_tag else ""
                    discount = discount_tag.get_text(strip=True).replace("%","").replace("OFF","") if discount_tag else None
                    discount_int = int(discount) if discount else None
                    title = title_tag.get_text(strip=True)
                    price = price_tag.get_text(strip=True)
                    price_float = float(price.replace("$","").replace(",","").strip())
                    link = link_tag["href"]
                    image_url = image_tag.get("data-src") or image_tag.get("data-lazy") or image_tag.get("src") #Mercado Libre usa lazy loading
                    self.ofertas.append({
                        "Tag":        highlight,
                        "Descuento":  discount,
                        "Descuento_int": discount_int,
                        "Titulo":     title,
                        "Precio":     price,
                        "Precio_float": price_float,
                        "Enlace":     link,
                        "Imagen":     image_url,
                        "Commerce":   "MercadoLibre"
                    })

        if self.n_paginas > 1:
            sleep(3)# Espera entre páginas para no saturar el sitio

    def crear_html(self,ofertas,cont_html,items_pag,cont_items,total_paginas,commerce) -> int: 
                html = f'''
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Ofertas de {self.busqueda} en {commerce}</title>
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
                        h5.discount {{
                            text-align: center;
                            margin: 0;
                            color: green;
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
                        <h1>Ofertas de {self.busqueda} en {commerce}</h1>
                    </div>
                    <div class="grid">
                '''

                # Renderizar productos
                cont_tmp = 1
                items_pag += 1
                for i in range(cont_items, len(ofertas)):
                    if cont_tmp % items_pag == 0:
                        break
                    tag_descuento = f'''<h5 class="discount">{ofertas[i]["Descuento"]}% Descuento</h5>''' if ofertas[i]["Descuento"]!=None else ""
                    html += f'''
                        <div class="card">
                            <h4>{ofertas[i]["Tag"]}</h4>
                            {tag_descuento}
                            <img src="{ofertas[i]["Imagen"]}" alt="Imagen del producto">
                            <div class="info">
                                <h3>{ofertas[i]["Titulo"]}</h3>
                                <p>{ofertas[i]["Precio"]}</p>
                                <a href="{ofertas[i]["Enlace"]}" target="_blank">Ver en {ofertas[i]["Commerce"]}</a>
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
                makedirs(f"PaginasHTML/{nombre_archivo}_{commerce}", exist_ok=True)
                with open(f"PaginasHTML/{nombre_archivo}_{commerce}/ofertas_{nombre_archivo}_{cont_html}.html", "w", encoding="utf-8") as file:
                    file.write(html)

                return cont_items

    def mostrar_resultados_mercadoLibre_html(self,orden=1,solo_descuento=False):
        if solo_descuento:
            self.ofertas = sorted(self.ofertas,
                    key = lambda x:( 
                        x["Tag"]=="",
                        x["Descuento_int"]*-1,
                        x["Precio_float"]*orden
                        )
                    )
        else:
            self.ofertas = sorted(self.ofertas,
                    key = lambda x:( 
                        x["Tag"]=="",
                        x["Precio_float"]*orden
                        )
                    )
        tamanio = len(self.ofertas)
        print(f"TAMAÑO OFERTAS: {self.ofertas}")
        items_por_pagina=24
        cont_items = 0
        cont_html = 0
        if len(self.ofertas)==1:
            cont_items=self.crear_html(self.ofertas,cont_html,items_por_pagina,cont_items,ceil(tamanio/items_por_pagina),"MercadoLibre")
        while cont_items<len(self.ofertas)-1:
            cont_items=self.crear_html(self.ofertas,cont_html,items_por_pagina,cont_items,ceil(tamanio/items_por_pagina),"MercadoLibre")
            cont_html+=1
        # Crear HTML
       
    def buscar_zegucom(self):
        producto = self.busqueda
        producto = producto.replace(" ", "+").strip()
        url = f"https://www.zegucom.com.mx/#271f/embedded/m=f&p={self.n_paginas}&q={producto}"
        print(f"Scrapeando {self.n_paginas} páginas de ZC con Selenium")

        # Opciones para que Selenium no abra una ventana
        options = Options()
        options.add_argument("--headless")  
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        # Abre el navegador
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        # Esperamos a que cargue 
        sleep(5)

        # Extrae el HTML ya renderizado
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Cerramos el navegador
        driver.quit()
        items = soup.find_all("div", class_="dfd-card dfd-card-preset-product dfd-card-type-productos")
        for item in items:
            title_tag = item.find("div", class_="dfd-card-title")
            search_price_discount= item.find("span", class_="dfd-card-price--sale")
            if  search_price_discount!= None:
                price_tag =search_price_discount
            else:
                price_tag = item.find("span", class_="dfprice4")
            link_tag = item.find("a", class_="dfd-card-link")
            image_tag = item.find("div", class_="dfd-card-thumbnail").find("img")
            highlight_tag =item.find("div",class_="search-on-sale")
            condition_tag =item.find("div",class_="dfd-availability")
            discount_tag = item.find("div",class_="dfd-card-flag")
            if title_tag and price_tag and link_tag and image_tag  and not condition_tag:
                highlight = highlight_tag.get_text(strip=True).upper() if highlight_tag else ""
                discount = discount_tag.get_text(strip=True).replace("%","") if discount_tag else None
                discount_int = int(discount) if discount else None
                title = title_tag.get_text(strip=True)
                price = price_tag.get_text(strip=True)
                price_float = float(price.replace("$","").replace(",","").strip())
                link = link_tag["href"]
                image_url = image_tag.get("data-src") or image_tag.get("data-lazy") or image_tag.get("src") #Mercado Libre usa lazy loading
                self.ofertas.append({
                    "Tag":        highlight,
                    "Descuento":  discount,
                    "Descuento_int": discount_int,
                    "Titulo":     title,
                    "Precio":     price,
                    "Precio_float": price_float,
                    "Enlace":     link,
                    "Imagen":     image_url,
                    "Commerce":   "Zegucom "
                })

    def mostrar_resultados_zegucom_html(self,orden=1,solo_descuento=False):
        if solo_descuento:
            self.ofertas = sorted(self.ofertas,
                    key = lambda x:( 
                        x["Tag"]=="",
                        x["Descuento_int"]*-1,
                        x["Precio_float"]*orden
                        )
                    )
        else:
            self.ofertas = sorted(self.ofertas,
                 key = lambda x:( 
                     x["Tag"]=="",
                     x["Precio_float"]*orden
                     )
                )
        tamanio = len(self.ofertas)
        items_por_pagina=24
        cont_items = 0
        cont_html = 0
        if len(self.ofertas)==1:
            cont_items=self.crear_html(self.ofertas,cont_html,items_por_pagina,cont_items,ceil(tamanio/items_por_pagina),"Zegucom")
        else:
            while cont_items<len(self.ofertas)-1:
                cont_items=self.crear_html(self.ofertas,cont_html,items_por_pagina,cont_items,ceil(tamanio/items_por_pagina),"Zegucom")
                cont_html+=1
        # Crear HTML

    def buscar_global(self):
        productos_en_mercadoLibre = 0
        productos_en_Zegucom = 0
        print("Buscando de manera global ...\nPORFAVOR ESPERE")
        self.buscar_mercadoLibre()
        productos_en_mercadoLibre = len(self.ofertas)
        self.buscar_zegucom()
        productos_en_Zegucom = len(self.ofertas)
        print("!Busqueda Finalizada!")
        print(f'Se encontraron:\n {productos_en_mercadoLibre}'
               f' productos en MercadoLibre\n {productos_en_Zegucom} productos en Zegucom')
        

    def mostrar_resultados_global_html(self,orden=1,solo_descuento=False):
        if solo_descuento:
            self.ofertas = sorted(self.ofertas,
                    key = lambda x:( 
                        x["Tag"]=="",
                        x["Descuento_int"]*-1,
                        x["Precio_float"]*orden
                        )
                    )
        else:
            self.ofertas = sorted(self.ofertas,
                 key = lambda x:( 
                     x["Tag"]=="",
                     x["Precio_float"]*orden
                     )
                )
        tamanio = len(self.ofertas)
        items_por_pagina=24
        cont_items = 0
        cont_html = 0
        if len(self.ofertas)==1:
            cont_items=self.crear_html(self.ofertas,cont_html,items_por_pagina,cont_items,ceil(tamanio/items_por_pagina),"Global")
        else:
            while cont_items<len(self.ofertas)-1:
                cont_items=self.crear_html(self.ofertas,cont_html,items_por_pagina,cont_items,ceil(tamanio/items_por_pagina),"Global")
                cont_html+=1
        # Crear HTML

def main():
    scraper = ScraperOfertas("laptop",2)
    '''
    scraper.buscar_mercadoLibre()
    scraper.mostrar_resultados_mercadoLibre_html(1)
    '''
    '''
    scraper.buscar_zegucom()
    scraper.mostrar_resultados_zegucom_html(1)
    '''
    scraper.buscar_global()
    scraper.mostrar_resultados_global_html(1)
main()