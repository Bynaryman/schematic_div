#!/usr/bin/env python

from helpers import *
import sys

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

	# main loop
	for i in range(n): # n clock cycles


		# get the signs of the divisor and dividend
		sign_divisor = divisor_reg[n-1]
		sign_dividend = dividend_reg[2*n-1]

		print("   dividend: " + str(dividend_reg.get_as_list()))
		print("   dividend as bin: {0:08b}".format(dividend_reg.get()))

		# left shift the dividend register
		dividend_reg.set(dividend_reg.get() << 1)

		# print signs
		print("   sign_divisor: " + str(sign_divisor))
		print("   sign_dividend: " + str(sign_dividend))

		# get the mathematical operation to do depending on the signs
		op_to_perform = sign_divisor ^ sign_dividend # xor: addition if 1, substraction if 0
		print("   op to perform: ", op_to_perform)

		# c_out xored with divisor sign is inputed to quotient register at index i
		# this could be implemented with always input at LSB and shift left
		quotient_reg[n-1-i] = 1-(sign_dividend ^ sign_divisor)

		for j in range(n): # n clock cycles
			print("clock cycle: ", i*n+j)

			# get 1 bit LSB order
			divisor_bit = divisor_reg[j]

			# get its complement
			divisor_bit_1_complement = 1-divisor_bit

			# get the adder operand depending on op_to_perform (MUX)
			if op_to_perform == 1:
				operand_b_adder = divisor_bit
			else:
				operand_b_adder = divisor_bit_1_complement

			if j == 0:
				carry_in_adder = 1-op_to_perform
			else:
			    carry_in_adder = c_out

			operand_a_adder = dividend_reg[n+j]

			s_out, c_out = full_adder_n_bits(1, operand_a_adder, operand_b_adder, carry_in_adder)
			print("  s_out: ", bin(s_out))
			print("  c_out: ", bin(c_out))


			# s_out is used to update the dividend register upper part without affecting the lower part
			#dividend_reg.set((dividend_reg.get() & ((2**n)-1)) | (s_out<<n))
			dividend_reg[n+j] = s_out

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

	# final results
	print("\n------")
	print("final results")
	print("  quotient as signed: " + str(quotient_reg.as_signed()))
	print("  remainder: " + str(remainder_reg.as_signed()))


if __name__ == "__main__":
	main()
