from django import forms
import json
from django.utils.safestring import mark_safe
from django.forms import widgets, Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class JSONTableFormat(forms.Textarea):

    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        html = '<table border="1" style="border-collapse: collapse; width: 100%;">'
        html += '<tr><th>Key</th><th>Step Action</th><th>Step Data</th><th>Expected Result</th></tr>'

        if isinstance(value, dict):  # If JSON is a dictionary
            for key, val in value.items():
                step_action = val.get('step_action', None)
                step_data = val.get('step_data', None)
                expected_result = val.get('expected_result', None)
                html += f'<tr><td>{key}</td><td>{step_action}</td><td>{step_data}</td><td>{expected_result}</td></tr>'
        elif isinstance(value, list):  # If JSON is a list
            for item in value:
                html += f'<tr><td colspan="2">{item}</td></tr>'
        else:
            html += f'<tr><td colspan="2">{value}</td></tr>'

        html += '</table>'
        return mark_safe(html)  # Render HTML safely


class JsonTableWidget(widgets.Widget):

    template_name = 'table.html'

    def __init__(self, testcase_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.testcase_id = testcase_id

    def render(self, name, value, attrs, renderer=None):
        if attrs is None:
            attrs = {}
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass

        if isinstance(value, dict):
            steps = sorted(((int(step_number), step_data) for step_number, step_data in value.items()),
                           key=lambda x: x[0],
            )
        else:
            steps = []
        print(self.testcase_id)
        context = {'steps': steps, 'attrs': attrs, 'name': name, 'testcase_id': self.testcase_id}
        html = render_to_string(self.template_name, context)
        return mark_safe(html)