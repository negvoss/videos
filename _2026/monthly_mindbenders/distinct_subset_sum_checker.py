from itertools import chain, combinations

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def all_distinct_subset_sums(numbers):
	sums = dict()
	for s in powerset(numbers):
		total = sum(s)
		if total in sums.keys():
			return f"Counterexample: {str(sums[total])}, {str(s)}"
		sums[total] = str(s)
	return "All distinct!"

print(all_distinct_subset_sums([100, 99, 98, 96, 93, 87, 76, 54]))