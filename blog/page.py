# !-*-coding=utf8-*-
'''
Created on 2015-1-25

@author: Administrator
'''
from django.conf import settings
from math import ceil
from django.core.paginator import Page

class MyPaginator(object):
    
    def __init__(self, objects, page_number):
        self.objects = objects
        self.per_page = int(settings.DEFAULT_PAGE_SIZE)
        self.num_pages = self.__get_num_pages()
        self.page_number = self.validate_number(page_number)
        self.page_range = self.__get_page_range()
        self.mini_page_range = self.__get_mini_page_range()
        
    def __get_num_pages(self):
        return int(ceil(self.objects.count() / float(self.per_page)))
    
    def validate_number(self, number):
        try:
            number = int(number)
        except (TypeError, ValueError):
            number = 1
        return max(min(int(number), self.num_pages), 1)
    
    def __get_page_range(self):
        return range(1, self.num_pages + 1)
    
    def __get_mini_page_range(self):
        page_range = self.page_range
        if self.num_pages > 5:
            # 开始页索引
            start = (self.page_number - 2) if (self.page_number - 2 > 1) else 1
            # 结束页索引
            end = start + 4
            # 如果结束页索引超出了页面总数，重新计算开始页索引
            if end > self.num_pages:
                start -= (end - self.num_pages)
            page_range = range(start, start + 5)
        return page_range

    def page(self):
        bottom = (self.page_number - 1) * self.per_page
        top = bottom + self.per_page
        return Page(self.objects.all()[bottom:top], self.page_number, self)