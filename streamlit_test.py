from PIL import Image
import streamlit as st

uploaded_file = st.file_uploader("Choose a image file", type="jpg")

if uploaded_file is not None:
    input_pil = Image.open(uploaded_file)
    rgb_testsample = input_pil.convert('RGB')
    rgb_testsample.show()