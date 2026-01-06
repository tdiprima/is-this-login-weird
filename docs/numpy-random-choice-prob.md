## Numpy Random Choice Probabilities Positional Matching

Why?

```py
hours = np.random.choice(range(24), n_samples, p=[
    0.02, 0.01, 0.01, 0.01, 0.01, 0.02,  # 0-5am (people should be asleep)
    0.03, 0.04, 0.06, 0.08, 0.06, 0.05,  # 6-11am (coffee-powered humans)
    0.06, 0.05, 0.04, 0.04, 0.05, 0.06,  # 12-5pm (steady grind)
    0.08, 0.07, 0.06, 0.04, 0.03, 0.02   # 6-11pm (doomscroll hours)
])
```

Short answer: **because Python is extremely literal and a little dumb (in a good way).**  
Bob's Burgers answer first, then the clean mental model.

---

## 🍔 Bob's Burgers version

**Bob:** "I handed Python a list. Python will not improvise."

You gave Python this:

```python
np.random.choice(range(24), n_samples, p=[ ... ])
```

* `range(24)` =

  ```python
  [0, 1, 2, 3, 4, 5, 6, ..., 23]
  ```

* `p=[...]` = a list of **24 probabilities**
* Python matches them **by position**, not by meaning

So Python does this internally:

| Hour | Probability  |
| ---- | ------------ |
| 0    | p[0] = 0.02  |
| 1    | p[1] = 0.01  |
| 2    | p[2] = 0.01  |
| 3    | p[3] = 0.01  |
| 4    | p[4] = 0.01  |
| 5    | p[5] = 0.02  |
| 6    | p[6] = 0.03  |
| ...    | ...            |
| 23   | p[23] = 0.02 |

**Tina:** "So... it's positional. Like seating charts."

Exactly.

---

## 🧠 The actual rule (no vibes, just facts)

`np.random.choice(values, size, p=probabilities)` follows **one hard rule**:

**The `p` list must be the same length as `values`, and index `i` applies to value `i`.**

In your case:

```python
values = range(24)      # [0, 1, 2, ..., 23]
p      = [p0, p1, ..., p23]
```

So:

* `p[0]` → probability of choosing `0`
* `p[1]` → probability of choosing `1`
* ...
* `p[23]` → probability of choosing `23`

That's it. No magic. No labels. No guessing.

---

## 🔍 Why the comment "0–5am" is valid

This comment:

```python
0.02, 0.01, 0.01, 0.01, 0.01, 0.02,  # 0–5am
```

Is correct **only because**:

1. `range(24)` starts at 0
2. Those are the **first six numbers** in the probability list
3. Hours `0–5` are midnight → 5:59am

If you changed this to:

```python
range(1, 25)
```

💥 **The entire meaning breaks.**  
Now `p[0]` applies to hour **1**, not 0.

---

## 🚨 Common gotcha (this bites people)

Python does **NOT** know this:

```python
# WRONG mental model ❌
0.02 means "2% chance at 0–5am"
```

Python only knows:

```python
# CORRECT mental model ✅
0.02 applies to whatever value is at index 0
```

---

## 🧪 Quick sanity check trick (10/10 recommend)

If you ever feel unsure, do this:

```python
import collections

hours = np.random.choice(range(24), 100_000, p=your_probs)
counter = collections.Counter(hours)

for h in range(6):
    print(h, counter[h] / 100_000)
```

You'll *see* that 0–5 happen less often.

---

## 🧩 TL;DR (Louise version)

* Python doesn't know time
* Python doesn't know "am"
* Python only knows **list positions**
* `range(24)` + `p[24]` = **index-to-index mapping**
* Comments are for humans, not Python

<br>
