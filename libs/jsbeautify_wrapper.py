import sublime
import sys
import os
import re

directory = os.path.dirname(os.path.realpath(__file__))
if directory not in sys.path:
    sys.path.append(directory)

import jsbeautifier.unpackers
import jsbeautifier
import cssbeautifier
import merge_utils


class JsBeautifyWrapper:

    def __init__(self, settings, type, view):
        self.settings = settings
        self.type = type
        self.view = view
        if self.type is "js":
            self.options = jsbeautifier.default_options()
        if self.type is "css":
            self.options = cssbeautifier.default_options()

        self.augment_options(settings)
        view_settings = self.view.settings()
        if view_settings.get("translate_tabs_to_spaces"):
            self.options.indent_char = "\t"
        if self.options.indent_char is " ":
            self.options.indent_size = int(view_settings.get("tab_size"))
        else:
            self.options.indent_size = 1

    def augment_options(self, subset):
        fields = [attr for attr in dir(self.options) if not
                  callable(getattr(self.options, attr))
                  and not attr.startswith("__")]
        for field in fields:
            value = subset.get(field)
        if value is not None:
            setattr(self.options, field, value)

    def beautify(self, code):
        if self.type is "js":
            return jsbeautifier.beautify(code, self.options)
        if self.type is "css":
            return cssbeautifier.beautify(code, self.options)

    def format(self, edit):
        selection = self.view.sel()[0]
        formatSelection = len(selection) > 0

        if formatSelection:
            self.__format_selection__(edit)
        else:
            self.__format_whole_file__(edit)

    def __format_whole_file__(self, edit):
        view = self.view
        region = sublime.Region(0, view.size())
        code = view.substr(region)
        formatted_code = self.beautify(code)

        settings = view.settings()
        if settings.get("ensure_newline_at_eof_on_save") \
           and not formatted_code.endswith("\n"):
            formatted_code = formatted_code + "\n"

        _, err = merge_utils.merge_code(view, edit, code, formatted_code)
        if err:
            print("WebSuite Format: Merge failure: '%s'" % err)

    def __format_selection__(self, edit):
        def get_line_indentation_pos(point):
            line_region = self.view.line(point)
            pos = line_region.a
            end = line_region.b
            while pos < end:
                ch = self.view.substr(pos)
                if ch != ' ' and ch != '\t':
                    break
                pos += 1
            return pos

        def get_indentation_count(start):
            indent_count = 0
            i = start - 1
            while i > 0:
                ch = self.view.substr(i)
                scope = self.view.scope_name(i)
                # Skip preprocessors, strings, characaters and comments
                if 'string.quoted' in scope or 'comment' in scope \
                   or 'preprocessor' in scope:
                    extent = self.view.extract_scope(i)
                    i = extent.a - 1
                    continue
                else:
                    i -= 1

                if ch == '}':
                    indent_count -= 1
                elif ch == '{':
                    indent_count += 1
            return indent_count

        regions = []
        for sel in self.view.sel():
            start = get_line_indentation_pos(min(sel.a, sel.b))
            region = sublime.Region(
                self.view.line(start).a,
                self.view.line(max(sel.a, sel.b)).b)
            indent_count = get_indentation_count(start)
            # HACK: Add braces for indentation
            code = '{' * indent_count
            if indent_count > 0:
                code += '\n'
            code += self.view.substr(region)
            formatted_code = self.beautify(code)
            if indent_count > 0:
                for _ in range(indent_count):
                    index = formatted_code.find('{') + 1
                    formatted_code = formatted_code[index:]
                formatted_code = re.sub(r'[ \t]*\n([^\r\n])', r'\1',
                                        formatted_code, 1)
            else:
                # HACK: While no identation a '{' will generate a blank line so
                # strip it
                search = "\n{"
                if search not in code:
                    formatted_code = formatted_code.replace(search, '{', 1)
            self.view.replace(edit, region, formatted_code)
            if sel.a <= sel.b:
                regions.append(sublime.Region(region.a,
                                              region.a + len(formatted_code)))
            else:
                regions.append(sublime.Region(region.a + len(formatted_code),
                                              region.a))
        self.view.sel().clear()
        [self.view.sel().add(region) for region in regions]
