import sublime, sublime_plugin

class HtmlFormatter:

  def __init__(self, view, settings):
     self.view = view
     self.settings = settings

  def format(self, edit):
    self.view.run_command("reindent", {'single_line': False} )