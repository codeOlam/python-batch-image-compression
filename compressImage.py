import os
import pathlib
import argparse
import shutil
from PIL import Image

def get_size_format(image_size:int, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if image_size < factor:
            return f"{image_size:.2f}{unit}{suffix}"
        image_size /= factor
    return f"{image_size:.2f}Y{suffix}"

def compress_img(image_name, new_size_ratio: float=0.9, quality: int=90, width: int=None, height: int=None, to_jpg: bool=True, destination_dir: pathlib.Path=None):
    # load the image to memory
    img = Image.open(image_name)

    # print the original image shape
    print("[*] Image shape:", img.size)

    # get the original image size in bytes
    image_size = os.path.getsize(image_name)

    # print the size before compression/resizing
    print("[*] Size before compression:", get_size_format(image_size))

    if new_size_ratio < 1.0:
        # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
        img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.ANTIALIAS)
        
        # print new image shape
        print("[+] New Image shape:", img.size)
    elif width and height:
        # if width and height are set, resize with them instead
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # print new image shape
        print("[+] New Image shape:", img.size)
   
    # split the filename and extension
    filename, ext = os.path.splitext(image_name)
    
    # make new filename appending _compressed to the original file name
    if to_jpg:
        # change the extension to JPEG
        new_filename = f"{filename}_compressed.jpg"
    else:
        # retain the same extension of the original image
        new_filename = f"{filename}_compressed{ext}"
    
    try:
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filename, quality=quality, optimize=True)
    except OSError:
        # convert the image to RGB mode first
        img = img.convert("RGB")
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filename, quality=quality, optimize=True)
      

    print("[+] New file saved:", new_filename)
    
    # get the new image size in bytes
    new_image_size = os.path.getsize(new_filename)
    
    # print the new size in a good format
    print("[+] Size after compression:", get_size_format(new_image_size))
    
    # calculate the saving bytes
    saving_diff = new_image_size - image_size
    
    # print the saving percentage
    print(f"[+] Image size change: {saving_diff/image_size*100:.2f}% of the original image size.")

    if destination_dir:
      try:
        cleaned_filename = os.path.split(new_filename)
        
        shutil.move(new_filename, f"{destination_dir}/{cleaned_filename[1]}")
        # shutil.move(new_filename, destination_dir)
      except Exception as e:
        print("[!] we are having some problems while moving file: ", e)


def batch_image_compress(new_size_ratio: float=0.9, quality: int=90, width: int=None, height: int=None, to_jpg: bool=True, source_dir: pathlib.Path=None, destination_dir: pathlib.Path=None): 
  if source_dir and destination_dir:
    for image in os.listdir(source_dir):
      
      #ignore MAC OS Destop Service Store file
      if image == '.DS_Store':
        pass
      else:
        compress_img(f"{source_dir}/{image}", new_size_ratio, quality, width, height, to_jpg, destination_dir)
    
    print("\n")
    print("="*50)
    print("[+] {0} images compressed successfully".format(len(os.listdir(destination_dir))))
  else:
    print('[-] batch compress requires source and destination folder!')
  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Python script for compressing and resizing images")
    parser.add_argument("-i", "--image", help="Target image to compress and/or resize")
    parser.add_argument("-j", "--to-jpg", action="store_true", help="Whether to convert the image to the JPEG format")
    parser.add_argument("-q", "--quality", type=int, help="Quality ranging from a minimum of 0 (worst) to a maximum of 95 (best). Default is 90", default=90)
    parser.add_argument("-r", "--resize-ratio", type=float, help="Resizing ratio from 0 to 1, setting to 0.5 will multiply width & height of the image by 0.5. Default is 1.0", default=1.0)
    parser.add_argument("-w", "--width", type=int, help="The new width image, make sure to set it with the `height` parameter")
    parser.add_argument("-hh", "--height", type=int, help="The new height for the image, make sure to set it with the `width` parameter")
    parser.add_argument("-b", "--batch", action="store_true", help="Whether to batch compress image from a source folder to a destination folder")
    parser.add_argument("-sdir", "--source-dir", type=pathlib.Path, help="`absolute/path/to/source/dir` where images to be compressed are")
    parser.add_argument("-ddir", "--destination-dir", type=pathlib.Path, help="`absolute/path/to/destination/dir` where compressed images are to be saved")
    args = parser.parse_args()

    # print the passed arguments
    print("="*50)
    print("[*] Image:", args.image)
    print("[*] To JPEG:", args.to_jpg)
    print("[*] Quality:", args.quality)
    print("[*] Resizing ratio:", args.resize_ratio)
    print("[*] Batch Compress:", args.batch)
    if args.width and args.height:
        print("[*] Width:", args.width)
        print("[*] Height:", args.height)
    print("="*50)

    if args.batch:
      # compress the image in batch
      batch_image_compress(
        args.resize_ratio, 
        args.quality, 
        args.width, 
        args.height, 
        args.to_jpg, 
        args.source_dir, 
        args.destination_dir
      )
    else:
      # compress the image
      compress_img(
        args.image,
        args.resize_ratio, 
        args.quality, 
        args.width, 
        args.height, 
        args.to_jpg,
        args.destination_dir
      )