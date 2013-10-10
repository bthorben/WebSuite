import sublime, sublime_plugin

class HtmlFormatter:

  def __init__(self, view):
     self.view = view

  def format(self, edit):
    self.view.run_command("reindent", {'single_line': False} )