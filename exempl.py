# -*- coding:utf-8 -*-
import urwid 

choices=u'1)Добавление ячеек,2)Редактирование одной ячейки,3)Перезагрузка сервера'.split(',')

def enter_row(button, data):
    response=urwid.Text([u'Количество ячеек: ', data.edit_text, u'\n'], align='center')
    done = urwid.Button('Ok')
    urwid.connect_signal(done,'click', exit_pr)
    main.original_widget=urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map='reversed')]))

def choice_item(button, choice):
    if choice[0]=='1':
        response = urwid.Edit((u'Введите количество стоек: \n'), align='left')
        done = urwid.Button(u'Ok')
        urwid.connect_signal(done, 'click', enter_row, response)
        main.original_widget=urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map='reversed')]))
    else:
        response=urwid.Text([u'Вы выбрали', choice, u'\n'],align='left')
        done = urwid.Button(u'Закрыть')
        urwid.connect_signal(done, 'click', exit_pr)
        main.original_widget=urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map='reversed')]))
def exit_pr(button):
    raise urwid.ExitMainLoop()

def menu(title, choices):
    body=[urwid.Text(title), urwid.Divider()]
    for c in choices:
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', choice_item, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))
main = urwid.Padding(menu(u'Редактор базы АКХ', choices), left=0, right=0)
top = urwid.Overlay(urwid.LineBox(main), urwid.SolidFill(u'\N{MEDIUM SHADE}'), 
    align='left', width=('relative',40),
    valign='top', height=('relative', 10),
    left=2,top=1,
    min_width=20, min_height=9)
urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()
