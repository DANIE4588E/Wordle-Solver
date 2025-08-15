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

def build_global_freq(words):
    """Position-agnostic letter frequency across a pool of words."""
    freq = {ch: 0 for ch in 'abcdefghijklmnopqrstuvwxyz'}
    for w in words:
        for ch in w:
            freq[ch] += 1
    return freq

def word_weight(word, freq, round_num):
    score = 0
    seen = set()
    for i, ch in enumerate(word):
        if ch in seen:
            score += freq[i][ch] / max(1, (6 - round_num)**2)
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

def best_guess_explore(word_pool, banned_letters, banned_words=None):
    """
    Choose from the full dictionary to maximize new-letter discovery.
    Score = sum of global frequencies of unique letters.
    Exclude words that contain any banned_letters or appear in banned_words.
    """
    if banned_words is None: banned_words = set()
    global_freq = build_global_freq(word_pool)

    best, best_score = None, -1
    for w in word_pool:
        if w in banned_words:
            continue
        if any(ch in banned_letters for ch in w):
            continue
        uniq = set(w)
        sc = sum(global_freq[ch] for ch in uniq)
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

# Track Round-1 letter info
present_letters_round1 = set()  
absent_letters_round1 = set() 

round2_guess = None

for r in range(1, rounds + 1):
    if r == 2:
        banned_letters_r2 = present_letters_round1 | absent_letters_round1
        guess = best_guess_explore(all_words, banned_letters_r2)
        if guess is None:
            freq = build_freq(candidates)
            guess = best_guess(candidates, freq, r)

    elif r == 3:
        banned_words_r3 = {round2_guess} if round2_guess else set()
        letters_from_r2 = set(round2_guess) if round2_guess else set()
        hard_ban_r3 = present_letters_round1 | absent_letters_round1 | letters_from_r2

        guess = best_guess_explore(all_words, hard_ban_r3, banned_words_r3)
        if guess is None:
            relax_ban = present_letters_round1 | absent_letters_round1
            guess = best_guess_explore(all_words, relax_ban, banned_words_r3)
            if guess is None:
                freq = build_freq(candidates)
                guess = best_guess(candidates, freq, r)

    else:
        # Normal position-weighted behavior
        freq = build_freq(candidates)
        guess = best_guess(candidates, freq, r)

    print(f"Round {r}: try '{guess}'")
    if r == rounds:
        break

    fb = [
        input(f"  Feedback for pos {i+1} (2=green,1=yellow,0=grey): ")
        for i in range(5)
    ]

    # Record letters
    if r == 1:
        raw_present = {g for g, f in zip(guess, fb) if f in ('1', '2')}
        raw_absent  = {g for g, f in zip(guess, fb) if f == '0'}
        present_letters_round1 |= raw_present
        absent_letters_round1 |= (raw_absent - raw_present)

    # Store Round-2 guess for Round-3 bans
    if r == 2:
        round2_guess = guess

    candidates = filter_candidates(candidates, guess, fb)
    if len(candidates) == 1:
        print("Solved:", candidates[0])
        break
    print(f"  {len(candidates)} candidates left\n")
