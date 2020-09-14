from fastapi import FastAPI, Response, Form, File, UploadFile
from coresubs import *
from database import connect as database_connect
from fastapi.responses import HTMLResponse
import os # для сохранения файла
import shutil

# для multiple-загрузки файлов
from typing import List
# uvicorn main:app --reload
db=database_connect()

app = FastAPI()

#@app.on_event("startup")
#async def startup():
    

@app.get("/")
async def root():
  return {'welcome':'hello!'}

@app.get('/manager')
async def get_managers_list():
  list=db.get(table='manager')
  return {'list':list}

# path_parametrs
@app.get('/manager/{id}')
async def get_manager(id: int):
  manager=db.getrow(table='manager',where='id=%s',values=[id])
  if manager:
    return manager
  else:
    return {'error':'manager not found'}

# query parametrs
@app.get('/learn/query-parametrs')
def learn_read_items(page: int =0, perpage: int =10):
  return {'page':page,'perpage':perpage}

# рендеринг формы
@app.get('/learn/form', response_class=HTMLResponse)
def learn_form_out():
  return template(
    template='./templates/index.html',
    vars={
      'page_type':'form'
    }
  )
# обработка формы
@app.post('/learn/form')
def learn_form_getting(name: str = Form(...), position: str = Form(...), attach: UploadFile = File(...)):
  orig_filename=attach.filename
  name_without_ext,ext=filename_split(orig_filename)
  new_file=gen_pas(20)+'.'+ext
  
  upload_folder='./uploads'
  file_object = attach.file
    
  upload_folder = open(os.path.join(upload_folder, new_file), 'wb+')
  shutil.copyfileobj(file_object, upload_folder)
  upload_folder.close()
  return {"filename": attach.filename}  
  # запись в файл
  # f = open('./uploads/' + new_file , 'w')
  # contents = attach.file.read()
  # f.write(str(contents))
  # print(contents)
  # f.close()

  # return {
  #   'name':name,
  #   'position':position,
  #   'filename':orig_filename, # орининальное имя файла
  #   'name_without_ext':name_without_ext,
  #   'new_file':new_file,
  #   'ext':ext
    #'file':attach.file,
  # }
@app.post('/learm/form-multiple')
def learn_form_getting_multiple(attach: List[UploadFile] = File(...)):
  uploaded=[]
  for file in attach:
    orig_filename=file.filename
    name_without_ext,ext=filename_split(orig_filename)
    new_file=gen_pas(20)+'.'+ext
    
    upload_folder='./uploads'
    file_object = file.file
      
    upload_folder = open(os.path.join(upload_folder, new_file), 'wb+')
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    uploaded.append(new_file)
  return uploaded

@app.get('/response-html', response_class=HTMLResponse)
async def response_html():
  return template(
    template='./templates/index.html',vars={
      'name':'sergey',
      'page_type':'main',
      'list':db.get(table='manager')
    }
  )

@app.get('/set-cookie')
async def create_cookie(response: Response):
  response.set_cookie(key="fakesession", value="fake-cookie-session-value")
  return {'message':'cookie_setted'}