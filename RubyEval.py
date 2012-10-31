import subprocess
import sublime, sublime_plugin

class RubyEvalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if region.a == region.b:
                # eval line
                region_of_line = self.view.line(region)
                script = self.view.substr(region_of_line)
                output = self.eval_as_ruby(script)
                self.view.insert(edit, region_of_line.b, "\n" + output)
                self.view.sel().subtract(region)
                self.view.sel().add(sublime.Region(region_of_line.b + 1, region_of_line.b + 1 + len(output)))
            else:
                # eval selected
                script = self.view.substr(region)
                output = self.eval_as_ruby(script)
                tail = max(region.a, region.b)
                self.view.insert(edit, tail, " " + output)
                self.view.sel().subtract(region)
                self.view.sel().add(sublime.Region(tail + 1, tail + 1 + len(output)))

    def ruby(self):
        try:
            return self.view.settings().get("ruby_eval").get("ruby")
        except AttributeError:
            return "ruby"

    def eval_as_ruby(self, script):
        proc = subprocess.Popen(self.ruby(),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE)

        ruby_input = u"""
            require 'stringio'

            io = StringIO.new
            begin
              $stdout = $stderr = io
              result = (lambda {
                %s
              }).call
            ensure
              $stdout = STDOUT
              $stderr = STDERR
            end

            if io.string.empty?
              case result
              when String
                print result
              else
                print result.inspect
              end
            else
              print io.string
            end
        """ % script

        output, error = proc.communicate(ruby_input.encode('utf-8'))
        output = output.strip()

        if proc.poll():
            output += "\n" + error

        return unicode(output ,encoding='utf-8')
