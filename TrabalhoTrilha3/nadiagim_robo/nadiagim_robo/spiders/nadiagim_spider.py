import scrapy
import os
import pathlib
import csv 

class NadiagimSpiderSpider(scrapy.Spider):
    name = 'nadiagim_spider'
    delimiter = ';'
    
    # abre o arquivo local, com todos os links
    start_urls = [f"{pathlib.Path(os.path.abspath('MYSELF_LojaNadiaGimenes_orig.html')).as_uri()}"]
    #start_urls = ["https://www.nadiagimenes.com.br/categoria/myself/"]
    
    # Apaga o arquivo caso exista, para evitar sobreposição
    if os.path.exists("produtos_nadia.csv"):
        os.remove("produtos_nadia.csv")

    # --------------------------------------------------------------------------------
    # ---------------------------------- PARSE 1 -------------------------------------
    # --------------------------------------------------------------------------------

    # Funcao que interpreta o arquivo do site e envia 
    def parse(self, response):
        colecao = response.css(".breadcrumb--active").css('span::text').get() 

        for link in response.css(".product-item__image").css("a::attr(href)").getall():
            text_page = f"https://www.nadiagimenes.com.br{link}"

            # Coletando informacoes basicas dos produtos disponiveis
            post = {
                'colecao': colecao,
                'links_disponiveis': text_page
            }

            yield scrapy.Request(text_page, callback=self.parse_products)   

        # Pegando a informacao do botao do next page
        next_page = response.css('.product-list__pagination__item').css('.product-list__pagination--next').css('a::attr(href)').get()  
        next_page = f"https://www.nadiagimenes.com.br/categoria/myself/{next_page}"

        # Chamando as proximas paginas
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse)

    # --------------------------------------------------------------------------------
    # ---------------------------------- PARSE 2 -------------------------------------
    # --------------------------------------------------------------------------------
             
    # função que interpreta os documentos com os textos 
    def parse_products(self, response):   

        # coletando a informacao na página para exportar no excel
        colecao ='MYSELF'
        nome_produto = response.css('.product-detail--title').css('span::text').get().strip()
        avaliacao_aprovacao = response.css('.product-detail__rating__stars--active').css('span::attr(style)').get().strip()
        numero_avaliacoes = response.css('.product-detail__rating__amount::text').get().strip()            
        preco = response.css('.product-detail__price--currency::text').get().strip()

        # Preparando a informacao do produto para exportar para a tabela  
        post = {
            'colecao': 'MYSELF',
            'nome_produto': nome_produto,
            'avaliacao_aprovacao': avaliacao_aprovacao,
            'numero_avaliacoes': numero_avaliacoes,            
            'preco': preco
        }

        # Exportando as informacoes para uma tabela
        with open('produtos_nadia.csv', 'a', newline='', encoding="utf-8")  as output_file:
             dict_writer = csv.DictWriter(output_file, post.keys())            
             #dict_writer.writerows([post])        
        yield post


    