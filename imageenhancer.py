from dotenv import load_dotenv
from google.genai import types
from google import genai
import magic
import os
from PIL import Image
from io import BytesIO
from datetime import datetime

load_dotenv()

class ImageEnhancer:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.description = None
        self.input_image = None
        self.output_image = None

    def reset(self):
        self.__init__()

    def set_input_image(self, image):
        self.input_image = image

    def set_description(self, description):
        self.description = description

    def get_mime_type(self, image_bytes):
        mime = magic.Magic(mime=True)
        return mime.from_buffer(image_bytes)
    
    def describe_image(self):
        image_to_explain = self.input_image
        mime_type = self.get_mime_type(image_to_explain)

        print(type(image_to_explain))
        client = genai.Client()
        
        response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_bytes(
            data=image_to_explain,
            mime_type=mime_type,
            ),
            'Describe this image in a detailed, descriptive way.'
        ]
        )

        return response.text

    
    def rotate_image(self, image):
        mime_type = self.get_mime_type(image)
        image = Image.open(BytesIO(image))
        image = image.rotate(90, expand=True)
        buf = BytesIO()
        image.save(buf, format=mime_type.split('/')[-1])
        return buf.getvalue()
        

    def make_image_update_prompt(self, user_input):
        image_to_explain = self.input_image
        mime_type = self.get_mime_type(image_to_explain)

        #print(type(image_to_explain))
        client = genai.Client()
        
        response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_bytes(
            data=image_to_explain,
            mime_type=mime_type,
            ),
            f"""The user wants to change the image the following way: {user_input}.
            Turn his inputs into a concise prompt for a text-to-image model. 
            Be as specific as possible in terms of which parts of the image he wants to change.
            Only output the prompt, nothing else.
            """
        ]
        )

        return response.text

    def generate_image_update(self, prompt):
        client = genai.Client()

        
        image_bytes = self.input_image
        mime_type = self.get_mime_type(image_bytes)

        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt, types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
            )],
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                
                now = datetime.now()
                timestamp = now.strftime("%Y%m%d_%H%M%S")
                folder = "output"
                if not os.path.exists(folder):
                    os.makedirs(folder)
                filename = f"{folder}/img_{timestamp}.png"
                image.save(filename)


                # Also capture PNG bytes
                buf = BytesIO()
                image.save(buf, format="PNG")
                png_bytes = buf.getvalue()
                
                self.output_image = png_bytes

        return png_bytes


if __name__ == "__main__":
    ie = ImageEnhancer()
    # input must be file
    image_path = "Input_Images/wohnzimmer.jpg"
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    print(type(image_bytes))

    #import magic
    #mime = magic.Magic(mime=True)
    #file_type = mime.from_buffer(image_bytes)
    #file_type = mime.from_file(image_bytes)
    #print(file_type) 


    
    #user_input = """Only do slight changes to the image. Keep its structure
    #Add 5-7 colorful cyberpunk elements like screens, consoles, in fitting places.
    #Change lighting only slightly to give it a cyberpunk vibe.
    #"""

    #ie.set_input_image(image_bytes)
    #prompt = ie.make_image_update_prompt(user_input)
    #print(prompt)

    ie.set_input_image(image_bytes)
    prompt = """
    Add country-style curtain panels ONLY on the left side of the window, made of light cotton or linen fabric with a striped pattern. Cozy farmhouse aesthetic.
    """
    result = ie.generate_image_update(prompt)
    print(type(result))

    ie.set_input_image(result)

    prompt = """
    Substitute the lamp in the corner, with a more fitting model.
    """
    
    result = ie.generate_image_update(prompt)
    print(type(result))