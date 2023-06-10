def task_test():
	return {
		'actions':['pytest test.py -v --disable-warnings'],
		'file_dep': ['test.py'],
		}

def task_html():
	return {
		'actions': ['sphinx-build -M html docs docs/_build'],
		}
		
def task_whl():
	return {
		'actions': ['python3 -m build -n -w'],
		'file_dep': ['pyproject.toml', 'src/en.ftl', 'src/ru.ftl'],
		'targets': ['dist/*.whl'],
		}
