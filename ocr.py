#!/usr/bin/env python3

import os, sys, argparse
import PIL, pytesseract
from PIL import Image, ImageFilter
import json

# DARK MAGIC!
SMPT_W1 = 0.384; SMPT_W2 = 0.47; SMPT_W3 = 0.871; SMPT_W4 = 0.954
SMPT_H1 = 0.27; SMPT_H2 = 0.328; SMPT_H3 = 0.652; SMPT_H4 = 0.718
SC_W1 = 0.33; SC_W2 = 0.46; SC_W3 = 0.817; SC_W4 = 0.949;
SC_H1 = 0.34; SC_H2 = 0.422; SC_H3 = 0.725; SC_H4 = 0.815;

def crop_image(img):
    if img.width / img.height > 1.5:
      context_height = img.height
      context_width = context_height * 1.5
      context_img = img.crop((int((img.width-context_width)/2+1), 0, int(img.width-(img.width-context_width)/2), context_height))
    else:
        context_width = img.width
        context_height = context_width / 1.5
        context_img = img.crop((0, int((img.height-context_height)/2+1), context_width, int(img.height-(img.height-context_height)/2)))
    return context_img

# Precondition: context_img is an image with no blank margin,
# with 1.5 width to height ratio.
# Returns List of Data in the form
# Data = [[smpt, smpt_delta], [score, combo]]
def get_data_from_context(context_img):
    context_height = context_img.height
    context_width = context_img.width
    smpt_coordinates = [(int(SMPT_W1*context_width), 
                         int(SMPT_H1*context_height), 
                         int(SMPT_W2*context_width), 
                         int(SMPT_H2*context_height)),
                        (int(SMPT_W3*context_width), 
                         int(SMPT_H1*context_height), 
                         int(SMPT_W4*context_width), 
                         int(SMPT_H2*context_height)),
                        (int(SMPT_W1*context_width), 
                         int(SMPT_H3*context_height), 
                         int(SMPT_W2*context_width), 
                         int(SMPT_H4*context_height)),
                        (int(SMPT_W3*context_width), 
                         int(SMPT_H3*context_height), 
                         int(SMPT_W4*context_width), 
                         int(SMPT_H4*context_height))]
    score_coordinates = [(int(SC_W1*context_width), 
                          int(SC_H1*context_height), 
                          int(SC_W2*context_width), 
                          int(SC_H2*context_height)),
                         (int(SC_W3*context_width), 
                          int(SC_H1*context_height), 
                          int(SC_W4*context_width), 
                          int(SC_H2*context_height)),
                         (int(SC_W1*context_width), 
                          int(SC_H3*context_height), 
                          int(SC_W2*context_width), 
                          int(SC_H4*context_height)),
                         (int(SC_W3*context_width), 
                          int(SC_H3*context_height), 
                          int(SC_W4*context_width), 
                          int(SC_H4*context_height))]
    
    result = []
    player_smpts = []
    for xy in smpt_coordinates:
        p_smpt_img = context_img.crop(xy)
        p_smpt_img = p_smpt_img.resize((p_smpt_img.width * 2, p_smpt_img.height*2),Image.BICUBIC).filter(ImageFilter.SHARPEN)
        p_smpts = pytesseract.image_to_string(p_smpt_img)
        p_smpts = p_smpts.split('\n')
        p_smpts = [x for x in p_smpts if x]
        player_smpts.append(p_smpts)
    player_score_combos = []
    for xy in score_coordinates:
        p_sc_img = context_img.crop(xy)
        p_sc = pytesseract.image_to_string(p_sc_img, config='-psm 11').split('\n')
        p_sc = [x for x in p_sc if x]
        player_score_combos.append(p_sc)
    return [[data[x][y] for x in range(len(data)) for y in range(len(data[0]))] for data in zip(player_smpts, player_score_combos)]

def sanitize_data(raw_data):
    stage1 = []
    for data in raw_data:
    # assume space can be removed
        smpt = ''
        smpt_delta = ''
        score = ''
        combo = ''
        for c in data[0]:
            if c != ' ':
                smpt += c
        for c in data[1]:
            if c in '+-1234567890':
                smpt_delta += c
        for c in data[2]:
            if c in '1234567890':
                score += c
        for c in data[3]:
            if c in '1234567890':
                combo += c
        stage1.append([smpt, smpt_delta, score, combo])
    # try to resolve smpt, the most noisy data
    smpts = []
    for d in stage1:
        curr = ''
        for c in d[0]:
            if c in '1234567890':
                curr += c
        smpts.append(int(curr))
    while max(smpts) - min(smpts) > min(smpts)*9:
        # must have off-by-one-digit error
        idx = smpts.index(max(smpts))
        smpts[idx] = smpts[idx] // 10 # leave the last one
    
    smpt_deltas = []
    scores = []
    combos = []
    for d in stage1:
        try:
            delta = int(d[1])
        except BaseException:
            delta = 65535
        smpt_deltas.append(delta)
        scores.append(int(d[2]))
        combos.append(int(d[3]))
    
    return list(zip(smpts, smpt_deltas, scores, combos))

def main(path):
    try:
        orig = Image.open(path)
    except BaseException:
        sys.exit("Error reading input file.")
    context_img = crop_image(orig)
    try:
        raw_data = get_data_from_context(context_img)
    except BaseException:
        sys.exit("Error processing image data.")
    final_data = sanitize_data(raw_data)

    output_dict = {'raw': raw_data, 'sanitized': final_data}
    print(json.dumps(output_dict))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="The path to the screenshot.")
    args = parser.parse_args()
    try:
        main(args.file)
    except BaseException:
        print("Unknown error. Please try with different screenshots.")
        sys.exit(1)
