import os
import glob
import sys
from xml.sax.saxutils import escape

# Read the SVG file
with open("mario-1-1.svg", "r") as svg_file:
    svg = svg_file.read()

workdir = sys.argv[1]
inputs = glob.glob(os.path.join(workdir, "*"))

# with open("./uniq.log", "r") as fp:
#     lines = fp.readlines()
# inputs = [os.path.join("./outputs", line.strip()) for line in lines]

print(len(inputs))
paths = {}

# load all the paths' trace of coordinates
for input in inputs:
    with open(input, "r") as fp:
        lines = fp.readlines()
    lines = [
        tuple(map(float, line.strip().split(",")))
        for line in lines
        if line.strip()
        # and "," in line
    ]
    data = [(x, y) for x, y in lines if x!=0 and y!= 0]
    paths[input] = data

paths_list = []
# generate svg path element
for input in inputs:
    color = "#f8bf00"
    alpha = "0.2"
    data = paths[input]
    path_data = " ".join(f"L{x + 8} {y + 16}" for x, y in data)
    path_element = (
        f'<path fill="none" stroke="{color}" stroke-opacity="{alpha}" '
        f'stroke-width="3" d="M40 176{path_data}">'
        f'<title>{escape(input)}</title></path>'
    )
    paths_list.append(path_element)


print(len(paths_list))
# replace placeholder in SVG and write to file
content = svg.replace("{{PATHS}}", "\n".join(paths_list))
with open("test2.svg", "w") as output_file:
    output_file.write(content)
