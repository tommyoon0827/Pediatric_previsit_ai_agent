# Per-answer alert evaluation

80 cases x 3 runs, gpt-4o-mini, temperature 0

## baseline

### clinical

- alert on flagged answers (app view): 93.3% (84/90)
- alert on normal answers (app view): 6.7% (6/90)
- raw labels: {'alert': 90, 'pass': 90}
- same result in all 3 runs: 60/60 cases

### lifestyle

- alert on flagged answers (app view): 50.0% (15/30)
- alert on normal answers (app view): 10.0% (3/30)
- raw labels: {'pass': 42, 'alert': 18}
- same result in all 3 runs: 20/20 cases

## with_criteria

### clinical

- alert on flagged answers (app view): 100.0% (90/90)
- alert on normal answers (app view): 11.1% (10/90)
- raw labels: {'alert': 100, 'pass': 80}
- same result in all 3 runs: 59/60 cases

### lifestyle

- alert on flagged answers (app view): 90.0% (27/30)
- alert on normal answers (app view): 30.0% (9/30)
- raw labels: {'alert': 36, 'pass': 24}
- same result in all 3 runs: 20/20 cases

## criteria_strict

### clinical

- alert on flagged answers (app view): 94.4% (85/90)
- alert on normal answers (app view): 5.6% (5/90)
- raw labels: {'alert': 90, 'pass': 90}
- same result in all 3 runs: 58/60 cases

### lifestyle

- alert on flagged answers (app view): 90.0% (27/30)
- alert on normal answers (app view): 13.3% (4/30)
- raw labels: {'alert': 31, 'pass': 29}
- same result in all 3 runs: 19/20 cases
