"""Independent calculations: no expected values are read from Markdown/data strings."""
import math
import unittest


def matmul(a, b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def f4bit(c):
    if not c:
        raise ValueError('zero has no bit')
    return abs(c) % 2 if c > 0 else 1 - abs(c) % 2


def syndrome(coefficients):
    s = 0
    for j, c in enumerate(coefficients, 1):
        if f4bit(c):
            s ^= j
    return s


class ReviewedExamples(unittest.TestCase):
    def test_affine_all_symbols(self):
        for x in range(26):
            y = (5*x+8) % 26
            self.assertEqual(pow(5,-1,26)*(y-8) % 26,x)
        self.assertEqual((5*7+8)%26,17)
        self.assertEqual((2*0+8)%26,(2*13+8)%26)

    def test_hill_matrix_and_inverse(self):
        k,ki=[[3,3],[2,5]],[[15,17],[20,9]]
        self.assertEqual([[x%26 for x in r] for r in matmul(ki,k)],[[1,0],[0,1]])
        self.assertEqual([r[0]%26 for r in matmul(k,[[7],[8]])],[19,2])
        self.assertEqual([r[0]%26 for r in matmul(ki,[[19],[2]])],[7,8])
        self.assertEqual(math.gcd(9,26),1)
        self.assertNotEqual(math.gcd(2,26),1)

    def test_classical_permutations(self):
        for text,perm,expected in [('ABCD',[2,1,4,3],'BADC'),('ABCD',[3,1,4,2],'CADB')]:
            cipher=''.join(text[i-1] for i in perm)
            self.assertEqual(cipher,expected)
            inverse=[perm.index(i)+1 for i in range(1,5)]
            self.assertEqual(''.join(cipher[i-1] for i in inverse),text)
        table={'A':'C','B':'A','C':'D','D':'B'}
        self.assertEqual(''.join(table[x] for x in 'ABBA'),'CAAC')
        grid=[['A','B'],['D','C']]
        self.assertEqual(''.join(grid[r][c] for r,c in [(0,0),(0,1),(1,1),(1,0)]),'ABCD')

    def test_playfair(self):
        table=['ABCDE','FGHIK','LMNOP','QRSTU','VWXYZ']
        positions={c:(r,col) for r,row in enumerate(table) for col,c in enumerate(row)}
        def transform(pair,step):
            (r,a),(s,b)=[positions[c] for c in pair]
            if r==s:return table[r][(a+step)%5]+table[s][(b+step)%5]
            if a==b:return table[(r+step)%5][a]+table[(s+step)%5][b]
            return table[r][b]+table[s][a]
        self.assertEqual([transform(p,1) for p in ['BA','LX','LO','ON']],['CB','NV','MP','PO'])
        self.assertEqual([transform(p,-1) for p in ['CB','NV','MP','PO']],['BA','LX','LO','ON'])

    def test_vigenere_and_secrecy(self):
        self.assertEqual([(x+[1,24][i%2])%26 for i,x in enumerate([2,0,19])],[3,24,20])
        joint={(m,k):p*.5 for m,p in [(0,.8),(1,.2)] for k in (0,1)}
        for c in (0,1):
            denominator=sum(p for (m,k),p in joint.items() if m^k==c)
            numerator=sum(p for (m,k),p in joint.items() if m==0 and m^k==c)
            self.assertAlmostEqual(numerator/denominator,.8)

    def test_size_color_rle(self):
        self.assertEqual(3*2*3*8//8,18)
        self.assertEqual(2*math.ceil(9/4)*4,24)
        rgb=(100,150,200)
        self.assertEqual([round(x) for x in [.299*rgb[0]+.587*rgb[1]+.114*rgb[2],128-.169*rgb[0]-.331*rgb[1]+.5*rgb[2],128+.5*rgb[0]-.419*rgb[1]-.081*rgb[2]]],[141,161,99])
        pairs=[(7,4),(2,2),(9,2)]
        self.assertEqual([x for x,n in pairs for _ in range(n)],[7,7,7,7,2,2,9,9])
        self.assertEqual(12000/(100+200+3700),3)

    def test_jpeg_dct_independent_sum(self):
        def dct(u,v):
            a=(1/math.sqrt(2) if u==0 else 1)*(1/math.sqrt(2) if v==0 else 1)
            return a/4*sum(2*math.cos((2*x+1)*u*math.pi/16)*math.cos((2*y+1)*v*math.pi/16) for x in range(8) for y in range(8))
        self.assertAlmostEqual(dct(0,0),16)
        for u in range(8):
            for v in range(8):
                if u or v:self.assertAlmostEqual(dct(u,v),0)
        self.assertEqual(32/8+128,132)

    def test_transforms_and_wavelets(self):
        t=[[1/math.sqrt(2),1/math.sqrt(2)],[1/math.sqrt(2),-1/math.sqrt(2)]]
        g=matmul(matmul(t,[[2,2],[0,0]]),t)
        for row,expected in zip(g,[[2,0],[2,0]]):
            for x,y in zip(row,expected):self.assertAlmostEqual(x,y)
        h=[[1,1,1,1],[1,-1,1,-1],[1,1,-1,-1],[1,-1,-1,1]]
        self.assertEqual(matmul(h,[[1],[2],[3],[4]]),[[10],[-2],[-4],[0]])
        self.assertEqual(matmul(h,[[10],[-2],[-4],[0]]),[[4],[8],[12],[16]])
        coeff=[]
        for a,b in [(4,2),(6,0)]:
            low,high=(a+b)/math.sqrt(2),(a-b)/math.sqrt(2);coeff.extend([low,high])
            self.assertAlmostEqual((low+high)/math.sqrt(2),a)
            self.assertAlmostEqual((low-high)/math.sqrt(2),b)
        self.assertAlmostEqual(sum(x*x for x in coeff),56)

    def test_pixel_methods_exhaustive(self):
        for p in range(256):
            for bit in (0,1):
                s=p-(p%2)+bit
                self.assertEqual(s%2,bit);self.assertLessEqual(abs(s-p),1)
                self.assertTrue(0<=s<=255)
        self.assertEqual([p-p%2+b for p,b in zip([124,115,117,255],[1,0,0,0])],[125,114,116,254])
        self.assertEqual([p%2 for p in [1,254,100,101]],[1,0,0,1])
        self.assertEqual([p%2 for p in [21,21,254,254]],[1,1,0,0])

    def test_qim_variants_and_boundary(self):
        floor_embed=lambda p,q,m:q*(p//q)+(q//2)*m
        self.assertEqual(floor_embed(124,4,1),126);self.assertEqual(floor_embed(117,4,0),116)
        nearest=lambda x,b:min((j*10+b*5 for j in range(-10,11)),key=lambda z:(abs(x-z),z))
        self.assertEqual(nearest(19,0),20);self.assertEqual(floor_embed(19,10,0),10)
        self.assertEqual(min((0,1),key=lambda b:(abs(13-nearest(13,b)),b)),1)
        self.assertEqual(min((0,1),key=lambda b:(abs(12.5-nearest(12.5,b)),b)),0)

    def test_pvd_and_nmi(self):
        d=100-90;target=8+int('101',2);delta=target-d
        pair=(100+delta//2,90-math.ceil(delta/2))
        self.assertEqual(pair,(101,88));self.assertEqual(abs(pair[0]-pair[1])-8,5)
        p12=(124+115)//2;p21=(124+158)//2;p22=(124+p12+p21)//3
        self.assertEqual((p12,p21,p22),(119,141,128))
        self.assertEqual((p12+3,p21+2,p22+3),(122,143,131))
        self.assertEqual([int(math.log2(abs(p-124))) for p in [p12,p21,p22]],[2,4,2])

    def test_jpeg_steganography(self):
        self.assertTrue(abs(14)-abs(-9)>4);self.assertFalse(abs(13)-abs(-9)>4)
        embed=lambda c,b:(1 if c>0 else -1)*(abs(c)-abs(c)%2+b)
        self.assertEqual([embed(c,b) for c,b in zip([-4,3,6],[1,0,1])],[-5,2,7])
        self.assertEqual(f4bit(-3),0);self.assertEqual(abs(-3)%2,1)
        self.assertEqual(syndrome([2,3,4]),2)
        self.assertEqual(syndrome([1,3,4]),3)
        self.assertEqual(syndrome([1,2,2]),1)
        self.assertEqual(syndrome([2,2,3]),3)
        self.assertEqual(syndrome([2,2,2]),0)

    def test_metrics_and_classifiers(self):
        mse=sum((a-b)**2 for a,b in zip([10,20,30,40],[11,20,29,42]))/4
        self.assertEqual(mse,1.5);self.assertAlmostEqual(10*math.log10(255**2/mse),46.369891,places=5)
        self.assertEqual(sum(a!=b for a,b in zip('10110010','10010000')),2)
        self.assertAlmostEqual(2/math.sqrt(4*2),1/math.sqrt(2))
        self.assertAlmostEqual(sum((x-10)**2/10 for x in [14,6]),3.2)
        self.assertAlmostEqual(sum((x-10)**2/10 for x in [8,12,5,15]),5.8)
        self.assertAlmostEqual(.24/(.03+.24),8/9)
        self.assertAlmostEqual((-math.log(.8)-math.log(.7))/2,.2899092476264711)
        self.assertAlmostEqual((10/100+30/100)/2,40/200)

    def test_planes_and_rounding(self):
        self.assertEqual([p%2 for p in [100,101,102,103]],[0,1,0,1])
        self.assertEqual([(p//2)%2 for p in [100,101,102,103]],[0,0,1,1])
        self.assertEqual([round(x) for x in [10.5,13.5]],[10,14])
        self.assertEqual([math.floor(x+.5) for x in [10.5,13.5]],[11,14])


if __name__=='__main__':unittest.main()
