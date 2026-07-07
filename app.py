import streamlit as st
import requests
import stripe
from supabase import create_client

DATAFORSEO_LOGIN = st.secrets["DATAFORSEO_LOGIN"]
DATAFORSEO_PASSWORD = st.secrets["DATAFORSEO_PASSWORD"]
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def hamta_sokdata(sokord):
    url = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
    data = [{"keywords": [sokord], "location_code": 2484, "language_code": "es"}]
    svar = requests.post(url, auth=(DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD), json=data)
    return svar.json()

def skapa_checkout(email):
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    price_id = st.secrets["STRIPE_PRICE_ID"]
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        customer_email=email,
        success_url="https://seo-espana-69mv3xbfba8ajnhmodf9jg.streamlit.app?paid=true",
        cancel_url="https://seo-espana-69mv3xbfba8ajnhmodf9jg.streamlit.app",
    )
    return session.url

def ar_prenumerant(email):
    res = supabase.table("subscribers_mexico").select("email").eq("email", email).execute()
    return len(res.data) > 0

def spara_prenumerant(email):
    if not ar_prenumerant(email):
        supabase.table("subscribers_mexico").insert({"email": email}).execute()

st.title("SEO México")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.subheader("Iniciar sesión / Crear cuenta")
    with st.form("login_form"):
        email = st.text_input("Correo electrónico")
        senha = st.text_input("Contraseña", type="password")
        col1, col2 = st.columns(2)
        with col1:
            entrar = st.form_submit_button("Entrar")
        with col2:
            criar = st.form_submit_button("Crear cuenta")
    if entrar:
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            st.session_state.user = res.user
            st.rerun()
        except Exception as e:
            st.error("Correo o contraseña incorrectos.")
    if criar:
        try:
            res = supabase.auth.sign_up({"email": email, "password": senha})
            st.success("¡Cuenta creada! Verifica tu correo para confirmar.")
        except Exception as e:
            st.error("Error al crear cuenta.")
else:
    params = st.query_params
    if params.get("paid") == "true":
        spara_prenumerant(st.session_state.user.email)
        st.success("¡Pago confirmado! ¡Bienvenido a SEO México Pro!")

    prenumerant = ar_prenumerant(st.session_state.user.email)

    st.write(f"Bienvenido, {st.session_state.user.email}")
    if st.button("Salir"):
        st.session_state.user = None
        st.rerun()

    st.divider()

    if prenumerant:
        st.subheader("Investigación de palabras clave")
        sokord = st.text_input("Introduce una palabra clave:", placeholder="ej: agencia de marketing Ciudad de México")
        if st.button("Buscar") and sokord:
            with st.spinner("Buscando datos en Google México..."):
                resultat = hamta_sokdata(sokord)
                try:
                    data = resultat['tasks'][0]['result'][0]
                    volym = data.get('search_volume', 0)
                    konkurrens = data.get('competition', 'N/A')
                    cpc = data.get('cpc', 0)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Volumen / mes", f"{volym:,}".replace(",", "."))
                    col2.metric("Competencia", str(konkurrens).capitalize())
                    col3.metric("CPC medio", f"€ {cpc:.2f}" if cpc else "N/A")
                    st.success(f"Datos de Google México para: {sokord}")
                except:
                    st.error("No se encontraron datos. Prueba otra palabra clave.")
    else:
        st.info("Suscríbete para acceder a la investigación de palabras clave.")
        if st.button("Suscribirse a SEO México Pro - €29/mes"):
            url = skapa_checkout(st.session_state.user.email)
            st.markdown(f"[Haz clic aquí para pagar]({url})")

st.divider()
st.caption("SEO México - Hecho para el mercado mexicano")