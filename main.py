import easyocr
import os
import google.generativeai as genai
from PIL import Image
import re
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # You can specify the HTTP methods you want to allow
    allow_headers=["*"],  # You can specify the HTTP headers you want to allow
)

def extract_text_from_image(image):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image)
    text = ' '.join([entry[1] for entry in result])
    return text

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

def get_gemini_response(question):
    response=model.generate_content(question)
    return response.text

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    contents = await file.read()
    
    # Use EasyOCR to extract text from the image
    extracted_text = extract_text_from_image(contents)
     
    prompt = """I'm going to give you a string which will contain some food items you have to recognise the food items and then 
    return whether they are healthy or not. You must ignore if any description of any food item if given."""

    input = prompt + extracted_text
    # Classifying whether the food item is healthy or unhealthy
    final_response = get_gemini_response(input)

    return {"filename": file.filename, "text": final_response}