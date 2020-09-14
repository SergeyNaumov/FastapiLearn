import pprint as pp
import datetime
import json
import random

def pre(stuff):
  pp.pprint(stuff)


def cur_date(delta=0):
  dat = datetime.date.today()
  dat = dat + datetime.timedelta(days=delta)
  return dat.strftime("%Y-%m-%d")

def cur_year(delta=0):
  dat = datetime.date.today()
  year = int(dat.strftime("%Y"))
  if delta != 0 :
    year += delta
  return year


# для удобной работы с шаблонами
from jinja2 import Environment, FileSystemLoader

def split_full_path(full_path):

  list = full_path.split('/')
  template=list.pop()

  dir='/'.join(list)
  #print({'dir':dir,'template':template})
  return dir,template

def template(**arg):
  dir,template=split_full_path(arg['template'])
  env = Environment(loader=FileSystemLoader(dir))
  tmpl = env.get_template(template)
  output=tmpl.render(**arg['vars'])
  if ('print' in arg) and arg['print'] :
    print(output)
  else:
    return output

def to_json(data):
    return json.dumps(data, sort_keys=False,indent=4,ensure_ascii=False,separators=(',', ': '))

def filename_split(filename):
  list=filename.split('.')
  ext=list.pop()
  name_without_ext='.'.join(list)
  return name_without_ext,ext

def gen_pas(length=8):
  letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
  return ''.join(random.choice(letters) for i in range(length))
  
