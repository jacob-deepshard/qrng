import time
import requests

def quantum_random_byte():
    """
    Fetch a single random byte (0-255) from the ANU Quantum Random Numbers server.
    Raises an exception if the request fails.
    """
    url = "https://qrng.anu.edu.au/API/jsonI.php?length=1&type=uint8"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and len(data['data']) == 1:
            return data['data'][0]
        else:
            raise ValueError("Unexpected API response structure.")
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch quantum random byte: {e}")

def quantum_choice(choices, weights=None):
    """
    Choose one element from choices using a quantum random number.

    Parameters:
    - choices: A list (or other sequence) of strings from which we are selecting.
    - weights: Optional list of non-negative numbers representing probabilities
      (do not need to be normalized). If None, uniform probability is assumed.

    Returns:
    A single randomly selected string.
    """
    if weights is None:
        weights = [1] * len(choices)

    # Normalize weights to sum to 255 (max value of a byte)
    total = sum(weights)
    normalized_weights = [int((w / total) * 255) for w in weights]
    
    # Ensure weights sum to exactly 255 by adjusting rounding errors
    adjustment = 255 - sum(normalized_weights)
    if adjustment > 0:
        # Add remaining weight to largest probability
        max_idx = weights.index(max(weights))
        normalized_weights[max_idx] += adjustment
    
    # Create mapping of byte values to choices
    choice_map = []
    for choice, weight in zip(choices, normalized_weights):
        choice_map.extend([choice] * weight)
        
    # Get quantum random byte and map to choice
    random_byte = quantum_random_byte()
    return choice_map[random_byte]

def test_quantum_choice_distribution():
    fruits = ["apple", "banana", "cherry"]
    weights = [1, 2, 3]
    
    # Run multiple samples to test distribution
    samples = 1000
    results = {}
    for _ in range(samples):
        choice = quantum_choice(fruits, weights)
        results[choice] = results.get(choice, 0) + 1
    
    # Calculate and display actual vs expected distributions
    total_weight = sum(weights)
    print("\nDistribution test results:")
    print(f"{'Fruit':<10} {'Actual %':>10} {'Expected %':>12}")
    print("-" * 32)
    for fruit, weight in zip(fruits, weights):
        actual_pct = (results.get(fruit, 0) / samples) * 100
        expected_pct = (weight / total_weight) * 100
        print(f"{fruit:<10} {actual_pct:>10.1f}% {expected_pct:>11.1f}%")

def test_quantum_choice_rate_limit():
    for freq in [0.1, 0.5, 1, 2, 5, 10, 20, 50, 100]:
        # test making freq calls per second
        sleep_time = 1 / freq
        for _ in range(10):
            quantum_choice(["test"], [1])
            time.sleep(sleep_time)
        print(f"Made {freq} calls per second")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Quantum random choice generator')
    parser.add_argument('choices', nargs='*', help='List of choices to select from')
    parser.add_argument('-w', '--weights', nargs='*', type=float, help='Optional weights for choices')
    parser.add_argument('--test-distribution', action='store_true', help='Run distribution test')
    parser.add_argument('--test-rate-limit', action='store_true', help='Run rate limit test')
    
    args = parser.parse_args()
    
    if args.test_distribution:
        test_quantum_choice_distribution()
    elif args.test_rate_limit:
        test_quantum_choice_rate_limit()
    else:
        if not args.choices:
            args.choices = ["apple", "banana", "cherry"]
            args.weights = [1, 2, 3]
        elif args.weights and len(args.weights) != len(args.choices):
            parser.error("Number of weights must match number of choices")
        elif not args.weights:
            args.weights = [1] * len(args.choices)
            
        print(quantum_choice(args.choices, args.weights))
