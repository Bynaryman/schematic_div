class HardwareRegister:
	def __init__(self, n_bits):
		self.n_bits = n_bits
		self.register = [0] * n_bits

	def set(self, value):
		for i in range(self.n_bits):
			self.register[i] = (value >> i) & 1

	def get(self):
		return sum([(bit << i) for i, bit in enumerate(self.register)])

	def get_as_list(self):
		return self.register

	def left_shift(self, n):
		for _ in range(n):
			self.register.pop(0)
			self.register.append(0)

	def right_shift(self, n):
		for _ in range(n):
			self.register.pop()
			self.register.insert(0, 0)

	def as_signed(self):
		return (self.get() + 2 ** (self.n_bits - 1)) % 2 ** self.n_bits - 2 ** (self.n_bits - 1)

	def as_unsigned(self):
		return self.get()

	def __getitem__(self, index):
		if isinstance(index, slice):
			start = index.start
			stop = index.stop
			step = index.step
			return self.register[start:stop:step]
		else:
			if index < 0 or index >= self.n_bits:
				raise IndexError("Index out of range.")
			return (self.register[index]) & 1

	def __setitem__(self, index, value):
		if index < 0 or index >= self.n_bits:
			raise IndexError("Index out of range.")
		if value not in [0, 1]:
			raise ValueError("Value must be either 0 or 1.")
		self.register[index] = value


def main():
	# implement some tests of the helpers
	register = HardwareRegister(8)
	register.set(0x55)
	print(register.get())
	print(register.as_unsigned())
	print(register.as_signed())
	print(register[0])
	print(register[1])
	print(register[2])

if __name__ == "__main__":
	main()
