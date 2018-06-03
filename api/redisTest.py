# -*- coding:utf-8 -*-
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.set('ximenyaoxue', {"2bb07b_12e674b2": ["#道剑#通冥记·吉羽（七）", "1527187945844", "\uFF08\u4E94\uFF09 \u5510\u5C3A\u548C\u90ED\u94C1\u7B49\u4EBA\u7D27\u5F20\u5730\u5E03\u7F6E\u4E86"]})
print(r.get('ximenyaoxue'))
r.append('ximenyaoxue', {"2bb07b_12e674b2": ["#道剑#通冥记·吉羽（八）", "1527187945844", "\uFF08\u4E94\uFF09 \u5510\u5C3A\u548C\u90ED\u94C1\u7B49\u4EBA\u7D27\u5F20\u5730\u5E03\u7F6E\u4E86"]})
print(r.get('ximenyaoxue'))
print({"2bb07b_12e674b2": ["#道剑#通冥记·吉羽（八）", "1527187945844", "\uFF08\u4E94\uFF09 \u5510\u5C3A\u548C\u90ED\u94C1\u7B49\u4EBA\u7D27\u5F20\u5730\u5E03\u7F6E\u4E86"]})
