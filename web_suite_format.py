import sublime, sublime_plugin, re, sys, os, json


directory = os.path.dirname(os.path.realpath(__file__))
libs_path = os.path.join(directory, "libs")
is_py2k = sys.version_info < (3, 0)


# Python 2.x on Windows can't properly import from non-ASCII paths, so
# this code added the DOC 8.3 version of the lib folder to the path in
# case the user's username includes non-ASCII characters
def add_lib_path(lib_path):
  def _try_get_short_path(path):
    path = os.path.normpath(path)
    if is_py2k and os.name == 'nt' and isinstance(path, unicode):
      try:
        import locale
        path = path.encode(locale.getpreferredencoding())
      except:
        from ctypes import windll, create_unicode_buffer
        buf = create_unicode_buffer(512)
        if windll.kernel32.GetShortPathNameW(path, buf, len(buf)):
          path = buf.value
    return path
  lib_path = _try_get_short_path(lib_path)
  if lib_path not in sys.path:
    sys.path.append(lib_path)

# crazyness to get jsbeautifier.unpackers to actually import
# with sublime's weird hackery of the path and module loading
add_lib_path(libs_path)

# if you don't explicitly import jsbeautifier.unpackers here things will bomb out,
# even though we don't use it directly.....
import jsbeautifier.unpackers
import merge_utils
from jsformat import JsFormatter

s = None
def plugin_loaded():
  global s
  s = sublime.load_settings("websuite.sublime-settings")
if is_py2k:
  plugin_loaded()


def augment_options(options, subset):
  fields = [attr for attr in dir(options) if not callable(getattr(options, attr)) and not attr.startswith("__")]

  for field in fields:
    value = subset.get(field)
    if value != None:
      setattr(options, field, value)

  return options


supported_types = ["js", "css"]
def get_type(view):
  fName = view.file_name()
  vSettings = view.settings()
  syntaxPath = vSettings.get('syntax')
  syntax = ""
  ext = ""

  if (fName != None): # file exists, pull syntax type from extension
    ext = os.path.splitext(fName)[1][1:]
  if(syntaxPath != None):
    syntax = os.path.splitext(syntaxPath)[0].split('/')[-1].lower()

  js = ext in ['js', 'json'] or "javascript" in syntax or "json" in syntax
  css = ext in ['css'] or "css" in syntax
  if js:
    return "js"
  if css:
    return "css"


class WebSuiteEventListener(sublime_plugin.EventListener):
  def on_pre_save(self, view):
    if(s.get("format_on_save") == True):
      view.run_command("web_suite_format")


class WebSuiteFormatCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    if(get_type(self.view) in supported_types == False):
      return

    settings = self.view.settings()
    opts = jsbeautifier.default_options()
    opts.indent_char = " " if settings.get("translate_tabs_to_spaces") else "\t"
    opts.indent_size = int(settings.get("tab_size")) if opts.indent_char == " " else 1
    opts = augment_options(opts, s)

    selection = self.view.sel()[0]
    formatSelection = len(selection) > 0

    f = JsFormatter(self.view);
    if formatSelection:
      f.format_selection(edit, opts)
    else:
      f.format_whole_file(edit, opts)

  def is_enabled(self):
    return get_type(self.view) in supported_types

  def is_visible(self):
    return get_type(self.view) in supported_types