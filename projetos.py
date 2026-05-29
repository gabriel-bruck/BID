import os
import time
import pandas as pd
from playwright.sync_api import sync_playwright

class BID:
    def __init__(self, input_file, base_download_path="./documentos_baixados_teste", output_csv="resultado_links_documentos2.csv", headless=True):
        self.input_file = input_file
        self.base_download_path = base_download_path
        self.output_csv = output_csv
        self.headless = headless
        self.error_log = []
        self.links_mapeados = []  # Lista que acumula o histórico
        self.context = None
        self.page = None
        self.playwright = None
        os.makedirs(self.base_download_path, exist_ok=True)

    def _get_page(self, p):
        """Reinicia o navegador controlando o comportamento do Modo Oculto Disfarçado ou Visível."""
        if self.page is None or self.page.is_closed():
            extra_args = [
                "--no-sandbox", 
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1920,1080",
                "--ignore-certificate-errors"
            ]
            
            if self.headless:
                print("--- Inicializando navegador (Modo Oculto Disfarçado: headless=new) ---")
                extra_args.append("--headless=new")
            else:
                print("--- Inicializando navegador (Modo Visível com Interface) ---")

            self.context = p.chromium.launch_persistent_context(
                user_data_dir="./playwright_session",
                headless=False, 
                args=extra_args,
                accept_downloads=True,
                no_viewport=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        return self.page

    def log_error(self, operation, url, error_msg):
        self.error_log.append({"Operation": operation, "URL": url, "Error": str(error_msg)})
        # Quebra uma nova linha para o erro ser impresso sem bagunçar a linha de progresso dinâmico
        print(f"\n[!] Erro registrado em {operation}: {error_msg}")

    def obter_documentos(self):
        df_input = pd.read_excel(self.input_file)
        operacoes_unicas = df_input['Operation Number'].dropna().unique()
        total_projetos = len(operacoes_unicas)
        
        print(f"Iniciando extração de {total_projetos} projetos...")
        
        with sync_playwright() as p:
            for index, operation in enumerate(operacoes_unicas, 1):
                op = str(operation).strip()
                project_folder = os.path.join(self.base_download_path, op)
                
                baixados = 0
                pulados = 0
                
                try:
                    page = self._get_page(p)
                    url_projeto = f"https://www.iadb.org/en/project/{op}"
                    
                    # Atualiza o status limpando a linha inteira primeiro (\r\033[K)
                    print(f"\r\033[K[{index}/{total_projetos}] Acessando: {op}...", end="", flush=True)
                    
                    page.goto(url_projeto, wait_until="networkidle", timeout=60000)
                    page.wait_for_timeout(2000)
                    
                    links_elements = page.locator("a[href*='document.cfm']").all()
                    
                    document_links = set()
                    for link in links_elements:
                        href = link.get_attribute("href")
                        if href:
                            if href.startswith("/"):
                                href = f"https://www.iadb.org{href}"
                            elif not href.startswith("http"):
                                href = f"https://www.iadb.org/{href}"
                            document_links.add(href)
                    
                    if not document_links:
                        self.links_mapeados.append({
                            "Operation Number": op,
                            "Project URL": url_projeto,
                            "Document URL": "Nenhum documento encontrado"
                        })
                        print(f"\r\033[K[{index}/{total_projetos}] Projeto {op}: Nenhum documento encontrado.")
                        continue
                    
                    os.makedirs(project_folder, exist_ok=True)
                    arquivos_existentes = os.listdir(project_folder)
                    
                    for href in sorted(document_links):
                        self.links_mapeados.append({
                            "Operation Number": op,
                            "Project URL": url_projeto,
                            "Document URL": href
                        })
                        
                        try:
                            doc_id = href.split('id=')[-1] if 'id=' in href else href.split('/')[-1]
                            doc_id = doc_id.split('&')[0] 
                            
                            if any(arq.startswith(doc_id) for arq in arquivos_existentes):
                                pulados += 1
                                continue
                            
                            # Mostra dinamicamente qual ID está baixando na mesma linha, limpando fantasmas
                            print(f"\r\033[K[{index}/{total_projetos}] {op} -> Baixando ID {doc_id}...", end="", flush=True)
                            response = page.context.request.get(href)
                            
                            if response.status == 200:
                                content_disposition = response.headers.get("content-disposition", "")
                                
                                
                                if "filename=" in content_disposition:
                                    _, extensao = os.path.splitext(content_disposition.split("filename=")[-1].strip('"'))
                                
                                nome_final = f"{doc_id}{extensao}"
                                caminho_final = os.path.join(project_folder, nome_final)
                                
                                with open(caminho_final, "wb") as f:
                                    f.write(response.body())
                                
                                baixados += 1
                            else:
                                self.log_error(op, href, f"Falha no download. Status HTTP: {response.status}")
                                
                            time.sleep(1.5)
                            
                        except Exception as e:
                            self.log_error(op, href, f"Erro ao processar download do link: {e}")
                            
                except Exception as e:
                    self.log_error(op, "Pagina do projeto", f"Falha ao acessar: {e}")
                    if self.context:
                        try: self.context.close()
                        except: pass
                    self.page = None 
                
                # --- SALVAMENTO INCREMENTAL SILENCIOSO ---
                # Removeu-se o print("[Progresso Salvo]") que pulava linha e destruía o terminal
                if self.links_mapeados:
                    df_resultado = pd.DataFrame(self.links_mapeados)
                    df_resultado.to_csv(self.output_csv, index=False, encoding='utf-8')

                # --- SINAL COMPLETO E LIMPO ---
                # Cospe apenas UMA linha definitiva por projeto concluído
                print(f"\r\033[K[{index}/{total_projetos}] Projeto {op}: {len(document_links)} links mapeados | {baixados} baixados | {pulados} já existiam.")

            if self.error_log:
                pd.DataFrame(self.error_log).to_csv("log_erros.csv", index=False)
            print("\n=== Execução de todos os projetos finalizada! ===")

