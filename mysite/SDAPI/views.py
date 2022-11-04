import pwd
from django.shortcuts import render
from curses.ascii import HT

# Create your views here.
from django.http import HttpResponse

"""
test. check if can receive seed etc. by URL.
"""

def test_show(request, seed_val, guidance_scale, height, width, prompt_txt, steps):
    output = f"Seed: {seed_val}, GS: {guidance_scale}, height: {height}, width: {width}, steps: {steps}, prompt: {prompt_txt}"
    return HttpResponse(output)

"""
test. check if can show img on browser
"""
#from django.template import loader
from django.shortcuts import render
def test_imshow(request):
    context = {
        "imgname" : "test.png"
    }
    return render(request, "SDAPI/index.html", context)

"""
use stable-sdk. reference: https://github.com/Stability-AI/stability-sdk/blob/main/nbs/demo_colab.ipynb
need to be installed stability_sdk
"""

import getpass, os
import io
import warnings
from IPython.display import display
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

#画像を保存
import sys
sys.path.append("../")
from mysite import settings
#画像をhtmlに反映
#リダイレクト←やめた
#render して HeepRequest で返すことにした

#Imgur API に送信
import requests
import json



def SDAPI_request(request, seed_val, guidance_scale, height, width, steps, prompt_txt):
    os.environ["STABILITY_HOST"] = 'grpc.stability.ai:443'
    os.environ["STABILITY_KEY"] = "sk-grnCOk3zjrmcyHnk7dggwLMz8SWHZbexCzb1KcFLekfTFoLq"

    #Imgur APIを使うとき、レスポンスをなぜか json にできないので
    #response の text 属性を辞書として扱うことにする
    #その時 true, false, null という文字がクオーテーションされておらず
    #エラーになるので、ここでデータ型にしておく
    true = True
    false = False
    null = None

    #Imgur API で使う
    client_id = "3f34176738ba79b"

    stability_api = client.StabilityInference(
        key=os.environ["STABILITY_KEY"],
        verbose=True,
    )
    # the object returned is a python generator
    answers = stability_api.generate(
        prompt=prompt_txt,
        seed=seed_val, # if provided, specifying a random seed makes results deterministic
        steps=steps, # defaults to 50 if not specified
        height = height,
        width = width,
        cfg_scale = guidance_scale,
        guidance_strength = 0.25,
        #samples = 1
    )

    # iterating over the generator produces the api response
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                #画像を保存
                if len(prompt_txt) > 252:
                    imgname = prompt_txt[:251] + ".png"
                else:
                    imgname = f"{prompt_txt}.png"
                
                img.save(str(settings.MEDIA_ROOT) + "/" + imgname)
                #画像を保存したディレクトリを参照してHTMLに反映
                ##反映したものを redirect で返す←やめた、render 使う
                #render して HttpResponse を試す

                #Stable Diffusionの結果の画像を直接requestに載せることができなかったので
                #一回保存してopenで読んでImgur APIに渡すことにする
                #渡したらディレクトリ上の画像は削除する

                image = open(str(settings.MEDIA_ROOT) + "/" + imgname, "rb")
                os.remove(str(settings.MEDIA_ROOT) + "/" + imgname)

                headers = {
                    "authorization": f"Client-ID {client_id}",
                }
                files = {
                    "image": (image),
                }
                response = requests.post('https://api.imgur.com/3/upload', headers=headers, files=files)

                context = {
                    "imgname" : imgname,
                    "link" : eval(response.text.replace("\n","").replace("true","True").replace("false","False"))["data"]["link"]
                    }
                return render(request, "SDAPI/index.html", context)
                #↑の辞書の link の値がImgurのURLになってるので、
                #それをテキストとかでHttpResponseとして return すれば良い