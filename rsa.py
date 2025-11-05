P = 1103
Q = 1181

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_inverse(e, phi):
    m0, x0, x1 = phi, 0, 1
    while e > 1:
        q = e // phi
        phi, e = e % phi, phi
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def generate_alice_keys():
    n = P * Q
    phi = (P - 1) * (Q - 1)

    e = 65537
    if gcd(e, phi) != 1:
        e = 3

    d = mod_inverse(e, phi)
    return (n, e, d)

def generate_bob_keys():
    n = P * Q
    phi = (P - 1) * (Q - 1)

    e = 17
    while gcd(e, phi) != 1 or e == 65537 or e == 3:
        e += 2

    d = mod_inverse(e, phi)
    return (n, e, d)

def encrypt(message, e, n):
    return pow(message, e, n)

def decrypt(ciphertext, d, n):
    return pow(ciphertext, d, n)