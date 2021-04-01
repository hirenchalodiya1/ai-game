from constats import MINIMUM_ASSISTANCE


class Path:
    path = list()
    cost = None
    has_ended = False
    last_shoot = False

    def __init__(self, start, cost):
        if isinstance(start, list):
            self.path = start
        else:
            self.path = [start]
        self.cost = cost

    def __repr__(self):
        return f"Path:{self.path}"

    def get_next(self, passing, shoot):
        last_p = self.path[-1]
        if self.has_ended:
            return []

        ret = []
        if last_p in passing:
            for next_p in passing[last_p]:
                if next_p not in self.path:
                    new_cost = self.cost + last_p.point.distance(next_p.point)
                    new_path = Path(self.path + [next_p], new_cost)
                    ret.append(new_path)

        if last_p in shoot:
            self.cost += last_p.point.distance(shoot[last_p])
            self.path += [shoot[last_p]]
            self.last_shoot = True
            self.has_ended = True

        if not self.last_shoot:
            self.has_ended = not bool(ret)

        return ret

    def is_valid(self):
        return self.has_ended and self.last_shoot and len(self.path) > MINIMUM_ASSISTANCE + 1


def all_paths(paths, passing, shoot):
    # recursion ending
    if all(map(lambda x: x.has_ended, paths)):
        return paths

    ret = []
    for path in paths:
        get_new = path.get_next(passing, shoot)
        ret += get_new

    return paths + all_paths(ret, passing, shoot)


def shortest_n_paths(start, passing, shoot, n):
    ap = all_paths([Path(start, 0)], passing, shoot)
    ap = list(filter(lambda x: x.is_valid(), ap))
    ap.sort(key=lambda x: x.cost)
    return ap[:n]
