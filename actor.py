"""
"""

from pure import shadowcast

class Actor:
    """An actor is an object that has an act function and can be scheduled"""

    actors = {}
    newactorid = 0

    def __init__(self):
        self.id = Actor.newactorid
        self.delay = 0
        self.char = '?'

        Actor.newactorid += 1
        Actor.actors[self.id] = self

    def act(self, schedule):
        nextactorid = schedule.pushpop(self.id, self.delay)
        self.delay = 0
        Actor.actors[nextactorid].act(schedule)

class Event(Actor):
    """An actor that calls a function once then removes itself"""

    def __init__(self, function, **kwargs):
        super().__init__(**kwargs)
        self.function = function

    def act(self, schedule):
        del Actor.actors[this.id]
        self.function()
        Actor.actors[schedule.pop()].act(schedule)

class Mover(Actor):
    """An actor that can move around the level"""

    def __init__(self, position, level, **kwargs):
        super().__init__(**kwargs)
        self.position = position
        self.level = level

    def canmove(self, dx, dy, level=None):
        if not level:
            level = self.level
        x, y = self.position
        return level.tiles[x+dx,y+dy] in ('floor', 'door', 'corridor')

    def move(self, dx, dy):
        x, y = self.position
        target = (x + dx, y + dy)
        self.level.actors.pop(self.position)
        self.position = target
        self.level.actors[self.position] = self
        self.delay = 12

    def movelevel(self, level):
        self.level = level
        if self.position in level.actors:
            print('movelevel: target is occupied')
        else:
            level.actors[self.position] = self
        self.delay = 12

class Player(Mover):
    """A player is an actor who can give and receive input and output"""

    def __init__(self, input, output, **kwargs):
        super().__init__(**kwargs)
        self.input = input
        self.output = output
        self.char = '@'

    def act(self, schedule):
        self.output(('done',))
        input = next(self.input)
        inputtype = input[0]
        inputargs = input[1:]
        if inputtype == 'quit':
            return
        actions = {'move': self.move}
        actions[inputtype](*inputargs)
        super().act(schedule)

    def move(self, dx, dy):
        if self.canmove(dx, dy):
            self.level.deathpath[self.position] = (dx, dy)
            super().move(dx, dy)
            self.see()
            delay = 12

    def movelevel(self, level):
        delay = super().movelevel(level)
        self.see()
        return delay

    def see(self):
        for position in shadowcast(*self.position, self.level.transparent):
            self.output(('put', *position, self.level.tiles[position]))
            if (position in self.level.deathpath):
                self.output(('put', *position, self.level.deathpath[position]))
            if (position in self.level.actors):
                self.output(('put', *position, self.level.actors[position].char))

class Reaper(Mover):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.char = 'R'
        self.spawned = False

    def act(self, schedule):
        if self.spawned:
            direction = self.level.deathpath[self.position]
            del self.level.deathpath[self.position]
            self.move(*direction)
        else:
            self.movelevel(self.level)
            self.spawned = True
        super().act(schedule)
