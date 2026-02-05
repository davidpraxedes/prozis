from PIL import Image

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
        
        # Crop transparent borders
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        
        # Resize maintaining aspect ratio to fit within size box
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        img.save(output_path, "PNG")
        print(f"Successfully processed {input_path} to {output_path}")
    except Exception as e:
        print(f"Error processing image: {e}")

remove_white_bg_and_resize("gift-card-original.png", "gift-card-100.png", size=(100, 100)) # Make it slightly larger initially to retain quality, regulate via CSS
