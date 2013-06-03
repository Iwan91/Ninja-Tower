"""Strictly basic objects. KISS for porting onto C++"""

class Rectangle(object):
    """Just a rectangle. Not oriented in the world"""
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.height = y2-y1+1
        self.width = x2-x1+1

        assert y1 <= y2
        assert x1 <= x2

    def upside_down(self):
        return Rectangle(self.x1, -self.y2, self.x2, -self.y1)

    def __repr__(self):
        return 'Rectangle(%s, %s, %s, %s)' % (self.x1, self.y1, self.x2, self.y2)

    def intersects_r(self, other, xs, ys, xo, yo):
        """xs, ys is base for position of this instance, xo, yo is base-position of the other rectangle"""
        return not ((other.x1+xo > self.x2+xs) or (other.x2+xo < self.x1+xs) or (other.y1+yo > self.y2+ys) or (other.y2+yo < self.y1+ys))

    def intersects_p(self, xs, ys, px, py):
        return (self.x1+xs <= px) and (self.y1+ys <= py) and (self.y2+ys >= py) and (self.x2+xs >= px)

    def intersects_g(self, other, xs, ys, xo, yo):
        if not self.intersects_r(other.mbr, xs, ys, xo, yo):
            return False

        for orect in other.rectangles:
            if self.intersects_r(orect, xs, ys, xo, yo):
                return True

        return False

class Geometry(object):
    """A set of rectangles"""
    def __init__(self, sr):
        """@type sr: sequence of Rectangle"""
        self.rectangles = sr
        self.mbr = Rectangle(min([x.x1 for x in sr]), min([x.y1 for x in sr]), max([x.x2 for x in sr]), max([x.y2 for x in sr]))

    def upside_down(self):
        return Geometry([rect.upside_down() for rect in self.rectangles])

    def intersects_p(self, xs, ys, px, py):
        if not self.mbr.intersects_p(xs, ys, px, py): return False
        for rect in self.rectangles:
            if rect.intersects_p(xs, ys, px, py):
                return True
        return False

    def intersects_g(self, other, xs, ys, xo, yo):
        if not self.mbr.intersects_r(other.mbr, xs, ys, xo, yo):
            return False
        
        for rect in self.rectangles:
            for orect in other.rectangles:
                if rect.intersects_r(orect, xs, ys, xo, yo):
                    return True

        return False
        
    def intersects_r(self, other, xs, ys, xo, yo):
        return other.intersects_g(self, xo, yo, xs, ys)