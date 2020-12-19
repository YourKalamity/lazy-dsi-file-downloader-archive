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

import re
import sys
import ast
import pickle as pkl

if sys.version_info.major == 2:
    import Tkinter as _tk
elif sys.version_info.major == 3:
    import tkinter as _tk


# Modified Misc._options(...) to make ColorVar work with tkinter
# {(self, option, tag): (var, cbname)}
_all_traces_colorvar = {}


def _colorvar_patch_cget(fn):
    """Internal function."""
    def _patch(self, key):
        """Return the resource value for a KEY given as string."""
        if (self, key) in _all_traces_colorvar:
            return _all_traces_colorvar[(self, key)][0]
        return fn(self, key)
    return _patch
            

def _colorvar_patch_destroy(fn):
    """Internal function.\n
    Deletes the traces if any when widget is destroy."""

    def _patch(self):
        """Interanl function."""
        if self._tclCommands is not None:
            # Deletes the widget from the _all_traces_colorvar 
            # and deletes the traces too.
            for key, value in dict(_all_traces_colorvar).items():
                if self == key[0]:
                    var, cbname = value
                    try: var.trace_vdelete('w', cbname)
                    except: pass
                    _all_traces_colorvar.pop(key)
        return fn(self)
    return _patch


def _colorvar_patch_configure(fn):
    """Internal function.\n
    Patch for Canvas items to support ColorVar functionality."""

    def _patch(self, cmd, cnf, kw):
        """Internal function."""

        cnf = _tk._cnfmerge((cnf, kw))
        cnf_copy = dict(cnf)
        # -------------------- Added the below block --------------------
        # Add the resources to the list to have ColorVar functionality.
        if isinstance(cmd, tuple) and isinstance(self, _tk.Canvas):
            tags = self.find('withtag', cmd[1])
            for tag in tags:
                for i in ('activefill', 'activeoutline', 'disabledfill',
                          'disabledoutline', 'fill', 'outline', 'background',
                          'activebackground', 'activeforeground',
                          'disabledbackground', 'disabledforeground',
                          'foreground'):
                    if isinstance(cnf_copy.get(i), _tk.Variable):
                        var = cnf_copy[i]
                        cbname = var.trace_variable('w', lambda a, b, c,
                                                    cls=self, opt=i,
                                                    tagId=tag, var=var:
                                                    cls._configure(('itemconfigure',tagId), 
                                                            {opt: var.get()}, None))
                        if (self, (i, tag)) in _all_traces_colorvar:
                            v, cb = _all_traces_colorvar.get((self, (i, tag)))
                            v.trace_vdelete('w', cb)
                            _all_traces_colorvar[(self, (i, tag))] = (var, cbname)
                        else:
                            _all_traces_colorvar[(self, (i, tag))] = (var, cbname)
                        cnf[i] = var.get()
        return fn(self, cmd, cnf, None)
    return _patch


def _colorvar_patch_options(fn):
    """Internal function.\n
    Patch for ColorVar to work with tkinter widgets."""
    
    def _patch(self, cnf, kw=None):
        """Internal function."""
        if kw:
            cnf = _tk._cnfmerge((cnf, kw))
        else:
            cnf = _tk._cnfmerge(cnf)
            
        for i in ('fg', 'foreground', 'bg', 'background',
                'activebackground', 'activeforeground', 'disabledforeground',
                'highlightbackground', 'highlightcolor', 'selectforeground',
                'readonlybackground', 'selectbackground', 'insertbackground',
                'disabledbackground'):
            if isinstance(cnf.get(i), _tk.Variable):
                var = cnf[i]
                cbname = var.trace_variable('w', lambda a, b, c, i=i, var=var,
                                            cls=self: cls.config({i: var.get()}))
                if (self, i) in _all_traces_colorvar:
                    v, cb = _all_traces_colorvar.get((self, i))
                    v.trace_vdelete('w', cb)
                    _all_traces_colorvar[(self, i)] = (var, cbname)
                else:
                    _all_traces_colorvar[(self, i)] = (var, cbname)
                cnf[i] = var.get()
            # [issue-1] once a ColorVar is assigned, it cannot be removed 
            #           untill the widget is destroyed or give another ColorVar
            # [issue-1] (trial) the below doesn't work as excepted.
            # elif (self, i) in _all_traces_colorvar:
            #     if self[i] != _all_traces_colorvar[(self, i)][0].get():
            #         print( self, i, self[i])
            #         v, cb = _all_traces_colorvar.pop((self, i))
            #         v.trace_vdelete('w', cb)
        return fn(self, cnf, None)
    return _patch


def _create(self, itemType, args, kw):  # Args: (val, val, ..., cnf={})
    """Internal function."""
    args = _tk._flatten(args)
    cnf = args[-1]
    if isinstance(cnf, (dict, tuple)):
        args = args[:-1]
    else:
        cnf = {}

    # -------------------- Added the below block --------------------
    # Add the resources to the list to have ColorVar functionality.
    ckw = _tk._cnfmerge((cnf, kw))
    var = None
    for i in ('activefill', 'activeoutline', 'disabledfill',
              'disabledoutline', 'fill', 'outline', 'background',
              'activebackground', 'activeforeground', 'foreground',
              'disabledbackground', 'disabledforeground'):
        if isinstance(ckw.get(i), _tk.Variable):
            var = ckw[i]
            _all_traces_colorvar[(self, (i, None))] = (var, None)
            if isinstance(cnf, dict) and i in cnf:
                cnf[i] = var.get()
            elif i in kw:
                kw[i] = var.get()
    # ---------------------------------------------------------------

    tagId = self.tk.getint(self.tk.call(
                self._w, 'create', itemType,
                *(args + self._options(cnf, kw))))

    for key, value in dict(_all_traces_colorvar).items():
        if isinstance(key[1], (tuple, list)):
            wid, (opt, tag_id) = key
            var, cbname = value
            if tag_id is None and cbname is None:
                cbname = var.trace_variable('w', lambda a, b, c,
                                            cls=self, opt=opt,
                                            tagId=tagId, var=var:
                                            cls._configure(('itemconfigure',tagId), 
                                                    {opt: var.get()}, None))
                _all_traces_colorvar[(self, (opt, tagId))] = (var, cbname)
                _all_traces_colorvar.pop((self, (opt, None)))
    return tagId


_tk.Misc.destroy = _colorvar_patch_destroy(_tk.Misc.destroy)
_tk.Misc._options = _colorvar_patch_options(_tk.Misc._options)
_tk.Misc._configure = _colorvar_patch_configure(_tk.Misc._configure)
_tk.Canvas._create = _create


class ColorVar(_tk.Variable):
    """Value holder for HEX color. Default is white"""

    _default = "white"
    _rgbstring = re.compile(r'#[a-fA-F0-9]{3}(?:[a-fA-F0-9]{3})?$')

    def __init__(self, master=None, value=None, name=None):
        """Construct a color variable. (bg, fg, ..)

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to "")
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        _tk.Variable.__init__(self, master, value, name)

    def set(self, value=''):
        """Set the variable to VALUE."""
        if value.startswith('#'):
            if not bool(self._rgbstring.match(value)):
                raise ValueError('"{}" is not a valid HEX.'.format(value))
        elif isinstance(value, str):
            try:
                r, g, b = self._root.winfo_rgb(value)
                c = (r/257, g/257, b/257)
                value = '#%02x%02x%02x' % (int(c[0]), int(c[1]), int(c[2]))
            except:
                raise ValueError(
                    'Could not find right HEX for "{}".'.format(value))
        return self._tk.globalsetvar(self._name, value)
    initialize = set

    def get(self):
        """Return value of variable color."""
        value = self._tk.globalgetvar(self._name)
        if isinstance(value, str):
            return value
        return str(value)


class DictVar(_tk.Variable):
    """
    #### Value holder for Dictionaries.
    Get a specific value by getting the key from this \
    `get(self, key=None, d=None)` method if exists in the dictionary. \n
    if `key=None` it will return the complete dictionary.
    """
    _default = {}

    def __init__(self, master=None, value=None, name=None):
        """Construct a string variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to {})
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        _tk.Variable.__init__(self, master, value, name)

    def get(self, key=None, d=None):
        """Return value of variable as string."""
        value = self._tk.globalgetvar(self._name)
        if not isinstance(value, dict):
            value = ast.literal_eval(value)
        if key:
            return value.get(key, d)
        else:
            return value


def SaveVar(var, master=None, value=None, name=None, filename='data.pkl'):
    """Save tkinter variable data in a pickle file and load the 
    same value when the program is executed next time. 

    #### If the content of the file changes, it might not load correct values \
        to the assigned variables. To avoid this issue use `name` to \
        refer to the exact assigned values later.

    ### Args:
    - `var`: Give the `tkinter.Variable` class like (`tk.StringVar`, `tk.IntVar`).
    - `master`: Parent widget.
    - `value`: Set value.
    - `name`: Set a name to group variables or to refer to assigned value when loaded.
    - `filename`: Set the name of the save file. (To make the file invisible in the \
            directory start the name of the file with "." like ".cache-savevar")

    ### Return:
    - returns the tk.Variable instance passed to `var` argument.

    ### Example:
        root = tk.Tk()
        var1 = SaveVar(tk.StringVar,'Enter Username','Var1','.cache-savevar')
        var2 = SaveVar(tk.StringVar,'Enter Password','Var2','.cache-savevar')
        tk.Entry(root,textvariable=var1).pack()
        tk.Entry(root,textvariable=var2).pack()
        root.mainloop()"""

    def update_val(*args):
        """Internal function for updating the value for variable"""
        try:    # try/except , if the file doesn't exists.
            open1 = open(filename, 'rb')
            tmpdict = pkl.load(open1)  # load saved dictionary data.
            # Block of code to check for the right value.
            if tmpdict.get(str(var)):
                old, default = tmpdict.get(str(var))
                new = var.get()
                if new != default:
                    var.set(new)
                elif new == default and not startup[0]:
                    var.set(default)
                else:
                    var.set(old)
            tmpdict.update({str(var): (var.get(), defaultval)})
            open1.close()
        except Exception as e:
            tmpdict = {}
            tmpdict[str(var)] = (var.get(), defaultval)

        open2 = open(filename, 'wb')
        pkl.dump(tmpdict, open2)
        startup[0] = False
        open2.close()

    startup = [True]
    if not(filename.endswith('.pickle') or filename.endswith('.pkl')) \
            and not filename.startswith('.'):
        filename = filename+'.pkl'
    var = var(master=master, value=value, name=name)
    defaultval = var.get()  # get a default value of the variable
    update_val()
    for mode, cbname in (var.trace_vinfo()):
        if mode[0] == 'w' and update_val.__name__ in cbname:
            try:
                var.trace_vdelete('w', cbname)
            except:
                pass
    res = var.trace_variable('w',  update_val)
    return var


# ------------------ Testing ------------------

def demo_colorvar():
    import tkmacosx.colors as colors
    root = _tk.Tk()
    root.geometry('100x100')
    color = ColorVar()
    color_list = list(colors.OrderedHex)
    L = _tk.Label(root, textvariable=color, bg=color)
    L.place(relx=0.5, rely=0.5, anchor='center')

    def change_color(c=0):
        if root.winfo_exists():
            if c >= len(color_list):
                c = 0
            color.set(color_list[c])
            root.after(100, change_color, c+1)

    change_color()
    root.mainloop()


def demo_savevar():
    root = _tk.Tk()
    var1 = SaveVar(_tk.StringVar, root, 'Enter Username',
                   'Var1', '.cache-savevar')
    var2 = SaveVar(_tk.StringVar, root, 'Enter Password',
                   'Var2', '.cache-savevar')
    _tk.Entry(root, textvariable=var1).pack()
    _tk.Entry(root, textvariable=var2).pack()
    root.mainloop()


if __name__ == "__main__":
    demo_colorvar()
    demo_savevar()
