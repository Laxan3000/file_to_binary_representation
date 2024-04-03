from PIL import Image
from PIL.PngImagePlugin import PngInfo
from math import ceil
from pathlib import Path
import numpy as np

IMAGE_MODE: str = "L" # Grayscale
IMAGE_FORMAT: str = "png"
METADATA_NAME: str = "OGFileSize"


def get_file(force_format: bool = False) -> Path:
    while True:
        path: str = input("Please drag and drop the file to convert here!: ")

        if not path:
            print('Path is empty!', end= ' ')
            continue
        
        file_path: Path = Path(path)

        if file_path.exists():
            if force_format and file_path.suffix.casefold() != f".{IMAGE_FORMAT}":
                continue

            return file_path
           
        print("Path is not valid!", end= ' ')


def get_compression() -> int:
    while True:
        compression: str = input(
            "Please select a compression level (0-9) [6]: "
        ) or '6'
        
        if '0' <= compression[0] <= '9':
            return int(compression)


def to_image() -> None:
    # Read the image from a numpy array
    with Image.fromarray(
        # Pad a coming array at its tail, adding 0 for each missed pixel
        np.pad(
            # Generate the array from the file
            a := np.frombuffer(open(get_file(), "rb").read(), np.uint8),
            
            # Explanation:
            # - (0, ...): 
            #   0 is how much padding has to be added at the head of the array
            #   ... is how much padding has to be added at the tail of the array
            (0, (side := ceil((size := len(a)) ** 0.5)) ** 2 - size),
            
            # "Constant" means it's keeping the upcoming value the same
            'constant',
            
            # The value to pad the array with
            constant_values= 0
            
        # reshape the array so to make a square
        ).reshape(side, side),
        IMAGE_MODE
    ) as image:
        # Prepare metadata to add to the image
        metadata: PngInfo = PngInfo()
        metadata.add_text(METADATA_NAME, str(size))
        
        # Save the image as png
        image.save(
            f"a.{IMAGE_FORMAT}",
            IMAGE_FORMAT,
            compress_level= get_compression(),
            pnginfo= metadata
        )
        

def from_image() -> None:
    # Asks the user if he remembers the file extension
    # This is pointless since it could be changed manually by the user
    format: str = (
        input(
            "What's the file extension? [txt]: "
        )
        or "txt"
    )

    while True:
        # Open the image, then the hard part with numpy comes..
        with Image.open(get_file(True)) as image:
            # Check if the image inserted by the user was made by this program
            if not hasattr(image, "text") \
            or not (size := image.text.get(METADATA_NAME)): # type: ignore
                print("That is not a valid image file!")
                continue
            
            # 1 - Convert the image to a numpy array
            # 2 - then flatten the array
            # 3 - then read only the valid bytes from the array
            # 4 - and finally save it to a file
            np.asarray(image, np.uint8) \
            .flatten()[:int(size)] \
            .tofile(f"a.{format}", "", format)
            
        break


# Returns True if the program has to be executed again
# Otherwise it returns False
def main() -> bool:
    global running
    
    print(
        "What would you like to do?:",
        "a - Generate image from file",
        "b - Generate file from image",
        "c - Close the program",
        sep="\n",
    )

    match (input("Select your answer: ") or ' ')[0]:
        case 'a':
            to_image()

        case 'b':
            from_image()
            
        case 'c':
            return False

        case _:
            return True

    print("Conversion done! Bye :)")
    input("-- Press any key to re-run the program --")

    return True


if __name__ == "__main__":
    print("Welcome to this amazing program!")
    while main(): print()
