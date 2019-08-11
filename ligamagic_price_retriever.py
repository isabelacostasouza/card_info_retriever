#Author: Isabela Costa Souza (isabela.costasouza10@gmail.com)
#GitHub: https://github.com/isabelacostasouza/wikipedia_data_collector
#Date: 08.10.2019 (MM/DD/YYYY)

import sys
import requests
from bs4 import BeautifulSoup

#Retorna o ID da ligamagic de uma carta
def get_card_id(card_name):
    ligamagic_url = 'https://www.ligamagic.com.br/?view=cards/card&card='

    card_name = card_name.replace("'", "%27")
    card_name = card_name.replace(" ", "+")
    card_name = card_name.replace(",", "%2C")
    ligamagic_url = ligamagic_url + card_name

    #get the First URL's html
    page = requests.get(ligamagic_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    store_link = soup.find("div", class_="box p10 box-cards-esquerda").find("div", {"id": "card-estoque"}).find("div", {"id": "aba-cards"}).find("div", class_="estoque-linha primeiro").find("div", class_="e-col8 e-col8-offmktplace")

    if(store_link == None):
        store_link = requests.get("https://www.ligamagic.com.br/" + str(soup.find("div", class_="box p10 box-cards-esquerda").find("div", {"id": "card-estoque"}).find("div", {"id": "aba-cards"}).find("div", class_="estoque-linha primeiro").find("div", class_="e-col8 e-col8-offmktplace e-col8-com-extras").find("div").find("a")["href"])).url
        
    else:
      store_link = requests.get("https://www.ligamagic.com.br/" + str(soup.find("div", class_="box p10 box-cards-esquerda").find("div", {"id": "card-estoque"}).find("div", {"id": "aba-cards"}).find("div", class_="estoque-linha primeiro").find("div", class_="e-col8 e-col8-offmktplace").find("a")["href"])).url

    return store_link.split("card=")[1].split("&")[0]


# Retorna as informações da carta (valor, quantidade disponível e tipo) da loja desejada
def get_card_info(wanted_store_url, card_name):
    try:
        store_url = wanted_store_url + get_card_id(card_name)

        page = requests.get(store_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        table_cards = soup.find("table").find_all("tr")

        informacoes_encontradas = set()

    except:
        return '0'     

    card_range = len(table_cards) - 1
    range_cards = 0

    for i in range(card_range):
        if(i > 11 and str(table_cards[i].contents[1])[4] == 's'):
            break
        else:
            range_cards += 1  

    card_range = range_cards - 1

    for i in range(card_range):
        if(i >= 11):
            total_produtos = str(table_cards[i].find_all("td")[3].contents[0])
            if(total_produtos[0] == '<'):
                total_produtos = table_cards[i].find_all("td")[4].contents[0]

            if(total_produtos != "0 unid."):

                #valor
                valor = ''
                if(table_cards[i].find_all("td")[4].find("font") == None):
                    valor = str(table_cards[i].find_all("td")[4].contents[0])
                    if(valor[0] != 'R'):
                        if(valor[0] == '-'):
                            valor = str(table_cards[i].find_all("td")[3].contents[0])
                        elif(valor == '\n'):
                            valor = (table_cards[i])
                            print(valor)
                        else:
                            valor = str(table_cards[i].find_all("td")[5].contents[0])
                else:
                    valor = str(table_cards[i].find_all("td")[4].find("font").contents[0])
                    if(valor[0] != 'R'):
                        valor = str(table_cards[i].find_all("td")[5].contents[0])
                        if(valor == '\n'):
                          valor = str(table_cards[i].find_all("td"))
                if(valor == '\n'):
                    valor = table_cards[i].find_all("td")[5].find("s").contents[0]

                #quantidade
                quantidade = ''
                tipo_especial = ""
                if(table_cards[i].find_all("td")[3].find("font") == None):
                    quantidade = table_cards[i].find_all("td")[3]
                    if(quantidade.find("i") == None):
                        quantidade = str(quantidade.contents[0])
                    else:
                        quantidade = str(table_cards[i].find_all("td")[4].contents[0])
                else:
                    tipo_especial = " (" + str(table_cards[i].find_all("td")[3].find("font").find("b").contents[0]) + ")"
                    quantidade = table_cards[i].find_all("td")[4]

                    if(quantidade.find("i") == None):
                        quantidade = str(quantidade.contents[0])
                    else:
                        quantidade = str(table_cards[i].find_all("td")[5].contents[0])

                informacoes_carta = valor + " - " + quantidade + tipo_especial

                if(valor[0] != "0"):
                    informacoes_encontradas.add(informacoes_carta)
                    
    return informacoes_encontradas
                
# Funcao principal
def main(wanted_store_url):

    list_cards = set()
    f = open("mtg_cards.txt", "r")
    if f.mode == 'r':
        contents = f.read()
        contents = contents.splitlines()
        for content in contents:
            list_cards.add(content)

    quantidade_cartas = len(list_cards)
    cartas_checadas = 0

    aux_url = wanted_store_url.split("www.")[1]
    file_name = "card_prices (" + aux_url + ")"
    file = open(file_name,"w+")
  
    wanted_store_url += "/?view=ecom/item&tcg=1&card="

    print("Cartas conferidas:\n")

    for card_name in list_cards:
        
        informacoes_encontradas = get_card_info(wanted_store_url, card_name)
        if(informacoes_encontradas == '0'):
            file.write("Card com nome incorreto: " + card_name + "\n\nO programa parou por uma das seguintes razoes:\n1. Voce nao soube escrever o nome da carta\n2. Esta carta nao esta disponivel em nenhuma loja da liga\n3. Eu programei algo errado, reporte o bug :)\n\nRetire ou altere o nome da carta, desculpe pelo incomodo\n")
            print("\nCard com nome incorreto: " + card_name + "\n\nO programa parou por uma das seguintes razoes:\n1. Voce nao soube escrever o nome da carta\n2. Esta carta nao esta disponivel em nenhuma loja da liga\n3. Eu programei algo errado, reporte o bug :)\n\nRetire ou altere o nome da carta, desculpe pelo incomodo\n")
            file.close
            sys.exit() 
            
        cartas_checadas += 1
        
        file.write(card_name + "\n\n")
                
        if(len(informacoes_encontradas) != 0):
            for info in informacoes_encontradas:
                file.write(info + "\n")
            if(cartas_checadas != quantidade_cartas):
                file.write("\n----------------\n\n")
        else:
            file.write("Carta indisponivel!")
            if(cartas_checadas != quantidade_cartas):
                file.write("\n\n----------------\n\n")
        
        print(card_name)

    print("\nAs informacoes recuperadas da loja estao no arquivo card_prices.txt :)\n")
    file.close

print("\nO programa está rodando!\nAguarde alguns segundos ou minutos se voce passou uma lista enorme!\n")

#link da loja desejada, nesse exemplo, TCGeek
wanted_store_url = "https://www.tcgeek.com.br"
main(wanted_store_url)
