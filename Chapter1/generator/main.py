import csv
import random
import json
import os

from bisect import bisect
from random import random

from PIL import Image


def weighted_choice(choices):
    """
    Given a list of choices with the layer followed by a weight, return one of the choices at random.
    :param choices: A list of choices following the form [ ('choices', <weight>) ]
    :return: The selected choice
    """
    values, weights = zip(*choices)
    total = 0
    aggregate_weights = []

    for w in weights:
        total += w
        aggregate_weights.append(total)
    x = random() * total
    i = bisect(aggregate_weights, x)

    return values[i]


def build_layer_list(file_path, header_row=True):
    """
    Read in the layer metadata and build a list of the layers.
    :param header_row: Default to true, skips the first row of the csv file.
    :param file_path: The path to the layer metadata.
    :return: A list of the layers
    """
    layer_list = []
    with open(str(file_path)) as csv_data:
        csv_reader = csv.reader(csv_data, delimiter='\t')
        for row in csv_reader:
            if header_row:
                header_row = False
                continue
            else:
                this_row = []
                for field in row:
                    this_row.append(field.strip())

            layer_list.append(this_row)

    return layer_list


def build_layer_dictionary(layers):
    """
    Build up a dictionary that contains the layer name as the key.
    :param layers: A list of layers.
    :return: A dictionary with the layer name as the key and a dictionary of metadata as the values.
    """
    layer_dictionary = {}

    for layer in layers:
        this_layer = str(layer[0])
        this_dict = {}

        if this_layer not in layer_dictionary:
            layer_dictionary[this_layer] = this_dict
        else:
            this_dict = layer_dictionary[this_layer]

        this_dict['group'] = layer[1]
        this_dict['order'] = layer[2]
        this_dict['weight'] = layer[3]

        if len(layer) > 4:
            this_dict['metadata_key'] = layer[4]
            this_dict['metadata_value'] = layer[5]
        else:
            this_dict['metadata_key'] = ''
            this_dict['metadata_value'] = ''
        layer_dictionary[this_layer] = this_dict

    return layer_dictionary


def build_layer_weights_by_group(layers):
    """
    Build up a dictionary that contains the group as the key and a list of the layers as the values with their names
    and their weights as a tuple.
    :param layers: A list of layers.
    :return: A dictionary with the group as the key and the values as a list of tuple with the layer and the weights.
    """
    layer_dictionary = {}

    for layer in layers:
        this_group = str(layer[1])
        group_layer_list = []

        if this_group not in layer_dictionary:
            layer_dictionary[this_group] = group_layer_list
        else:
            group_layer_list = layer_dictionary[this_group]

        layer_tuple = (layer[0], int(layer[3]))
        group_layer_list.append(layer_tuple)

    return layer_dictionary


def build_image_layers(layer_weights_by_group, layer_dict, number_of_images_to_mint):
    """
    Returns a list of image layers. Each set of image layers is unique.
    :param layer_dict: A dictionary of layers that reference metadata
    :param number_of_images_to_mint: The number of assets to mint.
    :return: A list of image layers where each set of image layers is unique.
    """
    image_set = set()
    layers = []
    for i in range(0, number_of_images_to_mint):

        delimiter = ','
        while True:
            layers_for_image = []
            for group in layer_weights_by_group.keys():
                choice = weighted_choice(layer_weights_by_group[group])
                layer_order = layer_dict[choice]['order']
                layers_for_image.append((choice, layer_order))

            layers_as_string = delimiter.join(layers_for_image[0])
            # if this set of assets is unique continue, otherwise roll again
            # this ensures we don't end up with duplicate NFTs.
            if str(layers_as_string) not in image_set:
                layers_sorted = sorted(layers_for_image, key=lambda x: x[1])
                layers.append(layers_sorted)
                image_set.add(layers_as_string)
                break

    return layers


def build_metadata_for_image(layers, layer_dict, image_number):
    """
    Build the metadata for the image.
    :param layers: The list of layers for the image.
    :param layer_dict: The dictionary with the layer name as the key.
    :param image_number: The image number.
    :return: A dictionary consisting of the metadata.
    """
    metadata = {}
    metadata['description'] = 'Helmet designed to explore moons!'
    metadata['external_url'] = 'https://www.reddit.com/r/CryptoCurrency'
    metadata['image'] = f'https://storage.googleapis.com/{image_number}.png'
    metadata['name'] = f'Moon Helmet #{image_number}'
    metadata['tokenId'] = image_number

    attributes = []
    for layer in layers:
        layer_name = layer[0]
        metadata_key = layer_dict[layer_name]['metadata_key']
        if metadata_key != '':
            attribute_dict = {'trait_type': metadata_key, 'value': layer_dict[layer_name]['metadata_value']}
            attributes.append(attribute_dict)

    if attributes:
        metadata['attributes'] = attributes
    else:
        metadata['attributes'] = []

    return metadata


def build_image(layers, asset_dir, image_dir, image_number):
    """
    Build the final image for the helmet
    :param layers: The layers of the helmet.
    :param asset_dir: The directory where the layer assets are held.
    :param image_dir: The directory where the images are placed.
    :param image_number: The image number.
    :return: None
    """
    base_image = Image.new('RGBA', size=(320, 320))
    for layer in layers:
        image_file = asset_dir + str(layer[0])
        paste_image = Image.open(image_file)
        base_image = Image.alpha_composite(base_image, paste_image)

    base_image.save(image_dir + str(image_number) + ".png", format="png")


def print_metadata(metadata_list, meta_dir):
    """
    Print out the metadata for the images
    :param metadata_list: A list of all the metadata dictionaries.
    :param meta_dir: The directory where the lists should be placed.
    :return: None
    """
    for d in metadata_list:
        json_string = json.dumps(d, indent=4)
        token_id = d['tokenId']
        file = meta_dir + str(token_id) + ".json"
        f = open(file, "w")
        f.write(json_string)
        f.close


def main():
    number_of_images_to_mint = 10

    script_dir = os.path.dirname(__file__)
    meta_dir = os.path.join(script_dir, "../output/metadata/")
    asset_dir = os.path.join(script_dir, "../assets/")
    image_dir = os.path.join(script_dir, "../output/images/")

    layers = build_layer_list('data/layer_metadata.tsv')
    layer_dict = build_layer_dictionary(layers)
    layer_weights_by_group = build_layer_weights_by_group(layers)

    image_layers = build_image_layers(layer_weights_by_group, layer_dict, number_of_images_to_mint)

    metadata_list = []
    image_number = 0
    for layers in image_layers:
        image_number += 1

        this_metadata = build_metadata_for_image(layers, layer_dict, image_number)
        metadata_list.append(this_metadata)

        build_image(layers, asset_dir, image_dir, image_number)

    print_metadata(metadata_list, meta_dir)


if __name__ == "__main__":
    main()
