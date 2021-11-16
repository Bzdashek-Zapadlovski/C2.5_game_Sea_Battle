from random import randint

class Place:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class LocationException(Exception): 
    pass

class LocationOutException(LocationException):
    def __str__(self):
        return "Вы выстрелили за границы игровой области!!!"

class LocationUsedException(LocationException):
    def __str__(self):
        return "Вы производили выстрел в данное место ранее!!!"

class LocationWrongBoatException(LocationException):
    pass

class Boat:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def points(self):
        boat_places = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            boat_places.append(Place(cur_x, cur_y))

        return boat_places

    def shooten(self, shot):
        return shot in self.points

class Player:
    def __init__(self, location, opponent):
        self.location = location
        self.opponent = opponent

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.opponent.shot(target)
                return repeat
            except LocationException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Place(randint(0, 5), randint(0, 5))
        print(f"Ходит компьютер: {d.x + 1} {d.y + 1}")
        return d

class User(Player):
    def ask(self):
        while True:
            coordinates = input("Произведите залп: ").split()

            if len(coordinates) != 2:
                print(" Необходимо ввести 2(две) координаты!!! ")
                continue

            x, y = coordinates

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Необходимо ввести числа!!! ")
                continue

            x, y = int(x), int(y)

            return Place(x - 1, y - 1)

class Location:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.boat = []

    def add_boat(self, boat):

        for d in boat.points:
            if self.out(d) or d in self.busy:
                raise LocationWrongBoatException()
        for d in boat.points:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.boat.append(boat)
        self.contour(boat)

    def contour(self, boat, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in boat.points:
            for dx, dy in near:
                cur = Place(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise LocationOutException()

        if d in self.busy:
            raise LocationUsedException()

        self.busy.append(d)

        for boat in self.boat:
            if d in boat.points:
                boat.lives -= 1
                self.field[d.x][d.y] = "X"
                if boat.lives == 0:
                    self.count += 1
                    self.contour(boat, verb=True)
                    print("Корабль потоплен!!!")
                    return False
                else:
                    print("Корабль подбит!!!")
                    return True

        self.field[d.x][d.y] = "T"
        print("Промах!!!")
        return False

    def begin(self):
        self.busy = []

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_location()
        co = self.random_location()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_location(self):
        location = None
        while location is None:
            location = self.random_place()
        return location

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        location = Location(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                boat = Boat(Place(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    location.add_boat(boat)
                    break
                except LocationWrongBoatException:
                    pass
        location.begin()
        return location

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print("  Вводимые данные  ")
        print(" X - номер строки  ")
        print(" Y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Ваше игровое поле:")
            print(self.us.location)
            print("-" * 20)
            print("Игровое поле компьютера:")
            print(self.ai.location)
            if num % 2 == 0:
                print("-" * 20)
                print("Сейчас ходит игрок!!!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Сейчас ходит компьютер!!!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.location.count == 7:
                print("-" * 20)
                print("Вы одержали победу!!!")
                break

            if self.us.location.count == 7:
                print("-" * 20)
                print("На сей раз победу одержал компьютер!!!  :) ")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()