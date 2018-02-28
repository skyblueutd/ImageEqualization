# ImageEqualization
The purpose of this project is changing the color of images based on the linear scaling or equalization of the histogram computed from a window in the image.


Procedure:
1.	Apply the user defined window to the input image, transform the image in the window to Luv space, use dynamic programming to find the max and min value of L.
2.	With the max and min value of L in step 1, apply linear scaling to the whole input image in Luv space. L value is normalized to [0,100] range. Any L less than min is set to 0, and any L greater than max is set to 100. Then the whole image in Luv space is transformed back to RGB space and output as “linearscale.png” image.
3.	Apply histogram equalization to the L value of image in Luv space generated in step 2. Then the new image in Luv space is transformed back to RGB space and output as “equalization.png” image.

Assumptions and strategies:
1.	When transforming from XYZ to Luv,
 d = X+15Y+3Z might be 0, then d is divided. To avoid divided by 0, if d = 0, u’, v’ values are set to 0.
2.	When transforming form Luv to XYZ,
L might be 0, if L = 0, u’, v’ are set to 0. When v’ is 0, X, Y equations are divided by 0. So, set X, Y to 0 when v’=0. 
3.	Any value in Luv, XYZ or RGB space is less than 0 will be set to 0.
4.	In step 1, use dynamic programming to find the max and min value of L. Since there are millions of pixels in an image, math function of min or max in python is very slow. Sometimes, the program dies.
5.	In step 3, L value is Luv space is a float value. To get the histogram in Luv space, L value is rounded to its nearest integer. The histogram is build with the L values in the specified windows. And min and max L values are applied to modify the whole input image.  If the L value of input image pixel is larger than max, then it is set to max. If the L value of input image pixel is less than max, then it is set to min.

Error
When the program is applied to an image with single color. There are some noisy points on the equalization result. It is due to some corner cases which are not calculated properly. Need more work to figure out what the corner cases are.
