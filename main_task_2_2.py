import argparse

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import torch
from lang_sam import LangSAM

import torch
from diffusers import AutoPipelineForInpainting,AutoPipelineForImage2Image
from diffusers.utils import load_image, make_image_grid
import numpy as  np

def main():

    # Parse the arguments and get the inputs from the user

    parser = argparse.ArgumentParser(description='Fill the class object pixels with red.')
    parser.add_argument('--image', help='Path to the input image containing the target object')
    parser.add_argument('--class_name', help='Class name of the target object to be masked')
    parser.add_argument('--output', help='Path to save the output image with the red mask')

    args = parser.parse_args()


    # Predict the mask and bounding boxes with the Language Segment Anything Model

    model = LangSAM()
    image_pil = Image.open(args.image)
    masks, boxes, phrases, logits = model.predict(image_pil.convert("RGB"), args.class_name)
    masks=masks.numpy()[0].astype(np.int8)
    
    mask_pil=Image.fromarray(masks*255)

    # Inpaint the Input Image with the Object Mask and the Prompt

    pipeline = AutoPipelineForInpainting.from_pretrained(
    "runwayml/stable-diffusion-inpainting", torch_dtype=torch.float16, variant="fp16")
    pipeline = pipeline.to("cuda")

    generator = torch.Generator("cuda")
    prompt = "background"
    image_pil =pipeline(prompt=prompt, image=image_pil, mask_image=mask_pil, generator=generator).images[0]

    # Save the Inpainted Image
    plt.imsave(args.output,np.array(image_pil))
    

    
if __name__ == "__main__":

    main()