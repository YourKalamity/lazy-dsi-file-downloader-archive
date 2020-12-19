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
if sys.version_info.major == 2:
    import Tkinter as _TK
elif sys.version_info.major == 3:
    import tkinter as _TK
import tkmacosx.basewidget as tkb


class SFrame(tkb.SFrameBase):
    """### Scrollable Frame ButtonBase.    
    (Only supports vertical scrolling)

    Sames as tkinter Frame. These are some extra resources.
    - `scrollbarwidth`: Set the width of scrollbar.
    - `mousewheel`: Set mousewheel scrolling.
    - `avoidmousewheel`: Give widgets that also have mousewheel scrolling and is a child of SFrame \
        this will configure widgets to support their mousewheel scrolling as well. \
        For eg:- Text widget inside SFrame can have mousewheel scrolling as well as SFrame.

    Scrollbar of SFrame can be configured by calling `scrollbar_configure(**options)`. 
    To access methods of the scrollbar it can be called through the scrollbar instance `self['scrollbar']`.

    ### How to use?
    Use it like a normal frame.

    ### Example:

        root = Tk()
        frame = SFrame(root, bg='pink')
        frame.pack()

        for i in range(100):
            Button(frame, text='Button %s'%i).pack()

        root.mainloop()
    """

    def __init__(self, master=None, cnf={}, **kw):
        tkb.SFrameBase.__init__(self, master=master, cnf=cnf, **kw)
        # Extra functions
        self.scrollbar_configure = self['scrollbar'].configure


class Button(tkb.ButtonBase):
    """Button for macos, supports almost all the features of tkinter button,
    - Looks very similar to ttk Button.
    - There are few extra features as compared to default Tkinter Button:
    - To check the list of all the resources. To get an overview about
        the allowed keyword arguments call the method `keys`. 
            print(Button().keys())

    ### Examples:
        import tkinter as tk
        import tkmacosx as tkm
        import tkinter.ttk as ttk

        root = tk.Tk()
        root.geometry('200x200')
        tkm.Button(root, text='Mac OSX', bg='lightblue', fg='yellow').pack()
        tk.Button(root, text='Mac OSX', bg='lightblue', fg='yellow').pack()
        ttk.Button(root, text='Mac OSX').pack()
        root.mainloop()

    ### Get a cool gradient effect in activebackground color.
        import tkinter as tk
        import tkmacosx as tkm

        root = tk.Tk()
        root.geometry('200x200')
        tkm.Button(root, text='Press Me!!', activebackground=('pink','blue') ).pack()
        tkm.Button(root, text='Press Me!!', activebackground=('yellow','green') ).pack()
        tkm.Button(root, text='Press Me!!', activebackground=('red','blue') ).pack()
        root.mainloop()"""

    def __init__(self, master=None, cnf={}, **kw):
        tkb.ButtonBase.__init__(self, 'normal', master, cnf, **kw)

    def invoke(self):
        """Invoke the command associated with the button.

        The return value is the return value from the command,
        or an empty string if there is no command associated with
        the button. This command is ignored if the button's state
        is disabled.
        """
        if self['state'] not in ('disable', 'disabled'):
            return self.cnf['command']() if self.cnf.get('command') else None


class CircleButton(tkb.ButtonBase):
    """
    #### Beta-Disclaimer: Please note that this is a BETA version of this widget. \
    Issues at https://github.com/Saadmairaj/tkmacosx/issues/new/choose \
    or email me at saadmairaj@yahoo.in.

    Circle shaped Button supports almost all options of a tkinter button 
    and have some few more useful options such as 'activebackground', overbackground', 
    'overforeground', 'activeimage', 'activeforeground', 'borderless' and much more. 

    To check all the configurable options for CircleButton run `print(CircleButton().keys())`.

    Example:
    ```
    import tkinter as tk
    import tkmacosx as tkm

    root = tk.Tk()
    cb = tkm.CircleButton(root, text='Hello')
    cb.pack()
    root.mainloop()
    ```
    """
    def __init__(self, master=None, cnf={}, **kw):
        tkb.ButtonBase.__init__(self, 'circle', master, cnf, **kw)

    def invoke(self):
        """Invoke the command associated with the button.

        The return value is the return value from the command,
        or an empty string if there is no command associated with
        the button. This command is ignored if the button's state
        is disabled.
        """
        if self['state'] not in ('disable', 'disabled'):
            return self.cnf['command']() if self.cnf.get('command') else None


class Marquee(tkb.MarqueeBase):
    """Use `Marquee` for creating scrolling text which moves from 
    right to left only if the text does not fit completely.

    ### Args:
    - `text`: Give a string to display.
    - `font`: Font of the text.
    - `fg`: Set foreground color of the text.
    - `fps`: Set fps(frames per seconds).
    - `left_margin`: Set left margin to make text move further to right before reset.
    - `initial_delay`: Delay before text start to move.
    - `end_delay`: Delay before text reset.
    - `smoothness`: Set the smoothness of the animation.

    ### Example: 
        root=tk.Tk()
        marquee = Marquee(root, 
                          text='This text will move from right to left if does not fit the window.')
        marquee.pack()
        root.mainloop()

    ### To move the text when cursor is over the text then follow the below example.

        text = "Please hover over the text to move it. \
        This text will move only if the cursor hovers over the text widget".
        root = tk.Tk()
        m = tkm.Marquee(root, bg='lightgreen', text=text)
        m.pack()
        m.stop(True)
        m.bind('<Enter>', lambda _: m.play())
        m.bind('<Leave>', lambda _: m.stop())
        root.mainloop()
        """

    def reset(self):
        """Reset the text postion."""
        self._reset(True)
        self._stop_state = False

    def stop(self, reset=False):
        """Stop the text movement."""
        if reset:
            self.reset()
        self._stop_state = True
        self.after_cancel(self.after_id)
        self.after_id = ' '

    def play(self, reset=False):
        """Play/continue the text movement."""
        if not self._stop_state and not reset:
            return
        self._stop_state = False
        if reset:
            self.reset()
        self._animate()


# ------------------ Testing ------------------


def demo_button():
    if sys.version_info.major == 2:
        import ttk
    elif sys.version_info.major == 3:
        from tkinter import ttk
    root = _TK.Tk()
    root.title('Mac OSX Button Demo')
    page_color = '#FFFFC6'
    root.geometry('300x400')
    root['bg'] = page_color
    _TK.Label(root, text='Can you tell the difference?', font=(
        '', 16, 'bold'), bg=page_color).pack(pady=(20, 5))
    Button(root, text='Press Me', disabledbackground='red').pack(pady=(0, 5))
    ttk.Button(root, text="Press Me").pack()
    _TK.Label(root, text='Change Background Color', font=(
        '', 16, 'bold'), bg=page_color).pack(pady=(20, 5))
    Button(root, text='Press Me', bg='pink',
           activebackground=('pink', 'blue')).pack()
    _TK.Label(root, text='Blend In', font=('', 16, 'bold'),
              bg=page_color).pack(pady=(20, 5))
    Button(root, text='Press Me', bg='yellow', activebackground=(
        'orange', 'lime'), borderless=1).pack()
    _TK.Label(root, text='Change bordercolor', font=(
        '', 16, 'bold'), bg=page_color).pack(pady=(20, 5))
    Button(root, text='Press Me', bg='red', fg='white',
           activebackground=('red', 'blue'), bordercolor='blue').pack()
    root.mainloop()


def demo_sframe():
    root = _TK.Tk()
    frame = SFrame(root, bg='pink')
    frame.pack()
    for i in range(50):
        Button(frame, text='Button %s' % i, borderless=1).pack()
    root.mainloop()


def demo_marquee():
    root = _TK.Tk()
    marquee = Marquee(
        root, text='This text will move from right to left if does not fit the window.')
    marquee.pack()
    root.mainloop()


if __name__ == "__main__":
    demo_sframe()
    demo_button()
    demo_marquee()
