from PIL import Image
import numpy as np

def remove_white_bg_and_resize(input_path, output_path, size=(60, 60), threshold=240):
    try:
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            # If r, g, b are all > threshold (near white), make transparent
            if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        
        # Resize maintaining aspect ratio
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        img.save(output_path, "PNG")
        print(f"Successfully processed {input_path} to {output_path}")
    except Exception as e:
        print(f"Error processing image: {e}")

remove_white_bg_and_resize("kit-light-blue.jpg", "kit-light-blue.png", size=(120, 120)) # Keep resolution decent, resize in CSS
