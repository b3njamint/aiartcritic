from __future__ import print_function
import binascii
from PIL import Image
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import imageio
import os.path

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import CriticItem, ArtPiece

import requests

import  PIL
from PIL import Image
import io
from io import BytesIO

import os, time, sys


def criticView(request):
    all_critic_items = CriticItem.objects.all()
    return render(request, 'critic.html',
        {'all_items': all_critic_items})

def addCritic(request):
    new_item = CriticItem(content = request.POST['content'])
    new_item.save()
    return HttpResponseRedirect('/home/')

def deleteCritic(request, critic_id):
    item_to_delete = CriticItem.objects.get(id=critic_id)
    item_to_delete.delete()
    return HttpResponseRedirect('/critic/')

def aboutView(request):
    all_critic_items = CriticItem.objects.all()
    return render(request, 'about.html',
        {'all_items': all_critic_items})

def contactView(request):
    all_critic_items = CriticItem.objects.all()
    return render(request, 'contact.html',
        {'all_items': all_critic_items})

def surveyView(request):
    all_critic_items = CriticItem.objects.all()
    return render(request, 'survey.html',
        {'all_items': all_critic_items})

def random_test(request):
    return render(request, 'random_test.html')

#######################################################################################################

valueRatioDark = ""
valueRatioMed = ""
valueRatioLight = ""
colorDomRgb = ""
colorDomHex = ""
colorAvgRgb = ""
colorAvgHex = ""

def classifyEra(request):
    image_type = "link"
    image_url = request.POST['url']
    if image_url: #if the user uploads a LINK
        url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelUrls/'
        headers = {
        'accept': 'application/x-www-form-urlencoded'
        }
        image_url_list=[]
        image_url_list.append(image_url)
        data = {
            'modelId': 'e483f029-8ad6-43c4-a0ca-1377a2d04078',
            'urls' : image_url_list
        }

        response = requests.request('POST', url, headers=headers, auth=requests.auth.HTTPBasicAuth('4S_Y0S2gS0DSpnZlz7fwPDa5W5oP5zuA', ''), data=data)

    else: #if the user uploads an IMAGE
        image_type = "file"
        img = request.FILES
        image_file = img['imgfile']
        fs = FileSystemStorage()
        new_image_name = fs.save(image_file.name, image_file)
        image_url = "static/" + fs.url(new_image_name)[1:]
        url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelFile/'
        data = {'file': open(image_url, 'rb'), 'modelId': ('', 'e483f029-8ad6-43c4-a0ca-1377a2d04078')}

        response = requests.post(url, auth= requests.auth.HTTPBasicAuth('4S_Y0S2gS0DSpnZlz7fwPDa5W5oP5zuA', ''), files=data)

    ratings = response.text
    
    labels = ["\"Minimalism\"", "\"Cubism\"", "\"Romanticism\"", "\"Rococo\"", "\"Early_Renaissance\"", "\"Post_Impressionism\"", "\"Ukiyo_e\"", "\"Symbolism\"", "\"Pointillism\"", "\"Art_Noveau_Modern\"", "\"Contemporary_Realism\"", "\"Northern_Renaissance\"", "\"Expressionism\"", "\"Mannerism_Late_Renaissance\"", "\"Baroque\"", "\"Action_painting\"", "\"Pop_Art\"", "\"Analytical_Cubism\"", "\"Fauvism\"", "\"Color_Field_Painting\"", "\"Synthetic_Cubism\"", "\"Realism\"", "\"Native_Art_Primitivism\"", "\"New_Realism\"", "\"Impressionism\"", "\"High_Renaissance\"", "\"Abstract_Expressionism\""]
    eras = ["Minimalism", "Cubism", "Romanticism", "Rococo", "Early Renaissance", "Post Impressionism", "Ukiyo-e", "Symbolism", "Pointillism", "Art Noveau (Modern)", "Contemporary Realism", "Northern Renaissance", "Expressionism", "Mannerism (Late Renaissance)", "Baroque", "Action Painting", "Pop Art", "Analytical Cubism", "Fauvism", "Color Field Painting", "Synthetic Cubism", "Realism", "Naïve Art (Primitivism)", "New Realism", "Impressionism", "High Renaissance", "Abstract Expressionism"]
    probabilities = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    # parse String response
    for i in range(27):
        try:
            era = labels[i]
            probabilities[i] = float(ratings[ratings.index(":", ratings.index(era)) + 1 : ratings.index("}", ratings.index(era))])
            # print ("%s: %.3f%%" % (eras[i], probabilities[i] * 100))
        except ValueError:    
            None

    # get highest probability era        
    era1Label = eras[probabilities.index(max(probabilities))]
    era1Probability = max(probabilities)
    # print ("\nPrimary era similarity is: %s, %.3f%%" % (era1Label, era1Probability * 100))

    # remove maximum to get second
    eras.remove(era1Label)
    probabilities.remove(era1Probability)

    # get second highest probability era
    era2Label = eras[probabilities.index(max(probabilities))]
    era2Probability = max(probabilities)
    # print ("Secondary era similarity is: %s, %.3f%%" % (era2Label, era2Probability * 100))

    cimg = ArtPiece()
    if image_type == "file":
        cimg.img = "/" + image_url[7:]
    elif image_type == "link":
        cimg.img = image_url
    cimg.era1 = str(era1Label)
    cimg.era1Prob = str("{:.2%}".format(era1Probability))
    cimg.era2 = str(era2Label)
    cimg.era2Prob = str("{:.2%}".format(era2Probability))

    #classityMood
    cimg.mood = classifyMood(image_type, image_url)
    # if image_type == "file":
    #     cimg.mood = classifyMood("", image_file)
    # elif image_type == "link":
    #     cimg.mood = classifyMood(image_url)

    #analyzeValue`
    analyzeValue(image_type, image_url)
    # if image_type == "file":
    #     analyzeValue("", image_file)
    # elif image_type == "link":
    #     analyzeValue(image_url)
    cimg.valueRatioDark = valueRatioDark
    cimg.valueRatioMed = valueRatioMed
    cimg.valueRatioLight = valueRatioLight

    #analyzeColor
    analyzeColor(image_type, image_url)
    # if image_type == "file":
    #     analyzeColor("", image_file)
    # elif image_type == "link":
    #     analyzeColor(image_url)
    cimg.colorDomRgb = colorDomRgb
    cimg.colorDomHex = colorDomHex
    cimg.colorAvgRgb = colorAvgRgb
    cimg.colorAvgHex = colorAvgHex

    # solely for formatting purposes
    cimg.result_era1 = "Your piece is most similar to artwork of the " + str(era1Label) + " style with a " + str("{:.2%}".format(era1Probability)) + " similarity."
    cimg.result_era2 = "It is also similar to artwork of the " + str(era2Label) + " style with a " + str("{:.2%}".format(era2Probability)) + " similarity."
    cimg.result_mood = "The mood of this piece is " + cimg.mood + " ."
    cimg.result_dark = "Dark ratio: " + valueRatioDark
    cimg.result_med = "Medium ratio: " + valueRatioMed
    cimg.result_light = "Light ratio: " + valueRatioLight
    cimg.result_dom = "Dominant color: rgb " + colorDomRgb + ", hex " + colorDomHex
    cimg.result_avg = "Average color: rgb " + colorAvgRgb + ", hex " + colorAvgHex

###################################################
# AUTODELTE FILED OLDER THAN 30 S.
    path = 'static/media'
    now = time.time()
    for f in os.listdir(path):
        f = os.path.join(path, f)
        if os.stat(f).st_mtime < now - 30:#7 * 86400:
            if os.path.isfile(f):
                os.remove(f)
####################################################

    return render(request, "critic.html", {'cimg':cimg})

#########################################################################################################

def classifyMood(image_type, image_url):
    if image_type == "link": # if the user inputs a LINK
        url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelUrls/'
        headers = {
        'accept': 'application/x-www-form-urlencoded'
        }
        image_url_list=[]
        image_url_list.append(image_url)
        data = {
            'modelId': '8ee76cc5-5c8a-4fa4-99bd-19185cf1eea4',
            'urls' : image_url_list
        }

        response = requests.request('POST', url, headers=headers, auth=requests.auth.HTTPBasicAuth('D9iah1hwZIVhR-TX23d3RR5wvJkxrBI9', ''), data=data)

    else: # if the user uploads an IMAGE
        url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelFile/'
        data = {'file': open(image_url, 'rb'), 'modelId': ('', '8ee76cc5-5c8a-4fa4-99bd-19185cf1eea4')}
        response = requests.post(url, auth= requests.auth.HTTPBasicAuth('D9iah1hwZIVhR-TX23d3RR5wvJkxrBI9', ''), files=data)
    
    ratings = response.text

    # parse data from model to get energized, calm, pleasant, unpleasant ratings
    try:
        energized = float(ratings[ratings.index("energized") + 25 : ratings.index("}", ratings.index("energized") + 25)])
    except ValueError:
        energized = 0

    try:
        calm = float(ratings[ratings.index("calm") + 20 : ratings.index("}", ratings.index("calm") + 20)])
    except ValueError:
        calm = 0
        
    try:
        pleasant = float(ratings[ratings.index("\"pleasant") + 25 : ratings.index("}", ratings.index("\"pleasant") + 25)])
    except ValueError:
        pleasant = 0
        
    try:
        unpleasant = float(ratings[ratings.index("unpleasant") + 26 : ratings.index("}", ratings.index("unpleasant") + 26)])
    except ValueError:
        unpleasant = 0
        
    # print ("Energized rating: %.3f%%" % (energized * 100))
    # print ("Calm rating: %.3f%%" % (calm * 100))
    # print ("Pleasant rating: %.3f%%" % (pleasant * 100))
    # print ("Unpleasant rating: %.3f%%" % (unpleasant * 100))

    # determine mood
    mood = ""

    if energized == max(energized, calm, pleasant, unpleasant):
        if calm == max(calm, pleasant, unpleasant):
            mood = "energized yet calm"
        elif pleasant == max(calm, pleasant, unpleasant):
            mood = "excited and lively"
        elif unpleasant == max(calm, pleasant, unpleasant):
            mood = "tense and nervous"
    elif calm == max(energized, calm, pleasant, unpleasant):
        if energized == max(energized, pleasant, unpleasant):
            mood = "calm yet energized"
        elif pleasant == max(energized, pleasant, unpleasant):
            mood = "calm and serene"
        elif unpleasant == max(energized, pleasant, unpleasant):
            mood = "gloomy and sad"
    elif pleasant == max(energized, calm, pleasant, unpleasant):
        if energized == max(energized, calm, unpleasant):
            mood = "cheerful and happy"
        elif calm == max(energized, calm, unpleasant):
            mood = "relaxed and carefree"
        elif unpleasant == max(energized, calm, unpleasant):
            mood = "pleasant yet unpleasant" #????????????????
    elif unpleasant == max(energized, calm, pleasant, unpleasant):
        if energized == max(energized, calm, pleasant):
            mood = "irritated and annoyed"
        elif calm == max(energized, calm, pleasant):
            mood = "bored and weary"
        elif pleasant == max(energized, calm, pleasant):
            mood = "unpleasant yet pleasant"
    # if one value is extremely high, ignore others
    if energized > 0.93:
        mood = "energized"
    if calm > 0.93:
        mood = "calm"
    if pleasant > 0.93:
        mood = "pleasant"
    if unpleasant > 0.93:
        mood = "unpleasant"

    return mood

 #########################################################################################

def analyzeValue(image_type, image_url):
    if image_type == "link":
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(image_url)
    # img = Image.open(BytesIO(response.content)).convert('L')
    img = img.convert('L')
    img.thumbnail((500,500))
    WIDTH, HEIGHT = img.size

    grayscaleValues = list(img.getdata()) # convert image data to a list of integers

    # convert to 2D list if necessary
    # grayscaleValues = [grayscaleValues[offset:offset+WIDTH] for offset in range(0, WIDTH*HEIGHT, WIDTH)]

    darkCount = 0
    medCount = 0
    lightCount = 0
    totalCount = len(grayscaleValues)

    for px in grayscaleValues:
        if px < 85:
            darkCount = darkCount + 1
        elif px > 170:
            lightCount = lightCount + 1
        else:
            medCount = medCount + 1

    darkRatio = darkCount / totalCount 
    medRatio = medCount / totalCount
    lightRatio = lightCount / totalCount

    # print ("WIDTH: " + str(WIDTH))
    # print ("HEIGHT: " + str(HEIGHT))
    # print ("PIXELS: " + str(totalCount))
    # print ("DARK RATIO: " + str(darkRatio))
    # print ("MEDIUM RATIO: " + str(medRatio))
    # print ("LIGHT RATIO: " + str(lightRatio))

    global valueRatioDark
    valueRatioDark = str("{:.2%}".format(darkRatio))
    global valueRatioMed
    valueRatioMed = str("{:.2%}".format(medRatio))
    global valueRatioLight
    valueRatioLight = str("{:.2%}".format(lightRatio))


def analyzeColor(image_type, image_url):    
    # number of colors to convert image to
    NUM_CLUSTERS = 4
    #################### determine main color  ####################
    # read image, compress

    if image_type == "link":
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(image_url)
    # img = Image.open(BytesIO(response.content))
    
    # img = Image.open('/Users/benjamin.0t/Desktop/Art/brockmann-mockup1.png')
    img.thumbnail((150, 150))
    arry = np.asarray(img)
    shape = arry.shape
    arry = arry.reshape(np.product(shape[:2]), shape[2]).astype(float)

    # modified https://stackoverflow.com/questions/3241929
    # calculate clustered colors 
    codes, dist = scipy.cluster.vq.kmeans(arry, NUM_CLUSTERS)
    # print('cluster colors:\n', codes)

    vecs, dist = scipy.cluster.vq.vq(arry, codes)    # assign codes
    counts, bins = np.histogram(vecs, len(codes))    # count occurrences

    # codes is numpy.ndarray
    index_max = np.argmax(counts)                    # sort and get dominant
    #domRgb = codes[index_max] # ["%.2f" % member for member in codes[index_max]]
    domRgb = [ "{:0.0f}".format(x) for x in codes[index_max] ]
    domHex = binascii.hexlify(bytearray(int(c) for c in codes[index_max])).decode('ascii')

    # print('DOMINANT COLOR: %s (#%s)' % (domRgb, domHex))

    # #################### saves clustered image ####################
    # # modified https://stackoverflow.com/questions/3241929
    # c = arry.copy()
    # for i, code in enumerate(codes):
    #     c[scipy.r_[np.where(vecs==i)],:] = code
    # # converts back to 2d array and saves as image
    # imageio.imwrite('clustered.png', c.reshape(*shape).astype(np.uint8))


    #################### find average color ####################
    def calcAvgColor (img):
        width, height = img.size
    
        rSum = 0
        gSum = 0
        bSum = 0
        aSum = 0
        count = 0
        # sum r g b values and divide by total to get average
        for x in range(0, width):
            for y in range(0, height):
                try:
                    r, g, b, a = img.getpixel((x,y))
                except:
                    r, g, b = img.getpixel((x,y))
                rSum += r
                gSum += g
                bSum += b
                count += 1
        return (rSum / count, gSum / count, bSum / count)

    avgRgbTemp = calcAvgColor(img)
    avgHex = binascii.hexlify(bytearray(int(c) for c in avgRgbTemp)).decode('ascii')
    avgRgbTemp = ["%.0f" % x for x in avgRgbTemp]
    avgRgb = "['" + avgRgbTemp[0] + "', '" + avgRgbTemp[1] + "', '" + avgRgbTemp[2] + "']"

    # print('AVERAGE COLOR: %s (#%s)' % (avgRgb, avgHex))

    global colorDomRgb
    colorDomRgb = str(domRgb)
    global colorDomHex
    colorDomHex = str("#" + domHex)
    global colorAvgRgb
    colorAvgRgb = str(avgRgb)
    global colorAvgHex
    colorAvgHex = str("#" + avgHex)

    



