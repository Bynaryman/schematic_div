#!/usr/bin/env python

from helpers import *
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


def xor(bit_a, bit_b):
	A1 = bit_a and (not bit_b)
	A2 = (not bit_a) and bit_b
	return int(A1 or A2)

def half_adder(bit_a, bit_b):
	return (xor(bit_a, bit_b), bit_a and bit_b)

def full_adder(bit_a, bit_b, carry=0):
	sum1, carry1 = half_adder(bit_a, bit_b)
	sum2, carry2 = half_adder(sum1, carry)
	return (sum2, carry1 or carry2)

def full_adder_n_bits_list(n, bits_a, bits_b, carry=0):
	sum_bits = []
	for i in range(n):
		sum_bit, carry = full_adder(bits_a[i], bits_b[i], carry)
		sum_bits.append(sum_bit)
	return (sum_bits, carry)

def full_adder_n_bits(n, bits_a, bits_b, carry=0):
	sum_bits = 0
	for i in range(n):
		bit_a = (bits_a >> i) & 1
		bit_b = (bits_b >> i) & 1
		sum_bit, carry = full_adder(bit_a, bit_b, carry)
		sum_bits |= (sum_bit << i)
	return (sum_bits, carry)


def binary_string_adder(bits_a, bits_b):
	carry = 0
	result = ''
	for i in range(len(bits_a)-1 , -1, -1):
		summ, carry = full_adder(int(bits_a[i]), int(bits_b[i]), carry)
		result += str(summ)
	result += str(carry)
	return result[::-1]


def main():

	# n-bit divisor / module parameter
	n = int(sys.argv[1])

	# setup some stuff about ploting
	fig = plt.figure(constrained_layout=True, figsize=set_size(fig_text_width), dpi=500)
	fig.tight_layout(pad=0)
	gs = GridSpec(1, 1, figure=fig)
	# Creating the axis.
	axis = fig.add_subplot(gs[:])
	axis.margins(x=0, tight=True)
	#axis.set_xticks(range(n))
	#axis.set_xticklabels(range(n))
	axis.grid(color='grey', linestyle='--', linewidth=0.25, axis='y')
	axis.set_axisbelow(True)



	# signal declaration
	divisor_reg  = HardwareRegister(n)
	dividend_reg = HardwareRegister(2*n)
	sign_divisor_ff = HardwareRegister(1)
	sign_dividend_ff = HardwareRegister(1)

	# output register
	quotient_reg = HardwareRegister(n)
	remainder_reg = HardwareRegister(n)
	quotient_reg.set(0)
	remainder_reg.set(0)

	# init state
	divisor_reg.set(int(sys.argv[3]))
	dividend_reg.set(int(sys.argv[2]))
	sign_divisor_ff.set(divisor_reg[n-1])
	sign_dividend_ff.set(dividend_reg[2*n-1])


	# plot values
	dividends = []

	# main loop
	for i in range(n): # n clock cycles

		print("clock cycle: ", i)

		# get the signs of the divisor and dividend
		sign_divisor = divisor_reg[n-1]
		sign_dividend = dividend_reg[2*n-1]

		print("   dividend: " + str(dividend_reg.get_as_list()))
		print("   dividend as bin: {0:08b}".format(dividend_reg.get()))
		print(dividend_reg.as_signed())
		print(dividend_reg.get())

		if (sign_dividend==0):
			print(((dividend_reg.get()>>n) & ((2**n)-1)))
		else:
			print(-((dividend_reg.get()>>n) & ((2**n)-1)))

		dividends.append(dividend_reg.as_signed())
		# left shift the dividend register
		#print(dividend_reg.as_signed()*2)
		dividend_reg.set(dividend_reg.get() << 1)
		dividends.append(dividend_reg.as_signed())

		# print signs
		print("   sign_divisor: " + str(sign_divisor))
		print("   sign_dividend: " + str(sign_dividend))

		# get the mathematical operation to do depending on the signs
		op_to_perform = sign_divisor ^ sign_dividend # xor: addition if 1, substraction if 0
		print("   op to perform: ", op_to_perform)

		# get the 1 complement of the divisor
		divisor_1_complement = ~divisor_reg.get() & ((2**n)-1)
		print("   divisor_1_complement: ", bin(divisor_1_complement))

		# get the adder operand depending on op_to_perform (MUX)
		if op_to_perform == 1:
			print("   addition")
			operand_b_adder = divisor_reg.get()
		else:
			operand_b_adder = divisor_1_complement
			print("   substraction")

		# n bit adder. todo verify if n+1 with signs is needed
		carry_in_adder = 1-op_to_perform
		print("   carry_in_adder: ", carry_in_adder)
		operand_a_adder = (dividend_reg.get()>>n) & ((2**n)-1) # get the n msb of the 2xdividend
		print("   operand_a_adder: ", bin(operand_a_adder))
		print("   operand_b_adder: ", bin(operand_b_adder))
		s_out, c_out = full_adder_n_bits(n, operand_a_adder, operand_b_adder, carry_in_adder)
		print("  s_out: ", bin(s_out))
		print("  c_out: ", bin(c_out))

		# c_out xored with divisor sign is inputed to quotient register at index i
		# this could be implemented with always input at LSB and shift left
		#quotient_reg[i] = c_out ^ sign_divisor
		quotient_reg[n-1-i] = 1-(sign_dividend ^ sign_divisor)

		# s_out is used to update the dividend register upper part without affecting the lower part
		dividend_reg.set((dividend_reg.get() & ((2**n)-1)) | (s_out<<n))

	# plot black lines connecting the point
	#line, = axis.plot( dividends, color='black', linewidth=0.5, marker='o', markersize=8, markerfacecolor='black', markeredgecolor='black', markeredgewidth=0.5)
	line, = axis.plot( dividends, color='black', marker="x")
	for i in range(len(dividends)):
		axis.annotate(str(dividends[i]), (i, dividends[i]), textcoords="offset points", xytext=(0,5), ha='center')

#	divisor_negative = int(sys.argv[3]) < 0  # This assumes the divisor is passed as the fourth command line argument and checks if it's negative.
	for i in range(1, len(dividends)):
		# Calculate midpoint coordinates between two consecutive points
		mid_x = (i - 1 + i) / 2  # Midpoint in the x-axis
		mid_y = (dividends[i-1] + dividends[i]) / 2  # Midpoint in the y-axis

		if i % 2 == 1:  # If the index is odd, annotate the shift operation
			axis.annotate(rf"$\times 2$", (mid_x, mid_y), textcoords="offset points", xytext=(0,10), ha='center')
		else:  # If the index is even, annotate the add/subtract operation
			#dividend_negative = dividends[i] < 0

			# Determine the operation and invert the sign if either dividend or divisor is negative
			#if dividend_negative != divisor_negative:
			#	operation = "-"
			#else:
			#	operation = "+"
			operation = "+" if dividends[i] >= dividends[i-1] else "-"

			# For the +/- operation, use the calculated midpoint in the y-axis
			value_to_display = rf"${operation}2^{n}\cdot {abs(int(sys.argv[3]))}$"
			offset_y = 10 if operation == "+" else -10
			axis.annotate(value_to_display, (mid_x, mid_y), textcoords="offset points", xytext=(0, offset_y), ha='center')

	# print the partial results, before quotient correction
	print("\n------")
	print("partial results before correction")
	print("  quotient: " + str(quotient_reg.get_as_list()))
	print("  quotient: " + str(quotient_reg.get()))
	print("  quotient: " + str(bin(quotient_reg.get())))
	print("  quotient as signed: " + str(quotient_reg.as_signed()))
	print("  remainder: " + str(dividend_reg.get_as_list())) # the remainder is the dividend at the end of the division
	print("  remainder as signed: " + str(dividend_reg.as_signed()>>n)) # the remainder is the dividend at the end of the division


	# quotient correction
	print("\n------")
	print("quotient correction")
	remainder_reg.set(dividend_reg.get()>>n)
	quotient_reg[n-1] = 1 - quotient_reg[n-1]
	print("quotient", bin(quotient_reg.get()))
	q_o = (quotient_reg.get()<<1)+1 # shift left and insert 1 at LSB
	print("quotient", bin(q_o))
	quotient_reg.set(q_o)


	if dividend_reg[2*n-1] != sign_dividend_ff.get():
		if dividend_reg[2*n-1] == sign_divisor_ff.get():
			print("  quotient++")
			q_o = (q_o + 1) & ((2**n)-1) # add 1 and mask to get n bits
			quotient_reg.set(q_o)
			remainder_reg.set(remainder_reg.get() - divisor_reg.get())
		else:
			print("  quotient--")
			q_o = (q_o - 1) & ((2**n)-1) # add 1 and mask to get n bits
			quotient_reg.set(q_o)
			remainder_reg.set(remainder_reg.get() + divisor_reg.get())


		#else:
		# 	print("  quotient-- AND remainder = remainder + divisor")
		# 	q_o = (q_o - 1) & 0b1111 # add 1 and mask to get n bits
		# 	quotient_reg.set(q_o)
		# 	remainder_reg.set((dividend_reg.get()>>n) + divisor_reg.get())

	# final results
	print("\n------")
	print("final results")
	print("  quotient as signed: " + str(quotient_reg.as_signed()))
	print("  remainder: " + str(remainder_reg.as_signed()))

	# plot the results
	fig.savefig('division.svg', dpi='figure')
	plt.close(fig='all')

if __name__ == "__main__":
	# Apply style configurations for publication quality
	plt.style.use('grayscale')
	tex_fonts = {
	    'text.usetex': True,
	    'font.family': 'serif',
	    'font.serif': ['Times New Roman'] + plt.rcParams['font.serif'],
	    'axes.labelsize': 8,
	    'font.size': 10,
	    'legend.fontsize': 6.0,
	    'xtick.labelsize': 8,
	    'ytick.labelsize': 8,
	    'lines.markeredgewidth': 0.3,
	    'lines.markersize': 4,
	    'lines.linewidth': 0.4,
	    'hatch.linewidth': 0.2,
	    'grid.color': '#A5A5A5',
	    'grid.linestyle': '--',
	    'grid.linewidth': 0.3,
	    'axes.grid': True,
	    'axes.grid.which': 'both'
	}
	plt.rcParams.update(tex_fonts)
	main()
