package utils

func CalculateEMA(prices []float64, n int) []float64 {
	ema := make([]float64, len(prices))

	// Calculate the initial SMA as the first value
	sum := 0.0
	for i := 0; i < n; i++ {
		sum += prices[i]
	}
	sma := sum / float64(n)
	ema[n-1] = sma

	// Calculate the EMA for the remaining values
	multiplier := 2.0 / float64(n+1)
	for i := n; i < len(prices); i++ {
		ema[i] = (prices[i]-ema[i-1])*multiplier + ema[i-1]
	}

	return ema
}
