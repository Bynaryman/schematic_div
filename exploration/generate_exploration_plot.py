#!/usr/bin/env python
import argparse
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import sys

# Figure width base on the column width of the Latex document.
fig_width = 252
fig_text_width = 516

def set_size(width, fraction=1, subplots=(1, 1)):
    """

    :param width:
    :param fraction:
    :return:
    """
    # Width of figure (in pts)
    fig_width_pt = width * fraction

    # Convert from pt to inches.
    inches_per_pt = 1 / 72.27

    # Golden ration to set aesthetic figure height.
    # https://disq.us/p/2940ij3
    golden_ratio = (5 ** (1 / 2) - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    if width == fig_text_width:
        fig_height_in /= 0.8

    #fig_height_in /= 1.3

    fig_dim = (fig_width_in, fig_height_in)

    return fig_dim




# https://electronics.stackexchange.com/questions/564908/asic-gate-count-estimation-and-sram-vs-flip-flops
# https://en.wikipedia.org/wiki/Standard_cell

# TODO: the count has to be in transistors not in cells, as different cells have different sizes (area). In one tehnology
# in one technology library (made of standard cells) there is for instance, fast AND, slow AND
models = {
	"pessimistic": {
		"NOT": lambda n:3,
		"OR": lambda n: 2,
		"NOR": lambda n: 3,
		"NAND": lambda n: 4,
		"XOR": lambda n: 3,
		"XNOR": lambda n: 4,
		"HA": lambda n: 3 * n,
		"FA": lambda n: 4 * n,
		"DFF": lambda n: 6,
		"REG": lambda n: 6 * n,
		"MUX": lambda n: 4 * n
	},
	"optimistic": {
		"NOT": lambda n:1,
		"OR": lambda n: 1,
		"NOR": lambda n: 2,
		"NAND": lambda n: 3,
		"AND": lambda n: 4,
		"XOR": lambda n: 2,
		"XNOR": lambda n: 3,
		"HA": lambda n: 2 * n,
		"FA": lambda n: 3 * n,
		"DFF": lambda n: 4,
		"REG": lambda n: 4 * n,
		"MUX": lambda n: 3 * n
	},
	"average": {
		"NOT": lambda n:2,
		"OR": lambda n: 1.5,
		"NOR": lambda n: 2.5,
		"NAND": lambda n: 3.5,
		"AND": lambda n: 4,
		"XOR": lambda n: 2.5,
		"XNOR": lambda n: 3.5,
		"HA": lambda n: 2.5*n,
		"FA": lambda n: 3.5*n,
		"DFF": lambda n: 5,
		"REG": lambda n: 5 * n,
		"MUX": lambda n: 3.5 * n
	},
	"sky130_hd": {
		"NOT": lambda n:2,
		"OR": lambda n: 6,
		"NOR": lambda n: 8,
		"NAND": lambda n: 8,
		"AND": lambda n: 6,
		"XOR": lambda n: 10,
		"XNOR": lambda n: 10,
		"HA": lambda n: 14*n,
		"FA": lambda n: 28*n,
		"DFF": lambda n: 40,
		"REG": lambda n: 40 * n,
		"MUX": lambda n: 10 * n

	}
}

circuits = {
	"div_non_restoring_32b":
	{
		"latency": 32,
		"gates":
		{
			"NAND": {"number": 32, "args": [0]},
			"FA": {"number": 1, "args": [32]},
		}
	}
}


parametric_circuits = {
	"div_non_restoring_bit_serial_adder_2REG": lambda n_div, n_add:
	{
		"latency": n_div*(n_div//n_add),
		"gates":
		{
			"NOT": {"number": n_div+1, "args": [0]},
			"XOR": {"number": 1, "args": [0]},
			"MUX": {"number": 1, "args": [n_div]},
			"FA":  {"number": 1, "args": [n_add]},
			"REG": {"number": 2, "args": [n_div]},
		}
	},
	"div_non_restoring_bit_serial_adder_3REG": lambda n_div, n_add:
	{
		"latency": n_div*(n_div//n_add),
		"gates":
		{
			"NOT": {"number": n_div+1, "args": [0]},
			"XOR": {"number": 1, "args": [0]},
			"MUX": {"number": 1, "args": [n_div]},
			"FA":  {"number": 1, "args": [n_add]},
			"REG": {"number": 3, "args": [n_div]},
		}
	}
}

def transistor_count(circuit, cell_usage_model):
  transistor_count = 0
  for gate in circuit["gates"]:
	  transistor_count = transistor_count + (circuit["gates"][gate]["number"]* models[cell_usage_model][gate](*circuit["gates"][gate]["args"]))

  return transistor_count


def get_cli_args():
	args = {}
	return args

# add to axis the scatter point (latency,area) of circuit with a model of cells
def plot_latency_vs_area(circuit, cell_usage_model, axis, marker, color):
	latency = circuit["latency"]
	area = transistor_count(circuit, cell_usage_model)
	axis.scatter(area,latency,color=color,marker=marker, label=cell_usage_model)

def main():
	args = get_cli_args()

	# Some configs on matplotlib.
	tex_fonts = {
	    # Use Latex to write all text.
	    'text.usetex': True,
	    'font.family': 'serif',
	    # Use 10pt font in plots, to match 10pt font in document.
	    'axes.labelsize': 10,
	    'font.size': 10,
	    # Make the legend/label fonts a little smaller.
	    'legend.fontsize': 10.0,
	    'legend.handlelength': 2.25,
	    'legend.columnspacing': 0.5,
	    'xtick.labelsize': 8,
	    'ytick.labelsize': 8,
	    'hatch.linewidth': 0.3,
	    'lines.linewidth': 0.7,
	    'lines.markersize': 2.5,
	}

	plt.style.use('grayscale')
	plt.rcParams.update(tex_fonts)

	# setup some stuff about ploting
	fig = plt.figure(constrained_layout=True, figsize=set_size(fig_text_width), dpi=500)
	fig.tight_layout(pad=0)
	gs = GridSpec(2, 1, figure=fig)
	# Creating the axis.
	axis_fp64 = fig.add_subplot(gs[0])
	axis_fp64.margins(x=0, tight=True)
	#axis_fp64.set_xticks(range(n))
	#axis_fp64.set_xticklabels(range(n))
	axis_fp64.grid(color='grey', linestyle='--', linewidth=0.25, axis='y')
	axis_fp64.set_axisbelow(True)

	axis_fp32 = fig.add_subplot(gs[1])
	axis_fp32.margins(x=0, tight=True)
	#axis_fp32.set_xticks(range(n))
	#axis_fp32.set_xticklabels(range(n))
	axis_fp32.grid(color='grey', linestyle='--', linewidth=0.25, axis='y')
	axis_fp32.set_axisbelow(True)

	for c in circuits:
		for m in models:
			area = transistor_count(circuits[c], m)
			print(c, m, area)

	for c in parametric_circuits:
		for m in models:
			area = transistor_count(parametric_circuits[c](32,32), m)
			print(c, m, area)

	current_marker="d"
	for i in range(1,25):
		current_color="red"
		plot_latency_vs_area(parametric_circuits["div_non_restoring_bit_serial_adder_2REG"](32,i),"pessimistic",axis_fp32, current_marker, current_color)
		current_color="orange"
		plot_latency_vs_area(parametric_circuits["div_non_restoring_bit_serial_adder_2REG"](32,i),"average"    ,axis_fp32, current_marker, current_color)
		current_color="green"
		plot_latency_vs_area(parametric_circuits["div_non_restoring_bit_serial_adder_2REG"](32,i),"optimistic" ,axis_fp32, current_marker, current_color)
		current_color="blue"
		plot_latency_vs_area(parametric_circuits["div_non_restoring_bit_serial_adder_2REG"](32,i),"sky130_hd"  ,axis_fp32, current_marker, current_color)

	current_marker="s"
	for i in range(1,54):
		current_color="red"
		plot_latency_vs_area(parametric_circuits["div_non_restoring_bit_serial_adder_2REG"](53,i),"pessimistic",axis_fp64, current_marker, current_color)
		current_color="orange"
		plot_latency_vs_area(parametric_circuits["div_non_restoring_bit_serial_adder_2REG"](53,i),"average"    ,axis_fp64, current_marker, current_color)
		current_color="green"
		plot_latency_vs_area(parametric_circuits["div_non_restoring_bit_serial_adder_2REG"](53,i),"optimistic" ,axis_fp64, current_marker, current_color)
		current_color="blue"
		plot_latency_vs_area(parametric_circuits["div_non_restoring_bit_serial_adder_2REG"](53,i),"sky130_hd"  ,axis_fp64, current_marker, current_color)

	# close and save plotting
	axis_fp64.set_title(r'FP64')
	axis_fp32.set_title(r'FP32')
	handles, labels = plt.gca().get_legend_handles_labels()
	by_label = dict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys(),edgecolor='white', fancybox=False, framealpha=1.0, ncols=4)#, bbox_to_anchor=(0.5,1.7))
	fig.suptitle(r'Area vs. Latency of 1 FPDiv unit')
	fig.supxlabel(r'Area (Number of Transistors)')
	fig.supylabel(r'Latency (Number of clock cycles)')
	fig.savefig('area_vs_latency.svg', dpi='figure')
	plt.close(fig='all')


if __name__ == '__main__':
	main()
