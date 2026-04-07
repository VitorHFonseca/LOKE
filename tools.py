import requests
import random
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO DE AUXÍLIO ---
def get_now_br():
    return datetime.now(pytz.timezone('America/Sao_Paulo'))

# 1. FINANÇAS & MERCADO (Crucial para seus REITs e Dividendos)
def get_finance_hub():
    try:
        # Cotações em tempo real (AwesomeAPI)
        r = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL")
        data = r.json()
        usd = float(data['USDBRL']['bid'])
        btc = float(data['BTCBRL']['bid'])
        return f"📊 **Mercado:** Dólar R$ {usd:.2f} | Bitcoin R$ {btc:,.2f}. Olho nos seus ativos nos EUA! 📈"
    except: return "⚠️ Erro ao conectar com a Bolsa."

# 2. BRASIL API (Utilidades para Corretagem e Betim)
def get_brasil_hub(tipo, parametro=None):
    try:
        if tipo == "feriado":
            ano = get_now_br().year
            r = requests.get(f"https://brasilapi.com.br/api/feriados/v1/{ano}")
            prox = [f for f in r.json() if f['date'] > get_now_br().strftime('%Y-%m-%d')][0]
            return f"🗓️ **Próximo Feriado:** {prox['name']} em {prox['date']}."
        elif tipo == "cep" and parametro:
            r = requests.get(f"https://brasilapi.com.br/api/cep/v1/{parametro}")
            d = r.json()
            return f"📍 **Endereço:** {d['street']}, {d['neighborhood']} - {d['city']}/{d['state']}."
    except: return "⚠️ BrasilAPI indisponível."

# 3. GLOBAL & ESPAÇO (Seu interesse em Sci-Fi)
def get_global_hub():
    try:
        # ISS (Onde está a estação espacial?)
        r_iss = requests.get("http://api.open-notify.org/iss-now.json")
        pos = r_iss.json()['iss_position']
        # News (Notícias espaciais)
        r_news = requests.get("https://api.spaceflightnewsapi.net/v4/articles/?limit=1")
        news = r_news.json()['results'][0]['title']
        return f"🚀 **Espaço:** {news}\n📡 **ISS agora sobre:** Lat {pos['latitude']}, Lon {pos['longitude']}."
    except: return "⚠️ Falha na telemetria espacial."

# 4. GEEK & LIFESTYLE (Culinária e o Luke)
def get_geek_lifestyle():
    try:
        # Conselho aleatório
        r_adv = requests.get("https://api.adviceslip.com/advice").json()
        advice = r_adv['slip']['advice']
        # Fato sobre Cães (Pro Luke)
        r_dog = requests.get("https://dogapi.dog/api/v2/facts").json()
        dog = r_dog['data'][0]['attributes']['body']
        # Drink (Para acompanhar sua massa)
        r_drk = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php").json()
        drink = r_drk['drinks'][0]['strDrink']
        
        return f"💡 **Conselho:** {advice}\n🐾 **Pro Luke:** {dog}\n🍸 **Drink Sugerido:** {drink}"
    except: return "⚠️ Erro no módulo Lifestyle."

# 5. MUNDO (Clima Global & Terremotos)
def get_world_alerts():
    try:
        r = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=1").json()
        eq = r['features'][0]['properties']
        return f"🌍 **Alerta Global:** Terremoto Mag {eq['mag']} em {eq['place']}."
    except: return "⚠️ Sem alertas globais."