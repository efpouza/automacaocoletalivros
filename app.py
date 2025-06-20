import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


# Configura o navegador para rodar no modo headless (sem interface gráfica)
def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa sem abrir janela
    chrome_options.add_argument("--no-sandbox")  # Necessário para ambientes como o Streamlit Cloud
    chrome_options.add_argument("--disable-dev-shm-usage")  # Para evitar problemas de memória compartilhada
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Exemplo de uso no Streamlit
st.title("Automação com Selenium no Streamlit Cloud")

if st.button("Iniciar automação"):
    with st.spinner("Abrindo navegador..."):
        try:
            driver = iniciar_driver()
            driver.get("https://www.google.com")
            time.sleep(2)

            st.success("Página carregada com sucesso!")
            st.write("Título da página:", driver.title)

            # Fecha o navegador
            driver.quit()

        except Exception as e:
            st.error("Erro ao executar o Selenium.")
            st.exception(e)


def raspar_livros(progress_bar, status_text, porcentagem_texto):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    driver.get('https://books.toscrape.com/')
    books = []
    current_page = 1

    while True:
        book_elements = driver.find_elements(By.CSS_SELECTOR, 'article.product_pod')

        for book in book_elements:
            title = book.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a').get_attribute('title')
            price = book.find_element(By.CLASS_NAME, 'price_color').text
            availability = book.find_element(By.CLASS_NAME, 'availability').text.strip()
            rating = book.find_element(By.CLASS_NAME, 'star-rating').get_attribute('class').split()[-1]

            books.append([title, price, availability, rating])

        progresso = min((current_page / 50), 1.0)
        progresso_percentual = int(progresso * 100)
        progress_bar.progress(progresso)
        status_text.markdown(f"<div style='text-align: center;'>📖 Coletando página {current_page}...</div>", unsafe_allow_html=True)
        porcentagem_texto.markdown(f"<div style='text-align: center;'>Progresso: <strong>{progresso_percentual}%</strong></div>", unsafe_allow_html=True)

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'li.next > a')
            next_page_url = next_button.get_attribute('href')
            driver.get(next_page_url)
            current_page += 1
            time.sleep(0.3)
        except NoSuchElementException:
            break

    driver.quit()
    df = pd.DataFrame(books, columns=["Título", "Preço", "Disponibilidade", "Avaliação"])
    df.to_csv("livros.csv", index=False, encoding="utf-8")
    return df

# --- Interface Streamlit ---
st.set_page_config(page_title="📚 Raspador de Livros", layout="wide")

# Título centralizado
st.markdown("<h1 style='text-align: center;'>📚 Coleta Livros - Loja Virtual</h1>", unsafe_allow_html=True)
st.markdown("---")

# Área fixa para barra de progresso e status
status_text = st.empty()
progress_bar = st.progress(0)
porcentagem_texto = st.empty()

# Exibir mensagem inicial
status_text.markdown("<div style='text-align: center;'>⏳ Aguardando ação do usuário...</div>", unsafe_allow_html=True)
porcentagem_texto.markdown("<div style='text-align: center;'>Progresso: <strong>0%</strong></div>", unsafe_allow_html=True)

# Espaço antes dos botões
st.markdown("###")

# Layout dos botões
col1, col2 = st.columns([1, 1])

with col1:
    iniciar = st.button("🔍 Iniciar Coleta", use_container_width=True)

with col2:
    limpar = st.button("🧹 Limpar", use_container_width=True)

st.markdown("---")

# Processamento
if iniciar:
    with st.spinner("Coletando dados..."):
        df_resultado = raspar_livros(progress_bar, status_text, porcentagem_texto)
        status_text.markdown(f"<div style='text-align: center;'>✅ Coleta finalizada com {len(df_resultado)} livros.</div>", unsafe_allow_html=True)
        porcentagem_texto.markdown("<div style='text-align: center;'>Progresso: <strong>100%</strong></div>", unsafe_allow_html=True)
        progress_bar.progress(1.0)
        st.dataframe(df_resultado, use_container_width=True)
        st.download_button("⬇️ Baixar CSV", df_resultado.to_csv(index=False), file_name="livros.csv", mime="text/csv")

# Limpeza (reinicializa o app)
if limpar:
    st.rerun()
