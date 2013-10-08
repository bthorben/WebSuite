import sublime, sublime_plugin
from web_suite_common import get_type, is_supported, augment_options, sublime_plugin, s

import jsbeautifier.unpackers
import merge_utils
import jsformatter
import cssformatter


class WebSuiteEventListener(sublime_plugin.EventListener):
  def on_pre_save(self, view):
    if(s.get("format_on_save") == True):
      view.run_command("web_suite_format")


class WebSuiteFormatCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    if(is_supported(self.view) == False):
      return

    settings = self.view.settings()
    opts = jsbeautifier.default_options()
    opts.indent_char = " " if settings.get("translate_tabs_to_spaces") else "\t"
    opts.indent_size = int(settings.get("tab_size")) if opts.indent_char == " " else 1
    opts = augment_options(opts, s)

    t = get_type(self.view)
    f = None
    if(t == "js"):
      f = jsformatter.JsFormatter(self.view)
    elif(t == "css"):
      f = cssformatter.CssFormatter(self.view)

    if(f != None):
      f.format(edit)

  def is_enabled(self):
    return is_supported(self.view)

  def is_visible(self):
    return is_supported(self.view)