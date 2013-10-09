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
# even though we don't use it directly ...
import cssformat
import jsbeautifier.unpackers
import merge_utils

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

def is_supported(view):
  return get_type(view) in ["js", "css"]