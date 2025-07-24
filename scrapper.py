import requests
from bs4 import BeautifulSoup

def get_text_from_url(url):

    #faz a solicitação HTTP para a url
    response = requests.get(url)

    #Verifica se a solicitação foi bem sucedida
    if response.status_code == 200:
        #Analisa o conteúdo HTML da página
        soup = BeautifulSoup(response.content, "html.parser")

        #Remove Scripts e Styles do texto
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose

        #Obtém o texto puro.
        text = soup.get_text()

        #Remove espaços brancos em excesso do texto. 
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        #Retorna o texto.
        return text
    
    else:
        return("Erro ao acessar a página: {response.status_code}")