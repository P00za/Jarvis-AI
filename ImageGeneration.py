import asyncio 
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# Ensure directories exist
os.makedirs("Data", exist_ok=True)
os.makedirs("Frontend/Files", exist_ok=True)

def open_images(prompt):
    """Display generated images from the Data directory"""
    prompt = prompt.replace(" ", "_")
    for i in range(1, 5):
        image_path = os.path.join("Data", f"{prompt}{i}.jpg")
        try:
            with Image.open(image_path) as img:
                print(f"Displaying: {image_path}")
                img.show()
                sleep(1)
        except (IOError, FileNotFoundError):
            print(f"Image not found: {image_path}")

# API Configuration
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

async def query(payload):
    """Send API request with error handling"""
    try:
        response = await asyncio.to_thread(
            requests.post,
            API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        return response.content if response.status_code == 200 else None
    except:
        return None

async def generate_image(prompt: str):
    """Generate multiple images with proper API format"""
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": prompt,
            "parameters": {
                "seed": randint(0, 1000000),
                "num_inference_steps": 25
            }
        }
        tasks.append(asyncio.create_task(query(payload)))
        await asyncio.sleep(2)  # Rate limiting
    
    for i, img_data in enumerate(await asyncio.gather(*tasks)):
        if img_data:
            with open(f"Data/{prompt.replace(' ', '_')}{i+1}.jpg", "wb") as f:
                f.write(img_data)

def GenerateImages(prompt: str):
    """Wrapper for image generation"""
    asyncio.run(generate_image(prompt))
    open_images(prompt)

# Main monitoring loop
while True:
    try:
        with open("Frontend/Files/ImageGeneration.data", "r+") as f:
            data = f.read().strip()
            if data:
                prompt, status = data.split(",", 1)
                if status.strip() == "True":
                    print("Generating Images...")
                    GenerateImages(prompt.strip())
                    f.seek(0)
                    f.write("False,False")
                    f.truncate()
        sleep(1)
    except (FileNotFoundError, ValueError):
        sleep(1)
    except KeyboardInterrupt:
        print("Stopping monitor...")
        break