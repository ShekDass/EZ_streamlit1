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

def main():
    st.title("PDF Upload and Text Extraction with Vertex AI")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:

        credentials = service_account.Credentials.from_service_account_file(key_file)

        # Create a unique filename or use the original filename
        destination_blob_name = os.path.join(destination_folder, uploaded_file.name)

        # Read the file content
        uploaded_file1 = uploaded_file
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

        # Call Vertex AI to get JSON
        # json_response = call_vertex_ai_gemini(gcs_uri, json.dumps(prompt))
        # gcs_uri1 = "gs://test_samples112/100_DAVID_BASS.pdf"
        json_response = generate_content(gcs_uri, prompt, model)
        # Display PDF as image and JSON response in two columns

        st.write("Filename: ", uploaded_file.name)

        col1, col2 = st.columns(2)

        with col1:
            st.header("PDF Preview")
            # uploaded_file.seek(0)  # Reset the file pointer to the start
            pdf_image = render_pdf_as_image(file_content)
            # image = display_pdf_as_image(uploaded_file)
            # st.image(image, use_column_width=True)
            st.image(pdf_image)

        with col2:
            st.header("Extracted JSON")
            st.json(json_response)

if __name__ == '__main__':
    main()
