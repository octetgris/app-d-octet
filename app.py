import streamlit as st
import openai
import json

# Configuration
st.set_page_config(page_title="Coach Wellness", page_icon="🥗")
st.title("🥗 Mon Coach Wellness")

# Sécurité : On récupère la clé depuis les "Secrets" de Streamlit
api_key = st.sidebar.text_input("Clé API OpenAI", type="password")

if 'frigo' not in st.session_state:
    st.session_state.frigo = ["oeufs", "poulet", "riz", "pommes"]
if 'courses' not in st.session_state:
    st.session_state.courses = []

# --- INTERFACE ---
st.sidebar.header("🛒 Mon Frigo")
st.sidebar.write(", ".join(st.session_state.frigo))

st.sidebar.header("📝 Liste de courses")
st.sidebar.write(", ".join(st.session_state.courses) if st.session_state.courses else "Vide")

evenement = st.text_area("Que s'est-il passé ?", placeholder="J'ai mangé...")
temps = st.select_slider("Temps pour cuisiner (min)", options=["10", "20", "30", "45", "60"])

if st.button("Générer ma solution"):
    if not api_key:
        st.error("Ajoute ta clé API à gauche !")
    else:
        client = openai.OpenAI(api_key=api_key)
        prompt = f"Utilisateur a mangé : {evenement}. Frigo: {st.session_state.frigo}. Temps: {temps}. Réponds en JSON avec 'analyse', 'recette', 'ingredients_utilises', 'ingredients_manquants'."
        
        with st.spinner('Analyse...'):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            data = json.loads(response.choices[0].message.content)
            
            # Mise à jour des stocks
            for item in data.get('ingredients_manquants', []):
                if item not in st.session_state.courses:
                    st.session_state.courses.append(item)
            
            st.success(data['analyse'])
            st.subheader(data['recette'])
            st.write(data.get('instructions', 'Cuisinez les ingrédients avec amour !'))
