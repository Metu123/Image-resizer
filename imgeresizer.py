from PIL import Image, ImageOps
import os
from concurrent.futures import ThreadPoolExecutor

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp")


def normalize_format(fmt):
    if not fmt:
        return None
    fmt = fmt.lower()
    if fmt == "jpg":
        return "jpeg"
    return fmt


def generate_output_path(image_path, output_format):
    directory = os.path.dirname(image_path)
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    ext = f".{output_format}" if output_format else os.path.splitext(image_path)[1]

    counter = 1
    output_path = os.path.join(directory, f"{base_name}_resized{ext}")

    # Prevent overwrite
    while os.path.exists(output_path):
        output_path = os.path.join(directory, f"{base_name}_resized_{counter}{ext}")
        counter += 1

    return output_path


def convert_mode_if_needed(img, output_format):
    # Handle transparency when converting to JPEG
    if output_format in ["jpeg"] and img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        return background
    return img.convert("RGB") if output_format == "jpeg" else img


def resize_single_image(image_path, width, height, keep_aspect, output_format, quality):
    try:
        with Image.open(image_path) as img:
            # Fix orientation (important for photos)
            img = ImageOps.exif_transpose(img)

            output_format = normalize_format(output_format)

            if keep_aspect:
                img.thumbnail((width, height), Image.LANCZOS)
            else:
                img = img.resize((width, height), Image.LANCZOS)

            img = convert_mode_if_needed(img, output_format)

            output_path = generate_output_path(image_path, output_format)

            save_kwargs = {}

            if output_format == "jpeg":
                save_kwargs.update({
                    "quality": quality,
                    "optimize": True,
                    "progressive": True
                })

            img.save(output_path, format=output_format.upper() if output_format else None, **save_kwargs)

            print(f"[OK] {image_path} → {output_path}")

    except Exception as e:
        print(f"[ERROR] {image_path}: {e}")


def process_folder(folder_path, width, height, keep_aspect, output_format, quality, workers=4):
    tasks = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(SUPPORTED_FORMATS):
                    image_path = os.path.join(root, file)

                    tasks.append(
                        executor.submit(
                            resize_single_image,
                            image_path,
                            width,
                            height,
                            keep_aspect,
                            output_format,
                            quality
                        )
                    )

        for task in tasks:
            task.result()  # Ensure exceptions surface


def get_user_input():
    path = input("Enter image or folder path: ").strip()

    if not os.path.exists(path):
        raise ValueError("Path does not exist.")

    width = int(input("Enter max width: "))
    height = int(input("Enter max height: "))

    keep_aspect = input("Keep aspect ratio? (y/n): ").strip().lower() == "y"

    output_format = input("Output format (jpg/png/webp or blank to keep original): ").strip()
    output_format = normalize_format(output_format)

    quality = 85
    if output_format == "jpeg":
        try:
            quality = int(input("Enter JPEG quality (1–100): "))
        except ValueError:
            print("Invalid quality, using default 85.")

    return path, width, height, keep_aspect, output_format, quality


def main():
    try:
        path, width, height, keep_aspect, output_format, quality = get_user_input()

        if os.path.isfile(path):
            resize_single_image(path, width, height, keep_aspect, output_format, quality)
        else:
            process_folder(path, width, height, keep_aspect, output_format, quality)

    except Exception as e:
        print(f"[FATAL] {e}")


if __name__ == "__main__":
    main()
