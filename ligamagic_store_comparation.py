#Author: Isabela Costa Souza (isabela.costasouza10@gmail.com)
#GitHub: https://github.com/isabelacostasouza/wikipedia_data_collector
#Date: 11.10.2019 (MM/DD/YYYY)

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

    NoneType = type(None)

    if isinstance(store_link, type(None)):

        store_link = soup.find('div', class_='box p10 box-cards-esquerda').find("div", {"id": "card-estoque"}).find("div", {"id": "aba-cards"}).find_all('div', class_='estoque-linha')[1].find('a')['href']

        store_link = requests.get("https://www.ligamagic.com.br/" + str(store_link)).url
        
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

    print(card_name)

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
                    if(valor[0] != 'R' and valor[1] != '$'):
                        if(valor[0] == '-'):
                            valor = str(table_cards[i].find_all("td")[3].contents[0])
                        elif(valor == '\n'):
                            valor = (table_cards[i])
                            print(valor)
                        else:
                            valor = str(table_cards[i].find_all("td")[5].contents[0])
                else:
                    valor = str(table_cards[i].find_all("td")[4].find("font").contents[0])
                    if(valor[0] != 'R' and valor[1] != '$'):
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

def get_file_array(file_name):

    file_array = []

    f = open(file_name, "r")
    if f.mode == 'r':
        contents = f.read()
        contents = contents.splitlines()
        for content in contents:
            file_array.insert(len(file_array), content)
    f.close()

    return file_array


def get_card_list(file_array):
  list_cards = []

  for line in file_array:
      if(line != '' and line != '----------------' and line != 'Carta indisponivel!'):
        if(line[0] != 'R'):
          list_cards.insert(len(list_cards)- 1, line)

  return list_cards


def get_best_prices(list_cards, file_array):

    dict_store = dict()

    array_aux = []
    array_aux.insert(0,0.0)
    array_aux.insert(1, 0)

    for card in list_cards:
        dict_store[card] = array_aux

    for i in range(len(file_array) + 1):
      
      if(len(file_array) > i):
        line = file_array[i]

      if(line != ''):

          if(line[0] != 'R' and line[1] != '$'and line != '----------------' and line != 'Carta indisponivel!'):
              card = line

          elif(line[0] == 'R' and line[1] == '$'):
              new_price = float(line.split("R$ ")[1].split(" -")[0].replace(",", "."))
              quantidade_disponivel = int(line.split("R$ ")[1].split(" - ")[1].split(' unid.')[0])

              info_unidade = []
              info_unidade.insert(0, new_price)
              info_unidade.insert(1, quantidade_disponivel)

              if(dict_store[card] == array_aux):
                dict_store[card] = info_unidade

              elif(dict_store[card][0] > new_price):
                  dict_store[card] = info_unidade

    return dict_store 


def get_store_comparation(store01_name, store02_name):

    file_name_store01 = 'card_prices (' + store01_name + ')'
    file_name_store02 = 'card_prices (' + store02_name + ')'

    file_array_store01 = get_file_array(file_name_store01)
    file_array_store02 = get_file_array(file_name_store02)

    card_list = get_card_list(file_array_store01)

    dict_prices_store01 = get_best_prices(card_list, file_array_store01)
    dict_prices_store02 = get_best_prices(card_list, file_array_store02)

    file_name = "store_comparation (" + store01_name + " vs " + store02_name + ")"
    file = open(file_name,"w+")

    for card in card_list:
      file.write("\n" + card + "\n\n")

      if(dict_prices_store01[card][0] < dict_prices_store02[card][0]):
        if(dict_prices_store01[card][0] != 0.0):
          file.write(store01_name + ": RS " + str(dict_prices_store01[card][0]) + " - " + str(dict_prices_store01[card][1]) + " unid. \n")

        if(dict_prices_store02[card][0] != 0.0):
          file.write(store02_name + ": RS " + str(dict_prices_store02[card][0]) + " - " + str(dict_prices_store02[card][1]) + " unid. \n\n")

      else:
        if(dict_prices_store02[card][0] != 0.0):
          file.write(store02_name + ": RS " + str(dict_prices_store02[card][0]) + " - " + str(dict_prices_store02[card][1]) + " unid. \n")
          
        if(dict_prices_store01[card][0] != 0.0):
          file.write(store01_name + ": RS " + str(dict_prices_store01[card][0]) + " - " + str(dict_prices_store01[card][1]) + " unid. \n\n")
      
      if(dict_prices_store02[card][0] == 0.0 and dict_prices_store01[card][0] == 0.0):
        file.write("Card indisponivel em ambas as lojas!\n\n")
      
      file.write('----------------\n')

    file.close()

def create_store_files(wanted_store_url):

    list_cards = set()
    f = open("mtg_cards.txt", "r")
    if f.mode == 'r':
        contents = f.read()
        contents = contents.splitlines()
        for content in contents:
            list_cards.add(content)

    quantidade_cartas = len(list_cards)
    cartas_checadas = 0

    aux_url = wanted_store_url.split("www.")[1].split(".com")[0]
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
        file.close


def main(wanted_store_url01, wanted_store_url02):

  print("\nO programa está rodando!\nAguarde alguns segundos ou minutos se voce passou uma lista enorme!\n")

  store01_name = wanted_store_url01.split("www.")[1].split(".com")[0]
  file_name = "card_prices (" + store01_name + ")"

  create_store_files(wanted_store_url01)
  print("\nAs informacoes recuperadas da loja " + store01_name + " estao no arquivo " + file_name + "\n\n--------------------\n\nAgora vamos fazer a checagem da segunda loja\n")

  store02_name = wanted_store_url02.split("www.")[1].split(".com")[0]
  file_name = "card_prices (" + store02_name + ")"

  create_store_files(wanted_store_url02)
  print("\nAs informacoes recuperadas da loja " + store01_name + " estao no arquivo" + file_name + ".\n\n")

  file_name = "store_comparation (" + store01_name + " vs " + store02_name + ")"
  store02_name = wanted_store_url01.split("www.")[1]

  get_store_comparation(wanted_store_url01.split("www.")[1].split(".com")[0], wanted_store_url02.split("www.")[1].split(".com")[0])

  print("Sua comparacao esta pronta!\n\nAs informacoes recuperadas estao no arquivo '" + file_name + "'\n\n")

wanted_store01_url = "https://www.tcgeek.com.br"
wanted_store02_url = "https://www.vaultofcards.com.br"
main(wanted_store01_url, wanted_store02_url)
