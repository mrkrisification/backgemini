import streamlit as st
import time
from imageenhancer import ImageEnhancer
from datetime import datetime

testing_mode = True

# set master columns for ui 
COLSIZE = [3,3]

if 'input_image' not in st.session_state:
    st.session_state['input_image'] = None

if 'ie' not in st.session_state:
    st.session_state['ie'] = ImageEnhancer()
else:
    ie = st.session_state['ie']
    st.session_state['input_image'] = ie.input_image
    
st.set_page_config(layout="wide")
# setting initial session state


def reset_app():
    st.session_state['ie'].reset()
    #st.session_state = {}
    st.rerun()

with st.sidebar:
    st.write("Options")
    reset = st.button(key="Reset", label="Reset", type="primary", width="stretch")
    if reset:
        reset_app()

    rotate = st.button(key="rotate", label="Rotate Image", type="primary", width="stretch")
    if rotate:
        ie = st.session_state['ie']
        img = ie.input_image
        ie.set_input_image(ie.rotate_image(img))
        st.rerun()
        

st.title("Image Enhancer")
st.write("powered by Gemini Flash 2.5 Image Preview")

imageenhancer_tab, chat_tab = st.tabs(["Image Enhancer", "Chat"])

with imageenhancer_tab:
    ###### Start of IMAGE ENHANCER TAB
    col1, col2 = st.columns(COLSIZE, gap="small")
    with col1:
        ie = st.session_state['ie']
        if ie.input_image is None:

            st.write("Upload an image")
            image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
            input_image = st.empty()

            if image is None:
                st.info("Please upload an image")
                st.stop()
            else:
                input_image.image(image, caption="Uploaded Image", width="stretch")
                st.session_state['input_image'] = image.getvalue()
                ie.set_input_image(image.getvalue())
        
            if testing_mode:
                st.write(type(st.session_state['input_image']))   
        
        elif ie.input_image is not None:
            input_image = st.empty()
            input_image.image(ie.input_image, caption="Input image", width="stretch")


    with col2:
        st.write("Describe the changes you want to make to the image")
        user_input = st.text_area("Prompt", height=200)

        if user_input:
            st.write("Your prompt:")
            st.write(user_input)
        else:
            st.info("Please enter a prompt")
        
        generate = st.button("Generate", type="primary")
        if generate:
            with st.spinner("Generating..."):

                ie = st.session_state['ie']
                ie.generate_image_update(user_input)
                
                # switch images - to possible revert to the old one
                #st.session_state['input_image'] = st.session_state['primary_image']
                input_image.image(ie.output_image, caption="Generated Image", width="stretch")
                #st.session_state['input_image'] = ie.input_image
                st.session_state['input_image'] = ie.output_image


    bottoncols = st.columns(COLSIZE)
    with bottoncols[0]:
        cols = st.columns(2, gap="medium")
        

        with cols[0]:
            ie = st.session_state['ie']
            if ie.output_image is not None:
                revert = st.button("Back to Input Image", width="stretch", type="secondary")
                if revert:    
                    ie.set_input_image(ie.input_image)
                    ie.output_image = None
                    input_image.image(ie.input_image, caption="Input image", width="stretch")

        with cols[1]:
            ie = st.session_state['ie']
            if ie.output_image is not None:
                save = st.button("Keep Image", width="stretch", type="primary")
            
                if save:
                    ie.set_input_image(ie.output_image)
                    input_image.image(ie.input_image, caption="Generated Image", width="stretch")
                    


        if ie.output_image is not None:
            mime_type = ie.get_mime_type(ie.output_image)
            MIME_EXTENSION_MAP = {
                "image/png": "png",
                "image/jpeg": "jpg",
                "image/webp": "webp",
                "image/gif": "gif",
                "image/bmp": "bmp",
                "image/tiff": "tiff",
                "image/x-icon": "ico",
                "image/svg+xml": "svg",
                "image/heif": "heif",
                "image/heic": "heic",
                "image/avif": "avif",
                }
            extension = MIME_EXTENSION_MAP[mime_type]
            st.write(extension)
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.{extension}"
            download = st.download_button("Download image", data=ie.output_image, mime=mime_type, file_name=filename, key='download', width="stretch", type="primary")

    with bottoncols[1]:
        st.empty()



    if testing_mode:
        ### for testing only - delete later
        img1, img2 = st.columns(2)
        ie = st.session_state['ie']

        with img1:
            if st.session_state.input_image is None:
                currentinputimage = st.empty()
            else:
                currentinputimage = st.empty()
                ie = st.session_state['ie']
                input_image = ie.input_image
                if input_image is None:
                    st.write("No input image")
                else:
                    currentinputimage.image(ie.input_image, caption="Current Input Image", width="stretch")
                

        with img2:
            if st.session_state.input_image is None:
                currentprimaryimage = st.empty()
            else:
                currentprimaryimage = st.empty()
                output_image = ie.output_image
                if output_image is None:
                    st.write("No Output image")
                else:
                    currentprimaryimage.image(ie.output_image, caption="Current Generated Image", width="stretch")


    ###### End of IMAGE ENHANCER TAB
    
    ###### CHAT TAB
with chat_tab:
    ie = st.session_state['ie']

    image_col, chat_col = st.columns([2,4])

    with image_col:
        if ie.input_image is not None:
            input_image = st.empty()
            input_image.image(ie.input_image, caption="Input image", width="stretch")

    with chat_col:
        st.write("Chat about the image")
    