#                       Copyright 2020 Saad Mairaj
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import sys
import random
if sys.version_info.major == 2:
    import ttk
    import Tkinter as tk
    import tkFont as font
    from tkColorChooser import askcolor
elif sys.version_info.major == 3:
    from tkinter import ttk
    import tkinter as tk
    import tkinter.font as font
    from tkinter.colorchooser import askcolor

from tkmacosx.widget import *
from tkmacosx.variables import *
from tkmacosx.colorscale import Colorscale
from tkmacosx.colors import Hex as C_dict, all_colors


color_list = [list(i.values())[0].get('hex') for i in all_colors]


def grid(root, row, column):
    "Defines rows and columns if grid method is used"
    if column:
        for y in range(column):
            tk.Grid.columnconfigure(root, y, weight=1)
    if row:
        for x in range(row):
            tk.Grid.rowconfigure(root, x, weight=1)
    return


def sort_random_values(fn):
    def wrapper(*args, **kwargs):
        value = fn(*args, **kwargs)
        if isinstance(value, (list, tuple)) and len(value) == 1:
            return value[0]
        return value
    return wrapper


def choices(seq, k):
    "Random choices."
    return tuple(random.choice(seq) for i in range(k))


@sort_random_values
def get_random_colors(k=1):
    return choices(color_list, k=k)


@sort_random_values
def get_random_font(k=1):
    def family(): return random.choice(font.families())

    def weight(): return random.choice(('bold', 'normal'))

    def slant(): return random.choice(('italic', 'roman'))

    def size(): return random.randrange(9, 30)

    def underline(): return random.choice((True, False))

    overstrike = underline
    return tuple(font.Font(family=family(), weight=weight(),
                           slant=slant(), underline=underline(),
                           overstrike=overstrike(), size=30,) for i in range(k))


@sort_random_values
def get_random_size(k=1, start=10, end=200):
    return tuple(choices([i for i in range(start, end)], k=k))


@sort_random_values
def get_random_relief(k=1):
    return choices(('flat', 'groove', 'raised',
                    'ridge', 'solid', 'sunken'), k=k)


class Sample(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.resizable(0, 0)
        self.geometry('420x700+300+100')
        self.title('Mac OSX Button Testing')
        self.wm_attributes('-modified', 1)
        self.main_color = ColorVar(value='#ffe6f4')
        self['bg'] = self.main_color
        grid(self, 25, 5)
        self.L1 = tk.Label(self, text='Comparison',
                           bg=self.main_color, font=('', 18, 'bold'))
        self.L1.grid(row=0, column=0, columnspan=5, sticky='nsew')
        Button(self, text='Hello').grid(row=1, column=1, sticky='s')
        ttk.Button(self, text='Hello').grid(row=1, column=3, sticky='s')
        tk.Button(self, text='Hello').grid(row=1, column=2, sticky='s')
        tk.Label(self, bg=self.main_color, font=('', 10),
                 text='(Mac OSX)').grid(row=2, column=1, sticky='n',)
        tk.Label(self, bg=self.main_color, font=('', 10),
                 text='(ttk themed)').grid(row=2, column=3, sticky='n')
        tk.Label(self, bg=self.main_color, font=('', 10),
                 text='(Default)').grid(row=2, column=2, sticky='n')
        ttk.Separator(self, orient='vertical').grid(
            row=3, column=0, columnspan=5, sticky='ew')

        # ------------ Seperator -------------

        # ------------ Demonstration ------------

        self.sfr = SFrame(self, bg=self.main_color)
        self.sfr.grid(rowspan=27, columnspan=5, sticky='nsew')
        for i in range(5):
            self.sfr.grid_columnconfigure(i, weight=1)
        self.L2 = tk.Label(self.sfr, text='Demonstration',
                           bg=self.main_color, font=('', 20, 'bold'))
        self.L2.grid(row=1, column=0, columnspan=5,
                     sticky='new', pady=(20, 10))

        # ------------ Active Color ------------

        self.L3 = tk.Label(self.sfr, text='1. Change Active color', bg=self.main_color,
                           font=('', 15, 'bold'))
        self.L3.grid(row=2, column=0, columnspan=5, sticky='nsew', pady=10)
        self.L4 = tk.Label(self.sfr, text='The active color can be changed to any gradient color.',
                           bg=self.main_color, font=('', 10))
        self.L4.grid(row=3, column=0, columnspan=5, sticky='new')
        self.B1 = Button(self.sfr, text='Press Me', pady=20)
        self.B1.grid(row=4, column=0, columnspan=5, pady=20)
        self.C1 = tk.StringVar(value='Select')
        self.L5 = tk.Label(self.sfr, text='From',
                           bg=self.main_color, font=('', 12))
        self.L5.grid(row=5, column=1, sticky='nwe')
        self.Om1 = tk.OptionMenu(self.sfr, self.C1, *C_dict.keys(),
                                 command=self.change_active_color)
        self.Om1.config(bg=self.main_color, width=15)
        self.Om1.grid(row=6, column=1, sticky='s', pady=(0, 10))
        for i in range(self.Om1['menu'].index('end')+1):
            self.Om1['menu'].entryconfig(i, foreground=list(C_dict)[i])
        self.C2 = tk.StringVar(value='Select')
        self.L6 = tk.Label(self.sfr, text='To',
                           bg=self.main_color, font=('', 12))
        self.L6.grid(row=5, column=3, sticky='nwe')
        self.Om2 = tk.OptionMenu(self.sfr, self.C2, *C_dict.keys(),
                                 command=self.change_active_color)
        self.Om2.config(bg=self.main_color, width=15)
        self.Om2.grid(row=6, column=3, sticky='s', pady=(0, 10))
        for i in range(self.Om2['menu'].index('end')+1):
            self.Om2['menu'].entryconfig(i, foreground=list(C_dict)[i])

        # ------------ Background Color ------------

        # ttk.Separator(self.sfr, orient='vertical').grid(row=6, column=2, columnspan=1, sticky='ew')
        self.L7 = tk.Label(self.sfr, text='2. Change Background color', bg=self.main_color,
                           font=('', 15, 'bold'))
        self.L7.grid(row=7, column=0, columnspan=5,
                     sticky='nsew', pady=(50, 0))
        self.L8 = tk.Label(self.sfr, text='Click on the button to choose the color.',
                           bg=self.main_color, font=('', 10))
        self.L8.grid(row=8, column=0, columnspan=5, sticky='new', pady=10)

        self.B2 = Button(self.sfr, text='Color me',
                         font=('', 30,), pady=10, padx=10)
        self.B2.grid(row=9, column=0, columnspan=5, sticky='', pady=20)

        self.B3 = Button(self.sfr, text='Change Background Color',
                         bg='#d0c0ea', borderless=1)
        self.B3['command'] = lambda: self.B2.config(bg=askcolor()[1])
        self.B3.grid(row=10, column=0, columnspan=5, sticky='w', pady=10, padx=10)
        self.B4 = Button(self.sfr, text='Change Foreground Color',
                         bg="#d0c0ea", borderless=1)
        self.B4['command'] = lambda: self.B2.config(fg=askcolor()[1])
        self.B4.grid(row=10, column=0, columnspan=5, sticky='e', pady=10, padx=10)

        # ------------ Borderless ------------

        self.L9 = tk.Label(self.sfr, text='3. Switch Between Borderless', bg=self.main_color,
                           font=('', 15, 'bold'))
        self.L9.grid(row=11, column=0, columnspan=5,
                     sticky='sew', pady=(50, 0))
        self.L10 = tk.Label(self.sfr, text="""
    In borderless it will blend with its parent widget background color.
    Give parameter `borderless = True / False` to use it.""", bg=self.main_color, font=('', 10))
        self.L10.grid(row=12, column=0, columnspan=5, sticky='new')

        self.B5 = Button(self.sfr, text='No Borders', borderless=1, height=40,
                         bg='#212F3D', fg='white', activebackground=("#EAECEE", "#212F3D"))
        self.B5.grid(row=13, columnspan=5, pady=(20, 5))

        self.B6 = Button(self.sfr, text='No Borders', borderless=1, height=40,
                         bg='#F7DC6F', fg='#21618C', activebackground=('#B3B6B7', '#58D68D'))
        self.B6.grid(row=14, columnspan=5, pady=(0, 20))
        self.var1 = tk.BooleanVar(value=True)
        self.CB1 = tk.Checkbutton(self.sfr, text='Toggle Borderless', variable=self.var1,
                                  bg=self.main_color, command=self.change_borderless_state)
        self.CB1.grid(row=15, columnspan=5, pady=(0, 10))

        # ------------ Bordercolor ------------

        self.L11 = tk.Label(self.sfr, text='4. Change Bordercolor', bg=self.main_color,
                            font=('', 15, 'bold'))
        self.L11.grid(row=16, column=0, columnspan=5,
                      sticky='sew', pady=(50, 0))
        self.L12 = tk.Label(self.sfr, text="Change Bordercolor of the button\nNote: if borderless=True, then the bordercolor won't work.",
                            bg=self.main_color, font=('', 10))
        self.L12.grid(row=17, column=0, columnspan=5, sticky='new')

        self.B7 = Button(self.sfr, text='Button', pady=10,
                         padx=5, font=('Zapfino', 12, 'bold'))
        self.B7.grid(row=18, columnspan=5, pady=30)

        self.CS1 = Colorscale(self.sfr, value='hex', mousewheel=1,
                              command=lambda e: self.B7.config(bordercolor=e))
        self.CS1.grid(row=19, columnspan=5, sticky='ew', padx=10)

        self.CS2 = Colorscale(self.sfr, value='hex', mousewheel=1,
                              gradient=('#FCF6F5', '#990011'),
                              command=lambda e: self.B7.config(bg=e))
        self.CS2.grid(row=20, columnspan=5, sticky='ew', padx=10, pady=5)

        self.CS3 = Colorscale(self.sfr, value='hex', mousewheel=1,
                              gradient=('green', 'yellow'),
                              command=lambda e: self.B7.config(fg=e))
        self.CS3.grid(row=21, columnspan=5, sticky='ew', padx=10)

        self.CS4 = Colorscale(self.sfr, value='hex', mousewheel=1,
                              gradient=('pink', 'purple'),
                              command=lambda e: self.B7.config(overforeground=e))
        self.CS4.grid(row=22, columnspan=5, sticky='ew', padx=10, pady=5)

        # ------------ Random button styling ------------
        self.L11 = tk.Label(self.sfr, text='5. Button Styling', bg=self.main_color,
                            font=('', 15, 'bold'))
        self.L11.grid(row=23, column=0, columnspan=5,
                      sticky='sew', pady=(50, 0))
        self.L12 = tk.Label(self.sfr, text="Press the button to ramdomise the style of the button.",
                            bg=self.main_color, font=('', 10))
        self.L12.grid(row=24, column=0, columnspan=5, sticky='new')

        self.B10 = Button(self.sfr, text='Button', borderless=1)
        self.B10.grid(row=25, columnspan=5, pady=20)

        self.B11 =  Button(self.sfr, text='Change Style', borderless=1, fg='#21618C', 
                           activebackground=('#B3B6B7', '#58D68D'), command=self.change_button_style)
        self.B11.grid(row=26, columnspan=5, ipady=5)

        self.button_clicks = 1
        self.Text1 = tk.Text(self.sfr, background=self.main_color, highlightthickness=0, 
                             relief='sunken', height=20, bd=2, padx=10)
        self.Text1.grid(row=27, columnspan=5, pady=20, padx=20)
        self.sfr._avoid_mousewheel((self.Text1, self.CS1, self.CS2, self.CS3, self.CS4))
        self.change_button_style()
        self.update_idletasks()

    def change_active_color(self, *ags):
        c1 = self.C1.get() if not self.C1.get() == 'Select' else None
        c2 = self.C2.get() if not self.C2.get() == 'Select' else None
        self.Om1.config(bg=c1)
        self.Om2.config(bg=c2)
        self.B1['activebackground'] = (c1, c2)

    def change_borderless_state(self):
        if self.var1.get():
            self.B5['borderless'] = 1
            self.B6['borderless'] = 1
        else:
            self.B5['borderless'] = 0
            self.B6['borderless'] = 0

    def change_button_style(self):
        cnf = dict(
            foreground=get_random_colors(),
            background=get_random_colors(),
            activebackground=get_random_colors(2),
            activeforeground=get_random_colors(),
            overrelief=get_random_relief(),
            relief=get_random_relief(),
            highlightthickness=get_random_size(1, 1, 5),
            borderwidth=get_random_size(1, 1, 5),
            font=get_random_font(),
            highlightbackground=get_random_colors(),
            focuscolor=get_random_colors(),
            overbackground=get_random_colors(),
            overforeground=get_random_colors(),
        )
        self.B10.config(**cnf)

        self.Text1.insert('end', '\n\nBUTTON STYLE %s\n\n'%self.button_clicks)
        for k,v in cnf.items():
            if k == 'font':
                self.Text1.insert('end', 'font:\n')
                for i, j in v.config().items():
                    self.Text1.insert('end', '\t%s\t\t= %s\n' %(i,j))
            else:
                self.Text1.insert('end', '%s\t\t\t= %s\n' %(k,v))
        self.Text1.see('end')
        self.Text1.insert('end', '\n\n'+'-'*40)
        self.button_clicks += 1
        self.sfr['canvas'].yview_moveto('1.0')
        self.update_idletasks()


def main():
    "Demonstration of tkmacosx."
    Sample().mainloop()


#  Testing Demo
if __name__ == "__main__":
    main()
