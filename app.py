import streamlit as st
import json
import os
from mealie_parser import parse_recipe_to_schema_org

st.set_page_config(page_title="Mealie Recipe Parser", layout="centered")

st.title("Importateur de Recettes Mealie")
st.markdown("Colle ton texte de recette ci-dessous et génère le JSON.")

raw_text = st.text_area("Texte de la recette", height=300, placeholder="Colle ici le texte brut de ta recette...")

if st.button("Générer le JSON", type="primary"):
    if not raw_text:
        st.warning("Merci de coller du texte d'abord.")
    else:
        with st.spinner("La recette arrive..."):
            try:
                recipe_data = parse_recipe_to_schema_org(raw_text)
                
                json_str = json.dumps(recipe_data, ensure_ascii=False, indent=2)
                
                st.success("Recette convertie avec succès !")
                
                st.code(json_str, language="json")
                
                with st.expander("Aperçu des données extraites"):
                    st.write(recipe_data)
                    
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")

st.markdown("---")
st.caption("Basé sur OpenAI & Schema.org Recipe pour générer des recettes mealie.io")
st.caption("Développé par Alexandre Eberhardt")
