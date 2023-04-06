import os
from flask import Flask, render_template, abort, Response, request, redirect, url_for
from mimetypes import add_type, guess_extension, guess_type
from werkzeug.utils import secure_filename


app = Flask(__name__)

import openai
openai.api_key=os.environ.get('OPENAI_API_KEY')
os.environ.get('MY_SECRET')
model_id = 'whisper-1'


@app.route('/submitdalle', methods=['POST'])
def submitdalle():
      req_data = request.get_json()
      prompt = req_data['dallePrompt']
      if not prompt:
         abort(400)
      print("dalle prompt: ", prompt)
      response = openai.Image.create(
         api_key=openai.api_key,
         prompt=prompt,
         n=1,
         size="1024x1024"
         )
      
      image_url = response['data'][0]['url']
      res = Response(image_url, status=200, mimetype='text/plain')
      return res


@app.route('/submitgpt3', methods=['POST'])
def submitgpt3():
      print("submitgpt3 called")
      gpt_id='gpt-3.5-turbo'

      req_data = request.get_json()
      prompt = req_data['gpt3Prompt']


      print("prompt received", prompt)
      if not prompt:
         abort(400)
      print("gpt3 prompt: ", prompt)
      response = openai.Completion.create(
         api_key=openai.api_key,
         model="text-davinci-003",
         prompt=prompt,
         max_tokens=150,
         top_p=1.0,
         temperature=0.9,
         frequency_penalty=0.0,
         presence_penalty=0.0,
         stop=[";"]
      )
      response = response['choices'][0]['text']
      print("gpt3 response: ", response)
      res = Response(response, status=200, mimetype='text/plain')
      return res

add_type('audio/aac', '.m4a', strict=True)
UPLOAD_FOLDER = "uploads"

@app.route('/submitaudio', methods=['POST'])
def submitaudio():
    print("submit audio called")

    if 'file' not in request.files:
        print("no file")
        abort(400)
    
    file = request.files['file']

    print("file.name: ", file.name)
    if file.filename == '':
        abort(400)
    
    if file:
        print("file.mimetype: ", file.mimetype)
        
        #extname = guess_extension(file.mimetype)
        #print("extname: ", extname)

        #print("testing extname")
        #if not extname:
        #    abort(400)
        #if extname == '.weba':
        extname = '.webm'
        i = 1
        print("starting while loop")
        while True:
            dst = os.path.join(
            app.config.get('UPLOAD_FOLDER', 'uploads'),
            secure_filename(f'audio_record_{i}{extname}'))
            if not os.path.exists(dst):
                break
            i += 1
        print("saving file to: ", dst)
        file.save(dst)

        send_file = open(dst, 'rb')
        print("sending file to openAI")
        response = openai.Audio.transcribe(
            api_key=openai.api_key,
            model=model_id,
            file=send_file,
            content_type=file.mimetype,
            response_format='text'
        )
        #make_response(response)
        print("response: ", response)
        res = Response(response, status=200, mimetype='text/plain')
        return res

    return redirect(url_for('index'))



@app.route("/")
def hello_world():
   return render_template("/index.html", title="Hello")
   
