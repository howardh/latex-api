import os
from flask import Flask, escape, request, send_file
from flask_cors import CORS

latex_template = """
\\documentclass{article}
%s
\\pagenumbering{gobble}
\\begin{document}
%s
\\end{document}
"""
def to_latex_doc(latex, imports_data):
    imports_latex = ''.join(['\\usepackage{%s}\n'%x for x in imports_data])
    return latex_template%(imports_latex,latex)

latex = 'Hello World'
imports_data = [
        'amsmath'
]
def create_svg(latex, imports_data=[], output_directory = './docs'):
    doc = to_latex_doc(latex,imports_data)

    file_name = hash(doc)
    tex_file_path = os.path.join(output_directory,'%s.tex'%file_name)
    dvi_file_path = os.path.join(output_directory,'%s.dvi'%file_name)
    svg_file_path = os.path.join(output_directory,'%s.svg'%file_name)

    with open(tex_file_path,'w') as f:
        f.write(doc)

    ret = os.system('pdflatex &latex -output-directory %s %s' % (output_directory,tex_file_path))
    if ret != 0:
        raise Exception('Something went wrong. Unable to compile LaTeX.')
    ret = os.system('dvisvgm -n --output=%s %s' % (svg_file_path,dvi_file_path))
    if ret != 0:
        raise Exception('Something went wrong. Unable to convert to SVG.')
    return svg_file_path

app = Flask(__name__)
CORS(app)

@app.route('/',methods=['GET'])
def foo():
    latex = request.args.get("l", "")
    imports_data = []
    output_file = create_svg(latex)
    return send_file(output_file, mimetype='image/svg+xml', attachment_filename='output.svg')

@app.route('/',methods=['POST'])
def bar():
    data = request.get_json()
    latex = data['latex']
    imports_data = data['imports']
    output_file = create_svg(latex)
    return send_file(output_file, mimetype='image/svg+xml', attachment_filename='output.svg')
