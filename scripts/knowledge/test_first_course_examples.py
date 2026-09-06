"""Independent reference computations; never use rendered prose as expected data."""
import math
import unittest


def gf_mul(a,b):
    product=0
    while b:
        if b&1:product^=a
        a<<=1
        if a&256:a^=0x11b
        b>>=1
    return product


def ec_add(p,q,mod,a):
    if p is None:return q
    if q is None:return p
    x,y=p;u,v=q
    if x==u and (y+v)%mod==0:return None
    slope=((3*x*x+a)*pow(2*y,-1,mod) if p==q else (v-y)*pow(u-x,-1,mod))%mod
    rx=(slope*slope-x-u)%mod
    return rx,(slope*(x-rx)-y)%mod


class FirstCourseCalculations(unittest.TestCase):
    def test_euclid_inverses(self):
        self.assertEqual(math.gcd(3931,1148),1)
        self.assertEqual(-33*3931+113*1148,1)
        self.assertEqual(pow(1148,-1,3931),113)
        self.assertEqual(pow(112,-1,423),34)
        self.assertEqual((112*306)%423,9)

    def test_crt_and_all_roots(self):
        roots=[x for x in range(1365) if [x%15,x%13,x%7]==[2,5,3]]
        self.assertEqual(roots,[122])
        self.assertEqual([x for x in range(1457) if x*x%1457==811],[118,211,1246,1339])
        self.assertEqual(len({1246%1457,-211%1457,1339%1457,-118%1457}),2)
        self.assertEqual([pow(x,378,757) for x in (3,11,17,561)],[1,1,1,1])

    def test_finite_field_and_polynomial(self):
        self.assertEqual([(2*x*x-2*x+1)%3 for x in range(3)],[1,1,2])
        def mul(x,y):
            a,b=x;c,d=y
            return ((a*c+b*d)%3,(a*d+b*c+b*d)%3)
        value=(1,0);powers=[]
        for _ in range(8):value=mul(value,(0,1));powers.append(value)
        self.assertEqual(powers,[(0,1),(1,1),(1,2),(2,0),(0,2),(2,2),(2,1),(1,0)])
        # Polynomial product in F2 represented by bit coefficients.
        p=0
        for i in range(3):
            if 0b110&(1<<i):p^=0b11<<i
        self.assertEqual(p^1,0b1011)

    def test_elliptic_curves(self):
        p=(5,1);two=ec_add(p,p,17,2)
        self.assertEqual(two,(6,3));self.assertEqual(ec_add(p,two,17,2),(10,6))
        self.assertIsNone(ec_add(p,(5,16),17,2))
        pts=[(x,y) for x in range(7) for y in range(7) if (y*y-x**3+2*x-1)%7==0]
        self.assertEqual(len(pts),11)
        p=(4,6);cur=None;values=[]
        for _ in range(12):cur=ec_add(cur,p,7,-2);values.append(cur)
        self.assertEqual(values[:6],[(4,6),(3,6),(0,1),(5,5),(6,3),(1,0)])
        self.assertIsNone(values[-1]);self.assertNotIn(None,values[:-1])

    def test_powers_factoring_and_miller_rabin(self):
        self.assertEqual(pow(7,13,23),20)
        self.assertEqual(pow(3,8,15),6)
        self.assertEqual(math.gcd(5-26,91),7)
        self.assertEqual(pow(2,7,23),13)
        self.assertEqual(pow(16,-1,23),13)
        self.assertEqual(13*13%23,8)
        self.assertEqual([pow(2,5,21),pow(2,10,21)],[11,16])

    def test_aes_mixcolumns_full_inverse(self):
        def apply(first,col):
            result=[]
            for i in range(4):
                row=first[-i:]+first[:-i] if i else first
                v=0
                for a,b in zip(row,col):v^=gf_mul(a,b)
                result.append(v)
            return result
        source=[0xdb,0x13,0x53,0x45]
        result=apply([2,3,1,1],source)
        self.assertEqual(result,[0x8e,0x4d,0xa1,0xbc])
        self.assertEqual(apply([14,11,13,9],result),source)
        for a in range(256):self.assertEqual(gf_mul(3,a),gf_mul(2,a)^a)

    def test_small_cipher_steps(self):
        left,right=0b1010,0b0110
        out=(right,left^(right^3))
        self.assertEqual(out,(6,15))
        self.assertEqual((out[1]^(out[0]^3),out[0]),(left,right))
        self.assertEqual((0xfffffffe+5)%2**32,3)
        c1=5^3^9;c2=6^c1^9
        self.assertEqual((c1,c2),(15,0))
        self.assertEqual((c1^9^3,c2^9^c1),(5,6))
        self.assertEqual(c1^9^2,4)

    def test_rsa_all_messages_and_rabin(self):
        self.assertEqual(pow(9,7,143),48)
        self.assertEqual(pow(48,103,143),9)
        self.assertEqual(7*103%120,1)
        for m in range(143):self.assertEqual(pow(pow(m,7,143),103,143),m)
        self.assertEqual(pow(4,3,33),31);self.assertEqual(pow(31,7,33),4)
        self.assertEqual([x for x in range(77) if x*x%77==15],[13,20,57,64])

    def test_elgamal_dh_schnorr(self):
        self.assertEqual(pow(5,6,23),8);self.assertEqual(pow(5,15,23),19)
        self.assertEqual(pow(19,6,23),2);self.assertEqual(pow(8,15,23),2)
        c1=pow(5,3,23);c2=10*pow(8,3,23)%23
        self.assertEqual((c1,c2),(10,14))
        self.assertEqual(c2*pow(pow(c1,6,23),-1,23)%23,10)
        g,p,q,x,r,e=2,23,11,3,4,5
        y=pow(g,x,p);commitment=pow(g,r,p);s=(r+x*e)%q
        self.assertEqual((y,commitment,s),(8,16,8))
        self.assertEqual(pow(g,s,p),commitment*pow(y,e,p)%p)
        self.assertEqual(pow(g,s,p)*pow(pow(y,-1,p),e,p)%p,commitment)

    def test_probability_and_linear_differential_tables(self):
        self.assertAlmostEqual(.6**2+.4**2,.52)
        self.assertAlmostEqual(16*15/2/256,.46875)
        self.assertEqual(sum(range(1,17))/16,8.5)
        s=[0,1,3,6,7,4,5,2]
        matches=[x for x in range(8) if (x&1)==(s[x]&1)]
        self.assertEqual(matches,[0,1]);self.assertEqual(len(matches)/8-.5,-.25)
        self.assertEqual([s[x]^s[x^1] for x in range(8)],[1,1,5,5,3,3,7,7])

    def test_pqc_and_sifting(self):
        self.assertEqual((2*2-1,0-3),(3,-3))
        self.assertAlmostEqual(math.hypot(.2,.2),.282842712474619)
        self.assertEqual(((2*2+3)%5,(2+3*3)%5),(2,1))
        self.assertEqual(sum(a!=b for a,b in zip('101','111')),1)
        self.assertEqual([b for b,a,c in zip([0,1,1,0],'+x+x','+++x') if a==c],[0,1,0])
        self.assertEqual(0b1100^0b0101,0b1010^0b0011)


if __name__=='__main__':unittest.main()
