"""封装关于已审批新闻缓存到Redis的类"""

from db.redis_db import pool
import redis


class RedisNewsDao(object):

    def insert_news(self, news_id, uid, title, username, type, content, is_top, create_time):
        """将已审批的新闻缓存到Redis中，置顶级别为了1的，保存只一天"""
        try:
            con = redis.Redis(
                connection_pool=pool
            )
            con.hmset(news_id, {
                'uid': uid,
                'title': title,
                'username': username,
                'type': type,
                'content': content,
                'is_top': is_top,
                'create_time': create_time
            })
            if is_top == 1:
                con.expire(news_id, 24 * 60 * 60)

        except Exception as e:
            print(e)

        finally:
            if con:
                del con

    def delete_cache(self, news_id):
        """删除已缓存的新闻"""
        try:
            con = redis.Redis(
                connection_pool=pool
            )
            con.delete(news_id)

        except Exception as e:
            print(e)
        finally:
            del con
