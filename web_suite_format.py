import sublime, sublime_plugin
import sys, os

is_py2k = sys.version_info < (3, 0)

def add_libs_path():
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
  directory = os.path.dirname(os.path.realpath(__file__))
  lib_path = os.path.join(directory, "libs")
  lib_path = _try_get_short_path(lib_path)
  if lib_path not in sys.path:
    sys.path.append(lib_path)

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

  if ext in ['js', 'json'] or "javascript" in syntax or "json" in syntax:
    return "js"
  if ext in ['css'] or "css" in syntax:
    return "css"
  if ext in ['html', 'htm'] or "html" in syntax:
    return "html"

def is_supported(view):
  return get_type(view) in ["js", "css", "html"]

s = None
def plugin_loaded():
  global s
  s = sublime.load_settings("websuite.sublime-settings")
if is_py2k:
  plugin_loaded()

add_libs_path()
import jsformatter
import cssformatter
import htmlformatter


class WebSuiteEventListener(sublime_plugin.EventListener):
  def on_pre_save(self, view):
    if(s.get("format_on_save") == True and is_supported(view)):
      view.run_command("web_suite_format")


class WebSuiteFormatCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    if(is_supported(self.view) == False):
      return

    t = get_type(self.view)
    f = None
    if t == "js":
      f = jsformatter.JsFormatter(self.view)
    elif t == "css":
      f = cssformatter.CssFormatter(self.view)
    elif t == "html":
      f = htmlformatter.HtmlFormatter(self.view)

    if(f != None):
      f.format(edit)

  def is_enabled(self):
    return is_supported(self.view)

  def is_visible(self):
    return is_supported(self.view)
