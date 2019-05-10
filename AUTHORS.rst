
        self.y1 = mul(self.u, self.g1 + self.b1 * 1j)
        self.y2 = mul(self.u, self.g2 + self.b2 * 1j)
        self.y12 = div(self.u, self.r + self.x * 1j)
        self.m = polar(self.tap, self.phi * deg2rad)
        self.m2 = abs(self.m)**2=======
Credits
=======

Maintainer
----------

* Hantao Cui <cuihantao@gmail.com>

Contributors
------------

None yet. Why not be the first? See: CONTRIBUTING.rst
