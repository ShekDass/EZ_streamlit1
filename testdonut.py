import streamlit as st
import run_prediction as model
#from run_prediction import image_to_json
from PIL import Image

st.title('Test Donut Model')
uploaded_file = st.file_uploader("Choose a image file", type="jpg")

if uploaded_file is not None:
    input_pil = Image.open(uploaded_file)
    rgb_testsample = input_pil.convert('RGB')
    # rgb_testsample.show()
    st.write("Reading Image and printing the JSON output")
    json_output = model.image_to_json(rgb_testsample)
    st.write(json_output)
    st.balloons()


# # input_image = 'C:\Anand\Great Lakes\Capstone\smartenroll\sparrowproject\sparrow\sparrow-ui\docs\smartenroll-images\Enrollment_David_Rizzuto.jpg'
# input_pil = Image.open(r'C:\Anand\Great Lakes\Capstone\smartenroll\sparrowproject\sparrow\sparrow-ui\docs\smartenroll-images\Enrollment_David_Rizzuto.jpg')


# rgb_testsample = input_pil.convert('RGB')





