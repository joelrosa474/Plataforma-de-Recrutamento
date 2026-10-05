import unittest

from src.infrastructure.security.hasher import Hasher


class TestHasher(unittest.TestCase):
    def test_gerar_hash_rejeita_senha_longa(self):
        senha = "a" * 73

        with self.assertRaisesRegex(ValueError, "72"):
            Hasher.gerar_hash(senha)


if __name__ == "__main__":
    unittest.main()
