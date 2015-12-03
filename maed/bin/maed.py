#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check a MATH-ED program.
"""
__version__ = '0.9.0'
__author__ = 'Jim Hefferon'
__license__ = 'GPL 3'
TODO = []

import sys, os, os.path, re, pprint, argparse, traceback, time

import csv # read the course data

import cgi
import cgitb
cgitb.enable()

import datetime  # determine year 
THISYEAR = datetime.date.today().year

# Global variables spare me from putting them in the call of each fcn.
VERBOSE = False
DEBUG = False

class maedException(Exception):
    pass


def warn(s):
    t = 'WARNING: '+s+"\n"
    sys.stderr.write(t)
    sys.stderr.flush()

def error(s):
    t = 'ERROR! '+s
    sys.stderr.write(t)
    sys.stderr.flush()
    sys.exit(10)


SEMESTERS = ["BEFORE", 
             "ONE_FALL", "ONE_SPRING", "ONE_SUMMER",
             "TWO_FALL", "TWO_SPRING", "TWO_SUMMER",
             "THREE_FALL", "THREE_SPRING", "THREE_SUMMER",
             "FOUR_FALL", "FOUR_SPRING", 
             "AFTER"]

# .. and an English version
SEMESTERS_LONG = {"BEFORE": "Transfered in", 
                  "ONE_FALL": "First year Fall", 
                  "ONE_SPRING": "First year Spring", 
                  "ONE_SUMMER": "First year Summer",
                  "TWO_FALL": "Second year Fall", 
                  "TWO_SPRING": "Second year Spring", 
                  "TWO_SUMMER": "Second year Summer",
                  "THREE_FALL": "Third year Fall", 
                  "THREE_SPRING": "Third year Spring", 
                  "THREE_SUMMER": "Third year Summer",
                  "FOUR_FALL": "Fourth year Fall", 
                  "FOUR_SPRING": "Fourth year Spring", 
                  "AFTER": "After SMC"}

CSS = """
  <STYLE> 
    h2 {color: blue;
        padding-top: 5ex;}
    h3 {color: #3131FA;
        padding-top: 3ex;}
    h4 {color: #3131FA;
        padding-top: 1.75ex;}
    th {color: #6D6D74}
    table td {padding-left: 1em}
    table.semester {padding-bottom: 1em}
    ol.errors {color: red}
    .course_table tr:nth-child(even) {background-color: #D9ECF2;}
    table.plans {
      border-collapse: collapse;
      border: 1px solid black;
    }
    table.plans td {
      border: 1px solid black;
      padding: 2px;
      padding-left: 5px;
      padding-right: 5px;
      }
    .right {
      position: absolute;
      right: 0px;
      width: 400px;
      border: none;
      padding: 10px;
    }
    .prereq {max-width: 75%;}
    </STYLE>
"""

SAMPLE_PLAN_INTRO = """<H3 id='sample_plans'>Sample Mathematics-Education plans</H3>
<P>
  Probably your plan will be a little different but these get you started.
  </P> 
"""

SAMPLE_EVEN="""
<h4>Secondary Education</h4>

<p>
  This person begins with MA&nbsp;150, Calculus&nbsp;I, and takes two Language
  courses.  
  </p>

<table class='plans'>
  <tr>
    <th></th>
    <th>Fall</th>
    <th>Spring</th>
    </tr>
  <tr>
    <td>First year, {firstyear}</td>
    <td>CS 111, MA 150, LSC, LSC (language)</td>
    <td>ED 231, MA 160, LSC, LSC (language)</td>
    </tr>
  <tr>
    <td>Sophmore, {sophmore}</td>
    <td>ED 361, MA 211, MA 213, LSC</td>
    <td>ED 271, MA 240, MA 251, LSC</td>
    </tr>
  <tr>
    <td>Junior, {junior}</td>
    <td>ED 343, MA 304, MA 401, LSC half course</td>
    <td>MA 381, MA 403, MA 410, LSC, other</td>
    </tr>
  <tr>
    <td>Senior, {senior}</td>
    <td>ED 370, MA 308, LSC, LSC</td>
    <td>ED 424, ED 430</td>
    </tr>
  </table>

<p>
  Note the substitution of MA&nbsp;381 for ED&nbsp;367 and ED&nbsp;423,
  and MA&nbsp;308 for ED&nbsp;450 (MA&nbsp;304 can also substitute for this).
  Any substitutions need to be discussed with your advisor and approved by the
  Department Chairs.
  Because of those substitutions, this person has one uncommitted
  slot, labelled &quot;other,&quot; where they could take another
  Mathematics course such as MA&nbsp;208, or a course in Computer Science
  such as CS&nbsp;211, or a natural science, or anything.
  </p>

<p>
  The next plan is for a person 
  who has taken Calculus&nbsp;I in high school and so starts
  with Calculus&nbsp;II. 
  They have also tested proficient at one of the two language classes, so they
  only have one left to go.
  </p>


<table class='plans'>
  <tr>
    <td>Transferred in</td>
    <td colspan='2'>MA 150, LSC (language)</td>
    </tr>
  <tr>
    <th></th>
    <th>Fall</th>
    <th>Spring</th>
    </tr>
  <tr>
    <td>First year, {firstyear}</td>
    <td>CS 111, MA 160, LSC, LSC (language)</td>
    <td>ED 231, MA 211, MA 251, LSC</td>
    </tr>
  <tr>
    <td>Sophmore, {sophmore}</td>
    <td>ED 361, MA 213, LSC, LSC</td>
    <td>ED 271, MA 240, MA 208, LSC</td>
    </tr>
  <tr>
    <td>Junior, {junior}</td>
    <td>ED 343, MA 304, MA 401, LSC</td>
    <td>MA 381, MA 403, MA 410, LSC half course, other</td>
    </tr>
  <tr>
    <td>Senior, {senior}</td>
    <td>ED 370, MA 308, LSC, other</td>
    <td>ED 424, ED 430</td>
    </tr>
  </table>

<p>
  Because this person started out with two courses already done, they
  have two free slots, labelled &quot;other&quot;.
  They can take additional Math courses, 
  or courses in Computer Science or a natural science, or whatever they like.
  </p>



<h4>Primary Education</h4>

<p>
  This person begins with MA&nbsp;150, Calculus&nbsp;I, and takes two Language
  courses.  
  </p>

<table class='plans'>
  <tr>
    <th></th>
    <th>Fall</th>
    <th>Spring</th>
    </tr>
  <tr>
    <td>First year, {firstyear}</td>
    <td>CS 111, MA150, LSC, LSC (language)</td>
    <td>ED 231, MA 160, LSC, LSC (language)</td>
    </tr>
  <tr>
    <td>Sophmore, {sophmore}</td>
    <td>ED 251, MA 211, MA 213, LSC</td>
    <td>ED 335, MA 240, MA 251, MA 381</td>
    </tr>
  <tr>
    <td>Junior, {junior}</td>
    <td>ED 300, ED 325, MA 304, LSC, LSC half course</td>
    <td>ED 339, ED 427, MA 208, MA 410, LSC</td>
    </tr>
  <tr>
    <td>Senior, {senior}</td>
    <td>ED 340, MA 308, LSC, LSC</td>
    <td>ED 428, ED 475</td>
    </tr>
  </table>

<p>
  Note that ED&nbsp;325 is substituted for MA&nbsp;401, 
  and ED&nbsp;421 is substituted for the additional 400's level
  Math class.
  Any substitutions need to be discussed with your advisor and approved by the
  Department Chairs.
  </p>
"""

SAMPLE_ODD = """
<h4>Secondary Education</h4>

<p>
  This person begins with MA&nbsp;150, Calculus&nbsp;I, and takes two Language
  courses.  
  </p>

<table class='plans'>
  <tr>
    <th></th>
    <th>Fall</th>
    <th>Spring</th>
    </tr>
  <tr>
    <td>First year, {firstyear}</td>
    <td>CS 111, MA 150, LSC, LSC (language)</td>
    <td>ED 231, MA 160, LSC, LSC (language)</td>
    </tr>
  <tr>
    <td>Sophmore, {sophmore}</td>
    <td>ED 271, ED 361, MA 211, MA 213</td>
    <td>MA 240, MA 251, LSC, LSC</td>
    </tr>
  <tr>
    <td>Junior, {junior}</td>
    <td>ED 343, MA 308, MA 401, LSC half course</td>
    <td>MA 381, MA 403, MA 410, LSC, other</td>
    </tr>
  <tr>
    <td>Senior, {senior}</td>
    <td>ED 370, MA 304, LSC, LSC</td>
    <td>ED 424, ED 430</td>
    </tr>
  </table>

<p>
  Note the substitution of MA&nbsp;381 for ED&nbsp;367 and ED&nbsp;423,
  and MA&nbsp;308 for ED&nbsp;450 (MA&nbsp;304 can also substitute for this).
  Any substitutions need to be discussed with your advisor and approved by the
  Department Chairs.
  Because of those substitutions, this person has one uncommitted
  slot, labelled &quot;other,&quot; where they could take another
  Mathematics course such as MA&nbsp;208, or a course in Computer Science
  such as CS&nbsp;211, or a natural science, or anything.
  </p>

<p>
  The next plan is for a person 
  who has taken Calculus&nbsp;I in high school and so starts
  with Calculus&nbsp;II. 
  They have also tested proficient at one of the two language classes, so they
  only have one left to go.
  </p>


<table class='plans'>
  <tr>
    <td>Transferred in</td>
    <td colspan='2'>MA 150, LSC (language)</td>
    </tr>
  <tr>
    <th></th>
    <th>Fall</th>
    <th>Spring</th>
    </tr>
  <tr>
    <td>First year, {firstyear}</td>
    <td>CS 111, MA 160, LSC, LSC (language)</td>
    <td>ED 231, MA 211, MA 251, LSC</td>
    </tr>
  <tr>
    <td>Sophmore, {sophmore}</td>
    <td>ED 271, ED 361, MA 213, LSC</td>
    <td>MA 240, MA 208, LSC, LSC</td>
    </tr>
  <tr>
    <td>Junior, {junior}</td>
    <td>ED 343, MA 308, MA 401, LSC</td>
    <td>MA 381, MA 403, MA 410, LSC half course, other</td>
    </tr>
  <tr>
    <td>Senior, {senior}</td>
    <td>ED 370, MA 304, LSC, other</td>
    <td>ED 424, ED 430</td>
    </tr>
  </table>

<p>
  Because this person started out with two courses already done, they
  have two free slots, labelled &quot;other&quot;.
  They can take additional Math courses, 
  or courses in Computer Science or a natural science, or whatever they like.
  </p>



<h4>Primary Education</h4>

<p>
  This person begins with MA&nbsp;150, Calculus&nbsp;I, and takes two Language
  courses.  
  </p>

<table class='plans'>
  <tr>
    <th></th>
    <th>Fall</th>
    <th>Spring</th>
    </tr>
  <tr>
    <td>First year, {firstyear}</td>
    <td>CS 111, MA150, LSC, LSC (language)</td>
    <td>ED 231, MA 160, LSC, LSC (language)</td>
    </tr>
  <tr>
    <td>Sophmore, {sophmore}</td>
    <td>ED 251, MA 211, MA 213, LSC</td>
    <td>ED 335, MA 240, MA 251, MA 381</td>
    </tr>
  <tr>
    <td>Junior, {junior}</td>
    <td>ED 300, ED 325, MA 308, LSC, LSC half course</td>
    <td>ED 339, ED 427, MA 208, MA 410, LSC</td>
    </tr>
  <tr>
    <td>Senior, {senior}</td>
    <td>ED 340, MA 304, LSC, LSC</td>
    <td>ED 428, ED 475</td>
    </tr>
  </table>

<p>
  Note that ED&nbsp;325 is substituted forfor MA&nbsp;401, 
  and ED&nbsp;421 is substituted for the additional 400's level
  Math class.
  Any substitutions need to be discussed with your advisor and approved by the
  Department Chairs.
  </p>
"""

MAJOR_REQUIREMENTS = """
<h3>Major requirements</h3>

<h4>Mathematics</h4>

<ul>
  <li>MA&nbsp;150,
    MA&nbsp;160, and MA&nbsp;211
    </li>
  <li>
     Computer Science&nbsp;111
    </li>
  <li>
    MA&nbsp;213, MA&nbsp;240, and MA&nbsp;251
    </li>
  <li>
    Two additional math courses numbered 200 or above.
    </li>
  <li>
    MA&nbsp;410, and also a mathematics Topics course numbered
    300 or above, such as MA&nbsp;381 (half course). 
    </li>
  <li>
    Either MA&nbsp;401 or MA&nbsp;403.
    </li>
  <li>
    One additional math course numbered 400 or above.
    </li>
  </ul>

<P>
  This digraph gives the prerequisite structure of the Math program.
  </P>  
  <IMG src='/math.png' alt='Mathematics prerequisite structure' style='width: 5in'>

<h4>Elementary Education</h4>

<ul>
  <li>ED&nbsp;231 and ED&nbsp;251
    </li>
  <li>ED&nbsp;300, ED&nbsp;325, and ED&nbsp;335 
    </li>
  <li>ED&nbsp;339, and ED&nbsp;340
    </li>
  <li>ED&nbsp;427 (half course)
    </li>
  <li>Student teaching consists of the two  courses ED&nbsp;428
    and ED&nbsp;475
  </ul>


<h4>Secondary Education</h3>

<ul>
  <li>ED&nbsp;231 and ED&nbsp;271
    </li>
  <li>ED&nbsp;343, ED&nbsp;361, and ED&nbsp;370
    </li>
  <li>ED&nbsp;367
    </li>
  <li>ED&nbsp;423 (half course)
    </li>
  <li>ED&nbsp;450
    </li>
  <li>Student teaching consists of the two  courses ED&nbsp;428 
    and ED&nbsp;475
  </ul>
"""
# <P>This is the Education's prerequisite structure.</P>  
# <IMG src='/ed.png' alt='Education prerequisite structure' style='width: 100%'>

COURSES_OFFERED = """
<H3>When courses are offered</H3>
<P>
  Many courses are offered every semester.
  But some are only offered every other semester, and some every other year.
  For the Math and Education courses that are not offered
  every semester, these tables give the schedule.
  Exceptions happen but this is the usual pattern.
  </p>

<P>
  First, the Math list.
  &quot;Even academic year&quot; means that the Fall semester of that
  Fall-Spring academic year is in an even-numbered year. 
  </P>

<table class='plans'>
  <tr>
    <th></th>
    <th>Fall</th>
    <th>Spring</th>
    </tr>
  <tr>
    <td>Even academic year</td>
    <td>MA 213, MA 304, MA 380, MA 401, MA 451</td>
    <td>MA 208, MA 240, MA 251, MA 303, MA 315, MA 381, MA 403, MA 410</td>
    </tr>
  <tr>
    <td>Odd academic year</td>
    <td>MA 213, MA 308, MA 351, MA 380, MA 406 </td>
    <td>MA 208, MA 217, MA 240, MA 251, MA 303, MA 305, MA 407, MA 410, MA 417</td>
    </tr>
  </table>

<p>
  This is the matching table for Education.
  These courses are offered every year so there is no distinction
  between even and odd academic years.
  </p>

<table class='plans'>
  <tr>
    <th></th>
    <th>Fall</th>
    <th>Spring</th>
    </tr>
  <tr>
    <td>Every year</td>
    <td>ED 343, ED 361, ED 365, ED 367, ED 370</td>
    <td>ED 271, ED 421, ED 424, ED 428, ED 430</td>
    </tr>
  </table>
"""


class course(object):
  def __init__(self, dept, num, name, credits, year_odd_fall, year_even_fall, fall, spring, notes, prerequisites=None, corequisites=None):
      self.dept = dept.upper()
      self.num = num
      self.catalogue = dept+"{0:03d}".format(num)
      self.name = name
      self.credits = credits
      self.year_odd_fall = year_odd_fall  # Offered in years with an odd fall?
      self.year_even_fall = year_even_fall #
      self.fall = fall    # Offered in fall? boolean
      self.spring = spring  # boolean
      self.notes = notes       # notes on the course; string or None
      # prerequisites and corequisites are sets of strings, that are catalogues
      self.prerequisites = set() 
      if not(prerequisites is None):
          for s in prerequisites.split():
              # print("!!! s=",s)
              self.prerequisites.add(s)
      self.corequisites = set() 
      if not(corequisites is None):
          for s in corequisites.split():
              self.corequisites.add(s)
  
  def __str__(self):
      return self.catalogue+": "+self.name

  def __repr__(self):
      s = "{catalogue}: {name}  Credits: {credits}\n  Years with odd fall? {year_odd_fall}  Even fall? {year_even_fall} Fall semester? {fall} Spring? {spring}\n  Prerequisites: {prereqs}\n  Notes: {notes}".format(catalogue=self.catalogue, name=self.name, credits=self.credits, year_odd_fall=self.year_odd_fall, year_even_fall=self.year_even_fall, fall=self.fall, spring=self.spring, prereqs=" ".join([x for x in self.prerequisites]), notes=self.notes)
      return s

  def check_prequisite_courses(self, prior_courses, current_courses):
      """Check that the prerequisites are among the prior courses
        prior_courses  set of catalogue designations
        current_courses  set of catalogue designations
      """
      r = []
      for c in self.corequisites:
          if not c in prior_courses | current_courses:
              r.append("Pre- or co-requisite not met: before you take "+self.catalogue+" you must take "+c+" (or you can take them at the same time).")
      for c in self.prerequisites:
          if not c in prior_courses:
              r.append("Prerequisite not met: before you take "+self.catalogue+" you must take "+c+".")
      return r

  def check_semester(self, fall_odd, fall_sem):
      """Check that this course is offered in this semester
        fall_odd  boolean  Is this a year with an odd fall?
        fall  boolean  Is this a fall semester?
      """
      r = []
      if fall_odd:
          if not(self.year_odd_fall):
              r.append('This course is not offered in years with an odd fall')
      else:
          if not(self.year_even_fall):
              r.append('This course is not offered in years with an even fall')
      if fall_sem:
          if not(self.fall):
              r.append('This course is not offered in the all')
      else:
          if not(self.spring):
              r.append('This course is not offered in the spring')
      

class semester(object):
    """A semester is a set of courses
    """
    def __init__(self, year_fall, fall, spring):
        self.year_fall = year_fall  # Year in which Fall semester happens
        self.fall = fall  
        self.spring = spring
        if fall and spring:
            raise maedException("Internal error: a semester is both Fall and Spring.")
        self.courses = set()
        
    def __str__(self):
        if self.fall:
            return "Fall "+self.year_fall
        elif self.spring:
            return "Spring "+self.year_fall+1
        else:
            return "Summer "+self.year_fall+1

    def __repr__(self):
        return self._str__()

    def is_summer(self):
        return not(self.fall) and not(self.spring)

    def test_credits(self):
        """Check that the number of credits is not too large.
        """
        r = []
        credits = 0
        for c in self.courses:
            credits = credits + c.credits
        if self.is_summer():
            if credits > 8:
                r.append(self.__str__()+" has more than eight credits.")
        else:
            if credits > 18:
                r.append(self.__str__()+" has more than eighteen credits.")


class student_semester(object):
    """A student's choices for a semester
    """
    def __init__(self, semester):
        if semester not in SEMESTERS:
            raise maedException("INTERNAL ERROR: No such semester")
        self.semester = semester
        self.courses = []  # list of course designations
        
    def __str__(self):
        r = [self.semester+":"]
        for c in courses:
            r.append(" "+c.catalogue)
        return "".join(r)

    def __repr__(self):
        return self._str__()

    def add_course(self, c):
        self.courses.append(c)

    def compute_credits(self, courses):
        """Compute how many credits the student is taking this semester.
        courses  dictionary  catalogue_designation_string -> course instance
        """
        total = 0
        for c in self.courses:
            try:
                total += courses[c].credits
            except:
                raise maedException('Unable to total credits in semester '+self.semester)
        return total


def bool_read(s):
    if s.strip().upper()[0] == 'False'.upper()[0]:
        return(False)
    else:
        return(True)

def read_coursefile(fn = "maed.csv"):
    d = {}
    with open(fn, newline='') as csvfile:
        coursefilereader = csv.reader(csvfile, quoting=csv.QUOTE_MINIMAL)
        for row in coursefilereader:
            dept = row[0]
            if dept[0]=='#':  # comment line
                continue
            num = int(row[1])
            name = row[2] 
            credits = int(row[3]) 
            year_odd_fall = bool_read(row[4]) 
            year_even_fall = bool_read(row[5])
            fall = bool_read(row[6]) 
            spring = bool_read(row[7]) 
            notes = row[8].strip()
            prerequisites = row[9].strip()
            corequisites = row[10].strip()
            c = course(dept, num, name, credits, year_odd_fall, year_even_fall, fall, spring, notes, prerequisites, corequisites)
            d[c.catalogue] = c
    return d

def make_program(program='secondary'):
    """Make the select widget for the program.
    program  string  one of 'primary', 'secondary'
    """
    r=["<SELECT name='program'>\n"]
    if program=='primary':
        s = ' SELECTED'
    else:
        s=''
    r.append("  <OPTION value='primary'{s}>Primary Education</OPTION>\n".format(s=s))
    if program=='secondary':
        s = ' SELECTED'
    else:
        s=''
    r.append("  <OPTION value='secondary'{s}>Secondary Education</OPTION>\n".format(s=s))
    r.append("  </SELECT>")
    return ''.join(r)

def find_this_academic_year():
    """Determine what academic year this is (so in Jan, it is the prior year).
    """
    d = datetime.date.today()
    thisyear, thismonth = d.year, d.month
    if d.month <= 2:
        return thisyear - 1
    else:
        return thisyear

def make_year(selected=THISYEAR):
    """Make academic year select widget.
    selected integer  Academic year to be pre-selected.
    """
    r = ["<SELECT name='catalogue_year'>\n"]
    academic_year = find_this_academic_year()
    for y in range(academic_year-4, academic_year+1):
        if selected == y:
            s = ' selected'
        else:
            s = ''
        r.append("  <OPTION value='{y}'{s}>{y}</OPTION>\n".format(y=str(y), s=s))
    r.append("  </SELECT>\n")
    return "".join(r)

def _make_select_tag(name, courses, catalogue_designations, selected_course):
    """Return as a string the <SELECT name='name'> .. tag
    name  string  HTML name of the tag
    courses  dictionary catalogue_designation -> course instance
    catalogue_designations  list of strings  ordered list
    selected_course  string or None catalogue designation of course selected
    """
    r=["<SELECT name='",
       name,
       "'>\n"]
    if selected_course and selected_course in catalogue_designations:        
       r.append("  <OPTION value=''> </OPTION>\n")
    else:
       r.append("  <OPTION value='' SELECTED> </OPTION>\n")
    for cd in catalogue_designations:
        c = courses[cd]
        if selected_course==cd:
            s = ' SELECTED'
        else:
            s = ''
        r.append("  <OPTION value='{catalogue}'{s}>{catalogue} {name}</OPTION>\n".format(catalogue=c.catalogue, name=c.name, s=s))
    r.append("  </SELECT>\n")
    return "".join(r)

COURSE_CHOICES = 6
def make_html_semester(student_sem, courses):
    r=["<TABLE class='semester' name='{semester}'>\n".format(semester=student_sem.semester)]
    selected_courses = sorted(student_sem.courses)
    catalogue_designations = sorted(courses.keys())
    selected_courses = selected_courses+([None,]*COURSE_CHOICES) # pad list 
    for i in range(COURSE_CHOICES):
        r.append("  <TR><TD>\n")
        name = student_sem.semester
        selected_course = selected_courses[i]
        r.append("    "+_make_select_tag(name, courses, catalogue_designations, selected_course))
        r.append("    </TD></TR>\n")
    r.append("  </TABLE>\n")
    return ''.join(r)

def make_html_tables(courses, student):
    """Produce the HTML for the course selection tables
    courses  dictionary  catalogue_designation -> course
    student  dictionary  semester_name -> student_semester
    """
    r=["<TABLE name='student_choices'>\n"]
    r.append("  <TR>\n")
    r.append("  <TD>Transferred in</TD>\n")
    r.append("  <TD>\n")
    r.append("  "+make_html_semester(student[SEMESTERS[0]], courses))
    r.append("  </TD></TR>\n")
    r.append("  <TR><TH></TH> <TH>Fall</TH> <TH>Spring</TH> <TH>Summer</TH> </TR>\n")
    for y in ['ONE', 'TWO', 'THREE']:
        r.append("  <TR>\n")
        if y=='ONE':
            s='First year'
        elif y=='TWO':
            s='Second year'
        else:
            s='Third year'
        r.append("  <TD>"+s+"</TD>\n")
        for w in ['FALL', 'SPRING', 'SUMMER']:
            x = y+'_'+w
            r.append("    <TD>\n")
            student_sem = student[x]
            r.append("    "+make_html_semester(student_sem, courses))
            r.append("    </TD>\n")
        r.append("  </TR>\n")
    # year FOUR has no summer
    y = 'FOUR'
    r.append("  <TR>\n")
    r.append("  <TD>Fourth year</TD>\n")
    for w in ['FALL', 'SPRING']:
        x = y+'_'+w
        r.append("    <TD>\n")
        student_sem = student[x]
        r.append("    "+make_html_semester(student_sem, courses))
        r.append("    </TD>\n")
    r.append("  </TR>\n")
    # AFTER is different
    r.append("  <TR>\n")
    r.append("  <TD>After four</TD>\n")
    r.append("  <TD>\n")
    r.append("  "+make_html_semester(student[SEMESTERS[12]], courses))
    r.append("  </TD></TR>\n")
    r.append("  </TABLE>\n")
    return ''.join(r)

def _make_html_courses(courses,header,notes):
    """Make a table of courses
    """
    r=["<H4>{header}</H4>\n<P>{notes}</p>\n".format(header=header, notes=notes),
       "<TABLE class='course_table'>\n",
       "  <TR><TH>Catalogue</TH> <TH>Name</TH> <TH>Credits</TH> <TH>Notes</TH> <TH>Prerequisites</TH> </TR>\n"]
    catalogue_designators = sorted(courses.keys())
    for cd in catalogue_designators:
        c = courses[cd]
        r.append("  <TR>\n")
        r.append("    <TD>{cd}</TD> <TD>{name}</TD> <TD>{credits}</TD>\n".format(cd=cd, name=c.name, credits=str(c.credits)))
        # When offered and notes 
        s = ""
        if not(c.year_odd_fall):
            s += "Only offered in academic years where Fall semester is in an even year. "
        elif not(c.year_even_fall):
            s += "Only offered in academic years where Fall semester is in an odd year. "
        if not(c.fall):
            s += "Spring semester only. "
        elif not(c.spring):
            s += "Fall semester only. "
        s += c.notes
        r.append("    <TD>{s}</TD>\n".format(s=s))
        # Prerequisites and corequisites
        p = ', '.join(sorted(c.prerequisites))
        if c.prerequisites:
            cors = [p]  # corequisites
        else:
            cors = []
        for coreq in sorted(c.corequisites): 
            cors.append(coreq+ "&nbsp;(corequisite)")
        q = ', '.join(cors)
        r.append("    <TD>{q}</TD>".format(q=q))
        r.append("  </TR>\n")
    r.append("  </TR>\n")
    r.append("</TABLE>\n")
    return ''.join(r)

def make_html_courses(courses):
    """Generate a list of courses
    """
    r = []
    math_courses = {}
    ed_courses = {}
    other_courses = {}
    for c in courses:
        crse = courses[c]
        if crse.dept in ['MA','CS']:
            math_courses[crse.catalogue] = crse
        elif crse.dept in ['ED']:
            ed_courses[crse.catalogue] = crse
        else:
            other_courses[crse.catalogue] = crse
    r.append(_make_html_courses(math_courses,"Mathematics courses",""))
    r.append(_make_html_courses(ed_courses,"Education courses",""))
    r.append(_make_html_courses(other_courses,"Other courses",""))
    return ''.join(r)
    
def make_html(courses, student, year=THISYEAR, program='secondary', name='', submit=None, extra=""):
    """Produce the HTML page.
    """
    if name is None:
        name = ''
    r=["Content-type: text/html\n\n"]
    r.append("<HTML>\n")
    r.append("<HEAD><TITLE>SMC Math-Education plan</TITLE>\n")
    r.append(CSS)
    r.append("  </HEAD>\n\n")
    r.append("<BODY>\n")
    r.append("<H2>Your plan for a Math-Education double major</H2>\n")
    r.append("<P>This worksheet helps you develop a plan to major in Mathematics and Education.\n")
    r.append("Fill out the form fields.  <a href='#sample_plans'>This list of sample plans</a> will help you get started.  Then hit <I>Submit</I>.</P>\n")
    r.append("<P>Below the form will appear notes saying which of the many rules the entered plan does not meet.  Make some changes and hit <I>Submit</I> again.  You may take a few iterations.  When you are finished hit <I>Done</I> and you will get a summary, to print.  <B>This form does not save any data so to keep your work you must print the summary</B>.</P>\n")
    r.append("<FORM action='' method='post'>\n")
    r.append("<P>Select the year that were a First Year student: "+make_year(selected=year)+".\n")
    r.append(" Select your program: "+make_program(program)+".\n")
    r.append(" Enter your name: <input type='text' name='name' value='{name}'></P>\n".format(name=name))
    r.append(make_html_tables(courses,student))
    r.append("  <INPUT type='submit' name='submit' value='Submit'>\n")
    r.append("  <INPUT type='submit' name='submit' value='Done'>\n")
    r.append("</FORM>\n")
    if extra:
        r.append("<H3 class='errors'>Notes on this plan</H3>\n")
        r.append("<P>These are the possible issues that the computer has found with the above plan.</P>\n")
        r.append("<OL class='errors'>\n")
        for msg in extra:
            r.append("  <LI>"+msg+"</LI>\n")
        r.append("  </OL>")
        r.append("<P><I>About any waivers or substitutions:</I> you should discuss them with your advisor and they must be approved by the Department Chairs.</P>\n")
    # Include a reference list of courses
    # r.append("<HR>")
    r.append("<H2>Reference information</H2>\n")
    r.append(SAMPLE_PLAN_INTRO)
    firstyear, sophmore, junior, senior = year, year+1, year+2, year+3
    if (year % 2) == 0:
        r.append(SAMPLE_EVEN.format(firstyear=firstyear, sophmore=sophmore, junior=junior, senior=senior))
    else:
        r.append(SAMPLE_ODD.format(firstyear=firstyear, sophmore=sophmore, junior=junior, senior=senior))  
    r.append(MAJOR_REQUIREMENTS)
    r.append(COURSES_OFFERED)
    r.append("<H3>All courses</H3\n>")
    r.append(make_html_courses(courses))
    # Get out
    r.append("</BODY>\n")
    r.append("</HTML>")
    return "".join(r)

#------------------------------------
# Make the plain text saveable version
def make_plain(courses, student, year=THISYEAR, program='secondary', name=None, submit=None, extra=[]):
    """
    """
    r=["Content-type: text/plain\n\n"]
    r.append("Summary of Mathematics-Education {program} Program\n\n".format(program=program.capitalize()))
    if name:
        r.append("Name: "+name+"\n")
    else:
        r.append("Name: --no name given--\n")
    r.append("Date: {date}\n\n".format(date=datetime.datetime.now().strftime("%Y-%b-%d")))
    for sem in SEMESTERS[1:-1]:
        if sem in student:
            course_list = student[sem].courses
            if not(course_list):
                courses_this_sem = ' No courses'
            else:
                course_list.sort()
                courses_this_sem = ', '.join(course_list)
        else:
            courses_this_sem = ' --'
        r.append("{sem_long}: {c}\n".format(sem_long=SEMESTERS_LONG[sem], c=courses_this_sem))
    # Messages
    if extra:
        r.append("\n\nMessages about this program\n")
        r.append("===========================\n")
        dex = 1
        for msg in extra:
            r.append("  "+str(dex)+") "+msg+"\n")
            dex += 1
    return ''.join(r)


# -------------------------------------
# Parse returned results
def parse_data():
    form = cgi.FieldStorage()
    program = form.getfirst('program','secondary')
    year = int(form.getfirst('catalogue_year', THISYEAR))
    name = form.getfirst('name','')
    submit = form.getfirst('submit',None)
    # Student's program data
    student = {}  # map semester -> student_semester
    for s in SEMESTERS:
        student[s] = student_semester(s)
        course_list = form.getlist(s)
        if course_list:
            for c in course_list:
                d = c.strip()
                if d:
                    student[s].add_course(d)
    return student, year, program, name, submit

# -------------------------------------
# Test the results
def total_credits(student, courses):
    total = 0
    for sem in SEMESTERS:
        if sem in student:
            total += student[sem].compute_credits(courses)
    return total

def credits_test(student, courses):
    """Test that the student will have the number of credits needed to graduate.
    Return a list of strings.
    """
    r = []
    creds = total_credits(student, courses)
    if creds < 128:
        r.append("Number of credits={creds} is less than the 128 required to graduate.".format(creds=str(creds)))
    return r

def credits_per_semester_test(student, courses):
    """Test that each semester does not have too many or too few credits.
    Return a list of strings 
    """
    r = []
    s = "Problem with the number of credits in a semester: "
    for sem in SEMESTERS[1:-1]:
        if sem in student:
            courses_this_sem = student[sem].courses
            credits_this_sem = 0
            for c in courses_this_sem:
                credits_this_sem += courses[c].credits 
            if credits_this_sem == 0:
                pass
            elif ((credits_this_sem < 12)
                  and (sem.endswith('FALL') or sem.endswith('SPRING'))):
                r.append(s+"with only "+str(credits_this_sem)+" credits in "+SEMESTERS_LONG[sem]+" semester you may have trouble with financial aid because full time requires 12 credits.")
            elif ((credits_this_sem > 18)
                  and (sem.endswith('FALL') or sem.endswith('SPRING'))):
                r.append(s+"you cannot take "+str(credits_this_sem)+" credits in "+SEMESTERS_LONG[sem]+" semester because the maximum is 18.")
    return r

def prerequisites_test(student, courses):
    """Test that the courses are arranged so their prerequisites and 
    corequisites are satisfied.  Return a list of strings 
    """
    r = []
    courses_so_far = set()
    for sem in SEMESTERS:
        if sem in student:
            courses_this_sem = set(student[sem].courses)
            for c in courses_this_sem:
                r += courses[c].check_prequisite_courses(courses_so_far,courses_this_sem)
            courses_so_far |= courses_this_sem
    return r

def lsc_test(student, courses):
    """Test that there are enough LSC's.  Return a list of strings 
    """
    r = []
    lsc_four_credit_total = 0
    lsc_two_credit_total = 0
    for sem in SEMESTERS:
        if sem in student:
            courses_this_sem = student[sem].courses
            for c in courses_this_sem:
                if c == 'LSC004':
                    lsc_four_credit_total += 1
                if c == 'LSC002':
                    lsc_two_credit_total += 1
    if lsc_four_credit_total < 9:
        r.append("You have "+str(lsc_four_credit_total)+" LSC full courses but you need to list nine of them.")
    if lsc_two_credit_total < 1:
        r.append("You don't have any LSC half courses but you need to list one for the arts requirement.")
    return r

def get_all_courses(student,courses):
    """Return a set of the catalogue description strings of all the 
    courses in the program.  Note that it returns a set, not a list.
    """
    courses_so_far = set()
    for sem in SEMESTERS:
        if sem in student:
            courses_this_sem = set(student[sem].courses)
            courses_so_far |= courses_this_sem
    return courses_so_far

def math_requirements_test(student, courses, program):
    """Check that the math requirements have been met.  Return a list of error
    strings.
    """
    r = []
    s = "Mathematics major requirement not met: "
    all_courses = get_all_courses(student,courses)
    # MA 150
    c = 'MA150'
    if not(c) in all_courses:
        r.append(s+"you must take "+c+".  If you transfered it into SMC then enter it into the first set of selections.")
    all_courses.discard(c)
    # Other required courses
    for c in ['CS111', 'MA160', 'MA211', 'MA213', 'MA240']:
        if not(c) in all_courses:
            r.append(s+"you must take "+c+".")
        all_courses.discard(c)
    # MA381 or MA380
    c1, c2 = 'MA381', 'MA380'
    if (not(c1 in all_courses)
        and not(c2 in all_courses)):
        r.append(s+"you must take one of "+c1+" or "+c2+".")
    all_courses.discard(c1)
    all_courses.discard(c2)
    # MA 401 or MA 406
    c1, c2 = 'MA401', 'MA406'
    if (not(c1 in all_courses)
        and not(c2 in all_courses)):
        if program=='primary':            
            r.append(s+"you must take one of "+c1+" or "+c2+" (unless it is waived, with a substitute of ED421).")
        else:
            r.append(s+"you must take one of "+c1+" or "+c2+".")
    if c1 in all_courses:
        all_courses.discard(c1)
    elif c2 in all_courses:
        all_courses.discard(c2)
    # MA410
    c = 'MA410'
    if not(c) in all_courses:
        r.append(s+"you must take "+c+" (unless it is waived, with a substitute of ED427).")
    all_courses.discard(c)
    # One more course numbered 400+
    found, c400 = False, None
    for c in all_courses:
        if c[:3]=='MA4':
            found, c400 = True, c
            break
    if not(found):
        r.append(s+"you must take an additional 400-level class.")
    if not(c400 is None):
        all_courses.discard(c400)
    # Two more courses numbered 200+
    c1, c2 = None, None
    for c in all_courses:
        prefix = c[:3]
        if prefix in ['MA2', 'MA3', 'MA4']:
            if c1 is None:
                c1 = c
            else:
                c2 = c
    if c1 is None:
        r.append(s+"you must take two additional classes numbered 200 or above.")
    elif c2 is None:
        r.append(s+"you must take an additional classes numbered 200 or above.")
    if not(c1 is None):
        all_courses.discard(c1)
    if not(c2 is None):
        all_courses.discard(c2)
    # Return the list of error strings
    return r

def ed_requirements_test(student, courses, program):
    """Check that the ed requirements have been met.  Return a list of error
    strings.
    """
    r = []
    s = "Education major requirement not met: " 
    all_courses = get_all_courses(student,courses)
    if program=='primary':
        # Required courses
        for c in ['ED231', 'ED251', 'ED300', 'ED325', 'ED335', 'ED339', 'ED340', 'ED427']:
            if not(c) in all_courses:
                r.append(s+"you must take "+c+".")
            all_courses.discard(c)
    else:  # program is 'secondary'
        # Required courses
        for c in ['ED231', 'ED271', 'ED343', 'ED361', 'ED370', 'ED423']:
            if not(c) in all_courses:
                r.append(s+"you must take "+c+".")
            all_courses.discard(c)
        # ED367
        c = 'ED367'
        if not(c) in all_courses:
            if 'MA381' in all_courses:
                r.append(s+"you must take "+c+", unless you get permission to substitute MA381.")
            else:
                r.append(s+"you must take "+c+", although if you take MA381 you may be allowed to substitute that course for this one.")
        all_courses.discard(c)
        # ED450
        c = 'ED450'
        if not(c) in all_courses:
            if (('MA304' in all_courses)
                or ('MA308' in all_courses)):
                r.append(s+"you must take "+c+", unless you have permission to substitute MA304 or MA308 for it.")
            else:
                r.append(s+"you must take "+c+", although if you take MA304 or MA308 you may be allowed to substitute that course for this one.")
        all_courses.discard(c)
    # ED 428 and ED 475
    c1, c2 = 'ED428', 'ED475'
    these_two = {c1, c2}
    if not(c1 in all_courses):
        r.append(s+"you must take "+c1+" along with "+c2+", and you must take those two in the same semester, and they must be the only two courses that you take in that semester.")
    elif not(c2 in all_courses):
        r.append(s+"besides "+c1+" you must also take "+c2+", and you must take them in the same semester, and they must be the only two courses that you take in that semester.")
    for sem in SEMESTERS:
        if sem in student:
            semester_courses = student[sem].courses  # set of cat designations of courses
            if ((c1 in semester_courses)
                or (c2 in semester_courses)):
                if not set(semester_courses) == these_two:
                    r.append(s+"you must take "+c1+" and "+c2+" in the same semester, and those can be the only courses that you take in that semester.")
            if c1 in semester_courses:
                all_courses.discard(c1)
            if c2 in semester_courses:
                all_courses.discard(c2)
    return r

def semester_offered_test(student, courses, year):
    """Check that the courses are offered in the semester they are being
    listed.
    """
    r = []
    s = "Problem with the semester or year that you've chosen a course: "
    # Find which progam semesters have a Fall with an even-numbered year
    odd, even = set(), set() 
    for sem in SEMESTERS:
        prefix = sem[:3]
        if prefix in ['ONE', 'THR']:
            if (year % 2) == 0:
                even.add(sem)
            else:
                odd.add(sem)
        elif prefix in ['TWO', 'FOU']: 
            if (year % 2) == 0:
                odd.add(sem)
            else:
                even.add(sem)
    # print("odd is",str(odd))
    # Go through the semesters and see if the courses are offered then.
    for sem in SEMESTERS:
        if sem in student:
            semester_courses = student[sem].courses  # set of cat designations of courses
            # r.append("semester_courses is "+str(semester_courses))
            for c in semester_courses:
                course_instance = courses[c]
                # r.append("  course_instance is "+str(course_instance))
                # r.append("  course_instance.fall is "+str(course_instance.fall))
                if ((sem in odd)
                    and not(course_instance.year_odd_fall)):
                    r.append(s+c+" is not given in odd-numbered years.")
                if ((sem in even)
                    and not(course_instance.year_even_fall)):
                    r.append(s+c+" is not given in even-numbered years.")
                if ((sem.endswith('FALL'))
                    and not(course_instance.fall)):
                    r.append(s+c+" is not given in the Fall semester.")
                if ((sem.endswith('SPRING'))
                    and not(course_instance.spring)):
                    r.append(s+c+" is not given in the Spring semester.")
    return r

def requirements_test(student, year, program, submit, courses):
    r = []
    r += prerequisites_test(student, courses)
    r += math_requirements_test(student, courses, program)
    r += ed_requirements_test(student, courses, program)    
    r += semester_offered_test(student, courses, year)
    r += credits_per_semester_test(student, courses)    
    r += lsc_test(student, courses)
    r += credits_test(student, courses)
    return r

#==================================================================
def main(args):
    courses = read_coursefile()
    # for c in courses:
    #     print(repr(courses[c]))
    # catalogue_designations = sorted(courses.keys())
    # print(_make_select_tag('BEFORE',courses,catalogue_designations,'MA150'))
    # ss = student_semester('BEFORE')
    # print(make_html_semester(ss,courses))
    student, year, program, name, submit = parse_data()
    extra = requirements_test(student, year, program, submit, courses)
    # extra.append("value of submit is "+str(submit))
    if submit=='Done':
        print(make_plain(courses, student, year, program, name, submit, extra))
    else:
        print(make_html(courses, student, year, program, name, submit, extra))


#==================================================================
if __name__ == '__main__':
    main(None)
    # sys.exit(0)
    # try:
    #     start_time = time.time()
    #     parser = argparse.ArgumentParser(description=globals()['__doc__'])
    #     parser.add_argument('-v','--version', action='version', version='%(prog)s '+globals()['__version__'])
    #     parser.add_argument('-D', '--debug', action='store_true', default=False, help='run debugging code')
    #     parser.add_argument('-V', '--verbose', action='store_true', default=False, help='verbose output')
    #     args = parser.parse_args()
    #     args = vars(args)
    #     if ('debug' in args) and args['debug']: 
    #         DEBUG = True
    #     if ('verbose' in args) and args['verbose']: 
    #         VERBOSE = True
    #     main(args)
    #     if VERBOSE: 
    #         print('elapsed secs: {:.2f}'.format(time.time()-start_time))
    #     sys.exit(0)
    # except KeyboardInterrupt as e:   # Ctrl-C
    #     raise e
    # except SystemExit as e:   # sys.exit()
    #     raise e
    # except Exception as e:
    #     print('UNEXPECTED OUTCOME')
    #     print(str(e))
    #     traceback.print_exc()
    #     os._exit(1)
