import streamlit as st
import json
from PIL import Image
from io import BytesIO
import base64
# import run_prediction as model
import os
# from pdf2image import convert_from_path, convert_from_bytes
import fitz  # PyMuPDF library for rendering PDFs

# Download the fixed image
def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

def save_json(output):
    # target_json = json.dumps(target, indent=2)
    prediction_json = json.dumps(output, indent=2)

    with open('prediction.json', 'w') as prediction_file:
        prediction_file.write(prediction_json)
        #return prediction_file

def render_pdf_as_image(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    pdf_page = pdf_document[0]  # Assuming you want to display the first page

    pdf_image = pdf_page.get_pixmap()
    pil_image = Image.frombytes("RGB", [pdf_image.width, pdf_image.height], pdf_image.samples)

    return pil_image


def image_to_json(upload):
    col1, col2 = st.columns(2, gap="medium")
    # print("Print from image_to_json", upload)

    if upload.type == "application/pdf":
        pdf_image = render_pdf_as_image(upload)
        # st.write(pdf_image)

        col1.write("Paper Enrollment Form Image :camera:")
        col1.image(pdf_image)

        col2.write("Converted JSON :wrench:")
        # json_output = model.image_to_json(pdf_image) # Modify to call the JSON output

        json_output = """
        {
       "image_id": "100",
        "insurancecompany": "HIGHMARK",
        "formheader": "ENROLLMENT/WAIVER FORM",
        "I EMPLOYEE/CONTRACT HOLDER INFORMATION": [
        {
            "Effective Date": "05/01/2023",
            "Employer/Group Name": "UNITED PARCEL SERVICE",
            "Group Number": "17381991",
            "Payroll Location": " ",
            "First Name": "DAVID",
            "MI": "A",
            "Last Name": "BASS",
            "Social Security Number": "990-90-3464",
            "Address": "85 SEYMOUR ST",
            "City": "HARTFORD",
            "State": "RI",
            "Zip": "6106",
            "County": " ",
            "Home/Cell Phone": "765-239-9623",
            "Marital Status": "Married",
            "Enrollment Status": "Active Employee",
            "Full-Time Hire": "07/16/2022",
            "Hours Worked Per Week": " ",
            "Gender": "Male",
            "Date of Birth": "12/14/1974",
            "Age": "49",
            "Product Selection": "Dental"
              }
          ],
          "SPOUSE/DOMESTIC PARTNER": [
              {
            "First Name": "LAKSHMI",
            "MI": "",
            "Last Name": "BASS",
            "Relationship to You": "Spouse",
            "Social Security Number": "114-91-3731",
            "Gender": "Female",
            "Date of Birth": "01/01/1952",
            "Age": "71",
            "Product Selection": "Dental"
              }
          ],
          "DEPENDENT CHILD": [
              {
            "First Name": "PAUL",
            "MI": " ",
            "Last Name": "BASS",
            "Relationship to You": "",
            "Social Security Number": "",
            "Gender": "Male",
            "Date of Birth": "09/18/1995",
            "Age": "28",
            "Product Selection": "Dental",
            "Dependent Status if Age 26 or Older": " "
                }
            ]
        }
        """

        col2.write(json_output)

        json_string = json.dumps(json_output)

        st.download_button\
        (
            label="Download JSON",
            file_name="prediction.json",
            data=json_string,
            mime="application/json",
        )

    else:
        image = Image.open(upload)
        # st.write(image)

        col1.write("Paper Enrollment Form Image :camera:")
        col1.image(image)

        input_pil = Image.open(upload)
        rgb_testsample = input_pil.convert('RGB')
        # rgb_testsample.show()
        col2.write("Converted JSON :wrench:")
        json_output = model.image_to_json(rgb_testsample)
        col2.write(json_output)

        json_string = json.dumps(json_output)

        st.download_button\
        (
            label="Download JSON",
            file_name="prediction.json",
            data=json_string,
            mime="application/json",
        )

##Previous approach to convert pdf to png - not used anymore
def pdf_to_png(pdf_file, dpi=300):
    images = convert_from_bytes(pdf_file.read(), dpi=dpi, poppler_path=r"C:\Program Files\Poppler\poppler-23.07.0\poppler-23.07.0\Library\bin")
    png_images = []

    for i, image in enumerate(images):
        png_image = image.convert("RGB")
        png_images.append(png_image)

    print("Print from pdf_to_png",png_images)
    return png_images

def main():

    st.set_page_config\
    (
        layout="wide",
        page_title="EazyEnroll",
        page_icon=":gear:",
        initial_sidebar_state="expanded",
    )

    menu = ["Home", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":

        # with st.form('Form 1', clear_on_submit=True):
        st.write("## Extract data from Healthcare Enrollment Form to a JSON format")
        st.divider()

        st.subheader("Upload an Enrollment form to create the respective JSON")
        st.caption("_AI-predicted JSON can be downloaded after the Converted JSON renders on the screen. Use Download JSON button._")

        # st.write("### Upload an image",)
        # if st.form_submit_button('Upload Image'):
        my_upload = st.file_uploader("Choose an Image file", type=["png", "jpg", "jpeg","pdf"],label_visibility="collapsed")
        # st.write(my_upload)
        st.divider()

        if my_upload is not None:
            image_to_json(upload=my_upload)


        # if my_upload is not None:
        #     # st.write(my_upload.name)
        #     if my_upload.type == "application/pdf":
        #         # st.write(my_upload.type)
        #         pdf_image = render_pdf_as_image(my_upload)
        #
        #         # my_upload_conv = pdf_to_png(pdf_file=my_upload)
        #         # st.write(my_upload_conv)
        #         # if my_upload_conv:
        #              # image_to_json(upload=my_upload_conv[0])
        #     else:
        #         image_to_json(upload=my_upload)

    else:
        st.subheader("About")
        st.write("Built with Streamlit")
        st.write("Web App to parse a Healthcare Enrollment form to it's JSON counterpart")
        st.write("Thank you for using our app")

if __name__ == '__main__':
	main()

