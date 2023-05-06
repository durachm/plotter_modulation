from PIL import Image
import numpy as np
import math

x_resolution = 450
x_width_in_mm = 150

img = Image.open('Bilder/leo.jpg')
f = open("Output/test.gcode", "w")

scaling = x_width_in_mm / x_resolution

def gcode(value, length, yvalue):
    # Gcode 
    #f.write('G1 X%.2f Y%.2f \n'% (x/4, x+2))   
    #print("Value %.1f length %.1f y %.1f"%(value,length, yvalue))
    if(value == 255):
        
        f.write('G01 X%.4f Y%.4f Z%.4f F1200 (straight line)\n'% (length * scaling, 0, 0))  #generate a streight line

    else:
        x = 0
        b = 0.5*math.pi
        temp_y = 0
        x_increment = 0.1
        while x < length:
                  
            if value == 0:
                b = 2*math.pi
            elif value == 75:
                b = math.pi
            elif value == 125:
                b = 0.5*math.pi 
            
            temp_y = math.sin(b*x)
            x += x_increment
            f.write('G01 X%.4f Y%.4f Z%.2f F1200 \n'% (x_increment * scaling,(math.sin(b*x)-temp_y) * scaling, 0))
        
        f.write('G90 (Change to absolut coordinates) \n')
        f.write('G01  Y%.4f  F1200 \n'% ((-3*yvalue + 3) * scaling))
        f.write('G91 (Change to incremental coordinates) \n')



def check_list_for_equals(lst, index=0):
    # if ele is None, assign the first element of the list to ele
    
    ele = lst[index]
    # base case: if index is equal to the length of the list, return True
    if index == len(lst) -1:
        return index, ele
    # if the current element at index is not equal to ele, return False
    elif lst[index] != lst[index+1]:
        return index, ele
    # otherwise, call the function again with the next index
    else:
        return check_list_for_equals(lst, index+1)


width, height = img.size
size = int(x_resolution), int(((height / width) * x_resolution)/3)    # remove *3 to get the orgiinal aspect ratio 
img_resized = img.resize(size, Image.ANTIALIAS)
ary = np.array(img_resized)

print('Resized picture x-pixels: ' + str(size[0]) + '  y-pixels: ' + str(size[1]))

# Split the three channels
r,g,b = np.split(ary,3,axis=2)
r=r.reshape(-1)
g=r.reshape(-1)
b=r.reshape(-1)

# Standard RGB to grayscale 
bitmap = (0.299 * r + 0.587 * g + 0.114 * b).astype('int')

for i in range(len(bitmap)):
    if(bitmap[i] <= 64):
        bitmap[i] = 0                               # 1 Step    - Black
    elif(bitmap[i] > 64 and bitmap[i] <= 128):
        bitmap[i] = 75                              # 2 Step
    elif(bitmap[i] > 128 and bitmap[i] <= 192):
        bitmap[i] = 125                             # 3 Step
    elif(bitmap[i] > 192):
        bitmap[i] = 255                             # 4 Step    - White

bitmap = np.array(bitmap).reshape([ary.shape[0], ary.shape[1]])
#bitmap = np.dot((bitmap > 160).astype(float),255)
im = Image.fromarray(bitmap.astype(np.uint8))
im.save('sloth_1.bmp')
print("Done converting picture")

print("Start generating g-code")

f.write('G00 Z9.000000 \n')
# f.write('G00 X96.352689 Y154.863781 \n')
f.write('G00 X0 Y0 \n')
f.write('G01 Z5.000000 F100.0(Penetrate) \n')
f.write('G91 (Change to incremental coordinates) \n')
y = 0

for y in range(len(bitmap)):
    x = 0 
    while x < len(bitmap[y]):
        result = check_list_for_equals(bitmap[y][x:], 0)
        x += result[0]
        gcode(result[1], result[0]+1, y)
        x += 1

    # begin a new line
    f.write('G90 (Change to absolut coordinates) \n')
    f.write('G00 Z%.2f \n' % (9))
    f.write('G00 X%.2f Y%.2f \n'% (0,( -3*y) * scaling))
    f.write('G01 Z5.000000 F100.0(Penetrate) \n')
    f.write('G91 (Change to incremental coordinates) \n')



f.close()

print("Done creating g-code")