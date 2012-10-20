import subprocess, os
import sublime, sublime_plugin

class RubyEvalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        input_str = ""
        for region in self.view.sel():
            input_str += self.view.substr(region) + "\n"

        if input_str != "":
            line_eval = False
        else:
            line_eval = True
            for region in self.view.sel():
                region_of_line = self.view.line(region)
                input_str += self.view.substr(region_of_line) + "\n"

        try:
            ruby = self.view.settings().get("ruby_eval").get("ruby")
        except AttributeError:
            ruby = "ruby"

        proc = subprocess.Popen(ruby,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,
                 stdin=subprocess.PIPE)

        output, error = proc.communicate("""
            result = (lambda {
                %s
            }).call
            print "#=> " + result.inspect
        """ % input_str)
        output = output.strip()

        if proc.poll():
            output += "\n" + error

        if line_eval == False:
            last_sel = self.view.sel()[-1]
            insert_pos = max(last_sel.a, last_sel.b)
        else:
            last_line = self.view.line(self.view.sel()[-1])
            insert_pos = last_line.b
            output = "\n" + output

        self.view.insert(edit, insert_pos, output)
