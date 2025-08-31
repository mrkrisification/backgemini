from google import genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

MODEL = "gemini-2.5-flash-image-preview"

client = genai.Client()
chat = client.chats.create(model=MODEL)

input_image_path = "Input_Images/1000025096.png"
image = Image.open(input_image_path)

image_content = ["Describe this image.", image]
response = chat.send_message(image_content)
print(response.text)

response = chat.send_message("What fun adaptations should I do to that image. Propose 3 things")
print(response.text)


for message in chat.get_history():
    print(f'role - {message.role}',end=": ")
    print(message.parts[0].text)