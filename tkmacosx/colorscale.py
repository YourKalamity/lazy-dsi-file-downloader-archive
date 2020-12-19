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

'''
Newer style colorchoosers for tkinter module.

Version: 0.1.4
'''

__version__ =  "0.1.4"

import re
import sys

if sys.version_info.major == 2:  # For python 2.x
    import Tkinter as _tk
    from tkFont import Font
    import tkFont as font
elif sys.version_info.major == 3:  # For python 3.x
    import tkinter as _tk
    from tkinter import font
    from tkinter.font import Font

import colour
import tkmacosx.basewidget as tkb


HEX = 'hex'
RGB = 'rgb'


def gradient(iteration):
    """This function returns a list of HSL values
    of all the colors in an order."""

    ops = {'+': lambda c, step: min(1.0, c + step),
           '-': lambda c, step: max(0.0, c - step)}

    index = 0
    operation = '+'
    iteration = max(0, iteration-2)
    rgb, _list = [1.0, 0.0, 0.0], []
    combo = ((2, 1, 0), (2, 0, 1), (0, 2, 1), (0, 1, 2), (1, 0, 2), (1, 2, 0))
    step = float(len(combo)) / float(iteration)
    _list.append('#%02x%02x%02x' % (round(rgb[0]*255),
                                    round(rgb[1]*255), round(rgb[2]*255)))
    for i in range(iteration):
        if (rgb[combo[index][1]] == 1.0 and operation == '+') or \
           (rgb[combo[index][1]] == 0.0 and operation == '-'):
            operation = '-' if operation == '+' else '+'
            index += 1
        rgb[combo[index][1]] = ops[operation](rgb[combo[index][1]], step)
        _list.append('#%02x%02x%02x' % (round(rgb[0]*255),
                                        round(rgb[1]*255), round(rgb[2]*255)))
    _list.append('#%02x%02x%02x' % (round(1.0*255),
                                    round(0.0*255), round(0.0*255)))
    return _list


class Colorscale(tkb._Canvas):
    """
    ## Color Scale.
    This is ColorScale alternate to tkinter's colorchooser. 

    ### Args: 
    - `value`: Get either 'RGB' or 'HEX'.
    - `command`: callback function with an argument.
    - `orient`: Set the orientation.
    - `mousewheel`: Set mousewheel to scroll marker.
    - `variable`: Give tkinter variable (`StringVar`).
    - `showinfo`: Shows hex or rbg while selecting color.
    - `gradient`: Take tuple of two colors or default.
    - `showinfodelay`: Delay before the showinfo disappears (in ms).
    """

    _features = ('value', 'command', 'orient', 'mousewheel', 'variable', 'showinfo',
                 'showinfodelay', 'gradient',)  # add more features

    def __init__(self, master=None, cnf={}, **kw):
        kw = {k: v for k, v in _tk._cnfmerge(
            (cnf, kw)).items() if v is not None}
        self.cnf = {k: kw.pop(k, None)
                    for k in kw.copy() if k in self._features}

        self.cnf['value'] = self.cnf.get('value', 'hex')
        self.cnf['orient'] = self.cnf.get('orient', 'vertical')
        self.cnf['gradient'] = self.cnf.get('gradient', 'default')
        self.cnf['showinfo'] = self.cnf.get('showinfo', True)
        self.cnf['showinfodelay'] = self.cnf.get('showinfodelay', 1500)

        kw['width'] = kw.get(
            "width", 250 if 'ver' in self.cnf['orient'] else 30)
        kw['height'] = kw.get(
            "height", 30 if 'ver' in self.cnf['orient'] else 250)
        kw['highlightthickness'] = kw.get('highlightthickness', 0)
        tkb._Canvas.__init__(self, master=master, cnf={}, **kw)

        # Protected members of the class
        self._size = (0, 0)
        self._marker_color = 'black'
        self._xy = int((self.winfo_reqwidth() if 'ver' in \
                    self['orient'] else self.winfo_reqheight()) / 3)

        binds = [{'className': 'set_size', 'sequence': '<Configure>', 'func': self._set_size},
                 {'className': 'b1_on_motion', 'sequence': '<B1-Motion>',
                     'func': self._move_marker},
                 {'className': 'b1_press', 'sequence': '<Button-1>', 'func': self._move_marker}]
        tkb._bind(self, *binds)
        self._set_mousewheel()

    def _set_size(self, evt=None):
        """Internal function."""
        if evt.width == self._size[0] and evt.height == self._size[1]:
            return
        self._size = (evt.width, evt.height)
        self._create_items('create', safe_create=True)

    def _callback(self, color):
        """Internal function."""
        if self.cnf.get('command'):
            self.cnf['command'](color)
        if self.cnf.get('variable'):
            self.cnf['variable'].set(color)

    def _create_items(self, cmd, safe_create=False, **kw):
        """Internal function.\n
        Checks and creates (text, marker, 
        showinfo, gradient lines) items."""

        def check_tag(tag):
            """Internal function.\n
            If `cmd="check"` and the tag does not exist then
            the tag is created, but if `cmd="create"` and
            safe_create=True this will delete the tag if exists
            and creates a new tag  with same settings."""
            if cmd == 'check':
                c = False
            elif cmd == 'create':
                c = True
            else:
                raise ValueError(
                    '%s is not a valid command! Takes -create, -check' % cmd)
            cond1 = bool(not self.find('withtag', tag) or c)
            cond2 = bool(tag not in kw.get('avoid', []))
            if safe_create and cond1 and cond2:
                self.delete(tag)
            return cond1 and cond2

        ids = []

        if check_tag('gradient'):
            w, h = self.winfo_width(), self.winfo_height()
            iteration = w if 'ver' in self.cnf['orient'] else h
            # iteration -=
            if self.cnf.get('gradient', 'default') == 'default':
                color_list = gradient(iteration)
            elif isinstance(self.cnf.get('gradient'), (list, tuple)):
                c1 = colour.Color(self.cnf.get('gradient')[0])
                c2 = colour.Color(self.cnf.get('gradient')[1])
                color_list = c1.range_to(c2, iteration)
            elif isinstance(self.cnf.get('gradient'), str):
                c = colour.Color(self.cnf.get('gradient'))
                color_list = c.range_to(c, iteration)

            for count, c in enumerate(color_list):
                if self.cnf['orient'] == 'vertical':
                    ags = (count, -1, count, h)
                elif self.cnf['orient'] == 'horizontal':
                    ags = (-1, count, w, count)
                ids.append(self._create('line', ags, {
                           'fill': c, 'tag': 'gradient'}))

        if check_tag('borderline'):
            w, h = self.winfo_width(), self.winfo_height()
            borderline_points = kw.get('borderline_points',
                                       (1, 1, self.winfo_width()-2,
                                        self.winfo_height()-2, 0))
            ids.append(self.rounded_rect(borderline_points, width=2,
                                         outline='#81b3f4', tag='borderline', 
                                         style='arc'))

        if check_tag('marker'):
            marker_points = kw.get('marker_points', (
                self._xy if 'ver' in self.cnf['orient'] else 2,
                2 if 'ver' in self.cnf['orient'] else self._xy,
                5 if 'ver' in self.cnf['orient'] else self.winfo_width() - 4,
                self.winfo_height() - 4 if 'ver' in self.cnf['orient'] else 5,
                2))
            ids.append(self.rounded_rect(marker_points, width=2,
                                         outline=self._marker_color, 
                                         tag="marker", style='arc'))

        if check_tag('markerbg'):
            markerbg_points = kw.get('markerbg_points')
            cnf = kw.get('markerbg_cnf')
            if not markerbg_points:
                return None
            ids.append(self._rounded(markerbg_points, **cnf))

        if check_tag('info'):
            info_points = kw.get('info_points')
            cnf = kw.get('info_cnf')
            if not info_points:
                return None
            ids.append(self._create('text', info_points, cnf))

        return ids

    def _release(self, evt=None):
        """Internal function."""
        self.delete('info', 'markerbg')

    def _move_marker(self, evt, mw=None):
        """Internal function."""
        if mw:
            evt.x = mw if 'ver' in self.cnf['orient'] else 10
            evt.y = 10 if 'ver' in self.cnf['orient'] else mw

        self.after_cancel(getattr(self, '_remove_id', ' '))
        self._remove_id = self.after(self.cnf['showinfodelay'], self._release)

        cond_x = bool(evt.x > 0 and evt.x < self.winfo_width())
        cond_y = bool(evt.y > 0 and evt.y < self.winfo_height())
        cond_state = bool(self['state'] not in 'disabled')

        if not (cond_x and cond_y and cond_state):
            return

        if not mw:
            self._xy = evt.x if 'ver' in self.cnf['orient'] else evt.y

        c_id = self.find('overlapping', evt.x, evt.y, evt.x, evt.y)
        hexcode = self.itemcget(c_id[0], 'fill')
        rgb = [int(i/65535.0*255.0) for i in self.winfo_rgb(hexcode)]
        self._marker_color = 'black' if (
            rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 110 else 'white'

        self._configure(('itemconfigure', 'borderline'),
                        {'outline': hexcode}, None)

        if self.cnf['value'] == "rgb":
            spacer, spacbg = 65, 55
            text = ' | '.join([v+':'+str(f)
                               for f, v in zip(rgb, ('R', 'G', 'B'))])
            self._callback(rgb)
        elif self.cnf['value'] == "hex":
            spacer, spacbg = 35, 25
            text = hexcode
            self._callback(hexcode)

        ver_cond = evt.x < self.winfo_width() - (spacbg+spacer)\
                        and self['orient'] == 'vertical'
        hor_cond = evt.y < self.winfo_height() - (spacbg+spacer)\
                         and self['orient'] == 'horizontal'
        markerbg_points = info_points = ()

        if bool(ver_cond or hor_cond) and self['showinfo']:
            markerbg_points = (
                evt.x+spacer - spacbg if 'ver' in self.cnf['orient'] else self.winfo_width()/2-6,
                self.winfo_height()/2-6 if 'ver' in self.cnf['orient'] else evt.y+spacer-spacbg,
                evt.x+spacer + spacbg if 'ver' in self.cnf['orient'] else self.winfo_width()/2+7,
                self.winfo_height()/2+7 if 'ver' in self.cnf['orient'] else evt.y+spacer+spacbg,
                6)

            info_points = (
                (evt.x+spacer if 'ver' in self.cnf['orient'] else self.winfo_width()/2,
                 self.winfo_height()/2 if 'ver' in self.cnf['orient'] else evt.y+spacer))

        elif self['showinfo']:
            markerbg_points = (
                evt.x-spacer - spacbg if 'ver' in self.cnf['orient'] else self.winfo_width()/2-6,
                self.winfo_height()/2-6 if 'ver' in self.cnf['orient'] else evt.y-spacer-spacbg,
                evt.x-spacer +spacbg if 'ver' in self.cnf['orient'] else self.winfo_width()/2+7,
                self.winfo_height()/2+7 if 'ver' in self.cnf['orient'] else evt.y-spacer+spacbg,
                6)

            info_points = (
                (evt.x-spacer if 'ver' in self.cnf['orient'] else self.winfo_width()/2,
                 self.winfo_height()/2 if 'ver' in self.cnf['orient'] else evt.y-spacer))

        markerbg_cnf = {'fill': self._marker_color, 'tag': 'markerbg'}
        info_cnf = {'angle': 0 if 'ver' in self.cnf['orient'] else 90,
                    'text': text, 'font': Font(size=10), 'tag': "info", 'fill': hexcode}

        self._create_items('create', safe_create=True, avoid=('gradient', 'borderline'),
                           info_points=info_points, markerbg_points=markerbg_points,
                           info_cnf=info_cnf, markerbg_cnf=markerbg_cnf)

        return True

    def _set_mousewheel(self, evt=None):
        """Internal function.\n
        Sets mousewheel scrolling."""

        def on_mousewheel(evt=None):
            "Internal function."
            ver_cond = self._xy < self.winfo_width() \
                        and self['orient'] == 'vertical'
            hor_cond = self._xy < self.winfo_height() \
                        and self['orient'] == 'horizontal'
            if tkb.delta(evt) <= -1 and (ver_cond or hor_cond):
                self._xy += 1
                if not self._move_marker(evt, mw=self._xy):
                    self._xy -= 1
            if tkb.delta(evt) >= 1 and self._xy > 1:
                self._xy -= 1
                if not self._move_marker(evt, mw=self._xy):
                    self._xy += 1

        if self.cnf.get('mousewheel'):
            tkb._bind(self, className='mousewheel',
                        sequence='<MouseWheel>', func=on_mousewheel)
            tkb._bind(self, className='mousewheel_x11',
                        sequence='<Button-4>', func=on_mousewheel)
            tkb._bind(self, className='mousewheel_x11',
                        sequence='<Button-5>', func=on_mousewheel)
        else:
            tkb._bind(self, className='mousewheel', 
                        sequence='<MouseWheel>')
            tkb._bind(self, className='mousewheel_x11',
                        sequence='<Button-4>')
            tkb._bind(self, className='mousewheel_x11',
                        sequence='<Button-5>')

    def _configure(self, cmd, cnf=None, kw=None):
        """Internal function."""
        kw1 = _tk._cnfmerge((cnf, kw))
        self.cnf.update(
            {k: kw.pop(k, None) for k in kw1.copy() if k in self._features})
        self.cnf = {k: v for k, v in self.cnf.copy().items() if v is not None}
        _return = tkb._Canvas._configure(self, cmd, None, kw1)
        if _tk._cnfmerge((cnf, kw)).get('gradient'):
            self._create_items('create', safe_create=True,
                               avoid=('borderline', 'marker', 
                                      'markerbg', 'info'))
        self._set_mousewheel()
        if _return and isinstance(_return, dict):
            _return.update(self.cnf)
        return _return

    def cget(self, key):
        """Return the resource value for a KEY given as string."""
        if key in self.cnf.keys():
            return self.cnf.get(key)
        return tkb._Canvas.cget(self, key)
    __getitem__ = cget

    def keys(self):
        """Return a list of all resource names of this widget."""
        return list(sorted(self.config() + self._features))

    def destroy(self):
        """Destroy this widget."""
        self.after_cancel(getattr(self, '_remove_id', ' '))
        return tkb._Canvas.destroy(self)


# ------------------------------------ #
#           Testing and demo           #
# ------------------------------------ #

def demo_colorscale():
    from tkmacosx.variables import ColorVar

    root = _tk.Tk()
    root.title("Tkinter Color Bar")
    var = ColorVar()
    _tk.Label(root, text="I am a Label, Hello! :-)",
              bg=var).pack(padx=10, pady=10)
    Colorscale(root, value='hex', variable=var, mousewheel=1,
               gradient=('pink', 'purple')).pack(padx=10, pady=10)
    Colorscale(root, value='hex', variable=var, mousewheel=1,
               gradient=('green', 'yellow')).pack(padx=10, pady=10)
    Colorscale(root, value='hex', variable=var, mousewheel=1,
               gradient=('purple', 'cyan')).pack(padx=10, pady=10)
    Colorscale(root, value='hex', variable=var, mousewheel=1,
               gradient=('white', '#89ABE3')).pack(padx=10, pady=10)
    Colorscale(root, value='hex', variable=var, mousewheel=1, 
               gradient=('#5F4B8B', '#E69A8D'), orient='horizontal'
               ).pack(padx=10, pady=10, side='left')
    Colorscale(root, value='hex', variable=var, mousewheel=1, 
               gradient=('#990011', '#FCF6F5'), orient='horizontal'
               ).pack(padx=60, pady=10, side='left')
    Colorscale(root, value='hex', variable=var, mousewheel=1, 
               orient='horizontal').pack(padx=10, pady=10, side='left')
    root.mainloop()


if __name__ == "__main__":
    demo_colorscale()
