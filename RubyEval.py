import subprocess, os
import sublime, sublime_plugin

class RubyEvalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        input_str = ''
        for region in self.view.sel():
            input_str += self.view.substr(region)

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
            puts '#=> ' + result.inspect
        """ % input_str)

        if proc.poll():
            output += "\n" + error

        self.view.insert(edit, self.view.sel()[-1].b, output.strip())
