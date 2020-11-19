""" Show a toggle which lets students mark things as done."""

from __future__ import absolute_import

import uuid

import six

from django.utils import translation
import pkg_resources
from xblock.core import XBlock
from xblock.fields import Boolean, DateTime, Float, Scope, String
from web_fragments.fragment import Fragment
from xblockutils.resources import ResourceLoader

_ = lambda text: text
loader = ResourceLoader(__name__)


def resource_string(path):
    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


@XBlock.needs('i18n')
class DoneWithAnswerXBlock(XBlock):
    """
    Show a toggle which lets students mark things as done.
    """

    description = String(
        scope=Scope.content,
        help=_("Problem description."),
        default=_("Default problem description")
    )

    done = Boolean(
        scope=Scope.user_state,
        help=_("Is the student done?"),
        default=False
    )

    feedback = String(
        scope=Scope.content,
        help=_("Feedback for student."),
        default=_("Default feedback")
    )

    button_name = String(
        scope=Scope.content,
        help=_("Button name."),
        default=_("Done")
    )

    has_score = True
    skip_flag = False

    display_name = String(
        default=_("Self-reflection question with feedback answer"), scope=Scope.settings,
        help=_("Display name")
    )

    def init_emulation(self):
        """
        Emulation of init function, for translation purpose.
        """
        if not self.skip_flag:
            i18n_ = self.runtime.service(self, "i18n").ugettext
            self.fields['display_name']._default = i18n_(self.fields['display_name']._default)
            self.skip_flag = True

    # pylint: disable=unused-argument
    @XBlock.json_handler
    def toggle_button(self, data, suffix=''):
        """
        Ajax call when the button is clicked. Input is a JSON dictionary
        with one boolean field: `done`. This will save this in the
        XBlock field, and then issue an appropriate grade.
        """
        if 'done' in data:
            self.done = data['done']
            if data['done']:
                grade = 1
            else:
                grade = 0
            grade_event = {'value': grade, 'max_value': 1}
            self.runtime.publish(self, 'grade', grade_event)
            # This should move to self.runtime.publish, once that pipeline
            # is finished for XBlocks.
            self.runtime.publish(self, "edx.done.toggled", {'done': self.done})

        return {'state': self.done}

    def student_view(self, context=None):  # pylint: disable=unused-argument
        """
        The primary view of the DoneXBlock, shown to students
        when viewing courses.
        """
        html_resource = resource_string("static/html/done.html")
        html = html_resource.format(done=self.done,
                                    feedback=self.feedback,
                                    description=self.description,
                                    button_name=self.button_name,
                                    id=uuid.uuid1(0))

        frag = Fragment(html)
        frag.add_css(resource_string("static/css/done.css"))
        frag.add_javascript(resource_string("static/js/src/done.js"))
        frag.initialize_js("DoneWithAnswerXBlock", {'state': self.done, 'button_name': self.button_name})
        return frag

    def studio_view(self, _context=None):  # pylint: disable=unused-argument
        '''
        Minimal view with no configuration options giving some help text.
        '''
        self.init_emulation()

        ctx = {
            'done': self.done,
            'feedback': self.feedback,
            'description': self.description,
            'button_name': self.button_name,
            'id': uuid.uuid1(0)
        }

        frag = Fragment()

        frag.add_content(loader.render_django_template(
            "static/html/studioview.html",
            context=ctx,
            i18n_service=self.runtime.service(self, "i18n"),
        ))

        frag.add_javascript(resource_string("static/js/src/studioview.js"))
        frag.initialize_js("DoneWithAnswerXBlockEdit")
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.description = data.get('description')
        self.feedback = data.get('feedback')
        self.button_name = data.get('button_name')

        return {'result': 'success'}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("DoneWithAnswerXBlock",
             """<vertical_demo>
                  <donewithanswer description="Click Mark as complete" button_name="Mark as complete" feedback="Good job!"> </donewithanswer>
                  <donewithanswer description="Think about Poland" button_name="Poland!" feedback="Well done!"> </donewithanswer>
                  <donewithanswer description="Pres Alt+F4" button_name="Alt+F4" feedback="Great!"> </donewithanswer>
                  <donewithanswer description="" feedback=""></donewithanswer>
                  <donewithanswer></donewithanswer>
                </vertical_demo>
             """),
        ]

    # Everything below is stolen from
    # https://github.com/edx/edx-ora2/blob/master/apps/openassessment/
    #        xblock/lms_mixin.py
    # It's needed to keep the LMS+Studio happy.
    # It should be included as a mixin.

    start = DateTime(
        default=None, scope=Scope.settings,
        help="ISO-8601 formatted string representing the start date "
             "of this assignment. We ignore this."
    )

    due = DateTime(
        default=None, scope=Scope.settings,
        help="ISO-8601 formatted string representing the due date "
             "of this assignment. We ignore this."
    )

    weight = Float(
        display_name="Problem Weight",
        help=("Defines the number of points each problem is worth. "
              "If the value is not set, the problem is worth the sum of the "
              "option point values."),
        values={"min": 0, "step": .1},
        scope=Scope.settings
    )

    def has_dynamic_children(self):
        """Do we dynamically determine our children? No, we don't have any.
        """
        return False

    def max_score(self):
        """The maximum raw score of our problem.
        """
        return 1
