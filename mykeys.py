import secrets

# Generate a random 256-bit key encoded as a hexadecimal string
secret_key = secrets.token_hex(32)  # 32 bytes = 256 bits
print("Generated JWT Secret Key:", secret_key)

uri = "postgresql+psycopg2://postgres:Borkounou%40123@localhost:5432/mahrasoft"