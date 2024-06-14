from tkinter.filedialog import askopenfilename, asksaveasfilename
from functools import partial
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from math import ceil
import numpy as np

IMAGE_MODE: str = "L" # Grayscale
IMAGE_FORMAT: str = "png"
METADATA_NAME: str = "OGFileSize"
FILE_TYPE: list[tuple[str, str]] = [("Binary Rapresentation", f"*.{IMAGE_FORMAT}")]


def get_file(force_format: bool = False) -> str:
    function = partial(askopenfilename, title= "Please select the file to convert")
    
    if force_format:
        function.keywords["filetypes"] = FILE_TYPE
    
    return function()


def get_compression() -> int:
    while True:
        compression: str = input(
            "Please select a compression level (0-9) [6]: "
        ) or '6'
        
        if '0' <= compression[0] <= '9':
            return int(compression)


def to_image() -> bool:
    if not (file_name := get_file()):
        return False
    
    # Read the image from a numpy array
    with Image.fromarray(
        # Pad a coming array at its tail, adding 0 for each missed pixel
        np.pad(
            # Generate the array from the file
            a := np.frombuffer(open(file_name, "rb").read(), np.uint8),
            
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
        
        save_name: str = asksaveasfilename(
            filetypes= FILE_TYPE,
            title= "What name do you want to give to your rapresentation?"
        )
        
        if not save_name.endswith(f".{IMAGE_FORMAT}"):
            save_name += f".{IMAGE_FORMAT}"
        
        # Save the image as png
        image.save(
            save_name,
            IMAGE_FORMAT,
            compress_level= get_compression(),
            pnginfo= metadata
        )
        
        return True
        

def from_image() -> bool:
    if not (file_name := get_file(True)):
        return False
    
    # Asks the user the name to save the new file
    save_name: str = asksaveasfilename(
        filetypes= [("Text Files", "*.txt"), ("All Files", "*.*")],
        title= "How do you want to save the file as?"
    )

    while True:
        # Open the image, then the hard part with numpy comes..
        with Image.open(file_name) as image:
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
            .tofile(save_name)
            
        break
    
    return True


# Returns True if the program has to be executed again
# Otherwise it returns False
def main() -> bool:
    print(
        "What would you like to do?:",
        "a - Generate image from file",
        "b - Generate file from image",
        "c - Close the program",
        sep="\n",
    )

    success: bool = bool()
    match (input("Select your answer: ") or ' ')[0]:
        case 'a':
            success = to_image()

        case 'b':
            success = from_image()
            
        case 'c':
            return False

        case _:
            return True

    print(
        "Conversion done! Bye :)"
        if success else
        "Operation canceled"
    )
        
    input("-- Press any key to re-run the program --")

    return True


if __name__ == "__main__":
    print("Welcome to this amazing program!")
    while main(): print()