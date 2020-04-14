"""封装mongo客户端对象"""
from pymongo import MongoClient

client = MongoClient(host='localhost', port=27017)
client.admin.authenticate('admin', '123456')
