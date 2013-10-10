import sublime, sublime_plugin
import time, sys, os

directory = os.path.dirname(os.path.realpath(__file__))
if directory not in sys.path:
  sys.path.append(directory)
  
import cssFormat
import merge_utils

class CssFormatter:

  def __init__(self, view, settings):
    self.view = view
    self.settings = settings

    self.opts = cssformat.CssFormatOptions()
    self.opts.end_with_newline = False
    self.opts.blank_line_above_comments = False
    self.opts.indent_string = " "
    self.opts.indent_size = 2
    self.opts.comment_line_max = 80

  def format(self, edit):
    self.curpos = self.view.viewport_position()
    self.selection = self.view.sel()[0]
    formatSelection = len(self.selection) > 0
    if formatSelection:
      # adding newlines after the file would also add that after the selection
      self.opts.end_with_newline = False
      for sel in self.view.sel():
        css = self.view.substr(sel)
        css = cssformat.format_css(css, opts=self.opts);
        self.view.replace(edit, sel, css)
    else:
      everything = sublime.Region(0, self.view.size())
      css = self.view.substr(everything)
      formatted_css = cssformat.format_css(css, opts=self.opts);
      _, err = merge_utils.merge_code(self.view, edit, css, formatted_css)
      if err:
        sublime.error_message("WebSuite: Merge failure: '%s'" % err)

      # reestablish selection
      sublime.set_timeout(self.reset_pos, 0)
      
  def reset_pos(self):
    self.view.sel().clear()
    self.view.sel().add(self.selection)
    self.view.set_viewport_position(self.curpos, False)