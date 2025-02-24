class BN:
    def __init__(self, value: int):
        self.value = int(value)
    
    def to_bytes(self, length: int, byteorder: str, signed: bool = False) -> bytes:
        return self.value.to_bytes(length, byteorder, signed=signed)
    
    def __add__(self, other):
        return BN(self.value + int(other))
    
    def __sub__(self, other):
        return BN(self.value - int(other))
    
    def __mul__(self, other):
        return BN(self.value * int(other))
    
    def __floordiv__(self, other):
        return BN(self.value // int(other))
    
    def __mod__(self, other):
        return BN(self.value % int(other))
    
    def __neg__(self):
        return BN(-self.value)
    
    def __repr__(self):
        return f"BN({self.value})"
    
    def __int__(self):
        return self.value
    
    def is_neg(self):
        return self.value < 0