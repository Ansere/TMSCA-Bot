import matplotlib.pyplot as plt
import sympy
import io
import base64
import numpy as np
import PIL.Image as Image
import aiohttp
import PIL.ImageOps as imgo
import asyncio

def latexRender(latexstr):
    try:
        lat = sympy.latex(r"" + latexstr)
        plt.figure(frameon = True, facecolor = "#2c2f33", figsize=(0.01, 0.01))
        plt.axes(frameon=0)
        plt.text(0, 0, r"$%s$" % lat, fontsize = 50, color = "w")
        plt.xticks(())
        plt.yticks(())
        owo = io.BytesIO()
        plt.savefig(owo, bbox_inches = 'tight', verticalalignment = True, facecolor = "#36393F")
        plt.close()
        owo.seek(0)
        return base64.b64encode(owo.read())
    except:
        if latexstr == "":
            return "Needs an argument!"
        else:
            return "Invalid LaTeX string!"

async def renderfromURL(url, filter):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print('Could not download file...')
                return False
            data = io.BytesIO(await resp.read())
    data.seek(0)
    im = Image.open(data).convert('RGB')
    im = imgo.invert(im)
    im = im.convert('RGBA')

    data = np.array(im)   # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T # Temporarily unpack the bands for readability
    # Replace white with red... (leaves alpha values alone...)
    black_areas = (red <= filter - 1) & (blue <= filter - 1) & (green <= filter - 1) & (red >= 0) & (blue >= 0) & (green >= 0)# Transpose back needed
    data[..., :-1][black_areas.T] = (54, 57, 63)
    im2 = Image.fromarray(data)
    imgbyte = io.BytesIO()
    im2.save(imgbyte, format = 'PNG')
    imgbyte.seek(0)
    return base64.b64encode(imgbyte.read())


