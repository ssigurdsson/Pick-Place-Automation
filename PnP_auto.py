#Stefan Sigurdsson, Brown University 8/1/2018
#Automated Pick&Place device sorting (creates files with coords of devices compatible with the P&P software)
#Initial position is x=-1650 y=-1550 on the P&P interface
import cv2, time
import numpy as np
import pyautogui as pya
pya.FAILSAFE = True


gpx, gpy = 0, 0 #internal coordinates relative to the top left corner of the device plane 
offsetx, offsety, offsetz = -1650 + 15, -1550 + 45, 8160 #Set P&P position of the nozzle (corrected for nozzle/purple-cross discrepancy (15,45) - CHECK THIS EVERY TIME)
poffsetx, poffsety, poffsetz, ppitch = -950, 1150, 8160, 50 #Set P&P position & pitch of placement locations

#Adjust these for greater device discrimination from the background
minarea, maxarea = 1550, 2320
surface_variance = 6
kernelsize, blursize = 3, 3

#Filenames for feeders and parts list
filenames = ['botfile.fdr', 'bpartsfile.pts', 'topfile.fdr', 'tpartsfile.pts']

#Calibration variables
d_plane_x, d_plane_y = 800, 800 #defining the area in which the devices reside in P&P units
pixel_to_unit = 25/45 #pixel to unit ratio
wait_constant = 1.2 #seconds delay to allow the machine to move and coordinates to update
unit_move = 100 #how far the P&P machine moves each time


#initializing sequence
time.sleep(3)
imginit = pya.screenshot()
imginit = cv2.cvtColor(np.array(imginit), cv2.COLOR_RGB2BGR)
cv2.imwrite("check.png", imginit[range(300,1000)]) #check that the purple cross is visible, adjust from 300,1000 if needed (depending on the monitor resolution)
#find the purple cross center on the screenshot
for yp in range(300,1000):
    for xp in range(300,1000):
        if np.all(imginit[yp][xp] == [250, 0, 250]):
                if np.all(imginit[yp+1][xp+1] == [250, 0, 250]):
                    initcenterx, initcentery = xp+1, yp
                    break

#Select the device plane
calx, caly = 100, 315 #Sets the frame position
xpp, ypp = initcenterx - calx, initcentery - caly #Relative positions to the purple cross



#Updates the device coordinates in the field of view every cycle
def update_device_cords(move_n):
    img = pya.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    file_name = "result%d.png" % move_n

    image = img[ypp:ypp+660, xpp:xpp+660] #crop device plane only
    #cv2.imshow('image', image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    #Deletes the 1-pixel wide purple crosshair (fade to nearby color)
    def purple_line_to_neighbor(imagein):
        for xp in range(660): imagein[caly][xp] = imagein[caly+1][xp]
        for yp in range(660): imagein[yp][calx] = imagein[yp][calx+1]
        return imagein

    def find_device_contours(imagein):
        imagein = imagein.copy()
        #Gives all the contours, contour approximation compresses the contours to a few points per contour.
        contours, hierarchy = cv2.findContours(imagein, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        #Finds the contour sizes
        contour_sizes = []
        for c in contours: contour_sizes.append([cv2.contourArea(c), c])

        #Choose contours based on target surface 
        filtered_contours = []
        for ctr in contour_sizes:
            if minarea < ctr[0] < maxarea: 
                filtered_contours.append(ctr[1])
        return filtered_contours



    def find_devices(imagergb):
        imagergb = purple_line_to_neighbor(imagergb)
        imagegray = cv2.cvtColor(imagergb, cv2.COLOR_BGR2GRAY)

        #Eliminates noise from our image by bluring it via a Gaussian filter
        image_blurred = cv2.GaussianBlur(imagegray, (blursize, blursize), 0)

        #Filter by intensity
        image_mask = cv2.inRange(image_blurred, 0, 235)

        #Clean up small holes and noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernelsize, kernelsize))
        image_mask = cv2.morphologyEx(image_mask, cv2.MORPH_CLOSE, kernel)
        image_mask = cv2.morphologyEx(image_mask, cv2.MORPH_OPEN, kernel)

        #Find device contours using the mask
        device_contours = find_device_contours(image_mask)
        #Overlay mask onto the image
        rgb_mask = cv2.cvtColor(image_mask, cv2.COLOR_GRAY2RGB)
        overlayed = cv2.addWeighted(rgb_mask, 0.35, imagergb, 0.65,0)


        centers = [] 
        #Draw squares and mark center points
        for ctr in device_contours:
            rect = cv2.minAreaRect(ctr)
            #filter by square shape (select only ones with ~even length sides)
            if max(rect[1])/min(rect[1]) < 1.13:
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                overlayed = cv2.drawContours(overlayed, [box], 0, (0, 255, 0), 1)
    
                #Mark the device center
                M = cv2.moments(ctr)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])

                #Determine if the device is upside down
                device_surface = imagegray[cy-9:cy+9, cx-9:cx+9]
                if np.std(device_surface) > surface_variance: 
                    cv2.putText(overlayed, ".", (cx, cy), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.1, (0, 0, 255), 1)
                    centers.append([cx, cy, 1]) #right-side-up
                else: 
                    cv2.putText(overlayed, ".", (cx, cy), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.1, (255, 0, 0), 1)
                    centers.append([cx, cy, 0]) #upside-down

        return overlayed, centers


    output_image, device_coords = find_devices(image)
    cv2.imwrite(file_name, output_image) #Save the image every cycle
    print(device_coords)
    return device_coords




#Move cursor and click to control the interface
def move(unit, dirr, axis):
    if dirr == 'pos' and axis == 'x':   #+xstep moves right
        pya.moveTo(initcenterx + 1134, initcentery - 114, duration=0.10)
    elif dirr == 'neg' and axis == 'x': #-xstep moves left
        pya.moveTo(initcenterx + 1184, initcentery - 114, duration=0.10)
    elif dirr == 'pos' and axis == 'y': #+ystep moves up
        pya.moveTo(initcenterx + 1184, initcentery - 94, duration=0.10)
    else:                         #-ystep moves down
        pya.moveTo(initcenterx + 1134, initcentery - 94, duration=0.10)
    time.sleep(0.12)
    pya.click()

#The Machine observes devices many times as it does not move that far each step
#This helps increase the accuracy of the device coordinates
#Unique devices found are added and already found ones have their coordinates updated through averaging
def corroborate_trck(dl, gpx, gpy, dcords):
    for dc in dcords:
        present = False
        cordx, cordy = round(gpx + dc[0]*pixel_to_unit), round(gpy + dc[1]*pixel_to_unit)
        for d in range(len(dl)-1,-1,-1): #Only needs to iterate through the last few devices usually
            if abs(cordx - dl[d][0]) < 12: #Checks if the device was previously found
                if abs(cordy - dl[d][1]) < 12:
                    present = True
                    times_seen = dl[d][3]+1
                    print('match is', [cordx,cordy])
                    #Updates the coordinate with the averag position for all encounters so far
                    dl[d] = [dl[d][0] + round((cordx-dl[d][0])/times_seen), dl[d][1] + round((cordy-dl[d][1])/times_seen), dl[d][2] + dc[2], times_seen]
                    break
        if not present: #If the device was not previously found
            dl.append([cordx, cordy, dc[2], 1])
            print('dl is', dl)
    return dl



device_list = []
move_n = 0
#While loop scans the entire device plane. The machine moves once per loop.
while 1:
    move_n +=1
    device_cords = update_device_cords(move_n)
    device_list = corroborate_trck(device_list, gpx, gpy, device_cords) #Lists devices found

    if gpx < d_plane_x:
        gpx += unit_move
        move(unit_move, 'pos', 'x')
    elif gpy < d_plane_y:
        gpy += unit_move
        move(unit_move, 'neg', 'y')
        #Moves all the way left when we move in the y-direction to reduce the effects of hysteresis
        for _ in range(d_plane_x//unit_move):
            gpx -= unit_move
            move(unit_move, 'neg', 'x')
            time.sleep(0.30)
    else: break
    time.sleep(wait_constant)



#Once the machine has run through the device plane and gathered all the device coordinates
#we write those coordinates into files that are fed into the machine for automatic picking & placing.

#Writes feeder and parts files based on device_list
files = ['']*4
tn = bn = 0
for d in device_list:
    if d[3] >= 3: #Ignores devices not seen consistently enough
        #Add device coords only if the device is consistently found to be upside-down or right-side-up
        if d[2] < 0.3*d[3]: #upside-down (stdev < surface_variance)
            bn += 1
            files[0] += str(d[0] + offsetx) + ',' + str(d[1] + offsety) + ',' + str(offsetz) + ',Yes,0,0,0,0,0,1,No,,0,,0,0,0,1,,,,,,,,0,0,1,1,0,0,0,0,0,0,0,0,\n'
            files[1] += ',' + str(poffsetx - (bn-1)*ppitch) + ',' + str(poffsety + bn*ppitch//4) + ',' + str(poffsetz) + ',0,' + str(bn) + ',No,,No,2000,,No\n'
        elif d[2] > 0.7*d[3]: #right-side-up (stdev > surface_variance)
            tn += 1
            files[2] += str(d[0] + offsetx) + ',' + str(d[1] + offsety) + ',' + str(offsetz) + ',Yes,0,0,0,0,0,1,No,,0,,0,0,0,1,,,,,,,,0,0,1,1,0,0,0,0,0,0,0,0,\n'
            files[3] += ',' + str(poffsetx - (tn-1)*ppitch) + ',' + str(poffsety + tn*ppitch//4) + ',' + str(poffsetz) + ',0,' + str(tn) + ',No,,No,2000,,No\n'

files[0] = 'Place Feeders List\n' + str(bn) + '\n' + files[0]
files[1] = 'Placing Parts List\n100,100,0,0,0,0\n' + str(bn) + '\n' + files[1] + '0,0,0,0,,,5000,5000,'
files[2] = 'Place Feeders List\n' + str(tn) + '\n' + files[2]
files[3] = 'Placing Parts List\n100,100,0,0,0,0\n' + str(tn) + '\n' + files[3] + '0,0,0,0,,,5000,5000,'
#Open, Write, and Close the files
for i in range(4):
    with open(filenames[i], 'w') as file:
        file.write(files[i])