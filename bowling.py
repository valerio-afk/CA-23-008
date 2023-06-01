from copy import deepcopy

allowed_roll = lambda lst, x: (x in lst) or (0 <= int(x) < Roll.PINS)
# Yes, a new class could have been used, but I prefer this to introduce you to dictionaries
new_frame = lambda: {'printable_rolls': [], 'rolls': [], 'score': 0, 'cum_score': 0}

is_strike = lambda r: isinstance(r, Strike)


class Roll:
    PINS = 10

    def __init__(this, value, look_ahead=0):
        this.value = value
        this.look_ahead = look_ahead

    def __str__(this):
        return str(this.value) if (this.value > 0) else '-'

    def __repr__(this):
        return str(this)

    def __add__(this, obj):
        if isinstance(obj, Roll) or (type(obj) == int):
            return this.value + int(obj)

    __radd__ = __add__

    def __int__(this):
        return this.value


class Spare(Roll):

    def __init__(this, previous_roll):
        super().__init__(Roll.PINS - previous_roll.value, 1)

    def __str__(this):
        return '/'


class Strike(Roll):

    def __init__(this):
        super().__init__(10, 2)

    def __str__(this):
        return 'X'


def convertToRoll(char, prev_roll=None):
    if ((char in ['X', 'x'])) or (int(char) == Roll.PINS):
        return Strike()
    elif (char == '/') or ( (prev_roll is not None) and ((int(char)+prev_roll.value)==Roll.PINS)):
        return Spare(prev_roll)
    elif (char == '-') or (int(char) == 0):
        return Roll(0)
    else:
        return Roll(int(char))


class Game:
    FRAMES = 10

    def __init__(this, sequence=None, player="Player"):
        this.__rolls = [0] * (Game.FRAMES*2)
        this.player = player

        if (sequence is not None):
            this.readSequence(sequence)

    #this has been changed to return just a list of rolls
    def __getitem__(this, key):
        return this.getFrames()[key]['rolls']

    #this method has been added to change a game at a frame level
    def __setitem__(this, key, frame):
        max_len=0

        value = []

        for i,r in enumerate(frame):
            prev_roll = None if i == 0 else value[i-1]
            value.append( r if isinstance(r,Roll) else convertToRoll(r,prev_roll) )

        if (key<(Game.FRAMES-1)):
            max_len = 1 if value[0].value == Roll.PINS else 2
        elif (key==(Game.FRAMES-1)):
            max_len = 2 if sum([x.value for x in value[:2]])<Roll.PINS else 3

        if (max_len==0):
            ValueError("The provided frame number or frame is invalid")

        if len(value)>max_len:
            raise ValueError("The provided frame can have up to {} rolls".format(max_len))

        pre_frame = []
        post_frame = []
        roll_idx = 0

        for i in range(Game.FRAMES):

            lst = None

            if i<key:
                lst = pre_frame
            elif i>key:
                lst = post_frame

            if (i==(Game.FRAMES-1)):
                if (lst is not None):
                    lst += this.__rolls[roll_idx:]
            else:
                if is_strike(this.__rolls[roll_idx]):
                    if (lst is not None):
                        lst.append(this.__rolls[roll_idx])
                    roll_idx+=1
                else:
                    if (lst is not None):
                        lst+=this.__rolls[roll_idx:(roll_idx+2)]
                    roll_idx+=2


        this.__rolls = pre_frame + value + post_frame


    def __iter__(this):
        return this.getFrames()

    #added - although a game must have 10 frames, it happened some games had less frames. Useful for debugging
    def __len__(this):
        return len(this.getFrames())

    #added to return the score of the game. Useful to calculate the fitness
    @property
    def score(this):
        return this.getFrames()[-1]['cum_score']


    #this has been changed to being a generator to return a list of frames
    def getFrames(this):
        prev_frame = None
        frame = new_frame()
        n_frame = 1

        frames = []

        for i, roll in enumerate(this.__rolls):
            frame["printable_rolls"].append(str(roll))
            frame["rolls"].append(int(roll))
            frame["score"] += roll.value

            if ((n_frame < Game.FRAMES) and ((is_strike(roll)) or (len(frame['rolls']) == 2))):
                frame["score"] += sum(this.__rolls[i + 1:(i + roll.look_ahead + 1)])
                frame['cum_score'] = frame['score'] + prev_frame['cum_score'] if (prev_frame is not None) else frame[
                    'score']

                frames.append(frame)

                prev_frame = frame
                frame = new_frame()
                n_frame += 1
            else:
                if ((len(frame['rolls']) == 2) and (
                        frame["score"] < Roll.PINS) or  # yields 10th frame if we have two rolls and cannot have more
                        (len(frame['rolls']) == 3)):  # yields 10th frame when we have 3 rolls

                    # here we could avoid copy n paste somehow (ex nested function, but let's not overdo)
                    frame['cum_score'] = frame['score'] + prev_frame['cum_score'] if (prev_frame is not None) else \
                    frame['score']

                    frames.append(frame)

        return frames

    def readSequence(this, sequence):
        this.__rolls = []

        frame = 1
        current_roll = 0
        previous_roll = None

        for i, c in enumerate(sequence):
            roll = None
            if (current_roll == 0):
                allowed_symbols = ['-', 'X', 'x']
            else:
                if ((frame < Game.FRAMES) or ((frame == Game.FRAMES) and not is_strike(previous_roll))):
                    allowed_symbols = ['-', '/']
                else:
                    allowed_symbols = ['-', 'X', 'x']

            if allowed_roll(allowed_symbols, c):
                roll = convertToRoll(c, previous_roll)
            else:
                raise Exception(f"I don't understand character {c} at position {i + 1}")

            if (frame == Game.FRAMES):
                roll.look_ahead = 0  # strikes and spares in the last frame are just 10

            this.__rolls.append(roll)
            previous_roll = roll

            if (frame < Game.FRAMES):
                if (((current_roll == 0) and (
                        roll.value == 10)) or  # move to next frame if we scored a strike not in the last frame
                        (current_roll > 0)):  # or when we are in the 2nd roll in any non-last frame
                    frame += 1
                    current_roll = 0
                else:
                    current_roll += 1

            else:  # this is the last frame
                if (current_roll < 2):
                    current_roll += 1

                    if (sum(this.__rolls[-2:]) < Roll.PINS):  # we are not entitled to the extra roll(s)
                        break  # exit for prematurely
                else:
                    break  # we reached the last roll

    #added to make deep copies of this object
    def copy(this):
        return deepcopy(this)

    def __str__(this):
        frame_line0 = []
        frame_line1 = []
        frame_line2 = []

        for i, frame in enumerate(this.getFrames()):
            size = 3 if i < (Game.FRAMES - 1) else 5

            frame_line0.append(str(i + 1).center(size))
            frame_line1.append(" ".join(frame['printable_rolls']).ljust(size))
            frame_line2.append(str(frame['cum_score']).rjust(size))

        line0 = "|{}|".format("|".join(frame_line0))
        line1 = "|{}|".format("|".join(frame_line1))
        line2 = f"|{'|'.join(frame_line2)}|"  # let's use a different string formatting approach

        dashed_line = "-" * len(line0)

        formatted_player = "|" + this.player.center(len(line0) - 2) + "|"

        return f"{dashed_line}\n{formatted_player}\n{line0}\n{dashed_line}\n{line1}\n{dashed_line}\n{line2}\n{dashed_line}\n"

    __repr__ = __str__