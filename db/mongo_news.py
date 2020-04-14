"""封装关于将新闻内容存入mongo的类"""
from db.mongo_db import client
from bson.objectid import ObjectId


class MongoNewsDao(object):
    def insert_news(self, uid, title, content):
        """添加新闻正文"""
        try:
            client.vega.news.insert_one({'uid': uid, 'title': title, 'content': content})
        except Exception as e:
            print(e)

    def search_id(self, uid):
        """根据新闻uid查询对应的ID"""
        try:
            news = client.vega.news.find_one({'uid': uid})
            return str(news['_id'])
        except Exception as e:
            print(e)

    def update(self, content_id, title, content):
        """更新新闻正文内容"""
        try:
            client.vega.news.update_one({'_id': ObjectId(content_id)},
                                        {'$set': {'title': title, 'content': content}})
        except Exception as e:
            print(e)

    def search_content(self, content_id):
        """根据正文ID查找正文内容"""
        try:
            news = client.vega.news.find_one({'_id': ObjectId(content_id)})
            return news['content']
        except Exception as e:
            print(e)

    def delete(self, content_id):
        """根据正文ID删除新闻"""
        try:
            client.vega.news.delete_one({'_id': ObjectId(content_id)})
        except Exception as e:
            print(e)
