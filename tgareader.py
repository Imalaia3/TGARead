import struct,sys
from PIL import Image

"""
Simple TGA Reader by Imalaia3
Does not support color-maps
and is only 24-bit color.

"""

if len(sys.argv) < 3:
    print("Syntax: tgareader <image> <showimg (1-True 0-False)>")
    exit()


fd = open(sys.argv[1],"rb").read()


class TGAImage:
    def __init__(self) -> None:
        self.id = b''   #ID Field Length (1 byte)
        self.cmt = b''  #Color Map Type (1 byte)
        self.type = b'' #Image Type (1 byte)
        self.spec = b'' #Color Map Specification (5 bytes)
        self.res = b''  #Image Specification (10 bytes)
        self.w,self.h,self.xo,self.yo = 0,0,0,0 #Used Later
        self.depth = b'' #Used Later

        # For more information, please visit https://en.wikipedia.org/wiki/Truevision_TGA

IMAGE = TGAImage()

#Setting fields
IMAGE.id = fd[0]
IMAGE.cmt = fd[1]
IMAGE.type = fd[2]
IMAGE.spec = fd[3:3+4]
coffset = 3+4+1+10
IMAGE.res = fd[3+4+1:coffset]

# Set type
imtype = ""
if IMAGE.type == 0:
    imtype = "No Image Data"
if IMAGE.type == 1:
    imtype = "Uncompressed Color mapped image"
if IMAGE.type == 2:
    imtype = "Uncompressed, True Color Image"
if IMAGE.type == 9:
    imtype = "Run-length encoded, Color mapped image"
if IMAGE.type == 11:
    imtype = "Run-Length encoded, Black and white image"


if imtype != "":
    print("Found an",imtype)
    if IMAGE.type == 1 and IMAGE.cmt == 0:
        print("WARN: TGA is type 2 but has no Color-Map Data")

IMAGE.xo = IMAGE.res[0:2] #X-Origin. Determines image oriantation
IMAGE.yo = IMAGE.res[2:4] #Y-Origin. Same as xo
IMAGE.w  = struct.unpack("<H",IMAGE.res[4:6])[0]  #unpack: little-endian unsigned short (width)
IMAGE.h  = struct.unpack("<H",IMAGE.res[6:8])[0]  #unpack: little-endian unsigned short (height)
IMAGE.depth = IMAGE.res[8] #Color/Pixel Depth https://en.wikipedia.org/wiki/Color_depth
print(f"Image resoloution is {IMAGE.w}x{IMAGE.h} pixels\n with a x-origin of {IMAGE.xo} and a y-origin of {IMAGE.yo}.")
print(f"The image has a color depth of {IMAGE.depth} bits.")
print("I'm not gonna decode the descriptor but here it is:",IMAGE.res[9])

print("Reading True-Color 24 bit depth (for now)")
if IMAGE.cmt != 0:
    print("Image has color-map data. UNIMPLEMENTED. ")
    exit()


#Load 24-bit color data to array
pixels = []
tmp = []
for c,pix in enumerate(fd[coffset::]):
    if len(tmp) == 3:
        pixels.append(tmp)
        tmp = []
    tmp.append(pix)

#Rotate Pixel Array according to Origins
if IMAGE.yo == b'\x00\x00' and IMAGE.xo == b'\x00\x00':
    pixels.reverse()
    print("Flipped Image")




# Show Image
if sys.argv[2] == "0":
    exit()

display = Image.new("RGB",(IMAGE.w,IMAGE.h))
print("Painting image...")

offset = 0
for y in range(IMAGE.h):
    for x in range(IMAGE.w):
        print("\r\r\r"+str(offset+x-1)+"/"+str(IMAGE.h*IMAGE.w),end=" pixels drawn.")
        try:
            display.putpixel((x,y),tuple(pixels[offset+x-1]))
        except IndexError:
            print("Hit IndexError. Probable Cause: Image Contains Color-Map Data.")
            print("Image will come out corrupted.")
    offset += IMAGE.w

print("\nDone")
display.show()