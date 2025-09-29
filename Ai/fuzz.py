import numpy as np
import skfuzzy as fuzz

def main():

    x = np.linspace(0, 10, 100)

    
    A = fuzz.trimf(x, [0, 2, 5])
    B = fuzz.trimf(x, [3, 5, 8])

    
    and_result = np.fmin(A, B)
    or_result = np.fmax(A, B)


    print("AND (first 5 values):", and_result[:5])
    print("OR (first 5 values):", or_result[:5])

if __name__ == "__main__":
    main()