```
python predict-tourney.py
```
It's currently looking for the data in my downloads directory, so that would need to be changed.

For my algorithm, I made a number of calculations and took the one that came out best on average over the last thirty years.  It is the calculation titled "thirdOrderFancyRawByDay".  It computed the following for every game:
1. Pace-independent 'Rating' for both teams by calculating the percentage of points they scored

It computed the following for every team:
1. Raw average rating for every game over the season - weighted at .5
2. Average performance of a team's opponents against all teams the team did not play (how well did your opponents do) - weighted at .25
3. Average of calculation #2 for a team's opponents (how well did your opponents of opponents do) - weighted at .125
4. It weighted the performance of every game by the day it occurred (games late in the season are worth more than games early).  

The only difference from last year is that I scaled back the weight by game.  It appears to improve historical results a little bit.

The data was taken from Kaggle