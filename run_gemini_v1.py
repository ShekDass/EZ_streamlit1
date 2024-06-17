# -*- coding: utf-8 -*-
"""EZ_Gemini2.ipynb
"""

#from google.colab import files
from google.oauth2 import service_account
import google.auth
import google.auth.transport.requests

from google.cloud import storage
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)

# from IPython.core.interactiveshell import InteractiveShell
import os
import json
from pdf2image import convert_from_path
import IPython.display
from IPython.display import display, Image
import tempfile


#from google.colab import files
# Upload the service account JSON key file
#uploaded = files.upload()
#service_account_file = list(uploaded.keys())[0]
service_account_file = "C:/Users/Sudhaa/PycharmProjects/pythonProject/.venv/service_account_key/eazyenroll_vertexai_user.json"

# Global variable to store credentials
global_credentials = None

def initialize_vertex_ai(service_account_file, project_id, location, model_id):
    try:
        # Upload the service account JSON key file
        # uploaded = files.upload()
        # service_account_file = list(uploaded.keys())[0]

        # Define the required scope
        SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

        # Authenticate using the service account
        global_credentials = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES
        )

        # Set the environment variable for authentication
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_file

        # Verify the credentials
        auth_req = google.auth.transport.requests.Request()
        global_credentials.refresh(auth_req)

        # Optionally, set the project ID
        # !gcloud config set project {project_id}

        print("Authentication successful.")

        # Initialize AI Platform SDK
        aiplatform.init(credentials=global_credentials, project=project_id)

        # Initialize Vertex AI SDK
        vertexai.init(credentials=global_credentials, project=project_id, location=location)

        # Load Generative Model
        model = GenerativeModel(model_id)

        return model  # Return the initialized model instance

    except Exception as e:
        print(f"Error initializing AI Platform and Vertex AI: {e}")
        return None

# Credentials
PROJECT_ID = "banded-anvil-426308-i1"
LOCATION = "us-central1"
MODEL_ID = "gemini-1.5-flash-001"

initialized_model = initialize_vertex_ai(service_account_file, PROJECT_ID, LOCATION, MODEL_ID)

def load_json_from_file(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r') as file:
            return json.load(file)
    else:
        return None


# Initialize Google Cloud Storage client
storage_client = storage.Client(credentials=global_credentials, project="banded-anvil-426308-i1")

# def initialize_storage_client(service_account_file):
#     # Initialize a GCS client with the service account credentials
#     client = storage.Client.from_service_account_json(service_account_file)
#     return client
#
# storage_client = initialize_storage_client(service_account_file)

def upload_to_gcs(file_stream, bucket_name, file_name, storage_client):
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Ensure the file stream is at the beginning
        file_stream.seek(0) # Reset file stream position

        # Upload the file to GCS
        blob.upload_from_file(file_stream)

        print(f"File uploaded to {bucket_name}/{file_stream.name}")
        return f"gs://{bucket_name}/{file_name}"

    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        return None


def generate_content(pdf_file_uri, prompt, model):
    try:

        # # Save the uploaded PDF file temporarily
        # with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        #     tmp_pdf.write(pdf_file_uri.read())
        #
        # # Get the temporary file path
        # # tmp_pdf_path = tmp_pdf.name
        # tmp_pdf_file_name = tmp_pdf.name

        # Bucket name and file name in GCS
        bucket_name = "eazyenroll_test_gemini/input"

        print("pdf_file_uri:", pdf_file_uri)
        print("bucket name:", bucket_name)
        # print("pdf_file name:", pdf_file_uri.name)
        # print("tmp_pdf_file_name:", tmp_pdf_file_name)

        # Example usage
        # with open(pdf_file_uri, 'rb') as file_stream:
        #     bucket_name = 'eazyenroll_test_gemini'  # Your bucket name
        #     object_path = 'input/file.pdf'  # The object path within the bucket
        #     pdf_in_gcs = upload_to_gcs(file_stream, bucket_name, object_path, storage_client)

        # Upload PDF file to GCS
        # pdf_in_gcs = upload_to_gcs(pdf_file_uri, bucket_name, pdf_file_uri.name)

        # Load PDF file from URI
        print("Before part:", pdf_file_uri)
        pdf_file = Part.from_uri(pdf_file_uri, mime_type="application/pdf")
        # pdf_file = Part.from_uri(pdf_in_gcs, mime_type="application/pdf")
        print("After Part:", pdf_file)

        # Extract text from the PDF file if needed
        # pdf_text = pdf_file.get_text()

        # Prepare contents for model generation
        # contents = [pdf_file_uri, prompt]
        contents = [pdf_file, prompt]
        print("Print Contents:", contents)

        # Generate content using the model
        response = model.generate_content(contents)

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

    except Exception as e:
        print(f"Error generating content and saving as JSON: {e}")

# pdf_file_uri = "./100_DAVID_BASS.pdf"
pdf_file_uri = "gs://test_samples112/100_DAVID_BASS.pdf"
# pdf_file_uri = "gs://eazyenroll_test_gemini/input/42_JEANNE_D'ARC.pdf"
# pdf_file = "/content/100_DAVID_BASS.pdf"

model = initialized_model  # Assume initialized_model is already defined

json_path = "./prompt.json"
# prompt = load_json_from_file(json_path)
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

# print("prompt:", prompt)
# def call_gemini(pdf_file):
#     output_json = generate_content(pdf_file, prompt, model)
#     return output_json

generate_content(pdf_file_uri, prompt, model)

# if model:
#     generate_content(pdf_file_uri, prompt, model)
# else:
#     print("Model initialization failed.")