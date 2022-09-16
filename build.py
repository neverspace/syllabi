import os
import json
import functools

SYLLABIPATH = 'courses'
FACULTYPATH = 'img/faculty'
MAPPATH = 'map.json'
CSSPATH = 'css/styles.css'
JSPATH  = 'js/scripts.js'
FAVICON = 'favicon.ico'
TITLE   = 'Hunter CS Syllabi'
HEADING = 'Hunter College Computer Science Syllabi'

html = \
"""<!DOCTYPE html>
<html lang="en">

<head>
	<title>{title}</title>
	<meta charset="utf-8"/>
	<meta name="viewport" content="width=device-width, initial-scale=1"/>
	<link rel="stylesheet" href="{stylesheet}">
	<link rel="icon" href="{favicon}">
</head>

<body>
	<div id="main">
		<h1>{heading}</h1>
		{courses}
	</div>
	<script src="{script}"></script>
</body>
</html>"""

def chronological(pdfs):
	"""
	An input to this function may look like:
	  + pdf1: CS127_ligorio_syllabus_s20.pdf
	  + pdf2: CS127_stjohn_syllabus_f21.pdf

	We want to display PDFs in reverse chronological order (most recent
	at the top). We compare chronology using the year and season.
	"""
	def compare(pdf1, pdf2):
		try:
			pdf1_semester = getsemester(pdf1)
			pdf1_season   = pdf1_semester[0].upper()
			pdf1_year     = int(pdf1_semester[1:])

			pdf2_semester = getsemester(pdf2)
			pdf2_season   = pdf2_semester[0].upper()
			pdf2_year     = int(pdf2_semester[1:])
		except:
			return 0

		"""
		An easy way to represent the fact that the fall semester is later
		in the year than the spring semester, and should be sorted accordingly.
		"""
		if pdf1_season == 'F': pdf1_year += 0.5
		if pdf2_season == 'F': pdf2_year += 0.5

		return pdf2_year - pdf1_year

	return sorted(pdfs, key=functools.cmp_to_key(compare))

def getsemester(pdf):
	terms = pdf.split('_')
	if(len(terms) < 3): return
	return terms[-1][:-4] # remove .pdf suffix

def getprofessor(pdf):
	terms = pdf.split('_')
	if(len(terms) < 3): return
	return terms[-3]

def facultyicon(pdf):
	professor = getprofessor(pdf)
	if not professor:
		return

	path = FACULTYPATH + '/' + professor.lower() + '.jpg'
	if not os.path.exists(path):
		return

	return '<img src="{src}" alt="{alt}">'.format(src=path, alt=professor)

def prettycoursename(pdf):
	semester, professor = getsemester(pdf), getprofessor(pdf)
	if not semester or not professor:
		return pdf

	# our funny convention of representing multiple professors
	if '+' in professor:
		professor = professor.replace('+', ', ')

	return professor + ' (' + semester + ')'	

def prettycategoryname(category):
	return category.replace('-', ' ').title().replace('Cs', 'CS')

def generatehtml(htmlmap):
	category_html = '<details open class="{classname}">{summary}{courses}</details>'
	course_html   = '<details class="{classname}">{summary}{div}</details>'

	categories = []
	for category in htmlmap:

		courses = []
		for course in htmlmap[category]:

			bullets = []
			for pdf in htmlmap[category][course]['pdfs']:
				course_dir = SYLLABIPATH + '/' + course.replace(' ', '_')
				course_name = htmlmap[category][course]['course_name']
				a = '<a href="{url}">{value}</a>'.format(
					url = course_dir + '/' + pdf,
					value = prettycoursename(pdf)
				)
				icon = facultyicon(pdf)
				li = '<li>{bullet}</li>'.format(
					bullet = a if not icon else (icon + a)
				)
				bullets.append(li)

			courses.append(course_html.format(
				classname = 'courses',
				summary   = '<summary class="course-title">' + course_name + '</summary>',
				div       = '<div><ul>' + '\n'.join(bullets) + '</ul></div>'
			))

		categories.append(category_html.format(
			classname = 'category',
			summary   = '<summary class="category-title">' + prettycategoryname(category) + '</summary>',
			courses   = '\n'.join(courses)
		))

	return '\n'.join(categories)

def getcoursemap():
	with open(MAPPATH) as f:
		coursemap = json.loads(f.read())

	htmlmap = {}
	for category in coursemap:
		htmlmap[category] = {}

		for course_code in coursemap[category]:
			course_dir = SYLLABIPATH + '/' + course_code.replace(' ', '_')
			try: pdfs = os.listdir(course_dir)
			except FileNotFoundError:
				continue

			course_name = coursemap[category][course_code]
			htmlmap[category][course_code] = {
				'course_name': course_code + ': ' + course_name,
				'pdfs': chronological(pdfs)
			}

	return generatehtml(htmlmap)

html = html.format(
	title      = TITLE,
	stylesheet = CSSPATH,
	favicon    = FAVICON,
	script     = JSPATH,
	heading    = HEADING,	
	courses    = getcoursemap()
)

print(html)