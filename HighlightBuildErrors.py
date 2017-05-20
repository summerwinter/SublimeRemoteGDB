import sublime, sublime_plugin
import importlib
import threading
import re
import os

SETTINGS_FILE = "HighlightBuildErrors.sublime-settings"
REGION_KEY_PREFIX = "build_errors_color"
REGION_FLAGS = {
    "none": sublime.HIDDEN,
    "fill": 0,
    "outline": sublime.DRAW_NO_FILL,
    "solid_underline": sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_SOLID_UNDERLINE,
    "stippled_underline":  sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_STIPPLED_UNDERLINE,
    "squiggly_underline":  sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_SQUIGGLY_UNDERLINE
}

try:
    defaultExec = importlib.import_module("Better Build System").BetterBuidSystem
except:
    defaultExec = importlib.import_module("Default.exec")

try:
    ansiEscape = importlib.import_module("ANSIescape").ansi
except:
    pass

class ErrorLine:
    def __init__(self, matchObject):
        global g_color_configs
        # only keep last line (i've seen a bad regex that capture several lines)
        self.file_name = get_filename(matchObject);
        self.line = get_line(matchObject);
        self.column = get_column(matchObject)
        self.message = get_message(matchObject)
        if self.message == None: return
        self.color_index = 0
        for config in g_color_configs:
            if not "compiled_regex" in config:
                break
            if config["compiled_regex"].search(self.message):
                break
            self.color_index = self.color_index+1;

    def get_region(self, view):
        if self.line is None:
            return None
        if self.column is None:
            point = view.text_point(self.line-1, 0)
            return view.full_line(point)
        point = view.text_point(self.line-1, self.column-1)
        point_class = view.classify(point)
        if point_class & (sublime.CLASS_WORD_START|sublime.CLASS_WORD_END):
            return view.word(point)
        else:
            return view.full_line(point)

class BuildErrorsViews:
    def __init__(self, name):
        self.name = name
        self.closed = True
        self.view = None
        self.lines = ""
        self.error_lines = []
        self.lock = threading.RLock()

    def is_open(self):
        return not self.closed

    def open(self, errors):
        self.create_view(errors)

    def create_view(self, errors):
        if not self.view:
            self.view = sublime.active_window().new_file()
            self.view.set_name(self.name)
            self.view.set_scratch(True)
            self.view.set_read_only(True)
            # Setting command_mode to false so that vintage
            # does not eat the "enter" keybinding
            self.view.settings().set('command_mode', False)
            self.closed = False
        self.view.run_command("error_view_clear")
        self.lines = ""
        self.end = -1
        for e in errors:
            self.add_line(e)
        self.view.run_command("error_view_add_line", {"line": self.lines, "doScroll": True})

    def destroy_view(self):
        if self.is_open(): 
            sublime.active_window().focus_view(self.view)
            # sublime.active_window().run_command("close")
            self.view = None
            self.lines = ""
            self.closed = True
            self.error_lines = []

    def clear(self):
        if self.is_open(): 
            self.view.run_command("error_view_clear")
            self.error_lines =[]
            self.lines = ""

    def set_syntax(self, syntax):
        if self.is_open():
            self.get_view().set_syntax_file(syntax)

    def add_line(self, errorline, now=True):
        if self.is_open():
            try:
                self.lock.acquire()
                self.lines += errorline.file_name + ":" + str(errorline.line) + ":" + errorline.message + "\n"
                self.end += 1;
                self.error_lines.append(errorline)
            finally:
                self.lock.release()

    def get_view(self):
        return self.view

    def select(self, row):
        if row >= len(self.error_lines):
            return
        errorline = self.error_lines[row]
        sublime.active_window().open_file("%s:%d" % (errorline.file_name, errorline.line), sublime.ENCODED_POSITION)

g_errors = {}
g_show_errors = True
g_color_configs = []
g_error_views = BuildErrorsViews("build_error_views")

def plugin_loaded():
    settings = sublime.load_settings(SETTINGS_FILE)
    settings.add_on_change("colors", load_config)
    load_config()

def load_config():
    global g_color_configs, g_default_color
    settings = sublime.load_settings(SETTINGS_FILE)
    g_color_configs = settings.get("colors", [{"color": "sublimelinter.mark.error"}])
    for config in g_color_configs:
        if "regex" in config:
            config["compiled_regex"] = re.compile(config["regex"])

def normalize_path(file_name):
    return os.path.normcase(os.path.abspath(file_name))

def update_errors_in_view(view):
    global g_color_configs, g_default_color
    file_name = view.file_name()
    if file_name is None:
        return
    file_name = normalize_path(file_name)
    for idx, config in enumerate(g_color_configs):
        region_key = REGION_KEY_PREFIX + str(idx)
        scope = config["scope"] if "scope" in config else "invalid"
        icon = config["icon"] if "icon" in config else ""
        default_display = "fill" if "scope" in config else "none"
        display = config["display"] if "display" in config else default_display
        if g_show_errors:
            regions = [e.get_region(view) for e in g_errors if e.file_name == file_name and e.color_index == idx]
            view.add_regions(region_key, regions, scope, icon, REGION_FLAGS[display])
        else:
            view.erase_regions(region_key)

def update_all_views(window):
    for view in window.views():
        update_errors_in_view(view)

def remove_errors_in_view(view):
    global g_color_configs
    for idx, val in enumerate(g_color_configs):
        view.erase_regions(REGION_KEY_PREFIX + str(idx))

class ViewEventListener(sublime_plugin.EventListener):
    def on_load_async(self, view):
        update_errors_in_view(view)

    def on_activated_async(self, view):
        update_errors_in_view(view)

    def on_modified_async(self, view):
        if not view.is_dirty():
            # Then most likely just reloaded or saved!
            update_errors_in_view(view)

def get_filename(matchObject):
    # only keep last line (i've seen a bad regex that capture several lines)
    return normalize_path(matchObject.group(1).splitlines()[-1])

def get_line(matchObject):
    if len(matchObject.groups()) < 3:
        return None
    try:
        return int(matchObject.group(2))
    except ValueError:
        return None

def get_column(matchObject):
    # column is optional, the last one is always the message
    if len(matchObject.groups()) < 4 or matchObject.group(3) is None:
        return None
    try:
        return int(matchObject.group(3))
    except ValueError:
        return None

def get_message(matchObject):
    if len(matchObject.groups()) < 3:
        return None
    # column is optional, the last one is always the message
    return matchObject.group(len(matchObject.groups()))

class ErrorParser:
    def __init__(self, pattern):
        self.regex = re.compile(pattern, re.MULTILINE)
        self.bad_regex = self.regex.groups < 3 or self.regex.groups > 4
        if self.bad_regex:
            print("Highlight Build Errors plugin warning: invalid configuration\nThe regular expression must capture filename,line,[column,]message\nPlease fix the 'file_regex' in build system configuration.")

    def parse(self, text):
        if self.bad_regex:
            return []
        else:
            return [ErrorLine(m) for m in self.regex.finditer(text)]

def doHighlighting(self):
    return
    output = self.output_view.substr(sublime.Region(0, self.output_view.size()))
    error_pattern = self.output_view.settings().get("result_file_regex")
    print(error_pattern)
    error_parser = ErrorParser(error_pattern)

    global g_errors
    g_errors = error_parser.parse(output)
    g_error_views.open(g_errors)
    update_all_views(self.window)

class ExecCommand(defaultExec.ExecCommand):

    def finish(self, proc):
        super(ExecCommand, self).finish(proc)
        doHighlighting(self)

try:
    class AnsiColorBuildCommand(ansiEscape.AnsiColorBuildCommand):

        def finish(self, proc):
            super(AnsiColorBuildCommand, self).finish(proc)
            doHighlighting(self)
except:
    pass

class HideBuildErrorsCommand(sublime_plugin.WindowCommand):

    def is_enabled(self):
        return g_show_errors

    def run(self):
        global g_show_errors
        g_show_errors = False
        update_all_views(self.window)

class ShowBuildErrorsCommand(sublime_plugin.WindowCommand):

    def is_enabled(self):
        return not g_show_errors

    def run(self):
        global g_show_errors
        g_show_errors = True
        update_all_views(self.window)

# class ErrorsClick(sublime_plugin.TextCommand):
#     def run(self, edit):
#         if not g_error_views.is_open():
#             return
#         row, col = self.view.rowcol(self.view.sel()[0].a)
#         if g_error_views.is_open() and self.view.id() == g_error_views.get_view().id():
#             g_error_views.select(row)
#     def is_enabled(self):
#         return g_error_views.is_open()

class ErrorViewClear(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.set_read_only(False)
        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.set_read_only(True)

class ErrorViewAddLine(sublime_plugin.TextCommand):
    def run(self, edit, line, doScroll):
        self.view.set_read_only(False)
        self.view.insert(edit, self.view.size(), line)
        self.view.set_read_only(True)
        if doScroll:
            self.view.show(self.view.size())

class ErrorViewEventListener(sublime_plugin.EventListener):
     def on_close(self, view):
        if g_error_views.get_view() and view.id() == g_error_views.get_view().id():
            g_error_views.destroy_view()