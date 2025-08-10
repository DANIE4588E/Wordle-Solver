import copy
import re

# load word list
with open('sgb-words.txt') as f:
	all_words = [w.strip() for w in f]


def build_freq(words):
	base = {ch: 0 for ch in 'abcdefghijklmnopqrstuvwxyz'}
	freq = [copy.deepcopy(base) for _ in range(5)]
	for w in words:
		for i, ch in enumerate(w):
			freq[i][ch] += 1
	return freq


def word_weight(word, freq, round_num):
	score = 0
	seen = set()
	for i, ch in enumerate(word):
		if ch in seen:
			score += freq[i][ch] / ((6 - round_num)**2)
		else:
			score += freq[i][ch]
			seen.add(ch)
	return score


def best_guess(candidates, freq, round_num):
	best, best_score = None, -1
	for w in candidates:
		sc = word_weight(w, freq, round_num)
		if sc > best_score:
			best, best_score = w, sc
	return best


def filter_candidates(candidates, guess, fb):
	new = []
	for w in candidates:
		match = True
		for i, (g, f) in enumerate(zip(guess, fb)):
			if f == '2' and w[i] != g: match = False
			if f == '1' and (g not in w or w[i] == g): match = False
			if f == '0' and g in w: match = False
		if match:
			new.append(w)
	return new


candidates = all_words.copy()


rounds = 6

for r in range(1, rounds + 1):
	freq = build_freq(candidates)
	guess = best_guess(candidates, freq, r)
	print(f"Round {r}: try '{guess}'")
	if r == rounds:
		break

	fb = [
	    input(f"  Feedback for pos {i+1} (2=green,1=yellow,0=grey): ")
	    for i in range(5)
	]
	candidates = filter_candidates(candidates, guess, fb)
	if len(candidates) == 1:
		print("Solved:", candidates[0])
		break
	print(f"  {len(candidates)} candidates left\n")
