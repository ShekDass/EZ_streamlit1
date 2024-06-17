import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import aiplatform

#from google.colab import files
from google.oauth2 import service_account
import google.auth
import google.auth.transport.requests

from google.cloud import aiplatform
from google.cloud import storage
import vertexai
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)

from PIL import Image
from pdf2image import convert_from_path
import fitz
import io
import os
import json
import time
import pandas as pd
import IPython.display
# from IPython.display import display, Image

# Path to your service account key file
key_file = 'C:/Users/Sudhaa/PycharmProjects/pythonProject/.venv/eazyenroll_vertexai_user.json'

# Google Cloud project ID and bucket name
project_id = 'banded-anvil-426308-i1'
bucket_name = 'eazyenroll_test_gemini'
destination_folder = 'input/'

# Initialize Vertex AI
# credentials = service_account.Credentials.from_service_account_file(key_file)
# aiplatform.init(project=project_id, credentials=credentials, location="us-central1")

def upload_to_gcs(file_content, bucket_name, destination_blob_name, credentials):
    """Uploads a file to the bucket."""
    storage_client = storage.Client(credentials=credentials, project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    # blob.upload_from_string(file.read(), content_type='application/pdf')
    blob.upload_from_string(file_content, content_type='application/pdf')
    return f'gs://{bucket_name}/{destination_blob_name}'

def initialize_vertex_ai(key_file, project_id, location, model_id):
    try:
        # Upload the service account JSON key file
        # uploaded = files.upload()
        # service_account_file = list(uploaded.keys())[0]

        # Define the required scope
        SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

        # Authenticate using the service account
        global_credentials = service_account.Credentials.from_service_account_file(
            key_file, scopes=SCOPES
        )

        # Set the environment variable for authentication
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file

        # Verify the credentials
        auth_req = google.auth.transport.requests.Request()
        global_credentials.refresh(auth_req)

        # Optionally, set the project ID
        # !gcloud config set project {project_id}

        print("Authentication successful.")

        # Initialize AI Platform SDK
        aiplatform.init(credentials=global_credentials, project=project_id, location="us-central1")

        # Initialize Vertex AI SDK
        vertexai.init(credentials=global_credentials, project=project_id, location=location)

        # Load Generative Model
        model = GenerativeModel(model_id)

        return model  # Return the initialized model instance

    except Exception as e:
        print(f"Error initializing AI Platform and Vertex AI: {e}")
        return None

prompt = """
{
	"insurancecompany": "",
	"form name": "",
    "I EMPLOYEE/CONTRACT HOLDER INFORMATION": [
        {
            "Effective Date": "",
            "Employer/Group Name": "",
            "Group Number": "",
            "Payroll Location": "",
            "First Name": "",
            "MI": "",
            "Last Name": "",
            "Social Security Number": "",
            "Address": "",
            "City": "",
            "State": "",
            "Zip": "",
            "County": " ",
            "Home/Cell Phone": "",
            "Marital Status": "",
            "Enrollment Status": "",
            "Full-Time Hire": "",
            "Hours Worked Per Week": "",
            "Gender": "",
            "Date of Birth": "",
            "Age": "",
            "Product Selection": ""
        }
    ],
    "SPOUSE/DOMESTIC PARTNER": [
        {
            "First Name": "",
            "MI": "",
            "Last Name": "",
            "Relationship to You": "",
            "Social Security Number": "",
            "Gender": "",
            "Date of Birth": "",
            "Age": "",
            "Product Selection": ""
        }
    ],
    "DEPENDENT CHILD": [
        {
            "First Name": "",
            "MI": "",
            "Last Name": "",
            "Relationship to You": "",
            "Social Security Number": "",
            "Gender": "",
            "Date of Birth": "",
            "Age": "",
            "Product Selection": "",
            "Dependent Status if Age 26 or Older": ""
        }
    ]
}
"""

def generate_content(pdf_file_uri, prompt, model):
    try:
        # Prepare the input for the model
        # content_dict = {
        #     "document": {"gcs_url": pdf_file_uri},
        #     "prompt": prompt
        # }

        print("pdf_file_uri:", pdf_file_uri)
        pdf_file = Part.from_uri(pdf_file_uri, mime_type="application/pdf")
        print("After Part:", pdf_file)

        # Prepare contents for model generation
        contents = [pdf_file, prompt]
        # prompt_part = Part.text(prompt)
        # contents = [pdf_file, prompt_part]
        print("Print Contents:", contents)

        # # Generate content using the model
        # response = model.predict(content_dict)

        # # Convert response to dictionary
        # response_dict = json.loads(response.text)
        # return response_dict

        # Generate content using the model
        response = model.generate_content(contents = contents)

        # Print the generated text (optional)
        print("Generated text:")
        print(response.text)

        # Determine the input PDF filename from the URI
        input_pdf_filename = os.path.basename(pdf_file_uri)

        # Prepare output JSON filename
        output_json = os.path.splitext(input_pdf_filename)[0] + ".json"

        # Assume response.text contains the JSON string
        try:
            json_data = json.loads(response.text)
        except json.JSONDecodeError as decode_error:
            print(f"JSON decode error: {decode_error}")
            return

        # Assume response.text contains the JSON string
        json_data = json.loads(response.text)

        # Write JSON data to file
        with open(output_json, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

        print(f"JSON output: {output_json}")
        return json_data

    except Exception as e:
        print(f"Error generating content and saving as JSON: {e}")
        return None


        # # Load PDF file from URI
        # pdf_file = Part.from_uri(pdf_file_uri, mime_type="application/pdf")
        # print("After Part:",pdf_file)
        #
        # # Prepare contents for model generation
        # contents = [pdf_file, prompt]
        # # print("contents:",contents)
        # # Generate content using the model
        # response = model.generate_content(conten

        # # Print the generated text (optional)
        # print("Generated text:")
        # print(response.text)
        #
        # # Convert response to dictionary
        # response_dict = response.to_dict()
        #
        # return response_dict

    #     # Determine the input PDF filename from the URI
    #     input_pdf_filename = os.path.basename(pdf_file_uri)
    #
    #     # Prepare output JSON filename
    #     output_json = os.path.splitext(input_pdf_filename)[0] + ".json"
    #
    #     # Write JSON data to file
    #     with open(output_json, 'w') as json_file:
    #         json.dump(response.to_dict(), json_file, indent=4)
    #
    #     print(f"JSON output: {output_json}")
    #
    # except Exception as e:
    #     print(f"Error generating content and saving as JSON: {e}")


def call_vertex_ai_gemini(gcs_uri, prompt):
    """Call Vertex AI Gemini model to generate JSON from PDF."""
    # model_name = "projects/eazyenroll-poc/locations/us-central1/models/gemini-1.5-flash-001"
    model_name = "gemini-1.5-flash-001"

    model = aiplatform.Model(model_name=model_name)
    response = model.predict(instances=[{"content": gcs_uri, "prompt": prompt}])
    return response.predictions[0]

def display_pdf_as_image(pdf_file):
    """Convert PDF to image for display."""
    image = Image.open(io.BytesIO(pdf_file.read()))
    return image

def render_pdf_as_image(pdf_file):
    pdf_document = fitz.open(stream=pdf_file, filetype="pdf")
    pdf_page = pdf_document[0]  # Assuming you want to display the first page

    pdf_image = pdf_page.get_pixmap()
    pil_image = Image.frombytes("RGB", [pdf_image.width, pdf_image.height], pdf_image.samples)

    return pil_image
    
def render_pdf_as_image1(pdf_file, max_width = 720, max_height = None):

    # Create a temporary file-like object
    temp_file = io.BytesIO(pdf_file)

    # Open the PDF using fitz
    doc = fitz.open(temp_file)
    
    # Get the first page (adjust for multi-page PDFs if needed)
    page = doc[0]
    
    # Determine the scaling factor to fit within max dimensions
    zoom_x = max_width / page.media_box.width
    zoom_y = (max_height or float('inf')) / page.media_box.height  # Auto-calculate height if not provided
    zoom = min(zoom_x, zoom_y)

    # Render the page at the calculated zoom factor
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)  # Set alpha=False for better performance

    # Convert the PIL Image to a format suitable for Streamlit
    return pix.asarray()    

def main():

    st.set_page_config(
        layout="wide",
        page_title="EazyEnroll",
        page_icon=":gear:",
        initial_sidebar_state="expanded",
    )

    st.sidebar.success('Select your option')

    menu = ["About", "Predict"]
    choice = st.sidebar.selectbox("Menu", menu)

    india_flag_image = Image.open("C:/Users/Sudhaa/PycharmProjects/pythonProject/.venv/India.jpg")
    usa_flag_image = Image.open("C:/Users/Sudhaa/PycharmProjects/pythonProject/.venv/USA.jpg")
    # st.title('Welcome to EazyEnroll  :flag-in: :flag-us:')
    # st.image(india_flag_image, width=30, use_column_width=False)
    # st.image(usa_flag_image, width=30, use_column_width=False)

    col1, col2 = st.columns([2,1])

    # Display title in the first column
    with col1:
        # background_color = "#FF0000"
        # background_color = "#7DF9FF"
        # st.markdown(f'<h1 style="background-color: {background_color}; color: black;">Welcome to EazyEnroll</h1>',unsafe_allow_html=True)
        st.title("Welcome to EazyEnroll")
        st.image(india_flag_image, width=50, use_column_width=False)
        st.image(usa_flag_image, width=50, use_column_width=False)

    with col2:
        col2.image('C:/Users/Sudhaa/PycharmProjects/pythonProject/.venv/chatbot3_small.gif')

    # with col2:
    #     col3a, col3b = st.columns(2)
    #     with col3a:
    #         st.image(india_flag_image, width=25, use_column_width=False)
    #         st.image(usa_flag_image, width=25, use_column_width=False)
    #
    #     with col3b:
    #         col3b.image('C:/Users/Sudhaa/PycharmProjects/pythonProject/.venv/chatbot3_small.gif')

    if choice == "Predict":

        # with st.form('Form 1', clear_on_submit=True):
        
        # st.write("### Upload an image",)
        # if st.form_submit_button('Upload Image'):
        #my_upload = st.file_uploader("Choose an Image file", type=["png", "jpg", "jpeg","pdf"],label_visibility="collapsed")
        # st.write(my_upload)
        
        # st.title("EazyEnroll")
        st.subheader("PDF Upload and Text Extraction with Vertex AI")

        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        st.divider()
        
        if uploaded_file is not None:

            credentials = service_account.Credentials.from_service_account_file(key_file)

            # Create a unique filename or use the original filename
            destination_blob_name = os.path.join(destination_folder, uploaded_file.name)

            # Read the file content
            #uploaded_file1 = uploaded_file
            uploaded_file.seek(0)
            file_content = uploaded_file.read()

            # Upload the file to GCP
            gcs_uri = upload_to_gcs(file_content, bucket_name, destination_blob_name, credentials)
            print("gcs_uri",gcs_uri)

            # Global variable to store credentials
            global_credentials = None

            project_id = "banded-anvil-426308-i1"
            location = "us-central1"
            model_id = "gemini-1.5-flash-001"

            initialized_model = initialize_vertex_ai(key_file, project_id, location, model_id)
            model = initialized_model  # Assume initialized_model is already defined

            
            with st.empty():    
                st.spinner("Authenticating.....")
                time.sleep(5)
                loading_text = st.write("Authentication Successful. \n Extracting Form document data.....")
            
            # import threading
            
            def generate_content_wrapper():
                # Call Vertex AI to get JSON
                # json_response = call_vertex_ai_gemini(gcs_uri, json.dumps(prompt))
                # gcs_uri1 = "gs://test_samples112/100_DAVID_BASS.pdf"
                json_response = generate_content(gcs_uri, prompt, model)
                
                st.empty()  # Clear the placeholder text
                
                # Display PDF as image and JSON response in two columns
                st.write("Filename: ", uploaded_file.name)

                col1, col2 = st.columns(2)

                with col1:
                    st.header("PDF Preview")
                    # uploaded_file.seek(0)  # Reset the file pointer to the start
                    pdf_image = render_pdf_as_image(file_content)
                    # image = display_pdf_as_image(uploaded_file)
                    # st.image(image, use_column_width=True)
                    st.image(pdf_image, use_column_width=True)

                # df = pd.DataFrame(json_response)

                with col2:
                    st.header("Extracted JSON")
                    st.json(json_response, expanded=True)
                    # st.experimental_dataframe(df, height=400)
                    
                    download_name = f"{uploaded_file.name.split('.')[0]}.json"
                    st.download_button\
                    (
                        label="Download JSON",
                        file_name=download_name,
                        #data=json_string,
                        data=json.dumps(json_response, ensure_ascii=False),
                        mime="application/json",
                    )

            generate_content_wrapper()
            # thread = threading.Thread(target=generate_content_wrapper)
            # thread.start()
        
    else:
        st.title("About EazyEnroll")
        st.subheader("Extract data from Healthcare Enrollment Forms to a JSON format")
        st.divider()
        #st.write("Built with Streamlit")
        # st.subheader("Upload an Enrollment form to create the respective AI predicted JSON")
        # st.caption("Use Download JSON button after the Converted JSON renders on the screen.")
        #st.write("Web App to parse a Healthcare Enrollment form to it's JSON counterpart")
        st.markdown(
        """
        EazyEnroll is for instant Document Entity Extraction and transform the data into a structured JSON

        This feature aims to provide the comprehensive !
        
        Upload an Enrollment form to create the respective AI predicted JSON
        
        or, if you have a specific query, 
        You can try our Chatbot option :robot_face: \n\n\n\n\n\n

        **👈 Select your menu option from the left side pane**   
        Use Download JSON button after the Converted JSON renders on the screen.
        \n\n\n\n\n\n
        Note: We are working towards integrating 
        
        """)
        st.write("Thank you for using our app")

    

if __name__ == '__main__':
    main()
