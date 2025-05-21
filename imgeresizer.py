from PIL import Image
import os

def resize_image():
    image_path = input("Enter the path to the image: ").strip()

    if not os.path.exists(image_path):
        print("Invalid image path.")
        return

    try:
        width = int(input("Enter new width: "))
        height = int(input("Enter new height: "))
    except ValueError:
        print("Invalid dimensions.")
        return

    try:
        img = Image.open(image_path)
        resized_img = img.resize((width, height))

        directory = os.path.dirname(image_path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        ext = os.path.splitext(image_path)[1]
        output_path = os.path.join(directory, f"{base_name}_resized{ext}")

        resized_img.save(output_path)
        print(f"Resized image saved as: {output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    resize_image()