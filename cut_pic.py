from math import ceil
from PIL import Image
import os
from config import config

def cut_without_gap(img):
    w_count = config['GITHUB_WIDTH_COUNT']
    sub_length = int(img.size[0] / 7)
    new_width = sub_length * w_count
    if config['whether_crop_image_height']:
        h_count = int(img.size[1] / sub_length)
    else:
        h_count = ceil(img.size[1] / sub_length)
    new_height = sub_length * h_count
    img_t = Image.new('RGBA', (new_width, new_height), config['color_to_fill_in_blank'])
    img_t.paste(img)
    img = img_t
    for x_i in range(0, w_count):
        for y_i in range(0, h_count):
            img_t = img.crop((x_i * sub_length, y_i * sub_length, (x_i + 1) * sub_length, (y_i + 1) * sub_length))
            img_t.save(f'./out/{y_i}-{x_i}.png')
    return (h_count, w_count)
    
def cut_with_gap(img):
    # sub_length = 35px, gap_length = 3px => gap_length = (sub_length * 3) / 35
    # sub_length * w_count + gap_length * (w_count - 1) = img.size[0]
    # => sub_length * w_count + (sub_length * 3 * (w_count - 1)) / 35 = img.size[0]
    # => sub_length * 35 * w_count + sub_length * 3 * (w_count - 1) = 35 * img.size[0]
    # => sub_length * (35 * w_count + 3 * w_count - 3) = 35 * img.size[0]
    # => sub_length = 35 * img.size[0] / (35 * w_count + 3 * w_count - 3)
    #################################################################
    # sub_length * h_count + gap_length * (h_count - 1) = img.size[1]
    # => sub_length * h_count + gap_length * h_count - gap_length = img.size[1]
    # => (sub_length + gap_length) * h_count = img.size[1] + gap_length
    # => h_count = (img.size[1] + gap_length) / (sub_length + gap_length) 
    w_count = config['GITHUB_WIDTH_COUNT']
    sub_length = int(35 * img.size[0] / (35 * w_count + 3 * w_count - 3))
    gap_length = int((sub_length * 3) / 35)
    new_width = sub_length * w_count + gap_length * (w_count - 1)
    if config['whether_crop_image_height']:
        h_count = int((img.size[1] + gap_length )/ (sub_length + gap_length))
    else:
        h_count = ceil((img.size[1] + gap_length )/ (sub_length + gap_length))
    new_height = sub_length * h_count + gap_length * (h_count - 1)
    img_t = Image.new('RGBA', (new_width, new_height), config['color_to_fill_in_blank'])
    img_t.paste(img)
    img = img_t
    for x_i in range(0, w_count):
        for y_i in range(0, h_count):
            img_t = img.crop((
                x_i * (sub_length + gap_length), 
                y_i * (sub_length + gap_length), 
                (x_i + 1) * (sub_length + gap_length) - gap_length, 
                (y_i + 1) * (sub_length + gap_length) - gap_length
            ))
            img_t.save(f'./out/{y_i}-{x_i}.png')
    return (h_count, w_count)

def cut():
    img = Image.open(config['pic_path'])
    if os.path.exists('./out'):
        for i in os.listdir('./out'):
            os.remove(f'./out/{i}')
    else:
        os.mkdir('./out')
    if config['whether_with_gap']:
        return cut_with_gap(img)
    else:
        return cut_without_gap(img)

if __name__ == "__main__":
    cut()