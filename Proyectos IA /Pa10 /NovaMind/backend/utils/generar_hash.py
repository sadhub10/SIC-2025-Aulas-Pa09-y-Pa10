from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "admin123"
hash_generado = pwd_context.hash(password)

print(f"Password: {password}")
print(f"Hash: {hash_generado}")
print()
print("Copia este hash al archivo usuarios.sql")
