# -*- coding:utf-8 -*-
import urwid 
import os
import sys
import sqlite3 as db 
from subprocess import Popen, PIPE

base='base.db'
con=db.connect(base)
cur=con.cursor()



def menu_button(caption, callback, data=None):
    button=urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback, data)
    return urwid.AttrMap(button, None, focus_map='reversed')

def sub_menu(caption, choices):#Принимает значения: заголовок и список пунктов меню
    contents = menu(caption, choices)
    def open_menu(button):
        return top.open_box(contents)
    return menu_button([caption, u'...'], open_menu)

def menu(title, choices):
    body=[urwid.Text(title), urwid.Divider()]
    body.extend(choices)
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def item_chosen(button):
    response=urwid.Text([u'Ваш выбор: \n', button.label, u'\n'])
    done=menu_button(u'Ok', exit_program)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))
#section SQL

SQL={}
SQL['row']=[]
SQL['cell']=[]


def query_num(data):
    SQL['cell'].append("UPDATE cells SET num=%d, size=2 WHERE rowindex=%d AND cellpos=%d"%data)

def query_rowindex(position, rownum):
    execute="UPDATE cells SET rowindex=%d WHERE secnum=%d"
    SQL['row'].append(execute % (position,rownum))

def startSQL(button):
    for val in SQL['row']:
        cur.execute(val)
    for val in SQL['cell']:
        cur.execute(val)
    con.commit()
#end section 

#******************************************************************#

#section AKH functions

def youroot():
    p, error = Popen(['whoami'], stdout=PIPE).communicate()
    result = u'(внимание привелегии root)'if p.find('root')!=-1 else u'(Вы не root)'
    return result

def exit_program(button):
    raise urwid.ExitMainLoop()

def reboot(button):
    p=Popen(['sudo', 'reboot'])
    p.communicate()

def timecorr(button,date=None):
    if date:
        timec='%s%s%s%s'%(date.edit_text[2:4],date.edit_text[0:2],date.edit_text[4:6],date.edit_text[6:])

        p=Popen(['sudo', 'date', timec]).communicate()
    else:
        response=urwid.Edit(u'Введите новую дату время: \nВ формате ДДММЧЧмм \n')
        done=menu_button(u'Ok', timecorr, response)
        top.open_box(urwid.Filler(urwid.Pile([response,done])))

def shutdown_P(button):
    p=Popen(['sudo', 'shutdown', '-P', 'now']).communicate()

def update_row(button, data):
    summ, num, secnum = data
    if int(summ.edit_text)>=num:
        if int(summ.edit_text)==num:
            response=urwid.Text([u'Все стойки прописаны'])
        else:
            response=urwid.Edit([u'Стойка ', str(num+1),u' из ', summ.edit_text,u' введите заводской номер' u'\n'])
        if secnum:
            SQL['row'].append("""UPDATE set rowinde=%d WHERE secnum=%d"""%(num, int(secnum.edit_text)))
            count=1
            for i in range(num*3-2,num*3+1):
                SQL['cell'].append("UPDATE cells SET num=%d, size=2 WHERE rowindex=%d AND cellpos=%d"%(i,num,count))
                count+=1
        done=menu_button(u'Ok', update_row, (summ, num+1,response))
        top.this_box(urwid.Filler(urwid.Pile([response, done])))
    else:
        for i in range(top.box_level-2):
            top.original_widget=top.original_widget[0]
            top.box_level-=1

def entery_row(button):
    response = urwid.Edit(u'Введите количество стоеек: \n')
    done=menu_button(u'Ok', update_row, (response,0,None))
    top.open_box(urwid.Filler(urwid.Pile([response,done])))
#end section
class CascadingBoxes(urwid.WidgetPlaceholder): 
    max_box_levels=4

    def __init__(self,box):
        super(CascadingBoxes, self).__init__(urwid.SolidFill(u'\N{MEDIUM SHADE}'))
        self.box_level=0
        self.open_box(box)
        self.palette=[('streak', 'black', 'dark red'),]
        self.text_header=(u'Редактор базы АКХ:')
        blank=urwid.Divider()
        listbox_content=[blank, urwid.Padding(urwid.Text(self.text_header), left=2, right=2,min_width=20)]
        header=urwid.AttrWrap(urwid.Text(self.text_header), 'header')
        listbox=urwid.ListBox(urwid.SimpleFocusListWalker(listbox_content))
        frame=urwid.Frame(urwid.AttrWrap(listbox, 'header'), header=header)

    def open_box(self,box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box), 
            self.original_widget,
            align='center', width=('relative', 80),
            valign='middle', height=('relative',80),
            min_width=24, min_height=8,
            left=self.box_level*3,
            right=(self.max_box_levels-self.box_level-1)*3,
            top=self.box_level*2,
            bottom=(self.max_box_levels-self.box_level-1)*2)
        self.box_level+=1
    def this_box(self,box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='center', width=('relative', 50),
            valign='middle', height=('relative',50),
            min_width=24, min_height=8)
        self.box_level+=1

    def keypress(self, size, key):
        if key == 'esc' and self.box_level>1:
            self.original_widget=self.original_widget[0]
            self.box_level-=1
        else:
            return super(CascadingBoxes, self).keypress(size, key)
menu_top= menu([u'Основное меню ', youroot()],[
    sub_menu(u'Редактирование стоеек',[
        menu_button(u'Прописывание новых стоеек', entery_row),
       # menu_button(u'Редактирование одной стойки', edit_row),
        
            ]),
            sub_menu(u'Работа с сервером', [
                menu_button(u'Перезагрузка сервера', reboot),
                menu_button(u'Выключение сервера', shutdown_P),
                menu_button(u'Установка даты и время', timecorr),
                ]),
            menu_button(u'Выход', exit_program),
            menu_button(u'Применить изменения', startSQL)
        ])
top = CascadingBoxes(menu_top)
urwid.MainLoop(top, palette=[('reversed', 'standout', ''),('header', 'black', 'dark red')]).run()
