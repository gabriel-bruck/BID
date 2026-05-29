
from projetos import BID


#input_file é o arquivo Excel contendo a coluna "Operation Number" com os números das operações a serem processadas.
#base_download_path é o diretório onde os documentos baixados serão armazenados, organizados
#output_csv é o nome do arquivo CSV onde os links mapeados serão salvos.
#headless é um parâmetro booleano que controla se o navegador deve ser executado em
#modo oculto (sem interface gráfica) ou visível (com interface gráfica). O valor padrão é True, o que significa que o navegador será executado em modo oculto.

coletor = BID(input_file="projetos_exemplo.xlsx",base_download_path="./documentos_baixados", output_csv="resultado_links_documentos.csv", headless=True)
coletor.obter_documentos()