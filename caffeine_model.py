from datetime import datetime
import matplotlib.pylab as plt
from collections import defaultdict
from typing import List, Tuple, Dict


def plot_caffeine_level(caffeine_levels: List[float]) -> None:
    """
    Creates png file with plot of caffeine level.

    Parameters
    ----------
    caffeine_levels: List[float]
        list of caffeine level values minute by minute
    """
    x_values: List[int] = [x for x in range(len(caffeine_levels))]
    plt.plot(x_values, caffeine_levels)
    plt.savefig("caffeine_levels.png")


def difference_in_minutes(fst_timestamp: datetime, snd_timestamp: datetime) -> int:
    """
    Calculates time difference in minutes between two timestamps.

    Parameters
    ----------
    fst_timestamp: datetime
        first timestamp
    snd_timestamp: datetime
        second timestamp

    Returns
    -------
    time difference: int
        time difference in minutes between two timestamps
    """
    difference = snd_timestamp - fst_timestamp
    return int(difference.total_seconds() // 60)


def process_purchases(purchases: List[Tuple[int, datetime]]) -> Dict[int, float]:
    """
    Processes coffee purchases into dictionary representing caffeine level growth.

    Parameters
    ----------
    purchases: List[Tuple[int, datetime]]
        List of purchases represented by Tuple:
            caffeine amount
            time of the purchase

    Returns
    -------
    growth_dict: Dict[int, float]
        dictionary representing caffeine level growth minute by minute since the first purchase
    """
    purchases.sort(key=lambda x: x[1])
    first_timestamp: datetime = purchases[0][1]
    growth_dict: Dict[int, float] = defaultdict(lambda: 0)

    for caffeine, timestamp in purchases:
        cur_time: int = difference_in_minutes(first_timestamp, timestamp)
        for time in range(cur_time, cur_time + 60):
            growth_dict[time] += caffeine / 60

    return growth_dict


def compute_caffeine_level(purchases: List[Tuple[int, datetime]]) -> List[float]:
    """
    Computes caffeine level based on coffee purchases

    Parameters
    ----------
    purchases: List[Tuple[int, datetime]]
        List of purchases represented by Tuple:
            caffeine amount
            time of the purchase

    Returns
    -------
    result: List[float]
        list of levels for past 24 hour using 1h resolution
    """
    if purchases == []:
        return [0 for _ in range(25)]

    growth_dict: Dict[int, float] = process_purchases(purchases)
    # current value
    caffeine_level: float = 0
    caffeine_levels: List[float] = []
    # constant representing caffeine level decrease between minutes
    r: float = 0.5 ** (1 / 300)

    time_range: int = difference_in_minutes(purchases[0][1], datetime.now())

    for i in range(time_range):
        caffeine_levels.append(caffeine_level)
        caffeine_level = caffeine_level * r + growth_dict[i]

    # Uncomment this line to generate caffeine level plot png file
    # plot_caffeine_level(caffeine_levels)

    caffeine_levels.reverse()
    result: List[float] = []

    for i in range(0, 1500, 60):
        if i < len(caffeine_levels):
            result.append(caffeine_levels[i])
        else:
            result.append(0)

    result.reverse()
    return result
