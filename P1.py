import cv2
import math
import numpy as np
import sys

def gamma(val):
    if val<0.00304:
        return 12.92*val
    else:
        return 1.055*val**(1/2.4) - 0.055

def invgamma(val):
    if val<0.03928:
        return val/12.92
    else:
        return ((val+0.055)/1.055)**2.4


def bgr2Luv(b, g, r):
    #sRGB -> non_linear RGB
    non_li_b = b / 255
    non_li_g = g / 255
    non_li_r = r / 255
    #non_linear RGB -> linear RGB
    li_b = invgamma(non_li_b)
    li_g = invgamma(non_li_g)
    li_r = invgamma(non_li_r)
    ######### linear RGB -> XYZ #############
    mat = ([0.412453, 0.35758, 0.180423],
           [0.212671, 0.71516, 0.072169],
           [0.019334, 0.119193, 0.950227])
    RGB = ([li_r, li_g, li_b])
    XYZ = np.dot(mat, RGB)
    X = XYZ[0]
    Y = XYZ[1]
    Z = XYZ[2]
    ########## XYZ -> Luv ##################
    Xw = 0.95
    Yw = 1.0
    Zw = 1.09
    uw = 4 * Xw / (Xw + 15 * Yw + 3 * Zw)
    vw = 9 * Yw / (Xw + 15 * Yw + 3 * Zw)

    t = Y / Yw
    if t > 0.008856:
        L = 116 * t ** (1 / 3) - 16
    else:
        L = 903.3 * t

    d = X + 15 * Y + 3 * Z
    if d == 0:
        uu = 0
        vv = 0
    else:
        uu = 4 * X / d
        vv = 9 * Y / d
    u = 13 * L * (uu - uw)
    v = 13 * L * (vv - vw)
    return L, u, v


def Luv2bgr(L, u, v):
    # L'uv -> XYZ
    Xw = 0.95
    Yw = 1.0
    Zw = 1.09
    uw = (4 * Xw) / (Xw + 15 * Yw + 3 * Zw)
    vw = (9 * Yw) / (Xw + 15 * Yw + 3 * Zw)

    if L == 0:
        uu = 0
        vv = 0
    else:
        uu = (u + 13 * uw * L) / (13 * L)
        vv = (v + 13 * vw * L) / (13 * L)

    if L > 7.9996:
        Y = (((L + 16) / 116) ** 3) * Yw
    else:
        Y = L * Yw / 903.3

    if vv == 0:
        X = 0
        Z = 0
    else:
        X = Y * 2.25 * uu / vv
        Z = Y * (3 - 0.75 * uu - 5 * vv) / vv

    # XYZ ->linear RGB
    mat = ([3.240479, -1.53715, -0.498535],
           [-0.969256, 1.875991, 0.041556],
           [0.055648, -0.204043, 1.057311])
    XYZ = ([X, Y, Z])
    RGB = np.dot(mat, XYZ)
    li_r = RGB[0]
    li_g = RGB[1]
    li_b = RGB[2]
    if li_r < 0:
        li_r = 0
    if li_g < 0:
        li_g = 0
    if li_b < 0:
        li_b = 0
    if li_r > 1:
        li_r = 1
    if li_g > 1:
        li_g = 1
    if li_b > 1:
        li_b = 1
    # linear RGB -> nonlinear RGB
    non_li_R = gamma(li_r)
    non_li_G = gamma(li_g)
    non_li_B = gamma(li_b)
    sR = non_li_R * 255
    sG = non_li_G * 255
    sB = non_li_B * 255

    return sB, sG, sR


if(len(sys.argv) != 8) :
    print(sys.argv[0], ": takes 6 arguments. Not ", len(sys.argv)-1)
    print("Expecting arguments: w1 h1 w2 h2 ImageIn ImageOut.")
    print("Example:", sys.argv[0], " 0.2 0.1 0.8 0.5 fruits.jpg out.png")
    sys.exit()

w1 = float(sys.argv[1])
h1 = float(sys.argv[2])
w2 = float(sys.argv[3])
h2 = float(sys.argv[4])
name_input = sys.argv[5]
name_output1 = sys.argv[6]
name_output2 = sys.argv[7]


if(w1<0 or h1<0 or w2<=w1 or h2<=h1 or w2>1 or h2>1) :
    print(" arguments must satisfy 0 <= w1 < w2 <= 1, 0 <= h1 < h2 <= 1")
    sys.exit()

inputImage = cv2.imread(name_input, cv2.IMREAD_COLOR)
if(inputImage is None) :
    print(sys.argv[0], ": Failed to read image from: ", name_input)
    sys.exit()

cv2.imshow("input image: " + name_input, inputImage)

rows, cols, bands = inputImage.shape # bands == 3
W1 = round(w1*(cols-1))
H1 = round(h1*(rows-1))
W2 = round(w2*(cols-1))
H2 = round(h2*(rows-1))


#find max and min of L in the window
min = 100
max = 0
for i in range(H1, H2):
    for j in range(W1, W2):
        b, g, r = inputImage[i, j]
        L, u, v =  bgr2Luv(b, g, r)
        if L > max and L <= 100:
            max = L
        if L < min and L >= 0:
            min = L
rate = 100 / (max - min)
# print(min,max)

#linearscal of the image
linearscaleImage = np.zeros([rows, cols, bands], dtype=np.uint8)
for i in range(0, rows):
    for j in range(0, cols):
        b, g, r = inputImage[i, j]
        L, u, v = bgr2Luv(b, g, r)
        if L < min:
            L1 = 0
        elif L > max:
            L1 = 100
        else:
            L1 = (L - min) * rate

        linearscaleImage[i, j] = Luv2bgr(L1, u, v)

cv2.imshow("linearscale:", linearscaleImage)
cv2.imwrite(name_output1, linearscaleImage);


#equalization of the image
listh = [0]*101
listf = [0]*101
listl = [0]*101
#count number of pixel for listh
c = 0
#get h(i)
for i in range(H1, H2):
    for j in range(W1, W2):
        c = c+1
        be,ge,re = inputImage[i, j]
        Le, ue, ve = bgr2Luv(be, ge, re)
        T = int(round(Le))
        listh[T] = listh[T]+1
#get f(i)
listf[0] = listh[0]
for k in range (1,101):
    listf[k] = listf[k-1]+listh[k]
#map L
listl[0] = math.floor(listf[0]*50.5/c)
for l in range (1,101):
    listl[l] = math.floor((listf[l-1]+listf[l])*50.5/c)

print(c)
print(listh)
print(listf)
print(listl)

equalizationImage = np.zeros([rows, cols, bands], dtype=np.uint8)
#equalization and output
for i in range(0, rows):
    for j in range(0, cols):
        bo,go,ro = inputImage[i, j]
        Lo,uo,vo = bgr2Luv(bo, go, ro)
        if Lo < min:
            Lo1 = 0
        elif Lo > max:
            Lo1 = 100
        else:
            Lo1 = Lo
        outT = int(round(Lo1))
        #map L value
        outL = listl[outT]
        equalizationImage[i,j]=Luv2bgr(outL,uo,vo)

cv2.imshow("equalizationImage:", equalizationImage)
cv2.imwrite(name_output2, equalizationImage);

# wait for key to exit
cv2.waitKey(0)
cv2.destroyAllWindows()
