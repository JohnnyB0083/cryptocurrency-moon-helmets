## Chapter 1 - Art Generation


### Summary
In this chapter we will explore how to generate art using python.
We will be using `.png` layers and stacking them on top of one another to make the images. 
Each layer is assigned an order and probability. The order is used to arrange the layers when building
the final composite image. The weights allow us to make some traits more rare if we want.

#### Generating the art
Under the [assets](assets/) folder there are a number of `.png` files. Each one of these files is a layer that
will ultimately make up the composite image when applied in a specific order. Under the [data](data/) folder
there is a file [layer_metadata](data/layer_metadata.tsv) that has each of the layers in it with some metadata around the
layer. The table below describes the fields in the metadata file.

|Layer Name|Group|Layer Order|Layer Weight|Metadata Key|Metadata Value|
|----------|----------|----------|----------|----------|----------|
|This is the name of the layer|This is a logical grouping|This is the order the layer should be painted ascending|This is the weight of the layer being picked, higher value means more frequently selected|This is the metadata key, will translate to trait_type|This is the value for the trait_type|

Using the metadata and the layers we can construct the images by doing the following:
1. Deciding how many images we want to mint.
2. Selecting each layer in a group using the weight. The larger the weight the more frequent the layer will be picked.
3. Once an image is built we need to make sure another image like it has not been created already. We can use a set in python to check if the selected layers have been produced already.
4. After the layers are built up we can then create the image and the metadata for the image.

#### Running the script

Simply run the main.py script, if you want to specify images use the -n command line argument to 
specify how many NFTs to generate.