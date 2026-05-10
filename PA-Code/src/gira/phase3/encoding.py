"""编码抽象层: 哥德尔编码、ASCII、UTF-8 等映射的统一接口。

每个编码器实现:
  encode(formula: Formula) -> int   # 公式 → 编码数
  decode(gn: int) -> str            # 编码数 → 公式串

当前实现:
  - GodelEncoder: 质数幂编码(严格版)
  - AsciiEncoder: ASCII 连接编码
  - Utf8Encoder:  UTF-8 字节编码

所有编码器支持查表缓存(System Cache):
  encode_cache: Dict[str, int]   # formula_str → code
  decode_cache: Dict[int, str]   # code → formula_str
"""

from __future__ import annotations
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, ClassVar


class EncodingCache:
    """编码缓存(避免大数分解/重复计算)。"""
    def __init__(self):
        self._encode: Dict[str, int] = {}
        self._decode: Dict[int, str] = {}

    def get_encode(self, formula_str: str) -> Optional[int]:
        return self._encode.get(formula_str)

    def set_encode(self, formula_str: str, code: int):
        self._encode[formula_str] = code
        self._decode[code] = formula_str

    def get_decode(self, code: int) -> Optional[str]:
        return self._decode.get(code)


# ============================================================
# 抽象基类
# ============================================================

class FormulaEncoder(ABC):
    """公式编码器抽象接口。"""

    def __init__(self):
        self.cache = EncodingCache()

    @abstractmethod
    def encode(self, formula_str: str) -> int:
        """公式字符串 → 编码数。"""
        pass

    @abstractmethod
    def decode(self, code: int) -> str:
        """编码数 → 公式字符串。"""
        pass

    def _encoded_length(self, code: int) -> int:
        """编码数的近似长度。"""
        return len(str(code)) if code > 0 else 0


# ============================================================
# GodelEncoder: 严格哥德尔编码
# ============================================================

class GodelEncoder(FormulaEncoder):
    """严格哥德尔编码: 符号→质数, 公式→Π p_i^code(s_i)。"""

    SYMBOL_CODE: ClassVar[Dict[str, int]] = {}
    CODE_SYMBOL: ClassVar[Dict[int, str]] = {}

    @classmethod
    def load_symbols(cls, symbol_map: Dict[str, int]):
        """加载符号→质数映射表。"""
        cls.SYMBOL_CODE = dict(symbol_map)
        cls.CODE_SYMBOL = {v: k for k, v in symbol_map.items()}

    def __init__(self, symbol_map: Optional[Dict[str, int]] = None):
        super().__init__()
        if symbol_map:
            self.load_symbols(symbol_map)
        self._position_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
                                 31, 37, 41, 43, 47, 53, 59, 61, 67,
                                 71, 73, 79, 83, 89, 97, 101, 103, 107,
                                 109, 113, 127, 131, 137, 139, 149, 151]

    def _pos_prime(self, i: int) -> int:
        """获取第 i 个位置质数, 动态扩展。"""
        if i < len(self._position_primes):
            return self._position_primes[i]
        p = self._position_primes[-1] + 2
        while len(self._position_primes) <= i:
            while True:
                is_prime = True
                for q in self._position_primes:
                    if q * q > p:
                        break
                    if p % q == 0:
                        is_prime = False
                        break
                if is_prime:
                    self._position_primes.append(p)
                    break
                p += 2
            p += 2
        return self._position_primes[i]

    def encode(self, formula_str: str) -> int:
        cached = self.cache.get_encode(formula_str)
        if cached is not None:
            return cached

        n = 1
        for i, ch in enumerate(formula_str):
            code = self.SYMBOL_CODE.get(ch, 1)
            n *= pow(self._pos_prime(i), code)

        self.cache.set_encode(formula_str, n)
        return n

    def decode(self, code: int) -> str:
        cached = self.cache.get_decode(code)
        if cached is not None:
            return cached

        chars = []
        n = code
        for i, p in enumerate(self._position_primes):
            if n <= 1:
                break
            exp = 0
            while n % p == 0:
                n //= p
                exp += 1
            if exp > 0 and exp in self.CODE_SYMBOL:
                chars.append(self.CODE_SYMBOL[exp])
            if n <= 1:
                break

        result = ''.join(chars)
        self.cache.set_decode(code, result)
        return result


# ============================================================
# AsciiEncoder: ASCII 编码(验证性)
# ============================================================

class AsciiEncoder(FormulaEncoder):
    """ASCII 连接编码: formula_str → 每个字符 ASCII 值的拼接。"""

    def encode(self, formula_str: str) -> int:
        cached = self.cache.get_encode(formula_str)
        if cached is not None:
            return cached
        code = int(''.join(str(ord(c)) for c in formula_str))
        self.cache.set_encode(formula_str, code)
        return code

    def decode(self, code: int) -> str:
        cached = self.cache.get_decode(code)
        if cached is not None:
            return cached
        s = str(code)
        chars = []
        i = 0
        while i < len(s):
            # ASCII 范围: 32-126, 按 2-3 位分割
            if i + 2 <= len(s) and 32 <= int(s[i:i+2]) <= 99:
                chars.append(chr(int(s[i:i+2])))
                i += 2
            elif i + 3 <= len(s):
                chars.append(chr(int(s[i:i+3])))
                i += 3
            else:
                break
        result = ''.join(chars)
        self.cache.set_decode(code, result)
        return result


# ============================================================
# Utf8Encoder: UTF-8 编码(验证性)
# ============================================================

class Utf8Encoder(FormulaEncoder):
    """UTF-8 字节码编码。"""

    def encode(self, formula_str: str) -> int:
        cached = self.cache.get_encode(formula_str)
        if cached is not None:
            return cached
        code = int.from_bytes(formula_str.encode('utf-8'), 'big')
        self.cache.set_encode(formula_str, code)
        return code

    def decode(self, code: int) -> str:
        cached = self.cache.get_decode(code)
        if cached is not None:
            return cached
        length = max(1, (code.bit_length() + 7) // 8)
        try:
            result = code.to_bytes(length, 'big').decode('utf-8')
        except:
            result = ""
        self.cache.set_decode(code, result)
        return result


# ============================================================
# 编码注册中心
# ============================================================

_encoders: Dict[str, FormulaEncoder] = {}

def register_encoder(name: str, encoder: FormulaEncoder):
    _encoders[name] = encoder

def get_encoder(name: str = "godel") -> FormulaEncoder:
    if not _encoders:
        _init_defaults()
    return _encoders.get(name, _encoders["godel"])

def _init_defaults():
    from gira.phase3.language import SYMBOL_GN
    godel = GodelEncoder(symbol_map=SYMBOL_GN)
    register_encoder("godel", godel)
    register_encoder("ascii", AsciiEncoder())
    register_encoder("utf8", Utf8Encoder())

def list_encoders() -> List[str]:
    if not _encoders:
        _init_defaults()
    return list(_encoders.keys())
