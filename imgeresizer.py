from PIL import Image
import os

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp")


def resize_single_image(image_path, width, height, keep_aspect, output_format, quality):
    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size

            if keep_aspect:
                img.thumbnail((width, height))
            else:
                img = img.resize((width, height), Image.LANCZOS)

            directory = os.path.dirname(image_path)
            base_name = os.path.splitext(os.path.basename(image_path))[0]

            ext = f".{output_format.lower()}" if output_format else os.path.splitext(image_path)[1]
            output_path = os.path.join(directory, f"{base_name}_resized{ext}")

            save_kwargs = {}
            if output_format.lower() in ["jpg", "jpeg"]:
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True

            img.save(output_path, **save_kwargs)
            print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Failed for {image_path}: {e}")


def process_folder(folder_path, width, height, keep_aspect, output_format, quality):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(SUPPORTED_FORMATS):
                image_path = os.path.join(root, file)
                resize_single_image(image_path, width, height, keep_aspect, output_format, quality)


def main():
    path = input("Enter image or folder path: ").strip()

    if not os.path.exists(path):
        print("Path does not exist.")
        return

    try:
        width = int(input("Enter max width: "))
        height = int(input("Enter max height: "))
    except ValueError:
        print("Invalid dimensions.")
        return

    keep_aspect = input("Keep aspect ratio? (y/n): ").strip().lower() == "y"
    output_format = input("Output format (jpg/png/webp or leave blank to keep original): ").strip()
    quality = 85

    if output_format.lower() in ["jpg", "jpeg"]:
        try:
            quality = int(input("Enter JPEG quality (1–100): "))
        except ValueError:
            print("Invalid quality, using default 85.")

    if os.path.isfile(path):
        resize_single_image(path, width, height, keep_aspect, output_format, quality)
    else:
        process_folder(path, width, height, keep_aspect, output_format, quality)


if __name__ == "__main__":
    main()
