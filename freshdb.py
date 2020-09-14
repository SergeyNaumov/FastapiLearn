import pymysql
import json

def exists_arg(key,dict):
  if (key in dict) and dict[key]:
    return True
  return False

def out_error(self,error,arg):
  self.err_str=error
  if 'error' in arg:
    if(type(arg['error']) == type([])): # type is list
        arg['error'].append(error)
    else: # type is str
        arg['error']=error
  else:
    print(error)
    print("\nQUERY:\n"+arg['query'])
    if ('values' in arg) and len(arg['values']):
      print(arg['values'])
    quit()


def get_query(self,arg): # для get и getrow
  self.error_str=''
  sf=''
  if not exists_arg('select_fields',arg):
    sf='*'
  else:
    sf=arg['select_fields']

  if not exists_arg('table',arg):
    out_error(self,"FreshDB::"+arg['method']+" not set attr table",arg)
    return ''
    
  
  query='select '+sf+' FROM '+arg['table']+' wt'
  
  # join-ы
  if 'tables' in arg:
    for table in arg['tables']:
      if ('lj' in table ) and (table['lj']) :
        query += ' LEFT '

      query += ' JOIN '
      query += table['t']

      if ('l' in table) and (table['l']):
        query += ' ON '+ table['l']

  if exists_arg('where',arg):
    query += ' WHERE '+arg['where']
  if exists_arg('order',arg):
    query += ' ORDER BY '+arg['order']
  
  if arg['method'] == 'getrow':
    arg['limit'] = 1
 
  if exists_arg('perpage',arg) and exists_arg('table',arg):
    arg['perpage']=int(arg['perpage'])
    if not(exists_arg('page',arg)):
      arg['page']=1

    query_count='SELECT CEILING(count(*) / ' + str(arg['perpage'])+') FROM '+arg['table'];

    if exists_arg('where',arg): query_count +=' WHERE '+arg['where']
    
    if exists_arg('group',arg): query_count +=' GROUP BY ' + arg['group']
    
    if not exists_arg('values',arg): arg['values']=[]

    arg['maxpage']=self.query(query=query_count,onevalue=1,values=arg['values'])

    limit1=(arg['page']-1) * arg['perpage'];
    arg['limit']=str(limit1)+','+str(arg['perpage']);


  if exists_arg('limit',arg):
    query += ' LIMIT ' + str(arg['limit'])
  return query

def to_json(data):
    return json.dumps(data, ensure_ascii=False) # ,separators=(',', ': ') sort_keys=False,indent=0,


class FreshDB():
    def go_connect(self,arg):
      self.connect = pymysql.connect(arg['host'], arg['user'], arg['password'], arg['dbname'])
      self.connect.ping(reconnect=True)

    def __init__(self, **arg):
      self.error_str=''
      self.tmpl_saver = None;
      self.error_str=''
      if not exists_arg('host',arg):
        arg['host']='localhost'

      if not exists_arg('password',arg):
        arg['password']=''

      if exists_arg('tmpl_saver',arg):
        self.tmpl_saver=arg['tmpl_saver']
      
      self.go_connect(arg)
      # , cursorclass=pymysql.cursors.DictCursor

    def execute(self,cur,arg):
      
      try:
        if ('debug' in arg) and (arg['debug']):
          print(arg['query'])
          print(arg['values'])
        if not exists_arg('values',arg):
          arg['values']=[]
        cur.execute(arg['query'],arg['values'])
        self.connect.commit()
      except pymysql.err.ProgrammingError as e:
          out_error(self,str(e),arg)
          self.error_str = e

      except pymysql.err.IntegrityError as e2:
          out_error(self,str(e2),arg)
          self.error_str=e2

      except pymysql.err.InternalError as e3:
          out_error(self,str(e3),arg)
          self.error_str=e3


    def desc(self, **arg):
      cur = pymysql.cursors.DictCursor(self.connect)
      
      if not('method' in arg) :
        self.error_str=''
        arg['method']='desc'
      
      if not exists_arg('table',arg):
        out_error(self,"FreshDB::"+arg['method']+" not set attr table",arg)
        return 

      arg['query']='desc '+arg['table']


      self.execute(cur, arg)
      if self.error_str: return {}
      
      fields=cur.fetchall()
      result={}
      for f in fields:
        result[ f['Field'] ]=f

      return result

    def getvalue(self, **arg):
      cur = self.connect.cursor()
      #print('arg:',arg)
      arg['method']='getvalue'
      arg['query']=get_query(self,arg)
      #print(arg)
      
      if self.error_str:
        return None
      self.execute(cur,arg)
      
      rez=cur.fetchone()
      
      if not rez: return rez

      return rez[0]

    def getrow(self, **arg):
      self.error_str=''
      cur = pymysql.cursors.DictCursor(self.connect)
      arg['method']='getrow'
      arg['query']=get_query(self,arg)

      if self.error_str:
        return {}

      self.execute(cur,arg)
      if self.error_str: return {}

      rez=cur.fetchone()
      
      if exists_arg('to_json',arg):
        return to_json(rez)
      #if not(rez):
      #  rez=False

      return rez 
    def prepare_result(self,rez,arg): # подготавливает и возвращает результат
      
      if exists_arg('to_json',arg):
        rez=to_json(rez)

      if exists_arg('to_tmpl',arg):
          if self.tmpl_saver :
            self.tmpl_saver(name=arg['to_tmpl'],value=rez)
            if exists_arg('perpage',arg) & exists_arg('maxpage',arg):
              return int(arg['maxpage'])
            else:
              return True

      if exists_arg('perpage',arg) & exists_arg('maxpage',arg):

        return int(arg['maxpage']),rez

      return rez
    def get(self, **arg):
      self.error_str=''
      cur = pymysql.cursors.DictCursor(self.connect)
      arg['method']='get'
      arg['query']=get_query(self,arg)

      if self.error_str:
        return []

      self.execute(cur,arg)

      if self.error_str:
        rez=[]
      else:
        rez=cur.fetchall()
      return self.prepare_result(rez,arg)

      

    def query(self, **arg):
      self.error_str=''
      if exists_arg('onevalue',arg):
        cur = self.connect.cursor()
      else:
        cur = pymysql.cursors.DictCursor(self.connect)
      
      arg['method']='query'
      if not exists_arg('query',arg):
        out_error(self,'FreshDB::query: not exists attribute query',arg)

      if self.error_str : return []
      
      self.execute(cur,arg)

      if exists_arg('onevalue',arg):
        rez = cur.fetchone()
        if rez: rez=rez[0]
      else: rez=cur.fetchall()
      
      if exists_arg('to_json',arg): rez=to_json(rez)

      #if exists_arg('to_tmpl',arg):
      #  self.tmpl_vars[arg['to_tmpl']]=rez

      #if exists_arg('perpage',arg) & exists_arg('maxpage',arg):return arg['maxpage']
      return rez

      #print("query:")
      #print({'arg':arg})

    def save(self, **arg):
        self.error_str=''
        arg['method']='save'
        if not exists_arg('table',arg):
          out_error(self,"FreshDB::"+arg['method']+" not set attr table",arg)
          return 
        
        if not exists_arg('data',arg):
          out_error(self,"FreshDB::"+arg['method']+" not set attr data",arg)
          return 

        
        exists_fields=self.desc(table=arg['table'])
        data=arg['data']
        

        insert_fields=[]
        insert_vopr=[]
        insert_values=[]

        update_names=[]
        for name in data.keys():
          if name in exists_fields:
            insert_fields.append(name)
            insert_vopr.append('%s')
            insert_values.append(data[name])
            update_names.append(name+'=%s')

        
        if exists_arg('update',arg):
              if not exists_arg('where',arg):
                out_error(self,"FreshDB::"+arg['method']+" not set attr where",arg)
                return False
              
              arg['query']='UPDATE '+arg['table']+' SET '+','.join(update_names) + ' WHERE '+arg['where']
        else:
              q=''
              if exists_arg('replace',arg):
                q='REPLACE'
              else:
                q='INSERT'
              q +=' INTO '+arg['table'] +'(' + ','.join(insert_fields)+') VALUES (' + ','.join(insert_vopr) + ')'
              arg['query']=q

        arg['values']=insert_values

        cur = pymysql.cursors.DictCursor(self.connect)
        self.execute(cur,arg)