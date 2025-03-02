import unittest
from src.Parser import Parser


class HW4Test(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(HW4Test, self).__init__(*args, **kwargs)
        self.__class__.score = 0

    @classmethod
    def tearDownClass(cls):
        print("\nHomework 3 - Total score:", cls.score, "/ 25\n")

    def test_1(self):
        parser = Parser()
        string = "(a + b)"
        result = parser.parse(string)
        self.assertEqual(str(result), "Parant (Plus (Var \"a\") (Var \"b\"))")
        HW4Test.score += 1
        
    def test_2(self):
        parser = Parser()
        string = "a + (b * c)"
        result = parser.parse(string)
        self.assertEqual(str(result), "Plus (Var \"a\") (Parant (Mult (Var \"b\") (Var \"c\")))")
        HW4Test.score += 1
        
    def test_3(self):
        parser = Parser()
        string = "(a - b) * (c + d)"
        result = parser.parse(string)
        self.assertEqual(str(result), "Mult (Parant (Minus (Var \"a\") (Var \"b\"))) (Parant (Plus (Var \"c\") (Var \"d\")))")
        HW4Test.score += 1
		
    def test_4(self):
        parser = Parser()
        string = "(a - 4) - (4 * (c + d))"
        result = parser.parse(string)
        self.assertEqual(str(result), "Minus (Parant (Minus (Var \"a\") (Val 4))) (Parant (Mult (Val 4) (Parant (Plus (Var \"c\") (Var \"d\")))))")
        HW4Test.score += 1
        
    def test_5(self):
        parser = Parser()
        string = "5 + ((x * 3) * (y - ((z * 2) * (x + (y -z)))))"
        result = parser.parse(string)
        self.assertEqual(str(result), "Plus (Val 5) (Parant (Mult (Parant (Mult (Var \"x\") (Val 3))) (Parant (Minus (Var \"y\") (Parant (Mult (Parant (Mult (Var \"z\") (Val 2))) (Parant (Plus (Var \"x\") (Parant (Minus (Var \"y\") (Var \"z\")))))))))))")
        HW4Test.score += 1
        
    def test_6(self):
        parser = Parser()
        string = "\\x.x"
        result = parser.parse(string)
        self.assertEqual(str(result), "Lambda (Var \"x\") -> Var \"x\"")
        HW4Test.score += 2
    
    def test_7(self):
        parser = Parser()
        string = "\\x.(x + 2)"
        result = parser.parse(string)
        self.assertEqual(str(result), "Lambda (Var \"x\") -> Parant (Plus (Var \"x\") (Val 2))")
        HW4Test.score += 2
        
    def test_8(self):
        parser = Parser()
        string = "\\x.(x + (7 * y))"
        result = parser.parse(string)
        self.assertEqual(str(result), "Lambda (Var \"x\") -> Parant (Plus (Var \"x\") (Parant (Mult (Val 7) (Var \"y\"))))")
        HW4Test.score += 2
    
    def test_9(self):
        parser = Parser()
        string = "\\x.\\y.(x + y)"
        result = parser.parse(string)
        self.assertEqual(str(result), "Lambda (Var \"x\") -> Lambda (Var \"y\") -> Parant (Plus (Var \"x\") (Var \"y\"))")
        HW4Test.score += 2
        
    def test_10(self):
        parser = Parser()
        string = "\\x.\\y.(x + (y / z))"
        result = parser.parse(string)
        self.assertEqual(str(result), "Lambda (Var \"x\") -> Lambda (Var \"y\") -> Parant (Plus (Var \"x\") (Parant (Div (Var \"y\") (Var \"z\"))))")
        HW4Test.score += 2
        
    def test_11(self):
        parser = Parser()
        string = "\\x.\\y.\\z.(x - (y + z))"
        result = parser.parse(string)
        self.assertEqual(str(result), "Lambda (Var \"x\") -> Lambda (Var \"y\") -> Lambda (Var \"z\") -> Parant (Minus (Var \"x\") (Parant (Plus (Var \"y\") (Var \"z\"))))")
        HW4Test.score += 2
        
    def test_12(self):
        parser = Parser()
        string = "\\x.\\y.\\z.(7 + ((y * z) + (x - y)))"
        result = parser.parse(string)
        self.assertEqual(str(result), "Lambda (Var \"x\") -> Lambda (Var \"y\") -> Lambda (Var \"z\") -> Parant (Plus (Val 7) (Parant (Plus (Parant (Mult (Var \"y\") (Var \"z\"))) (Parant (Minus (Var \"x\") (Var \"y\"))))))")
        HW4Test.score += 2
        
    def test_13(self):
        parser = Parser()
        string = "\\x.\\y.\\z.(x + (z * \\x.(x * y)))"
        result = parser.parse(string)
        self.assertEqual(str(result), "Lambda (Var \"x\") -> Lambda (Var \"y\") -> Lambda (Var \"z\") -> Parant (Plus (Var \"x\") (Parant (Mult (Var \"z\") (Lambda (Var \"x\") -> Parant (Mult (Var \"x\") (Var \"y\"))))))")
        HW4Test.score += 3
        
    def test_14(self):
        parser = Parser()
        string = "\\x.\\y.\\z.\\v.(x + (z * \\x.(x * \\y.(y - \\z.(z * \\v.(v + x))))))"
        result = parser.parse(string)
        self.assertEqual(str(result), "Lambda (Var \"x\") -> Lambda (Var \"y\") -> Lambda (Var \"z\") -> Lambda (Var \"v\") -> Parant (Plus (Var \"x\") (Parant (Mult (Var \"z\") (Lambda (Var \"x\") -> Parant (Mult (Var \"x\") (Lambda (Var \"y\") -> Parant (Minus (Var \"y\") (Lambda (Var \"z\") -> Parant (Mult (Var \"z\") (Lambda (Var \"v\") -> Parant (Plus (Var \"v\") (Var \"x\"))))))))))))")
        HW4Test.score += 3
        
    
