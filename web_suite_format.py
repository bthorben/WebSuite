import sublime, sublime_plugin
from web_suite_common import get_type, is_supported, s

import jsbeautifier.unpackers
import merge_utils
import cssformat
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