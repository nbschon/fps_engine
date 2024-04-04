import sys

def hex_to_srgb(comp: int) -> float:
    adj = ((comp / 255 + 0.055) / 1.055) ** 2.4
    return adj

def main():
    if len(sys.argv) == 2:
        hex = int(sys.argv[1], 16)
        r: int = (hex & 0xFF0000) >> 16
        g: int = (hex & 0x00FF00) >> 8
        b: int = (hex & 0x0000FF)
        r_adj = hex_to_srgb(r)
        g_adj = hex_to_srgb(g)
        b_adj = hex_to_srgb(b)
        print(f"Hex vals #{r:02X}{g:02X}{b:02X}, sRGB vals: ({r_adj:.5}, {g_adj:.5}, {b_adj:.5})")

if __name__ == "__main__":
    main()
