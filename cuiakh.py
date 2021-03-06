# -*- coding:utf-8 -*-
import urwid 
import re
import os
import os.path
import sys
import sqlite3 as db 
from subprocess import Popen, PIPE


base=None
con=None
cur=None


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
def setAdmincard(button, data=None):
    global base
    if base==None:
        chbase(None)
        return None
    if data==None:
        usercard=urwid.Edit(u'Введите номер карты: \n')
        text=urwid.Text(u'Введите номер пользователя от 9 до 12,\nесли введете больше или меньше \nбудете посланы на хуй:')
        userid=urwid.Edit(u'')
        done=menu_button(u'Ok', setAdmincard,(usercard, userid))
        top.open_box(urwid.Filler(urwid.Pile([usercard, text, userid,done])))
    else:
        usercard, userid =data
        if int(userid.edit_text) not in [9,10,11,12]:
            clear_level(2)
            response=urwid.Text(u'Ну не мудак ли? \nОт 9 до 12\n')
            done=menu_button(u'Ok', setAdmincard, None)
            top.this_box(urwid.Filler(urwid.Pile([response,done])))
        else:
            execute="UPDATE users SET usercard=%s WHERE userid=%d"

            
            cur.execute(execute%(str(usercard.edit_text),int(userid.edit_text)))
            con.commit()
            clear_level(2)

#section SQL

SQL={}
SQL['row']=[]
SQL['cell']=[]


def query_num(data):
    SQL['cell'].append("UPDATE cells SET num=%d, size=%d WHERE rowindex=%d AND cellpos=%d"%data)

def query_rowindex(position, rownum):
    execute="UPDATE cells SET rowindex=%d WHERE secnum=%d"
    SQL['row'].append(execute % (position,rownum))

def startSQL(button):
    global base
    if base==None:
        chbase(None)
    else:
        for val in SQL['row']:
            cur.execute(val)
        for val in SQL['cell']:
            cur.execute(val)
        con.commit()
        clear_level(2)
#end section 

#******************************************************************#

#section AKH functions
def logVIM(button):
    global base
    if base==None:
        chbase(None)
    else:
        p=Popen(['vim','avkars.log'])
    #p.communicate()
        p.wait()

def youroot():
    p, error = Popen(['whoami'], stdout=PIPE).communicate()
    result = u'(внимание привелегии root)'if p.find('root')!=-1 else u'(Вы не root)'
    return result

def exit_program(button):
    raise urwid.ExitMainLoop()

def reboot(button):
    p=Popen(['sudo', 'reboot'])
    p.communicate()

def chbase(button, pat=None):
    buton=[menu_button(u'...', chbase,u'...')]
    def show_dir(direct):
        buton=[]
        for val in direct:
            m=re.match('^\.[0-9a-zA-Z\-\_]*', val)
            if os.path.isdir(val) and m==None or val=='base.db':
                buton.append(menu_button(val, chbase, os.path.abspath(val)))
        return buton
    if pat==None:
        direct=os.listdir(os.curdir)
        pat=os.path.abspath(os.curdir)
        buton=buton+show_dir(direct)
        buton.append(urwid.Text(pat))
        top.this_box(urwid.Filler(urwid.Pile(buton)))
    elif pat==u'...':
        absp=os.path.abspath(os.curdir).split('/')
        absp='/'.join(absp[:-1])
        absp='/' if absp==''else absp
        os.chdir(absp)
        direct=os.listdir(absp)

        buton=buton+show_dir(direct)
    
        buton.append(urwid.Text(absp))
        top.this_box(urwid.Filler(urwid.Pile(buton)))
    elif pat.find('base.db')!=-1:
        global base
        base=pat
        global con
        con=db.connect(base)
        global cur
        cur=con.cursor()
        while top.box_level>1:
            top.original_widget=top.original_widget[0]
            top.box_level-=1
    else:
        os.chdir(pat)
        direct=os.listdir(pat)
        buton=buton+show_dir(direct)
        buton.append(urwid.Text(pat))
        top.this_box(urwid.Filler(urwid.Pile(buton)))


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
            query_rowindex(num, int(secnum.edit_text))
            count=1
            for i in range(num*3-2,num*3+1):
                query_num((i,2,num,count))
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


def redo_row(button,data=None):
    if data==None:
        row=urwid.Edit(u'Введите порядковый номер стойки:\n')
        rang=urwid.Edit(u'Введите заводской номер контроллера:\n')
        done=menu_button(u"Ok",redo_row,(row, rang) )
        top.open_box(urwid.Filler(urwid.Pile([row,rang, done])))
    else:
        row, rang=data
        query_rowindex(int(row.edit_text),int(rang.edit_text))
        done=menu_button(u'Записать', startSQL)
        top.this_box(urwid.Filler(urwid.Pile([done])))
def edit_cell(button,data=None,Type=None):
    if data==None:
        bgroup=[]
        b1=urwid.RadioButton(bgroup, u'4 ячейки',False)
        urwid.connect_signal(b1, 'change', edit_cell,(1))
        b2=urwid.RadioButton(bgroup, u'3 ячейки',False)
        urwid.connect_signal(b2, 'change', edit_cell,2)
        b3=urwid.RadioButton(bgroup, u'2 ячейки',False)
        urwid.connect_signal(b3, 'change', edit_cell,3)
        b4=urwid.RadioButton(bgroup, u'1 ячейка',False)
        urwid.connect_signal(b4, 'change', edit_cell,4)
        top.this_box(urwid.Filler(urwid.Pile([b1,b2,b3,b4])))
    else:
        if Type!=None:
            cell=Type
            response=urwid.Edit([u'Введите диапозон стоек,\nв качестве разделителя используйте "-"\n'])
            startcell=urwid.Edit([u'Введите номер начальной ячейки: \n'])
            done=menu_button(u'Ok',eddcel,(response,cell,startcell))
            top.this_box(urwid.Filler(urwid.Pile([response,startcell,done])))

def eddcel(button,data):
    rang, cell, startcell = data
    startcell=int(startcell.edit_text)
    rang=rang.edit_text.split('-')
    start=int(rang[0])
    num=[0,4,3,2,1]
    summ=1
    if len(rang)>1:
        summ=(int(rang[1])-int(rang[0]))
    for val in range(summ+1):
        count=1
        for i in range(1,5):
            query_num((99999,2,start,i))
        for number in range(startcell,startcell+num[cell]):
            query_num((number,cell,start,count))
            count+=1
        startcell+=num[cell]
        start+=1
    done=menu_button(['Ok'], startSQL)
    top.this_box(urwid.Filler(urwid.Pile([done])))

def clear_level(data):
    for i in range(top.box_level-data):
        top.original_widget=top.original_widget[0]
        top.box_level-=1
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
    menu_button(u'Выбор файла базы', chbase),
    sub_menu(u'Редактирование стоеек',[
        menu_button(u'Прописывание новых стоеек', entery_row),
        menu_button(u'Редактирование одной стойки', redo_row),
        menu_button(u'Редактирование ячеек', edit_cell),
        menu_button(u'Прописывание административных карт', setAdmincard),
            ]),
            sub_menu(u'Работа с сервером', [
                menu_button(u'Перезагрузка сервера', reboot),
                menu_button(u'Выключение сервера', shutdown_P),
                menu_button(u'Установка даты и время', timecorr),
                ]),
            menu_button(u'Просмотреть лог файл (VIM)',logVIM),
            menu_button(u'Выход', exit_program),
            menu_button(u'Применить изменения', startSQL)
        ])
top = CascadingBoxes(menu_top)
urwid.MainLoop(top, palette=[('reversed', 'standout', ''),('header', 'black', 'dark red')]).run()
