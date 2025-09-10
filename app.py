from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

import os
import sys

# Ensure src/ is on sys.path when running on platforms that do not install the package automatically
repo_root = Path(__file__).resolve().parent
src_dir = repo_root / "src"
if src_dir.exists() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from euri_codegen.config import Settings
from euri_codegen.euri_client import Euri
from euri_codegen.catalog_loader import load_catalog
from euri_codegen.codegen.generator import generate_code_for_topic, explain_code
from euri_codegen.codegen.optimizer import optimize_code
from euri_codegen.models import validate_specs


# Load env variables from .env if present
load_dotenv()

st.set_page_config(page_title="Vijay AI CodeGen", layout="wide")
st.title("Vijay AI CodeGen: Python Code Generator & Optimizer")

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    try:
        settings = Settings.load()
        st.success("EURI_API_KEY found")
    except Exception as e:
        st.error(f"Config error: {e}")
        st.stop()

    temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=settings.temperature, step=0.05)
    max_tokens = st.number_input("Max tokens", min_value=256, max_value=32000, value=settings.max_tokens, step=256)
    model = st.selectbox("Model", ["gpt-4.1-nano", "gpt-4.1-mini", "gemini-2.5-flash"], index=0)
    out_dir = Path(st.text_input("Output directory", value="generated"))

# Memoize Euri client
@st.cache_resource(show_spinner=False)
def get_euri(_settings: Settings) -> Euri:
    cfg = Settings(api_key=_settings.api_key, model=model, temperature=temp, max_tokens=max_tokens)
    return Euri(cfg)


euri = get_euri(settings)

# Tabs for features
tab_gen, tab_opt, tab_explain, tab_catalog, tab_doctor = st.tabs(
    ["Generate", "Optimize", "Explain", "Catalog", "Doctor"]
)


with tab_gen:
    st.subheader("Generate DSA Implementation + Tests")
    specs_data = load_catalog()
    try:
        specs = validate_specs(specs_data)
    except Exception as e:
        st.error(f"Catalog validation failed: {e}")
        st.stop()

    id_to_spec = {s.id: s for s in specs}
    topic_id = st.selectbox("Topic", options=list(id_to_spec.keys()))
    do_all = st.checkbox("Generate all topics", value=False)

    if st.button("Generate", type="primary"):
        out_dir.mkdir(parents=True, exist_ok=True)
        if do_all:
            for sp in specs:
                with st.status(f"Generating {sp.id}…", expanded=False):
                    try:
                        module_path, test_path = generate_code_for_topic(
                            euri, sp.model_dump(), out_dir
                        )
                        st.success(f"OK: {module_path} | {test_path}")
                    except Exception as ex:
                        st.error(f"Failed {sp.id}: {ex}")
        else:
            sp = id_to_spec[topic_id]
            with st.spinner(f"Generating {sp.id}…"):
                try:
                    module_path, test_path = generate_code_for_topic(
                        euri, sp.model_dump(), out_dir
                    )
                except Exception as ex:
                    st.error(f"Generation failed: {ex}")
                else:
                    code = Path(module_path).read_text(encoding="utf-8")
                    tests = Path(test_path).read_text(encoding="utf-8")
                    st.success(f"Generated: {module_path}")
                    st.code(code, language="python")
                    st.download_button(
                        "Download module", data=code, file_name=Path(module_path).name, mime="text/x-python"
                    )
                    st.divider()
                    st.success(f"Tests: {test_path}")
                    st.code(tests, language="python")
                    st.download_button(
                        "Download tests", data=tests, file_name=Path(test_path).name, mime="text/x-python"
                    )


with tab_opt:
    st.subheader("Optimize Python File")
    uploaded = st.file_uploader("Upload a .py file to optimize", type=["py"]) 
    level = st.selectbox("Level", ["all", "one", "readability", "performance", "memory"], index=0)

    if st.button("Optimize", type="primary"):
        if not uploaded:
            st.warning("Please upload a .py file.")
        else:
            code_text = uploaded.read().decode("utf-8")
            with st.spinner("Optimizing…"):
                try:
                    new_code = optimize_code(euri, code_text, level=level)  # strips code fences internally
                except Exception as ex:
                    st.error(f"Optimization failed: {ex}")
                else:
                    st.success("Optimized code:")
                    st.code(new_code, language="python")
                    st.download_button(
                        "Download optimized.py",
                        data=new_code,
                        file_name="optimized.py",
                        mime="text/x-python",
                    )


with tab_explain:
    st.subheader("Explain Python Code")
    uploaded2 = st.file_uploader("Upload a .py file to explain", type=["py"], key="explain_upl")
    if st.button("Explain", type="primary"):
        if not uploaded2:
            st.warning("Please upload a .py file.")
        else:
            code_text = uploaded2.read().decode("utf-8")
            with st.spinner("Explaining…"):
                try:
                    explanation = explain_code(euri, code_text)
                except Exception as ex:
                    st.error(f"Explain failed: {ex}")
                else:
                    st.text(explanation)
                    st.download_button(
                        "Download explanation.txt",
                        data=explanation,
                        file_name="explanation.txt",
                        mime="text/plain",
                    )


with tab_catalog:
    st.subheader("Catalog")
    st.write("These specs drive generation. Edit the JSON to extend.")
    st.json(specs_data)
    st.caption("File: src/euri_codegen/catalog/dsa_catalog.json")


with tab_doctor:
    st.subheader("Environment Doctor")
    ok = True
    try:
        _ = Settings.load()
        st.success("EURI_API_KEY detected")
    except Exception as e:
        ok = False
        st.error(f"Config error: {e}")
    st.write(f"Default model: {model}")
    st.write(f"Temperature: {temp}")
    st.write(f"Max tokens: {max_tokens}")
    if ok:
        st.success("Environment looks good.")
