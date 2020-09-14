from freshdb import FreshDB

def connect():
  return FreshDB(dbname='crm',user='crm')